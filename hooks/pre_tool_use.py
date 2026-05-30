#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import re
import os
from pathlib import Path
from utils.constants import ensure_session_log_dir

# Allowed directories where rm -rf is permitted
ALLOWED_RM_DIRECTORIES = [
    'trees/',
]

# Catastrophic `rm -r` targets — the cases this guard actually exists for.
# Deliberately NOT "any path containing a slash or dot": routine recursive
# deletes of real subdirectories (`git rm -r pkg/foo`, `rm -rf node_modules`)
# must pass. Matched against the lowercased, whitespace-normalized statement.
_CATASTROPHIC_TARGETS = [
    r'(?:^|\s)/\*?(?:\s|$)',  # root only: bare "/" or "/*" (not a trailing slash)
    r'~(?:/\S*)?(?:\s|$)',    # home: ~ or ~/...
    r'\$home\b',              # $HOME (normalized to lowercase)
    r'\.\.(?:/|\s|$)',        # parent dir ..
    r'(?:^|\s)\*',            # bare wildcard target
    r'(?:^|\s)\.(?:\s|$)',    # current dir . as a target
    # absolute delete rooted at a system directory (/etc, /usr/local/lib, ...).
    # NOT /tmp, /home, /Users, /private — those are legitimate work roots.
    r'(?:^|\s)/(?:etc|usr|var|bin|sbin|lib|boot|dev|proc|sys|opt|system|library)(?:/|\s|$)',
]


def _split_statements(command):
    """
    Split a compound command into individual statements on shell separators
    (&&, ||, ;, |, newline). Without this, a recursive flag in one statement
    (e.g. a trailing `grep -rn`) gets misattributed to an `rm` in another.
    """
    return re.split(r'&&|\|\||[;\n|]', command)


def _executable(statement):
    """Return the basename of the command word, ignoring a leading sudo/doas."""
    m = re.match(r'\s*(?:sudo\s+|doas\s+)?((?:\S*/)?[\w.+-]+)', statement)
    return os.path.basename(m.group(1)) if m else ''


def is_path_in_allowed_directory(statement, allowed_dirs):
    """
    Check if an `rm` statement targets paths exclusively within allowed dirs.
    Returns True only if every path argument is within an allowed directory.
    """
    match = re.search(r'rm\s+(?:-[\w]+\s+|--[\w-]+\s+)*(.+)$', statement, re.IGNORECASE)
    if not match:
        return False

    paths = [p.strip('\'"') for p in match.group(1).split() if p.strip('\'"')]
    if not paths:
        return False

    return all(
        any(path.startswith(d) or path.startswith('./' + d) for d in allowed_dirs)
        for path in paths
    )


def is_dangerous_rm_command(command, allowed_dirs=None):
    """
    Detect genuinely destructive `rm` invocations: a recursive `rm` whose
    target is catastrophic (/, ~, $HOME, .., *, ., or a system dir like
    /etc or /usr). Scoped per-statement and
    to the actual `rm` executable, so `git rm`/`npm rm`/`cargo rm` and a
    later unrelated `-r` flag (grep -rn, ls -R) no longer trigger it.

    Returns True only when the statement is dangerous AND its targets are not
    confined to `allowed_dirs`.
    """
    allowed_dirs = allowed_dirs or []

    for statement in _split_statements(command):
        if _executable(statement) != 'rm':
            continue  # not the rm executable — skip git/npm/cargo rm, grep, ls

        low = ' '.join(statement.lower().split())
        has_recursive = bool(re.search(r'(?<![\w])-[a-z]*r', low))  # also matches --recursive
        if not has_recursive:
            continue  # non-recursive rm of named files is never blocked

        if any(re.search(target, low) for target in _CATASTROPHIC_TARGETS):
            if allowed_dirs and is_path_in_allowed_directory(statement, allowed_dirs):
                continue  # confined to an allowed directory
            return True

    return False

def confirm_tool(reason):
    """
    Surface a tool call for human confirmation via the JSON
    hookSpecificOutput.permissionDecision pattern. Uses "ask" (not "deny")
    so a genuinely-intended destructive command can be approved rather than
    hard-blocked. Prints JSON to stdout and exits with code 0.
    """
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)


