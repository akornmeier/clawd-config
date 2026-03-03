#!/usr/bin/env python3
"""Stop hook validator: checks that files written THIS SESSION contain required strings.

Usage:
    uv run .claude/hooks/validators/validate_file_contains.py \
        --directory specs --extension .md \
        --contains '## Task Description' \
        --contains '## Objective'

Reads the Stop hook JSON from stdin, including transcript_path. Parses the
session transcript to identify which files were written via Write/Edit tools
to the target directory, then checks those specific files for required strings.
Exits 0 if all found, exits 2 with missing sections on stderr.
"""
import argparse
import json
import sys
from pathlib import Path


def find_written_files_from_transcript(transcript_path, target_dir, ext):
    """Parse the JSONL transcript to find files written via Write/Edit tools.

    Returns a set of Path objects for files that were written to the target
    directory with the specified extension during this session.
    """
    written = set()
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

                if msg.get("type") != "assistant":
                    continue

                content = msg.get("message", {}).get("content", [])
                if not isinstance(content, list):
                    continue

                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") not in ("Write", "Edit"):
                        continue

                    file_path = block.get("input", {}).get("file_path", "")
                    if not file_path:
                        continue

                    fp = Path(file_path).resolve()
                    resolved_target = target_dir.resolve()

                    if fp.suffix == ext and fp.parent == resolved_target:
                        written.add(fp)

    except (FileNotFoundError, PermissionError, OSError):
        pass

    return written


def validate_file(file_path, required_strings):
    """Check a file for required strings. Returns list of missing strings."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return required_strings  # All missing if can't read

    return [s for s in required_strings if s not in content]


def main():
    parser = argparse.ArgumentParser(description="Validate file contains required sections")
    parser.add_argument("--directory", required=True, help="Directory to check")
    parser.add_argument("--extension", required=True, help="File extension to look for")
    parser.add_argument("--contains", action="append", required=True, help="Required string (repeatable)")
    args = parser.parse_args()

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        hook_input = {}

    # If stop_hook_active, exit immediately to prevent infinite loops
    if hook_input.get("stop_hook_active", False):
        sys.exit(0)

    cwd = hook_input.get("cwd", ".")
    search_dir = Path(cwd) / args.directory
    ext = args.extension if args.extension.startswith(".") else f".{args.extension}"
    transcript_path = hook_input.get("transcript_path", "")

    if not search_dir.exists():
        print(
            f"BLOCKED: Directory '{args.directory}' does not exist. "
            f"The plan must be saved to {args.directory}/",
            file=sys.stderr,
        )
        sys.exit(2)

    # Primary: find files written this session via transcript
    target_files = []
    used_transcript = False

    if transcript_path:
        written_files = find_written_files_from_transcript(transcript_path, search_dir, ext)
        existing = [fp for fp in written_files if fp.exists()]

        if existing:
            target_files = existing
            used_transcript = True

    # Fallback: no transcript or no files found in transcript — use most recent file
    if not target_files:
        matching = sorted(
            search_dir.glob(f"*{ext}"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        if not matching:
            print(f"BLOCKED: No {ext} files found in '{args.directory}'", file=sys.stderr)
            sys.exit(2)

        target_files = [matching[0]]
        if transcript_path:
            print(
                f"WARNING: No Write/Edit calls to '{args.directory}/' found in session transcript — "
                f"falling back to most recent file '{matching[0].name}' by mtime.",
                file=sys.stderr,
            )
        else:
            print(
                f"WARNING: transcript_path not available — "
                f"falling back to most recent file '{matching[0].name}' by mtime.",
                file=sys.stderr,
            )

    # Validate each written file
    all_passed = True
    for target_file in target_files:
        missing = validate_file(target_file, args.contains)
        if missing:
            all_passed = False
            print(f"BLOCKED: File '{target_file.name}' is missing required sections:", file=sys.stderr)
            for section in missing:
                print(f"  - {section}", file=sys.stderr)

    sys.exit(0 if all_passed else 2)


if __name__ == "__main__":
    main()
