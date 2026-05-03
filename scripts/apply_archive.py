#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Apply the archive plan from plan_archive.py.

Defaults to dry-run. Pass --apply to actually mutate state.

Actions when --apply:
  1. Backup ~/.claude/settings.json -> settings.json.bak.<timestamp>
  2. Flip enabledPlugins entries to false for the disable list
  3. Create ~/.claude/agents/_archive/ and mv non-keep loose agents into it

Reversal: restore settings.json.bak.<ts>; mv _archive/*.md back to agents/.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
PROJECTS_DIR = HOME / ".claude" / "projects"
LOOSE_AGENTS_DIR = HOME / ".claude" / "agents"
SETTINGS = HOME / ".claude" / "settings.json"
ARCHIVE_DIR = LOOSE_AGENTS_DIR / "_archive"
NOW = datetime.now(timezone.utc)
CUTOFF_DAYS = 90

# Final overrides per user decisions:
KEEP_PLUGINS_REGARDLESS = {
    "vercel@claude-plugins-official",
    "code-simplifier@claude-plugins-official",
    "context7@claude-plugins-official",
    "code-review@claude-plugins-official",
    "feature-dev@claude-plugins-official",
    "superpowers@superpowers-marketplace",
    "learning-output-style@claude-plugins-official",  # user: Y keep
}


def parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def scan_usage() -> tuple[set[str], set[str]]:
    """Return (agent_names_invoked_within_cutoff, skill_names_invoked_within_cutoff)."""
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

    cutoff = NOW.timestamp() - CUTOFF_DAYS * 86400
    a = {n for n, t in agents.items() if t.timestamp() >= cutoff
         and not n.startswith("compound-engineering")}
    s = {n for n, t in skills.items() if t.timestamp() >= cutoff
         and not n.startswith("compound-engineering")}
    return a, s


def parse_frontmatter_name(fp: Path) -> str | None:
    try:
        text = fp.read_text(errors="ignore")
    except OSError:
        return None
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
    if not m:
        return None
    nm = re.search(r"^name:\s*(.+?)\s*$", m.group(1), re.MULTILINE)
    return nm.group(1).strip() if nm else None


def compute_disable_list(settings: dict, used_skills: set[str], used_agents: set[str]) -> list[str]:
    enabled = settings.get("enabledPlugins", {})
    used_namespaces = {n.split(":", 1)[0] for n in (used_skills | used_agents) if ":" in n}
    out = []
    for plugin_id, currently_on in enabled.items():
        if not currently_on:
            continue
        if plugin_id in KEEP_PLUGINS_REGARDLESS:
            continue
        short = plugin_id.split("@", 1)[0]
        if short in used_namespaces and "compound-engineering" not in plugin_id:
            continue
        out.append(plugin_id)
    return sorted(out)


def compute_loose_archive(used_agents: set[str]) -> list[Path]:
    out = []
    for fp in sorted(LOOSE_AGENTS_DIR.glob("*.md")):
        yaml_name = parse_frontmatter_name(fp) or fp.stem
        if yaml_name in used_agents or fp.stem in used_agents:
            continue
        out.append(fp)
    return out


def main() -> None:
    apply = "--apply" in sys.argv
    mode = "APPLY" if apply else "DRY-RUN"
    print(f"[{mode}] starting")

    settings = json.loads(SETTINGS.read_text())
    used_agents, used_skills = scan_usage()

    disable_list = compute_disable_list(settings, used_skills, used_agents)
    archive_list = compute_loose_archive(used_agents)

    print(f"[{mode}] plugins to disable: {len(disable_list)}")
    for p in disable_list:
        print(f"  - {p}")
    print(f"[{mode}] loose agents to archive: {len(archive_list)}")

    if not apply:
        print(f"\n[DRY-RUN] no changes made. Re-run with --apply to mutate.")
        return

    # 1. Backup settings.json
    ts = NOW.strftime("%Y%m%d-%H%M%S")
    backup = SETTINGS.with_suffix(f".json.bak.{ts}")
    shutil.copy2(SETTINGS, backup)
    print(f"[APPLY] backed up settings -> {backup}")

    # 2. Mutate enabledPlugins
    enabled = settings.setdefault("enabledPlugins", {})
    for plugin_id in disable_list:
        enabled[plugin_id] = False
    SETTINGS.write_text(json.dumps(settings, indent=2) + "\n")
    print(f"[APPLY] settings.json updated ({len(disable_list)} plugins disabled)")

    # 3. Move loose agents
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    moved = 0
    for fp in archive_list:
        dest = ARCHIVE_DIR / fp.name
        if dest.exists():
            print(f"[APPLY] skip (exists in archive): {fp.name}")
            continue
        shutil.move(str(fp), str(dest))
        moved += 1
    print(f"[APPLY] moved {moved} loose agents -> {ARCHIVE_DIR}")
    print(f"[APPLY] done. Reversal: restore {backup.name}; mv {ARCHIVE_DIR}/*.md back.")


if __name__ == "__main__":
    main()