def summarize_tool_input(tool_name, tool_input):
    """
    Create a summary dict of key fields for the tool, for logging purposes.
    """
    summary = {"tool_name": tool_name}

    if tool_name == 'Bash':
        summary["command"] = tool_input.get("command", "")[:200]
        if tool_input.get("description"):
            summary["description"] = tool_input["description"][:100]
        if tool_input.get("timeout"):
            summary["timeout"] = tool_input["timeout"]
        if tool_input.get("run_in_background"):
            summary["run_in_background"] = True

    elif tool_name == 'Write':
        summary["file_path"] = tool_input.get("file_path", "")
        summary["content_length"] = len(tool_input.get("content", ""))

    elif tool_name == 'Edit':
        summary["file_path"] = tool_input.get("file_path", "")
        summary["replace_all"] = tool_input.get("replace_all", False)

    elif tool_name == 'Read':
        summary["file_path"] = tool_input.get("file_path", "")
        if tool_input.get("offset"):
            summary["offset"] = tool_input["offset"]
        if tool_input.get("limit"):
            summary["limit"] = tool_input["limit"]

    elif tool_name == 'Glob':
        summary["pattern"] = tool_input.get("pattern", "")
        if tool_input.get("path"):
            summary["path"] = tool_input["path"]

    elif tool_name == 'Grep':
        summary["pattern"] = tool_input.get("pattern", "")
        if tool_input.get("path"):
            summary["path"] = tool_input["path"]
        if tool_input.get("glob"):
            summary["glob"] = tool_input["glob"]

    elif tool_name == 'WebFetch':
        summary["url"] = tool_input.get("url", "")
        summary["prompt"] = tool_input.get("prompt", "")[:100]

    elif tool_name == 'WebSearch':
        summary["query"] = tool_input.get("query", "")
        if tool_input.get("allowed_domains"):
            summary["allowed_domains"] = tool_input["allowed_domains"]
        if tool_input.get("blocked_domains"):
            summary["blocked_domains"] = tool_input["blocked_domains"]

    elif tool_name == 'Task':
        summary["description"] = tool_input.get("description", "")[:100]
        summary["subagent_type"] = tool_input.get("subagent_type", "")
        if tool_input.get("model"):
            summary["model"] = tool_input["model"]
        if tool_input.get("run_in_background"):
            summary["run_in_background"] = True
        if tool_input.get("resume"):
            summary["resume"] = tool_input["resume"]

    elif tool_name == 'TaskOutput':
        summary["task_id"] = tool_input.get("task_id", "")
        summary["block"] = tool_input.get("block", True)
        if tool_input.get("timeout"):
            summary["timeout"] = tool_input["timeout"]

    elif tool_name == 'TaskStop':
        summary["task_id"] = tool_input.get("task_id", "")

    elif tool_name == 'SendMessage':
        summary["type"] = tool_input.get("type", "")
        if tool_input.get("recipient"):
            summary["recipient"] = tool_input["recipient"]
        if tool_input.get("summary"):
            summary["summary"] = tool_input["summary"]

    elif tool_name == 'TaskCreate':
        summary["subject"] = tool_input.get("subject", "")[:100]
        if tool_input.get("activeForm"):
            summary["activeForm"] = tool_input["activeForm"]

    elif tool_name == 'TaskGet':
        summary["taskId"] = tool_input.get("taskId", "")

    elif tool_name == 'TaskUpdate':
        summary["taskId"] = tool_input.get("taskId", "")
        if tool_input.get("status"):
            summary["status"] = tool_input["status"]
        if tool_input.get("owner"):
            summary["owner"] = tool_input["owner"]

    elif tool_name == 'TaskList':
        pass  # No params

    elif tool_name == 'TeamCreate':
        summary["team_name"] = tool_input.get("team_name", "")
        if tool_input.get("description"):
            summary["description"] = tool_input["description"][:100]

    elif tool_name == 'TeamDelete':
        pass  # No params

    elif tool_name == 'NotebookEdit':
        summary["notebook_path"] = tool_input.get("notebook_path", "")
        if tool_input.get("cell_type"):
            summary["cell_type"] = tool_input["cell_type"]
        if tool_input.get("edit_mode"):
            summary["edit_mode"] = tool_input["edit_mode"]

    elif tool_name == 'EnterPlanMode':
        pass  # No params

    elif tool_name == 'ExitPlanMode':
        if tool_input.get("allowedPrompts"):
            summary["allowedPrompts_count"] = len(tool_input["allowedPrompts"])

    elif tool_name == 'AskUserQuestion':
        if tool_input.get("questions"):
            summary["questions_count"] = len(tool_input["questions"])

    elif tool_name == 'Skill':
        summary["skill"] = tool_input.get("skill", "")
        if tool_input.get("args"):
            summary["args"] = tool_input["args"][:100]

    elif tool_name.startswith('mcp__'):
        # MCP tools - log the full tool name and available input keys
        summary["mcp_tool"] = tool_name
        summary["input_keys"] = list(tool_input.keys())[:10]

    return summary


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})
        tool_use_id = input_data.get('tool_use_id', '')

        # Note: .env access is intentionally NOT guarded here — the worktree
        # command needs to create .env files automatically.

        # Check for dangerous rm -rf commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')

            # Surface catastrophic recursive deletes for confirmation. Routine
            # recursive deletes of real subdirectories pass through silently.
            if is_dangerous_rm_command(command, ALLOWED_RM_DIRECTORIES):
                confirm_tool(
                    "Recursive delete targeting a catastrophic path "
                    "(/, ~, $HOME, .., *, or a system dir like /etc). "
                    "Confirm this is intended."
                )

        # Extract session_id
        session_id = input_data.get('session_id', 'unknown')

        # Ensure session log directory exists
        log_dir = ensure_session_log_dir(session_id)
        log_path = log_dir / 'pre_tool_use.json'

        # Read existing log data or initialize empty list
        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        # Build log entry with tool_use_id and tool summary
        log_entry = {
            "tool_name": tool_name,
            "tool_use_id": tool_use_id,
            "session_id": session_id,
            "hook_event_name": input_data.get("hook_event_name", "PreToolUse"),
            "tool_summary": summarize_tool_input(tool_name, tool_input),
        }

        # Append log entry
        log_data.append(log_entry)

        # Write back to file with formatting
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        sys.exit(0)

    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()
