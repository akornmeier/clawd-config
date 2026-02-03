#!/usr/bin/env python3
"""
Storybook Validator - PostToolUse Hook

Checks if new React components have corresponding Storybook stories.
Blocks if a component is created without stories.

Usage: uv run ~/.claude/hooks/validators/storybook_validator.py
Input: JSON on stdin with tool_input.file_path
Output: JSON with decision (allow/block) and reason
"""

import json
import sys
from pathlib import Path


def is_component_file(file_path: str) -> bool:
    """Check if a file is a React component file."""
    path = Path(file_path)

    # Must be TSX/JSX
    if path.suffix not in {".tsx", ".jsx"}:
        return False

    name = path.name.lower()

    # Skip test files, stories, and index files
    skip_patterns = [
        ".test.", ".spec.", ".stories.",
        "index.", "types.", ".d."
    ]
    if any(pattern in name for pattern in skip_patterns):
        return False

    # Skip non-component directories
    skip_dirs = ["hooks", "utils", "lib", "types", "api", "services", "providers"]
    if any(d in path.parts for d in skip_dirs):
        return False

    # Likely a component if in components, atoms, molecules, organisms, features
    component_dirs = ["components", "atoms", "molecules", "organisms", "features", "ui"]
    if any(d in path.parts for d in component_dirs):
        return True

    # Check if file starts with uppercase (PascalCase component)
    if path.stem[0].isupper():
        return True

    return False


def find_story_file(component_path: str) -> Path | None:
    """Find the corresponding story file for a component."""
    path = Path(component_path)
    stem = path.stem
    parent = path.parent
    suffix = path.suffix

    # Possible story file patterns
    story_patterns = [
        parent / f"{stem}.stories{suffix}",
        parent / f"{stem}.stories.tsx",
        parent / f"{stem}.stories.ts",
        parent / "__stories__" / f"{stem}.stories{suffix}",
        parent / "stories" / f"{stem}.stories{suffix}",
    ]

    for story_path in story_patterns:
        if story_path.exists():
            return story_path

    return None


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

    # Check if this is a component file
    if not is_component_file(file_path):
        print(json.dumps({"decision": "allow"}))
        return

    # Check if story file exists
    story_file = find_story_file(file_path)

    if story_file:
        print(json.dumps({"decision": "allow"}))
        return

    # No story file found - provide guidance but allow (soft warning)
    # Change to "block" for strict enforcement
    path = Path(file_path)
    suggested_story = path.parent / f"{path.stem}.stories.tsx"

    print(json.dumps({
        "decision": "allow",  # Change to "block" for strict mode
        "reason": f"UI Component without Storybook story.\n\nConsider creating: {suggested_story}\n\nStories help document component variants and enable visual testing."
    }))


if __name__ == "__main__":
    main()
