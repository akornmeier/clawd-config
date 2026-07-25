---
name: planf3
description: Creates, updates, and executes HTML implementation plans saved to specs/. Use when the user asks to plan, spec, or design work before building it; to revise or re-reference an existing plan; or to implement a plan that already exists. Handles embedded diagrams and append-only plan metadata. Triggers on /planf3, "write a plan", "spec this out", "update the plan", "build the plan".
argument-hint: "[user-prompt] [--questionable]"
---

# Plan F3

A plan is one self-contained `.html` page in `specs/` — opens in a browser, carries its own
styling and diagrams, and is written, revised, and executed by engineers and agents alike.

## Variables

RAW_ARGS: $ARGUMENTS
USER_PROMPT: `RAW_ARGS` with any `--questionable` flag removed and surrounding whitespace trimmed
QUESTIONABLE: true if `RAW_ARGS` contains `--questionable`, otherwise false
PLAN_OUTPUT_DIRECTORY: `specs/`
PLAN_FILE: `PLAN_OUTPUT_DIRECTORY/<descriptive-kebab-name>.html`
IMAGES_OUTPUT_DIR: `PLAN_OUTPUT_DIRECTORY/<plan-name>/`
TEMPLATE: `templates/plan.html`
AI_DOCS: `AI_DOCS/` — read only if the directory exists
APP_DOCS: `APP_DOCS/` — read only if the directory exists
BROWSER: `chrome`

## Contracts

The rules you cannot derive from the files themselves. Everything else is your judgment.

- If no `USER_PROMPT` is given, stop and ask for it.
- Plans are authored from `TEMPLATE`. Read it in full, replace every double-brace
  placeholder with real content, and duplicate the blocks marked `repeat` as many times as
  the plan needs. No unfilled placeholder and no leftover marker ships in a saved plan.
- `TEMPLATE`'s `:root` block is the identity source of truth for the page *and* for every
  image embedded in it. Re-tune the values per plan; keep the variable names.
- The page stays self-contained: one style block, no external stylesheets, fonts, or scripts.
- Every metadata field except `created` is an append-only list. Add to it, never overwrite it.
- Omit the Questionables section entirely unless `QUESTIONABLE` is true. When it is, put open
  decisions, assumptions, and risks there instead of deciding them silently.
- Size the plan to the size of the work. No padded sections, no summary restating a section
  the reader just passed.
- Plan what was asked at the scope asked. Note a concern in a sentence and keep going rather
  than quietly widening the plan.

## Workflow

Select the single best-matching workflow and read its file for step-by-step instructions
before acting.

| Workflow | When to call it | File to read |
| --- | --- | --- |
| Create Plan | The prompt asks to plan, spec, or design new work and no existing plan is referenced | `workflows/create-plan.md` |
| Update Plan | The prompt asks to change, extend, or revise the content of an existing plan | `workflows/update-plan.md` |
| Update References | The prompt asks to refresh plan metadata or back/forward references (created, modified, commits, agent, session) | `workflows/update-references.md` |
| Build Plan | The prompt asks to implement, execute, or carry out the work described in an existing plan | `workflows/build-plan.md` |

### Subworkflow

Called by other workflows rather than selected directly from the `USER_PROMPT`.

| Subworkflow | When it's called | File to read |
| --- | --- | --- |
| Image Generation | Invoked by other workflows (e.g. Create Plan) to generate, fill, or regenerate the embedded images in a plan | `workflows/image-generation.md` |

## Files

Paths below are relative to this skill's own directory — Claude Code announces it as
"Base directory for this skill" when the skill loads — not to the working directory.

| Path | What it is | Read it when |
| --- | --- | --- |
| `templates/plan.html` | The HTML artifact every plan is authored from, styling included | Creating or updating a plan |
| `workflows/*.md` | One file per workflow above | Routing to that workflow |
| `scripts/*.py` | gpt-image generation and editing | Never — the Image Generation subworkflow executes them |
