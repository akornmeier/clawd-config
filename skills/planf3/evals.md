# planf3 evaluations

Three scenarios, one per distinct load path through the skill. Run each in a **fresh
session** from `/Users/tk/.claude`, in order — B depends on A's output, C on B's. A fresh
session is required because description-driven discovery only shows up when the skill has
to fire on its own.

Deliberately not linked from `SKILL.md`: an unreferenced file costs nothing at runtime.

Baselines below were recorded on 2026-07-24, immediately after the Claude 5
context-engineering rewrite (`SKILL.md` 241 → 72 lines, template extracted to
`templates/plan.html`).

## Scenario A — create

**Query**, typed without `/planf3`: *"write a plan for adding rate limiting to the API"*

**Load path**: `SKILL.md` → `workflows/create-plan.md` → `templates/plan.html`, then
`workflows/image-generation.md` for the figure slots.

**Expected**
- Fires from the description alone, with no slash command.
- Reads `templates/plan.html` in full before authoring.
- Writes exactly one kebab-case `.html` to `specs/`.
- Zero unfilled double-brace placeholders and zero leftover `repeat` markers in the output.
- Metadata header populated: `created` set, `agent name` and `session id` present.
- No Questionables section (the `--questionable` flag was not passed).
- Opens in Chrome styled, with figures centred and SVG colours resolving against the
  plan's own `:root`.

**Baseline**: structural path verified by construction — template exists, declares all six
image-contract roles, and slot replacement works from an arbitrary working directory.
Behavioural baseline pending first fresh-session run; record the result here.

## Scenario B — update

**Query**: *"add a rollback phase to that plan"*

**Load path**: `SKILL.md` → `workflows/update-plan.md`. Should **not** need
`templates/plan.html`, since the plan already exists.

**Expected**
- Edits the phases section only; Purpose, Problem, Solution, and Notes untouched.
- Appends a second timestamp to `modified` rather than overwriting the first.
- Appends to `agent name` and `session id` rather than replacing them.
- Appends one Amendments entry at the bottom describing the rollback phase.

**Baseline**: append-only metadata is stated once, in `SKILL.md`'s Contracts, and restated
operationally in `update-plan.md` step 4. Behavioural baseline pending first run.

## Scenario C — build

**Query**: *"build the rate limiting plan"*

**Load path**: `SKILL.md` → `workflows/build-plan.md`. This is the scenario the refactor
exists for: the template must never be read.

**Expected**
- Reads `build-plan.md`; does **not** read `templates/plan.html` at any point.
- Flips status markers `[]` → `[wip]` → `[x]` in the plan file as it works, `[f]` for
  anything it cannot make pass.
- Runs each phase's validation commands and loops on failure before moving on.
- Appends the commit SHA and session id to the metadata header on completion.

**Baseline**: before the refactor, the 175-line template loaded on this path unavoidably,
since it lived inside `SKILL.md`. After it, the template is a separate file no step in
`build-plan.md` references. Confirm from the transcript that the read never happens — that
absence is the whole measurement.
