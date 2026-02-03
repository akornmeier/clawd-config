#!/usr/bin/env python3
"""
TDD Enforcer - PreToolUse Hook

Blocks implementation file writes until the corresponding test file
has been modified in this session. This enforces Test-Driven Development
by requiring tests to be written before implementation.

Usage: uv run ~/.claude/hooks/validators/tdd_enforcer.py
Input: JSON on stdin with tool_input.file_path
Output: JSON with decision (allow/block) and reason
"""

import json
import sys
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "data" / "tdd_session_state.json"


def load_state() -> dict:
    """Load the current session state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, IOError):
            return {"test_files_modified": [], "session_id": None}
    return {"test_files_modified": [], "session_id": None}


def save_state(state: dict) -> None:
    """Save the session state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def is_test_file(file_path: str) -> bool:
    """Check if a file is a test file."""
    path = Path(file_path)
    name = path.name.lower()

    # Check common test file patterns
    test_patterns = [
        ".test.", ".spec.", "_test.", "_spec.",
        "test_", "spec_"
    ]

    # Check if in __tests__ directory
    if "__tests__" in path.parts:
        return True

    # Check if in tests/ directory at any level
    if "tests" in path.parts:
        return True

    return any(pattern in name for pattern in test_patterns)


def is_impl_file(file_path: str) -> bool:
    """Check if a file is an implementation file (TypeScript/JavaScript)."""
    path = Path(file_path)
    extensions = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}

    if path.suffix not in extensions:
        return False

    # Not an impl file if it's a test file
    if is_test_file(file_path):
        return False

    # Skip config files
    config_patterns = [
        "config.", ".config.", "rc.", ".d.ts",
        "vite.config", "vitest.config", "jest.config",
        "tsconfig", "eslint", "prettier"
    ]

    name = path.name.lower()
    return not any(pattern in name for pattern in config_patterns)


def find_matching_tests(impl_path: str) -> list[str]:
    """Find possible test file paths for an implementation file."""
    path = Path(impl_path)
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    # Generate possible test file locations
    possible_tests = []

    # Same directory patterns
    possible_tests.extend([
        parent / f"{stem}.test{suffix}",
        parent / f"{stem}.spec{suffix}",
        parent / f"{stem}_test{suffix}",
        parent / f"{stem}_spec{suffix}",
    ])

    # __tests__ directory pattern
    possible_tests.extend([
        parent / "__tests__" / f"{stem}.test{suffix}",
        parent / "__tests__" / f"{stem}.spec{suffix}",
        parent / "__tests__" / f"{stem}{suffix}",
    ])

    # tests/ sibling directory pattern
    if "src" in parent.parts:
        # Replace src with tests in path
        parts = list(parent.parts)
        try:
            src_idx = parts.index("src")
            parts[src_idx] = "tests"
            tests_parent = Path(*parts)
            possible_tests.extend([
                tests_parent / f"{stem}.test{suffix}",
                tests_parent / f"{stem}.spec{suffix}",
            ])
        except ValueError:
            pass

    return [str(p) for p in possible_tests]


def normalize_path(file_path: str) -> str:
    """Normalize a file path for comparison."""
    return str(Path(file_path).resolve())


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

    # Load current state
    state = load_state()
    normalized_path = normalize_path(file_path)

    # If it's a test file, record it and allow
    if is_test_file(file_path):
        if normalized_path not in state["test_files_modified"]:
            state["test_files_modified"].append(normalized_path)
            save_state(state)
        print(json.dumps({"decision": "allow"}))
        return

    # If it's not an implementation file, allow
    if not is_impl_file(file_path):
        print(json.dumps({"decision": "allow"}))
        return

    # It's an implementation file - check if corresponding test exists
    possible_tests = find_matching_tests(file_path)
    modified_tests = set(state.get("test_files_modified", []))

    # Check if any matching test has been modified
    for test_path in possible_tests:
        normalized_test = normalize_path(test_path)
        if normalized_test in modified_tests:
            print(json.dumps({"decision": "allow"}))
            return
        # Also check if test file exists and was modified (case-insensitive)
        for modified in modified_tests:
            if Path(modified).name.lower() == Path(test_path).name.lower():
                print(json.dumps({"decision": "allow"}))
                return

    # No matching test found - block with helpful message
    suggested_test = possible_tests[0] if possible_tests else f"{file_path.replace('.ts', '.test.ts')}"

    print(json.dumps({
        "decision": "block",
        "reason": f"TDD Violation: Write test first!\n\nYou're trying to write implementation code without a test.\n\nSuggested test file: {suggested_test}\n\nWrite and save the test file first, then you can write the implementation."
    }))


if __name__ == "__main__":
    main()
