# Strategy Overview

Open the visual strategy dashboard. Use the **strategy-awareness skill** in MODE 5 (VISUALIZE).

Steps:

1. If `~/.claude/strategy.md` does not exist, run MODE 1 (SETUP) instead — ask the 6-question setup flow first, then return here.
2. Read `~/.claude/strategy.md` and parse it into structured JSON (sections, items with stable IDs).
3. Read the visualization template at `~/.claude/skills/strategy-awareness/strategy-view-template.html`.
4. Inject the JSON into the template (replacing the `{{STRATEGY_JSON}}` marker inside the `<script id="strategy-data">` block).
5. Write the result to `~/.claude/strategy-view.html`.
6. Open it in the browser: `open ~/.claude/strategy-view.html`.
7. Confirm in one line: *"Strategy view opened. Edit visually, then paste the diff back here when ready."*

When the user pastes a diff back (a structured block starting with `Apply these changes to ~/.claude/strategy.md:`), parse and apply each operation surgically. Then offer to regenerate the view.
