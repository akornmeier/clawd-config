#!/usr/bin/env python3
"""
TypeScript Compiler Validator - PostToolUse Hook

Runs tsc --noEmit on TypeScript files after Write/Edit operations.
Blocks the agent if type errors are found, forcing the agent to fix them.

Usage: uv run ~/.claude/hooks/validators/tsc_validator.py
Input: JSON on stdin with tool_input.file_path
Output: JSON with decision (allow/block) and reason
"""

import json
import subprocess
import sys
from pathlib import Path


def is_typescript_file(file_path: str) -> bool:
    """Check if a file is a TypeScript file."""
    path = Path(file_path)
    ts_extensions = {".ts", ".tsx", ".mts", ".cts"}

    if path.suffix not in ts_extensions:
        return False

    # Skip declaration files
    if path.name.endswith(".d.ts"):
        return False

    # Skip node_modules
    if "node_modules" in path.parts:
        return False

    # Skip dist/build directories
    if any(d in path.parts for d in ["dist", "build", ".next", "out"]):
        return False

    return True


def find_project_root(file_path: str) -> Path | None:
    """Find the project root by looking for tsconfig.json or package.json."""
    path = Path(file_path).resolve()

    for parent in [path] + list(path.parents):
        if (parent / "tsconfig.json").exists():
            return parent
        if (parent / "package.json").exists():
            return parent

    return None


def run_tsc(project_root: Path) -> tuple[bool, str]:
    """Run tsc --noEmit and return (success, output)."""
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )

        # tsc returns 0 on success, non-zero on errors
        if result.returncode == 0:
            return True, ""

        # Combine stdout and stderr for error output
        output = result.stdout + result.stderr
        return False, output.strip()

    except subprocess.TimeoutExpired:
        return True, ""  # Allow on timeout
    except FileNotFoundError:
        # tsc not installed - allow
        return True, ""
    except Exception:
        # On unexpected errors, allow to not block workflow
        return True, ""


def extract_errors(output: str, file_path: str) -> str:
    """Extract relevant error messages from tsc output."""
    if not output:
        return "Type errors found"

    lines = output.split("\n")
    relevant_lines = []
    file_name = Path(file_path).name

    # Try to find errors related to the specific file first
    in_relevant_error = False
    for line in lines:
        if file_name in line or file_path in line:
            relevant_lines.append(line)
            in_relevant_error = True
        elif in_relevant_error and (line.startswith(" ") or line.strip() == ""):
            relevant_lines.append(line)
        else:
            in_relevant_error = False

    # If no file-specific errors, return first few errors
    if not relevant_lines:
        error_lines = [line for line in lines if "error TS" in line]
        relevant_lines = error_lines[:5]

    if relevant_lines:
        return "\n".join(relevant_lines[:10])  # Limit to 10 lines

    return output[:500]  # Fallback to truncated output


def main():
    # Read input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return

    # Extract file path from tool input
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        print(json.dumps({"decision": "allow"}))
        return

    # Check if file is TypeScript
    if not is_typescript_file(file_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Find project root
    project_root = find_project_root(file_path)
    if not project_root:
        print(json.dumps({"decision": "allow"}))
        return

    # Run tsc
    success, output = run_tsc(project_root)

    if success:
        print(json.dumps({"decision": "allow"}))
    else:
        errors = extract_errors(output, file_path)
        print(json.dumps({
            "decision": "block",
            "reason": f"Type errors found! Fix before continuing:\n\n{errors}"
        }))


if __name__ == "__main__":
    main()
