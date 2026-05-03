#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Generate dry-run archive plan based on 90-day usage cutoff.

Reads usage from session JSONL files, then produces:
  1. List of plugins to disable (zero invocations + not in keep-overrides)
  2. List of loose agents to archive (YAML name not in invoked set)
  3. settings.json patch preview
  4. `mv` commands to relocate loose agent files to ~/.claude/agents/_archive/

Does NOT modify anything. Output the plan only.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
PROJECTS_DIR = HOME / ".claude" / "projects"
LOOSE_AGENTS_DIR = HOME / ".claude" / "agents"
SETTINGS = HOME / ".claude" / "settings.json"
ARCHIVE_DIR = LOOSE_AGENTS_DIR / "_archive"

NOW = datetime.now(timezone.utc)
CUTOFF = timedelta(days=90)

# User keep-overrides (per conversation):
# - keep simplify, vercel:* skills regardless of usage
# - archive compound-engineering even though recently used
KEEP_PLUGINS_REGARDLESS = {
    "vercel@claude-plugins-official",  # user wants vercel:* skills kept
    "code-simplifier@claude-plugins-official",  # user wants simplify kept (assumed source)
    "tk-agent-team@tk-agent-team",
    "context7@claude-plugins-official",  # MCP, used implicitly
    "code-review@claude-plugins-official",
    "feature-dev@claude-plugins-official",
    "superpowers@superpowers-marketplace",  # superpowers:* used within 90d
    # Disable explicitly even though recently invoked (per user):
}
ARCHIVE_PLUGINS_REGARDLESS: set[str] = set()  # populate if any compound-engineering plugin appears in enabledPlugins


def parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def scan_usage() -> tuple[dict[str, datetime], dict[str, datetime]]:
    """Return (last-seen-by-agent-name, last-seen-by-skill-name)."""
    agents: dict[str, datetime] = {}
    skills: dict[str, datetime] = {}
    for fp in PROJECTS_DIR.rglob("*.jsonl"):
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
                    ts = parse_iso(rec.get("timestamp", ""))
                    if ts is None:
                        continue
                    msg = rec.get("message") or {}
                    for block in msg.get("content") or []:
                        if not isinstance(block, dict) or block.get("type") != "tool_use":
                            continue
                        name = block.get("name")
                        inp = block.get("input") or {}
                        if name == "Agent":
                            sub = inp.get("subagent_type")
                            if sub:
                                agents[sub] = max(agents.get(sub, ts), ts)
                        elif name == "Skill":
                            sk = inp.get("skill")
                            if sk:
                                skills[sk] = max(skills.get(sk, ts), ts)
        except (OSError, PermissionError):
            continue
    return agents, skills


def within_cutoff(d: datetime) -> bool:
    return (NOW - d) <= CUTOFF


def parse_frontmatter_name(fp: Path) -> str | None:
    try:
        text = fp.read_text(errors="ignore")
    except OSError:
        return None
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        return None
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+?)\s*$", fm, re.MULTILINE)
    return nm.group(1).strip() if nm else None


def loose_agent_inventory() -> list[tuple[Path, str]]:
    rows = []
    for fp in sorted(LOOSE_AGENTS_DIR.glob("*.md")):
        name = parse_frontmatter_name(fp) or fp.stem
        rows.append((fp, name))
    return rows


