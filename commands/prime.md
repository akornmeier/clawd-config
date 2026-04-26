---
allowed-tools: Bash, Read
description: Load context for a new agent session by analyzing codebase structure, documentation and README
---

# Prime

Run the commands under the `Execute` section to gather information about the project, and then review the files listed under `Read` to understand the project's purpose and functionality then `Report` your findings.

## Execute
- `git ls-files`

## Read

Read the project README first:
- `README.md`

Then read each reference doc below. For each one, prefer the project-local copy at `ai_docs/<file>` if it exists; otherwise fall back to the global copy at `~/.claude/ai_docs/<file>`:

- `cc_hooks_docs.md`
- `uv-single-file-scripts.md`
- `anthropic_custom_slash_commands.md`
- `anthropic_docs_subagents.md`

If a doc is missing from both locations, skip it and note that in the report.

## Report

- Provide a summary of your understanding of the project