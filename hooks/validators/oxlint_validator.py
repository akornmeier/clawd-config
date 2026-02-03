#!/usr/bin/env python3
"""
OXLint Validator - PostToolUse Hook

Runs oxlint on TypeScript/JavaScript files after Write/Edit operations.
Blocks the agent if lint errors are found, forcing the agent to fix them.

Usage: uv run ~/.claude/hooks/validators/oxlint_validator.py
Input: JSON on stdin with tool_input.file_path
Output: JSON with decision (allow/block) and reason
"""

import json
import subprocess
import sys
from pathlib import Path


def is_lintable_file(file_path: str) -> bool:
    """Check if a file should be linted."""
    path = Path(file_path)
    lintable_extensions = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

    if path.suffix not in lintable_extensions:
        return False

    # Skip node_modules
    if "node_modules" in path.parts:
        return False

    # Skip dist/build directories
    if any(d in path.parts for d in ["dist", "build", ".next", "out"]):
        return False

    return True


def find_project_root(file_path: str) -> Path | None:
    """Find the project root by looking for package.json."""
    path = Path(file_path).resolve()

    for parent in [path] + list(path.parents):
        if (parent / "package.json").exists():
            return parent

    return None


def run_oxlint(file_path: str, project_root: Path) -> tuple[bool, str]:
    """Run oxlint on the file and return (success, output)."""
    try:
        result = subprocess.run(
            ["pnpm", "exec", "oxlint", file_path],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )

        # oxlint returns 0 on success, non-zero on errors
        if result.returncode == 0:
            return True, ""

        # Combine stdout and stderr for error output
        output = result.stdout + result.stderr
        return False, output.strip()

    except subprocess.TimeoutExpired:
        return True, ""  # Allow on timeout
    except FileNotFoundError:
        # oxlint not installed - allow but warn
        return True, ""
    except Exception:
        # On unexpected errors, allow to not block workflow
        return True, ""


def extract_errors(output: str, file_path: str) -> str:
    """Extract relevant error messages from oxlint output."""
    if not output:
        return "Lint errors found"

    lines = output.split("\n")
    relevant_lines = []

    for line in lines:
        # Skip empty lines and summary lines
        if not line.strip():
            continue
        if "error" in line.lower() or "warning" in line.lower():
            relevant_lines.append(line)
        elif line.strip().startswith("×") or line.strip().startswith("⚠"):
            relevant_lines.append(line)

    if relevant_lines:
        return "\n".join(relevant_lines[:10])  # Limit to first 10 errors

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

    # Check if file should be linted
    if not is_lintable_file(file_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Find project root
    project_root = find_project_root(file_path)
    if not project_root:
        print(json.dumps({"decision": "allow"}))
        return

    # Run oxlint
    success, output = run_oxlint(file_path, project_root)

    if success:
        print(json.dumps({"decision": "allow"}))
    else:
        errors = extract_errors(output, file_path)
        print(json.dumps({
            "decision": "block",
            "reason": f"Lint errors found! Fix before continuing:\n\n{errors}"
        }))


if __name__ == "__main__":
    main()
