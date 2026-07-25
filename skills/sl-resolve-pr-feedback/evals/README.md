# sl-resolve-pr-feedback eval suite

## Purpose

Two suites in one file.

**Evals 1–6 — the step 5b Codex pre-push review gate**, the step that hands the resolvers' uncommitted diff to `codex review` before it becomes a public PR commit.

**Evals 7–9 — the core loop**: step 2 triage and verdict selection. These are the paths the skill exists for, and until 2026-07-25 they had no measurement at all.

The gate's correctness is almost entirely negative. It must **not** block the push, **not** re-review its own fix, **not** widen scope to files no resolver touched, **not** leak findings into the thread reply/resolve pipeline, and **not** run at all when there is no diff. None of those properties is checkable by `bun test`: the gate is skill prose, and a regression in prose produces no test failure. This suite is how they stay measurable.

Still out of scope: GraphQL mechanics and the step-8 quiescence gate. Both are separate behaviors with their own failure modes.

## Files

| File | Purpose |
|------|---------|
| `evals.json` | Nine scenarios, each with a prompt, expected terms by criticality tier, and an explicit `required_behavior` / `forbidden_behavior` pair |
| `grader.md` | Two-stage rubric — programmatic term match, then routing-decision grading where `forbidden_behavior` is decisive |
| `README.md` | This file |

## Test cases at a glance

| # | Name | Risk tested |
|---|------|-------------|
| 1 | gate-skipped-when-cli-absent | Hard dependency on an optional tool |
| 2 | p0-finding-does-not-block-push | Gate traps the loop |
| 3 | finding-outside-changed-files-is-pre-existing | Scope creep / path-normalization failure |
| 4 | findings-stay-out-of-the-thread-pipeline | Verdict tally contamination |
| 5 | reply-only-round-never-engages-the-gate | Wasted spend and latency |
| 6 | no-self-review-loop | Unbounded advice loop |
| 7 | pending-decision-is-not-reprocessed | Arguing with the PR author |
| 8 | non-actionable-review-body-is-dropped-silently | Noise in the user-facing count |
| 9 | plausible-but-wrong-finding-gets-evidence-not-a-fix | Fixing over reading |

## Design rationale

**Why these six.** Each isolates one property the gate would silently lose:

- **1 and 5 are the availability and cost cases.** Most users will not have the Codex CLI installed, and every needless invocation costs a paid run plus ~25s. Both are decided in `full-mode.md`, which Full mode always reads.
- **2 is the safety case, and the one most likely to regress.** A `P0` finding creates real pressure to "be safe" by refusing to push — which is exactly backwards. In an unattended run that strands validated fixes in an uncommitted tree with nobody present, while the PR's own required checks were already the real gate. The eval exists because the wrong answer is the intuitive one.
- **3 is two-sided on purpose.** Fixing a finding in an untouched file inflates the PR mid-review. But the opposite failure is worse and much quieter: Codex reports absolute paths while `files_changed` is repo-relative, so an agent that compares them naively sees *every* finding as pre-existing and the gate silently does nothing while appearing to work.
- **4 guards the number the user actually reads.** Counting a Codex finding among the `fixed` verdicts misreports how much reviewer feedback was addressed, and attempting to resolve a finding that has no thread ID errors outright.
- **6 guards against the advice loop.** A reviewer asked to check its own fix will usually find something else to say. One pass, no re-review.

**Why 7, 8 and 9.** The same test as the first six — each isolates a property that fails quietly:

- **7 is the conversation case.** A deferral reply is a human decision in flight. Re-processing it posts a second reply underneath the first, which reads as the skill arguing with the PR author and buries the open question. Nothing errors; the thread just gets worse.
- **8 is the signal-to-noise case.** Review bodies have no resolve mechanism, so they reappear every run. The subtle failure is not replying to the wrapper — it is *narrating* the drop, which is not wrong but trains the user to skim summary lines that never matter.
- **9 is the counter-pressure case for "default to fixing".** The disposition that makes this skill useful is also the one that, pushed too far, adds a redundant null check next to an existing guard: dead defensive code, plus a reviewer taught that their misreading was right. It is the mirror of eval 2 — there the intuitive answer was too cautious, here it is too eager.

**Why `forbidden_behavior` is decisive rather than weighted.** Every safety property here is negative. A grader that weighed positives against negatives would pass a response that routes correctly and also, say, posts a GitHub reply for a Codex finding. The rubric therefore fails any run exhibiting a forbidden behavior even when everything else is right.

**Why an intermittent violation fails the eval.** `forbidden_rate > 0` fails regardless of `correct_rate`. This skill runs unattended inside `lfg`; the one run in three that violates is the run nobody is watching.

**Why evals 2 and 5 need 3/3 rather than 2/3.** They are the two cases whose failure is unrecoverable in an unattended run — a stranded working tree, and spend the user never authorized. The rest degrade to noise or a slightly worse PR.

## How to run

Through the `skill-creator` framework, **not** `bun test`. `bun test` checks only that this suite has the required file shape (`tests/skill-evals-shape.test.ts`); it does not execute the scenarios.

Plugin skill content caches at session start, so a run dispatched from the session that edited the skill tests the pre-edit content. skill-creator injects the current skill source at dispatch time, which is why it is the right harness here.

**Workspace:** `/tmp/super-looper/sl-resolve-pr-feedback/evals/iteration-<N>/` per the repo's scratch conventions.

With `runs_per_eval: 3` and nine evals, that is 27 dispatches per pass. Each subagent receives the eval prompt, invokes the skill, and writes its response verbatim to `<workspace>/eval-<ID>-<name>/run-<R>/response.txt`. A grader subagent then applies `grader.md` and writes `grading.json` per run, aggregated to `summary.json` per eval.

**Baselines are not useful here.** A without-skill agent has no step numbering, no gate, and no routing table to follow, so it fails every case trivially. The signal comes from grading against `required_behavior`, not from a with/without delta.

## Interpreting outcomes

| Outcome | Interpretation | Action |
|---------|----------------|--------|
| All nine pass | Gate and core loop behave as specified. | Ship. |
| Eval 1 fails | The gate reads as a hard dependency. | Strengthen the skip rows in the step 5b routing table. Highest priority — this breaks the skill for every user without Codex. |
| Eval 2 fails | The gate can trap the loop. | Move the never-blocks rule above the fix instructions in `codex-gate.md`. Ship-blocking. |
| Eval 3 fails on the touched file | Path normalization is being missed; the gate is decorative. | Make the absolute-path note prominent in the triage table, not a trailing remark. |
| Eval 4 fails | Verdict tallies are contaminated. | Restate the isolation rule in the step 9 summary template itself, where the tallies are composed. |
| Eval 6 fails | Advice loop is reachable. | Move the no-re-review rule adjacent to the fix-pass steps. |
| 1 and 5 pass, 2/4/6 fail together | Not a rule-content problem — `codex-gate.md` is not being loaded. | Fix the load instruction in the step 5b stub. See the risk-attribution note at the end of `grader.md`. |
| Eval 7 fails | Triage re-processes handled threads. | Strengthen the pending-decision paragraph in `full-mode.md` step 2. |
| Eval 8 fails | Non-actionable items reach the summary. | The Silent drop paragraph is being read as "drop but mention". State the no-narration rule in the step 9 summary section too. |
| Eval 9 fails | "Default to fixing" is overriding the evidence. | The tripwires in the agent rubric are subordinate to the disposition above them. Raise the finding-does-not-hold case. |
| High variance, no forbidden behaviors | Routing is right but justification wanders. | Acceptable. Grade on the decision, not the prose. |
