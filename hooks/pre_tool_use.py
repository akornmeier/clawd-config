#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""
PreToolUse guard: surface catastrophic recursive deletes for confirmation.

This is the only hook still wired. It does one job and does not log, so a
failure here can only ever cost the guard, never a tool call.
"""

import json
import sys
import re
import os

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


# Wrappers that prefix a real command; their leading options must be skipped to
# find the actual executable. Flags listed here take a separate argument
# (`sudo -u root`, `env -u VAR`), so the following token is consumed too. The
# set is best-effort: a missed arg-flag only risks an over-cautious confirm.
_COMMAND_WRAPPERS = {'sudo', 'doas', 'env', 'nice', 'nohup', 'time', 'command'}
_WRAPPER_ARG_FLAGS = {'-u', '-g', '-h', '-p', '-C', '-U', '-r', '-t', '-D', '-a'}


def _executable(statement):
    """
    Basename of the command word, skipping privilege/env wrappers (sudo, doas,
    env, ...) plus their option flags, flag-arguments, and leading VAR=val
    assignments. So `sudo -E rm`, `sudo -u root rm`, and `env FOO=bar rm` all
    resolve to `rm`, while `git rm` resolves to `git`.
    """
    tokens = statement.split()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if re.match(r'\w+=', tok):  # leading VAR=val assignment
            i += 1
            continue
        base = os.path.basename(tok)
        if base in _COMMAND_WRAPPERS:
            i += 1  # consume the wrapper, then its option flags/arguments
            while i < len(tokens) and tokens[i].startswith('-'):
                takes_arg = tokens[i] in _WRAPPER_ARG_FLAGS
                i += 1
                if takes_arg and i < len(tokens):
                    i += 1
            continue
        return base
    return ''


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


def main():
    try:
        input_data = json.load(sys.stdin)

        if input_data.get('tool_name', '') == 'Bash':
            command = input_data.get('tool_input', {}).get('command', '')

            # Surface catastrophic recursive deletes for confirmation. Routine
            # recursive deletes of real subdirectories pass through silently.
            if is_dangerous_rm_command(command, ALLOWED_RM_DIRECTORIES):
                confirm_tool(
                    "Recursive delete targeting a catastrophic path "
                    "(/, ~, $HOME, .., *, or a system dir like /etc). "
                    "Confirm this is intended."
                )

        sys.exit(0)

    except json.JSONDecodeError:
        # Malformed input: fail open rather than blocking the tool call.
        sys.exit(0)
    except Exception as e:
        # Fail open, but make the failure visible — a silently dead guard is
        # worse than a noisy one. Exit 1 is non-blocking; stderr shows in the
        # transcript.
        print(f"pre_tool_use guard error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
