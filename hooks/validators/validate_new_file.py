#!/usr/bin/env python3
"""Stop hook validator: checks that a new file was actually WRITTEN during this session.

Usage:
    uv run .claude/hooks/validators/validate_new_file.py --directory specs --extension .md

Reads the Stop hook JSON from stdin, including transcript_path. Parses the
session transcript to find Write tool calls targeting the specified directory.
If a matching file was written, exits 0 (allow stop). If none written,
exits 2 with an error on stderr (block stop).
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

                # Only assistant messages contain tool_use blocks
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

                    if fp.suffix == ext and fp.is_relative_to(resolved_target):
                        written.add(fp)

    except (FileNotFoundError, PermissionError, OSError):
        pass

    return written


def main():
    parser = argparse.ArgumentParser(description="Validate a new file was written this session")
    parser.add_argument("--directory", required=True, help="Directory to check")
    parser.add_argument("--extension", required=True, help="File extension to look for")
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

    # Primary: check transcript for Write/Edit calls to the target directory
    if transcript_path:
        written_files = find_written_files_from_transcript(transcript_path, search_dir, ext)
        existing = {fp for fp in written_files if fp.exists()}

        if existing:
            sys.exit(0)

        if written_files:
            # Write was attempted but file doesn't exist on disk
            names = ", ".join(fp.name for fp in written_files)
            print(
                f"BLOCKED: Write tool targeted {names} but file(s) not found on disk.",
                file=sys.stderr,
            )
            sys.exit(2)

        # No Write calls found in transcript targeting this directory
        print(
            f"BLOCKED: No file was written to '{args.directory}/' during this session. "
            f"The plan must be saved as a {ext} file in {args.directory}/",
            file=sys.stderr,
        )
        sys.exit(2)

    # Fallback: transcript_path not available — check for any recent file
    # This is less reliable but better than silently passing
    matching = list(search_dir.glob(f"*{ext}"))
    if not matching:
        print(
            f"BLOCKED: No {ext} files found in '{args.directory}'. "
            f"The plan must be saved to {args.directory}/",
            file=sys.stderr,
        )
        sys.exit(2)

    # Files exist but we can't verify they were written this session
    print(
        f"WARNING: transcript_path not available — cannot verify file was written this session. "
        f"Found {len(matching)} existing {ext} file(s) in '{args.directory}/'.",
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
