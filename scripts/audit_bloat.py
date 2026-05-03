#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Audit which skills/agents have actually been invoked across all sessions.

Reads session JSONL files in ~/.claude/projects/, counts Agent(subagent_type=X)
and Skill(skill=Y) tool calls, ranks by usage and recency.

The "keep" list is whatever you've actually invoked. Everything else is a
candidate to archive.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
NOW = datetime.now(timezone.utc)
BUCKETS = [
    ("last_7d", timedelta(days=7)),
    ("last_30d", timedelta(days=30)),
    ("last_90d", timedelta(days=90)),
]


def parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def scan_sessions() -> tuple[dict[str, list[datetime]], dict[str, list[datetime]]]:
    agent_usage: dict[str, list[datetime]] = defaultdict(list)
    skill_usage: dict[str, list[datetime]] = defaultdict(list)

    files = list(PROJECTS_DIR.rglob("*.jsonl"))
    print(f"scanning {len(files)} session files...", file=sys.stderr)

    for fp in files:
        try:
            with fp.open() as f:
                for line in f:
                    if '"tool_use"' not in line:
                        continue
                    if '"Agent"' not in line and '"Skill"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    msg = rec.get("message") or {}
                    content = msg.get("content") or []
                    if not isinstance(content, list):
                        continue
                    ts = parse_iso(rec.get("timestamp", ""))
                    if ts is None:
                        continue
                    for block in content:
                        if not isinstance(block, dict) or block.get("type") != "tool_use":
                            continue
                        name = block.get("name")
                        inp = block.get("input") or {}
                        if name == "Agent":
                            sub = inp.get("subagent_type")
                            if sub:
                                agent_usage[sub].append(ts)
                        elif name == "Skill":
                            sk = inp.get("skill")
                            if sk:
                                skill_usage[sk].append(ts)
        except (OSError, PermissionError):
            continue

    return agent_usage, skill_usage


def bucket(timestamps: list[datetime]) -> str:
    if not timestamps:
        return "never"
    age = NOW - max(timestamps)
    for label, delta in BUCKETS:
        if age <= delta:
            return label
    return "older_than_90d"


def render(kind: str, usage: dict[str, list[datetime]]) -> None:
    print(f"\n{'=' * 78}")
    print(f"{kind.upper()} ACTUALLY INVOKED")
    print(f"{'=' * 78}")

    if not usage:
        print("(none)")
        return

    rows = [(name, len(ts), max(ts), bucket(ts)) for name, ts in usage.items()]
    rows.sort(key=lambda r: (-r[1], r[0]))

    by_bucket: dict[str, list] = defaultdict(list)
    for r in rows:
        by_bucket[r[3]].append(r)

    summary = {b: len(by_bucket.get(b, [])) for b in
               ["last_7d", "last_30d", "last_90d", "older_than_90d"]}
    total_calls = sum(r[1] for r in rows)
    print(f"\nUnique {kind} ever invoked: {len(rows)}  |  "
          f"Total invocations: {total_calls}")
    print(f"Recency buckets: {summary}\n")

    for b in ["last_7d", "last_30d", "last_90d", "older_than_90d"]:
        items = by_bucket.get(b, [])
        if not items:
            continue
        print(f"--- {b} ({len(items)}) ---")
        for name, count, last, _ in items:
            print(f"  {name:60s}  uses={count:<5d}  last={last.date().isoformat()}")
        print()


def main() -> None:
    agent_usage, skill_usage = scan_sessions()
    render("agents", agent_usage)
    render("skills", skill_usage)


if __name__ == "__main__":
    main()
