#!/usr/bin/env python3
"""Stop hook validator for build-and-ship command.

Ensures all 5 phases of the build-and-ship pipeline completed before allowing stop.
Parses the session transcript JSONL to find evidence of each phase.

Exit codes:
  0 = all phases complete (or stop_hook_active guard)
  2 = blocked — missing phases (stderr explains which)
"""
import json
import re
import sys


def parse_transcript(transcript_path):
    """Parse JSONL transcript and return all tool_use blocks and tool results."""
    tool_uses = []
    tool_results = []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")
                content = msg.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue

                for block in content:
                    if not isinstance(block, dict):
                        continue

                    if msg_type == "assistant" and block.get("type") == "tool_use":
                        tool_uses.append(block)
                    elif block.get("type") == "tool_result":
                        tool_results.append(block)

    except (FileNotFoundError, PermissionError, OSError):
        pass

    return tool_uses, tool_results


def check_phase_1(tool_uses, tool_results):
    """Phase 1: Implementation — look for TaskUpdate with status completed."""
    for block in tool_uses:
        if block.get("name") == "TaskUpdate":
            inp = block.get("input", {})
            if inp.get("status") == "completed":
                return True
    return False


def check_phase_2(tool_uses, tool_results):
    """Phase 2: Local pre-flight — look for code-review dispatch + PASS."""
    has_review_dispatch = False
    has_pass = False

    for block in tool_uses:
        name = block.get("name", "")
        inp = block.get("input", {})

        # Check Agent dispatch with code-review
        if name == "Agent":
            subagent = inp.get("subagent_type", "")
            prompt = inp.get("prompt", "")
            if subagent == "code-review" or re.search(r"\bcode-review(?!-)", prompt):
                has_review_dispatch = True

    # Check tool results for PASS
    for block in tool_results:
        content = block.get("content", "")
        if isinstance(content, str) and "PASS" in content:
            has_pass = True
        elif isinstance(content, list):
            for sub in content:
                if isinstance(sub, dict) and "PASS" in str(sub.get("text", "")):
                    has_pass = True

    return has_review_dispatch and has_pass


def check_phase_3(tool_uses, tool_results):
    """Phase 3: Git operations — look for git-ops agent dispatch or gh pr create."""
    for block in tool_uses:
        name = block.get("name", "")
        inp = block.get("input", {})

        if name == "Agent":
            subagent = inp.get("subagent_type", "")
            prompt = inp.get("prompt", "")
            if "git-ops" in subagent or "git-ops" in prompt:
                return True

        if name == "Bash":
            cmd = inp.get("command", "")
            if "gh pr create" in cmd or "git push" in cmd:
                return True

    return False


def check_phase_4(tool_uses, tool_results):
    """Phase 4: PR review loop — look for pr-review-monitor or review polling."""
    for block in tool_uses:
        name = block.get("name", "")
        inp = block.get("input", {})

        if name == "Agent":
            subagent = inp.get("subagent_type", "")
            prompt = inp.get("prompt", "")
            if "pr-review-monitor" in subagent or "pr-review-monitor" in prompt:
                return True

        if name == "Bash":
            cmd = inp.get("command", "")
            if "gh pr checks" in cmd or ("pulls" in cmd and "comments" in cmd):
                return True

    return False


def check_phase_5(tool_uses, tool_results):
    """Phase 5: Notification — look for osascript or twilio_sms.py."""
    for block in tool_uses:
        if block.get("name") == "Bash":
            cmd = block.get("input", {}).get("command", "")
            if "osascript" in cmd or "twilio_sms.py" in cmd:
                return True
    return False


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    # Guard: prevent infinite loops
    if hook_input.get("stop_hook_active", False):
        sys.exit(0)

    transcript_path = hook_input.get("transcript_path", "")
    if not transcript_path:
        # No transcript available — allow stop (can't validate)
        sys.exit(0)

    tool_uses, tool_results = parse_transcript(transcript_path)

    phases = {
        "Phase 1 (Implementation)": check_phase_1(tool_uses, tool_results),
        "Phase 2 (Local Pre-flight Review)": check_phase_2(tool_uses, tool_results),
        "Phase 3 (Git Operations)": check_phase_3(tool_uses, tool_results),
        "Phase 4 (PR Review Loop)": check_phase_4(tool_uses, tool_results),
        "Phase 5 (Notification)": check_phase_5(tool_uses, tool_results),
    }

    missing = [name for name, passed in phases.items() if not passed]

    if not missing:
        sys.exit(0)

    print(
        "BLOCKED: Build-and-ship pipeline incomplete.\n"
        "Missing: " + ", ".join(missing),
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