def main() -> None:
    agents_used, skills_used = scan_usage()

    # Filter to within 90-day cutoff
    agents_kept = {n: t for n, t in agents_used.items() if within_cutoff(t)}
    skills_kept = {n: t for n, t in skills_used.items() if within_cutoff(t)}

    # Identify compound-engineering family for forced archive
    ce_agents = {n for n in agents_used if n.startswith("compound-engineering")}
    ce_skills = {n for n in skills_used if n.startswith("compound-engineering")}
    for n in ce_agents:
        agents_kept.pop(n, None)
    for n in ce_skills:
        skills_kept.pop(n, None)

    # Plugins from skill/agent namespaces that should be KEPT (because their items are used)
    used_plugin_namespaces: set[str] = set()
    for n in list(agents_kept) + list(skills_kept):
        if ":" in n and not n.startswith("compound-engineering"):
            used_plugin_namespaces.add(n.split(":", 1)[0])

    settings = json.loads(SETTINGS.read_text())
    enabled = settings.get("enabledPlugins", {})

    plugin_decisions: list[tuple[str, str, str]] = []  # (name, current, decision, reason)
    for plugin_id, currently_enabled in enabled.items():
        short = plugin_id.split("@", 1)[0]
        if plugin_id in KEEP_PLUGINS_REGARDLESS:
            decision = "KEEP"
            reason = "user override (active toolchain)"
        elif short in used_plugin_namespaces:
            decision = "KEEP"
            reason = f"items invoked: {short}:* within 90d"
        elif "compound-engineering" in plugin_id:
            decision = "DISABLE"
            reason = "user override: superseded by tk-agent-team"
        elif not currently_enabled:
            decision = "ALREADY-OFF"
            reason = "currently disabled"
        else:
            decision = "DISABLE"
            reason = "zero invocations in 90d"
        plugin_decisions.append((plugin_id, "on" if currently_enabled else "off", decision, reason))

    # Loose agents — keep if YAML name in agents_kept
    keep_loose: list[tuple[Path, str]] = []
    archive_loose: list[tuple[Path, str]] = []
    for fp, name in loose_agent_inventory():
        if name in agents_kept or fp.stem in agents_kept:
            keep_loose.append((fp, name))
        else:
            archive_loose.append((fp, name))

    # Render
    print("=" * 78)
    print("PLUGIN DECISIONS (settings.json enabledPlugins)")
    print("=" * 78)
    will_disable = [p for p in plugin_decisions if p[2] == "DISABLE" and p[1] == "on"]
    will_keep = [p for p in plugin_decisions if p[2] == "KEEP"]
    print(f"\nWill DISABLE (currently on): {len(will_disable)}")
    for plugin_id, _, _, reason in sorted(will_disable):
        print(f"  - {plugin_id:55s}  ({reason})")
    print(f"\nWill KEEP enabled: {len(will_keep)}")
    for plugin_id, _, _, reason in sorted(will_keep):
        print(f"  + {plugin_id:55s}  ({reason})")

    print("\n" + "=" * 78)
    print(f"LOOSE AGENTS — {LOOSE_AGENTS_DIR}")
    print("=" * 78)
    print(f"\nKEEP ({len(keep_loose)}):")
    for fp, name in keep_loose:
        last = agents_kept.get(name) or agents_kept.get(fp.stem)
        last_str = last.date().isoformat() if last else "?"
        print(f"  + {fp.name:50s}  yaml-name={name!r:30s}  last={last_str}")
    print(f"\nARCHIVE ({len(archive_loose)}):")
    for fp, name in archive_loose:
        print(f"  - {fp.name:50s}  yaml-name={name!r}")

    print("\n" + "=" * 78)
    print("MV COMMANDS (preview, not executed)")
    print("=" * 78)
    print(f"mkdir -p {ARCHIVE_DIR}")
    for fp, _ in archive_loose:
        print(f"mv {fp} {ARCHIVE_DIR}/")

    # Estimated impact
    print("\n" + "=" * 78)
    print("ESTIMATED IMPACT")
    print("=" * 78)
    total_agents_before = len(list(LOOSE_AGENTS_DIR.glob("*.md")))
    print(f"Loose agents: {total_agents_before} -> {len(keep_loose)} "
          f"({len(archive_loose)} archived)")
    total_plugins_before = sum(1 for _, on, _, _ in plugin_decisions if on == "on")
    new_disabled = sum(1 for _, _, d, _ in plugin_decisions if d == "DISABLE")
    print(f"Enabled plugins: {total_plugins_before} -> "
          f"{total_plugins_before - len(will_disable)} "
          f"({len(will_disable)} newly disabled, {new_disabled - len(will_disable)} already off)")


if __name__ == "__main__":
    main()
