---
description: Build the codebase based on the plan
argument-hint: [path-to-plan]
---

# Build

Follow the `Workflow` to implement the `PATH_TO_PLAN` then `Report` the completed work.

## Variables

PATH_TO_PLAN: $ARGUMENTS

## Workflow

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user to provide it.
- Read the plan at `PATH_TO_PLAN`. Ultrathink about the plan and implement it into the codebase.

## Review & Simplify

After implementation is complete, dispatch the `code-review-simplify` agent to review and simplify the changed code:

1. Get the list of changed files with `git diff --name-only`
2. Launch the `code-review-simplify` agent with the changed file list
3. If the agent reports **NEEDS_FIXES**: apply the fixes before proceeding to the report
4. If the agent reports **PASS**: proceed to the report

## Report

- Summarize the work you've just done in a concise bullet point list.
- Report the files and total lines changed with `git diff --stat`
