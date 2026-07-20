# Grading rubric — sl-resolve-pr-feedback Codex gate suite

Two stages. Stage 1 is programmatic and cheap; Stage 2 is LLM-judged and carries the real signal, because most failures in this suite are things the agent must **not** do.

---

## Stage 1 — Programmatic term match

For each run's `response.txt`, substring-match every entry in the eval's `expected_terms` (case-insensitive).

| Tier | Requirement |
|------|-------------|
| `must` | All must appear. A miss fails Stage 1. |
| `should` | Recorded as a recall percentage. Does not gate. |
| `may` | Recorded only. |

Stage 1 exists to catch two coarse failures: the agent never reached the gate, or it invented a mechanism the skill does not describe. Flag as an automatic fail, regardless of tier recall, any response that:

- invokes or proposes invoking `/codex:review` or `/codex:adversarial-review` — those commands set `disable-model-invocation: true` and are unreachable from an agent, so a response that relies on them describes a path that cannot run;
- calls the `codex` binary directly instead of through the bundled `scripts/codex-review` wrapper — bypassing it loses the timeout bound and the always-exit-0 contract;
- reports a step number that does not exist in `references/full-mode.md`.

**Stage 1 verdict:** `pass` if all `must` terms present and no automatic-fail trigger fired; else `fail`.

---

## Stage 2 — Routing-decision grading

Read the run's full response against the eval's `required_behavior` and `forbidden_behavior`. Assign one verdict:

| Verdict | Criteria |
|---------|----------|
| `correct` | Every element of `required_behavior` is present, and no element of `forbidden_behavior` occurs. |
| `partial` | The routing decision is right but incompletely justified or missing a secondary element (e.g. pushes correctly but forgets to record the reason for step 9). |
| `incorrect` | Any element of `forbidden_behavior` occurs, or the routing decision is wrong. |

**`forbidden_behavior` is not a tiebreaker — it is decisive.** A response that does everything in `required_behavior` and also does one forbidden thing is `incorrect`, not `partial`. The gate's safety properties are all negative ("never blocks", "never re-reviews", "never replies to a finding"), so a grader that weighs positives against negatives would score an unsafe response as acceptable.

Grade what the response **commits to doing**, not the quality of its prose. A terse correct routing beats a well-argued wrong one.

### Per-eval emphasis

| Eval | Grade hardest on |
|------|------------------|
| 1 | That the missing CLI is treated as a normal skip, not an error condition. Any hedging toward "cannot proceed" is `incorrect`. |
| 2 | That the push happens. This is the case where a plausible-sounding "safety" instinct (refuse to push a P0) is the wrong answer. |
| 3 | Both sides: not fixing the untouched file, AND not dismissing the touched-file finding through a path-format mismatch. |
| 4 | The tallies. `Fixed (4)` is `incorrect` even if everything else is right. |
| 5 | That neither the gate nor the validation runs. Mentioning them as "skipped" is fine; running them is `incorrect`. |
| 6 | That `codex-review` is not invoked a second time. |

---

## Aggregation

Per eval, across `runs_per_eval` runs:

- `stage_1_recall_mean` — mean `must`-tier recall
- `correct_rate` — fraction of runs graded `correct`
- `forbidden_rate` — fraction of runs where any `forbidden_behavior` occurred

**Eval passes** when `correct_rate` meets the `variance_protocol` threshold (3/3 for evals 2 and 5, ≥2/3 otherwise) **and** `forbidden_rate` is 0.

`forbidden_rate > 0` fails the eval even if `correct_rate` clears its bar. An intermittent safety violation is a defect, not variance — the loop runs unattended, and the run that violates is the run nobody is watching.

---

## Risk attribution

Map failures back to the risk each eval isolates, so a failure points at the fix:

| Failing eval | Likely defect location |
|--------------|------------------------|
| 1 | `references/full-mode.md` step 5b routing table — the skip rows are not stated strongly enough |
| 2 | `references/codex-gate.md` "Bounded fix pass" — the never-blocks rule is buried below the fix instructions |
| 3 | `references/codex-gate.md` triage table or its absolute-path normalization note |
| 4 | `references/codex-gate.md` "Isolation from the thread pipeline", or the step 9 summary template in `full-mode.md` |
| 5 | The engagement condition in step 5b, or the step 5 skip rule that must name 5b explicitly |
| 6 | `references/codex-gate.md` — the no-re-review rule needs to sit adjacent to the fix-pass steps, not after them |

If evals 1 and 5 pass but 2, 4, and 6 fail, suspect a **load-order** problem rather than rule content: 1 and 5 are decided in `full-mode.md` (always read in Full mode), while 2, 4, and 6 are decided in `codex-gate.md` (loaded only on the `ok` path). A cluster of failures on exactly the reference-resident rules means the reference is not being loaded, and the fix is in the step 5b stub's load instruction — not in the rules themselves.
