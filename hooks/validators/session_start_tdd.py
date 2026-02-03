#!/usr/bin/env python3
"""
Session Start TDD Reset - SessionStart Hook

Clears the TDD session state at the start of each new session.
This ensures each conversation starts with a clean slate for
tracking test file modifications.

Usage: uv run ~/.claude/hooks/validators/session_start_tdd.py
"""

import json
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "data" / "tdd_session_state.json"


def main():
    """Reset the TDD session state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    initial_state = {
        "test_files_modified": [],
        "session_id": None,
        "started_at": None
    }

    STATE_FILE.write_text(json.dumps(initial_state, indent=2))

    # Output confirmation (hooks expect JSON or empty output)
    print(json.dumps({"status": "reset", "message": "TDD session state cleared"}))


if __name__ == "__main__":
    main()
