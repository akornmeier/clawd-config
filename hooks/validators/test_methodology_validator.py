#!/usr/bin/env python3
"""
Test Methodology Validator - PostToolUse Hook

Validates that components follow the proper testing methodology:
1. Unit tests (.test.tsx) for structure/rendering
2. Storybook interaction tests (play functions) for user interactions

Usage: uv run ~/.claude/hooks/validators/test_methodology_validator.py
Input: JSON on stdin with tool_input.file_path
Output: JSON with decision (allow/block) and reason
"""

import json
import re
import sys
from pathlib import Path


def is_component_file(file_path: str) -> bool:
    """Check if a file is a React/Vue component file."""
    path = Path(file_path)

    if path.suffix not in {".tsx", ".jsx", ".vue"}:
        return False

    name = path.name.lower()

    # Skip test files, stories, and index files
    skip_patterns = [".test.", ".spec.", ".stories.", "index.", "types."]
    if any(pattern in name for pattern in skip_patterns):
        return False

    # Component directories
    component_dirs = ["components", "atoms", "molecules", "organisms", "features", "ui"]
    return any(d in path.parts for d in component_dirs)


def is_story_file(file_path: str) -> bool:
    """Check if file is a Storybook story file."""
    return ".stories." in Path(file_path).name.lower()


def check_story_has_play_function(story_path: Path) -> tuple[bool, list[str]]:
    """Check if story file has play functions for interaction testing."""
    if not story_path.exists():
        return False, []

    content = story_path.read_text()

    # Look for play function patterns
    play_patterns = [
        r"play:\s*async",
        r"play:\s*\(",
        r"play\s*=\s*async",
    ]

    has_play = any(re.search(p, content) for p in play_patterns)

    # Find which stories have play functions
    stories_with_play = re.findall(r"export\s+const\s+(\w+).*?play:", content, re.DOTALL)

    return has_play, stories_with_play


def check_unit_test_exists(component_path: str) -> Path | None:
    """Check if unit test file exists for component."""
    path = Path(component_path)
    stem = path.stem
    parent = path.parent

    test_patterns = [
        parent / f"{stem}.test.tsx",
        parent / f"{stem}.test.ts",
        parent / f"{stem}.spec.tsx",
        parent / f"{stem}.spec.ts",
        parent / "__tests__" / f"{stem}.test.tsx",
        parent / "__tests__" / f"{stem}.test.ts",
    ]

    for test_path in test_patterns:
        if test_path.exists():
            return test_path

    return None


def check_story_file_exists(component_path: str) -> Path | None:
    """Check if story file exists for component."""
    path = Path(component_path)
    stem = path.stem
    parent = path.parent

    story_patterns = [
        parent / f"{stem}.stories.tsx",
        parent / f"{stem}.stories.ts",
        parent / "__stories__" / f"{stem}.stories.tsx",
    ]

    for story_path in story_patterns:
        if story_path.exists():
            return story_path

    return None


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        print(json.dumps({"decision": "allow"}))
        return

    path = Path(file_path)

    # If writing a story file, check for play functions
    if is_story_file(file_path):
        if path.exists():
            has_play, stories_with_play = check_story_has_play_function(path)
            if not has_play:
                print(json.dumps({
                    "decision": "allow",  # Warning, not block
                    "reason": f"""Storybook Interaction Tests Missing!

Your story file should include play functions for interaction testing:

```tsx
export const ClickInteraction: Story = {{
  play: async ({{ canvasElement }}) => {{
    const canvas = within(canvasElement);
    const button = canvas.getByRole("button");

    await userEvent.click(button);
    await expect(button).toHaveAttribute("aria-expanded", "true");
  }},
}};
```

Stories with play functions test real user interactions in a browser environment.
This catches issues that unit tests miss."""
                }))
                return

        print(json.dumps({"decision": "allow"}))
        return

    # If writing a component file, check test coverage
    if is_component_file(file_path):
        issues = []

        # Check for unit test
        unit_test = check_unit_test_exists(file_path)
        if not unit_test:
            suggested_test = path.parent / f"{path.stem}.test.tsx"
            issues.append(f"Unit test missing: {suggested_test}")

        # Check for story file with play functions
        story_file = check_story_file_exists(file_path)
        if not story_file:
            suggested_story = path.parent / f"{path.stem}.stories.tsx"
            issues.append(f"Story file missing: {suggested_story}")
        elif story_file.exists():
            has_play, _ = check_story_has_play_function(story_file)
            if not has_play:
                issues.append(f"Story file lacks play functions for interaction tests: {story_file}")

        if issues:
            print(json.dumps({
                "decision": "allow",  # Warning, not block
                "reason": f"""Test Methodology Check:

{chr(10).join(f"⚠️  {issue}" for issue in issues)}

Required testing pattern:
1. Unit tests (.test.tsx) - Rendering, props, variants
2. Storybook play functions - User interactions, state changes"""
            }))
            return

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
