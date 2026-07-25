# Full Mode

Read this reference when Mode Detection (in SKILL.md) routes to **Full Mode** — no argument given, or a PR number was provided. Full mode processes all unresolved threads on the PR.

**Bundled script paths.** The Bash tool's working directory is the user's project root, not this skill's directory, and shell state does not persist between Bash calls. Every fenced block below therefore sets `SKILL_DIR` in the same Bash call as the script it resolves — copy the block whole. Substitute the absolute skill directory Claude Code announces as "Base directory for this skill" when the skill loads.

## 1. Fetch Unresolved Threads

If no PR number was provided, detect from the current branch:
```bash
gh pr view --json number -q .number
```

Then fetch all feedback using the GraphQL script at [scripts/get-pr-comments](../scripts/get-pr-comments):

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/get-pr-comments" PR_NUMBER
```

Returns a JSON object with three keys:

| Key | Contents | Has file/line? | Resolvable? |
|-----|----------|---------------|-------------|
| `review_threads` | Unresolved inline code review threads (includes outdated; each carries its `isOutdated` flag so the resolver can account for line drift) | Yes | Yes (GraphQL) |
| `pr_comments` | Top-level PR conversation comments (excludes PR author) | No | No |
| `review_bodies` | Review submission bodies with non-empty text (excludes PR author) | No | No |

If the script fails, fall back to:
```bash
gh pr view PR_NUMBER --json reviews,comments
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments
```

## 2. Triage: Separate New from Pending

Before processing, classify each piece of feedback as **new** or **already handled**.

**Review threads**: Read the thread's comments. If there's a substantive reply that acknowledges the concern but defers action (e.g., "need to align on this", "going to think through this", or a reply that presents options without resolving), it's a **pending decision** -- don't re-process. If there's only the original reviewer comment(s) with no substantive response, it's **new**.

**PR comments and review bodies**: These have no resolve mechanism, so they reappear on every run. Apply two filters in order:

1. **Actionability**: Skip items that contain no actionable feedback or questions to answer. Examples: review wrapper text ("Here are some automated review suggestions..."), approvals ("this looks great!"), status badges ("Validated"), CI summaries with no follow-up asks. If there's nothing to fix, answer, or decide, it's not actionable -- drop it from the count entirely.
2. **Already replied**: For actionable items, check the PR conversation for an existing reply that quotes and addresses the feedback. If a reply already exists, skip. If not, it's new.

The distinction is about content, not who posted what. A deferral from a teammate, a previous skill run, or a manual reply all count. Similarly, actionability is about content -- bot feedback that requests a specific code change is actionable; a bot's boilerplate header wrapping those requests is not.

**Silent drop.** Non-actionable items are dropped without narration. Do not announce, list, or count dropped items in conversation, the task list, or the step 9 summary. Review-bot wrappers (bodies like "Here are some automated review suggestions...") commonly appear here -- recognize them by their boilerplate content, drop silently. Only CI/status bot summaries (Codecov) are pre-filtered at the script level; everything else relies on this content-aware check so bot format changes cannot silently hide actionable findings.

If there are no new items across all feedback types, skip steps 3-8 and go straight to step 9.

## 3. Plan

Create a task list of all **new** unresolved items (`TaskCreate`) -- one entry per thread or comment to resolve.

### Cluster by root cause

Reviewers file one thread per *location*; the same mistake in three files is three threads. Dispatching per thread then asks the same question three times, in three contexts that cannot see each other, and lets them answer differently on the same PR.

Group the new items into clusters. Two items share a cluster when either holds:

- **Same file** -- parallel edits to one file collide.
- **Same decision** -- they name the same symbol, convention, or suggested replacement, so answering one answers the other. Two comments saying "use `X` instead of `Y`" in different files are one decision, not two.

One cluster, one agent. This subsumes the old conflict-avoidance rule: files never overlap across clusters, so every cluster dispatches in parallel with no serialization.

### Check cited premises once

Some findings assert a fact about the repo to justify themselves: "we already use `X`", "the convention here is `Y`", "this is handled in `Z`". That claim is what makes the finding persuasive, and it is the part most likely to be wrong -- a reviewer, especially a bot, generalizes from the few files it read.

**Verify each distinct claim once, before dispatch, and pass the result to the cluster that rests on it.** Usually one `grep`, one file read, or one command settles it. Items that assert nothing about the repo skip this entirely.

This is one pass over the *claims*, not over the items -- two findings citing the same convention share one check. Doing it here rather than inside each agent is the point: an agent handed a single thread sees only the assertion, not whether it holds repo-wide.

## 4. Implement (PARALLEL)

Process all three feedback types. Review threads are the primary type; PR comments and review bodies are secondary but should not be ignored.

### Dispatch

**For review threads** (`review_threads`): Spawn one `sl-pr-comment-resolver` agent per cluster from step 3, not per thread. A cluster is usually one thread; when it is several, the agent resolves them together and returns one summary per thread.

Each agent receives, for every thread in its cluster:
- The thread ID
- The file path and location fields: `line`, `originalLine`, `startLine`, `originalStartLine` (any can be null; outdated and file-level threads often have `line == null` and must fall back to `originalLine`)
- The full comment text (all comments in the thread)
- The PR number (for context)
- The feedback type (`review_thread`)
- The `isOutdated` flag from the thread node (tells the agent the reported line may have drifted)

Plus, when step 3 found one, the **verified premise** for its cluster: the claim the findings rest on and whether it actually holds, with the evidence. An agent told "the repo does not in fact use `X` -- `grep` returns 0 hits outside these two files" reaches a different verdict than one left to take the reviewer's word.

**For PR comments and review bodies** (`pr_comments`, `review_bodies`): These lack file/line context. Cluster and dispatch them the same way. The agent receives the comment ID, body text, PR number, and feedback type (`pr_comment` or `review_body`), and must identify the relevant files from the comment text and the PR diff.

### Agent return format

Each agent returns one short summary **per item it handled** -- a single-thread cluster returns one, a three-thread cluster returns three, each with its own `feedback_id` and `reply_text`. Aggregate across all agents before step 5.
- **verdict**: `fixed`, `fixed-differently`, `replied`, `not-addressing`, `declined`, or `needs-human`
- **feedback_id**: the thread ID or comment ID it handled
- **feedback_type**: `review_thread`, `pr_comment`, or `review_body`
- **reply_text**: the markdown reply to post (quoting the relevant part of the original feedback)
- **files_changed**: list of files modified (empty if replied/not-addressing)
- **reason**: brief explanation of what was done or why it was skipped

Verdicts are defined and assigned in `sl-pr-comment-resolver`. The parent only routes on them:

- `fixed` / `fixed-differently` are the verdicts that carry a non-empty `files_changed`, which is what engages steps 5, 5b, 6 and 8.
- `needs-human` gets its reply posted and its thread left **open**.
- `replied` / `not-addressing` / `declined` change nothing. A round of only these is a reply-only round.

### Batching

Clusters are independent by construction, so they all dispatch in parallel -- no serialization, no file-overlap check. Batch in groups of 4 above 4 clusters. Platforms without parallel dispatch run them sequentially.

Fixes can occasionally expand beyond their cluster (e.g. renaming a method updates callers elsewhere). This is rare but can cause parallel agents to collide. Step 5 (combined validation) catches test breakage; step 8 (verify) catches unresolved threads. If either surfaces inconsistent changes, re-cluster the affected items together and re-run them as one agent.

## 5. Validate Combined State

After all agents complete, aggregate `files_changed` across every returned summary. If it's empty -- all verdicts are `replied`, `not-addressing`, `declined`, or `needs-human` -- skip steps 5, 5b, and 6 entirely and proceed to step 7.

Resolvers run only targeted tests on their own changes. This step runs the project's full validation **once** against the combined diff to catch cross-agent interactions that targeted runs can't see.

1. **Run the project's validation command** (test suite, type check, or whatever the repo's AGENTS.md/CLAUDE.md specifies). Run once, not per-agent.

2. **Green** -> proceed to step 6.

3. **Red, failures touch files resolvers changed** -> one inline diagnose-and-fix pass. Re-run validation. If still red, escalate with a `needs-human` item containing the test output; do **not** commit.

4. **Red, failures touch only files no resolver changed** -> treat as pre-existing. Proceed to step 6, but add a footer to the commit message: `Note: pre-existing failure in <test> not addressed by this PR.`

Record the validation outcome (command run, pass/fail counts, any pre-existing failures noted) for the step 9 summary.

Also record whether the output was **identical** to the same command's output before this round's fixes. A round whose fixes leave validation byte-identical changed comments, wording, or style but nothing the project's own checks can observe. Step 8 uses this to tell defect-finding from polishing.

## 5b. Codex Pre-Push Review Gate

The test suite is the only correctness signal between a resolver's edit and a public PR commit. Anything it does not encode -- a fix that satisfies the reviewer's letter but not their intent, a regression in an untested branch -- is caught by the PR's review bots on the *next* round, costing a ~5-minute quiescence wait and one of only three permitted fix-verify cycles. This gate gives the combined diff a second-model read while fixing it is still free.

**Engage the gate only when this round changed files** -- i.e. step 5's aggregated `files_changed` was non-empty. A reply-only round has no diff to review; skip straight to step 7.

**Opt-out check.** Resolve the repo root, then `Read` `<repo-root>/.super-looper/config.local.yaml`. If it sets `resolve_pr_codex_review: off`, skip this step and proceed to step 6. A missing root, missing file, or unrecognized value falls through to the default (on) -- never fail or block on config.

```bash
git rev-parse --show-toplevel
```

Run the review over the uncommitted diff:

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/codex-review"
```

Keep this a single pinned command, not an `if [ -f … ]` guard. A guard that evaluates false skips the gate *silently* and the round reads as reviewed when it never was; an unguarded call that cannot find its script fails loudly and is fixed in one step. Prefer the loud failure.

Route on the **first token of line 1**:

| First line | Action |
|-----------|--------|
| `codex-review: ok` | Read `references/codex-gate.md` and follow it. |
| `codex-review: unavailable` | Gate skipped -- Codex is not installed. Note the reason for step 9 and proceed to step 6. |
| `codex-review: timed-out` / `codex-review: failed` | Gate skipped -- note the reason for step 9 and proceed to step 6. |

**The gate never blocks the push.** Every path terminates at step 6. It is advisory: a gate that can refuse to push would, in an unattended run, strand validated fixes in an uncommitted working tree with no human to unblock it -- strictly worse than pushing with a noted concern, since the PR's own bots and required status checks remain as the real gate.

## 6. Commit and Push

1. Stage only files reported by sub-agents and commit with a message referencing the PR:

```bash
git add [files from agent summaries]
git commit -m "Address PR review feedback (#PR_NUMBER)

- [list changes from agent summaries]"
```

2. Push to remote:
```bash
git push
```

## 7. Reply and Resolve

After the push succeeds, post replies and resolve where applicable. The mechanism depends on the feedback type.

### What to post

Each resolver returned a composed `reply_text`, already quoting the relevant part of the original feedback. **Post it verbatim.** Do not re-write or re-format it here — the per-verdict formats live in `sl-pr-comment-resolver`, where the text is actually written.

For `needs-human` verdicts, post the reply but do NOT resolve the thread. Leave it open for human input.

### Review threads

0. **Verify the thread ID** before replying. GitHub Enterprise can return inconsistent node IDs for the same thread depending on the query path. Always confirm the ID from `get-pr-comments` resolves to the correct thread using [scripts/get-thread-for-comment](../scripts/get-thread-for-comment) with the comment's numeric URL ID:
```bash
# Extract numeric comment ID from the comment URL (e.g. discussion_r2589700 → 2589700)
GH_REPO=OWNER/REPO gh api repos/{owner}/{repo}/pulls/comments/COMMENT_ID --jq .node_id
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/get-thread-for-comment" PR_NUMBER COMMENT_NODE_ID OWNER/REPO
```
The returned `id` is the authoritative thread ID to use for reply and resolve. If it differs from what `get-pr-comments` returned, use the one from this script.

1. **Reply** using [scripts/reply-to-pr-thread](../scripts/reply-to-pr-thread):
```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/reply-to-pr-thread" THREAD_ID <<'EOF'
REPLY_TEXT
EOF
```
Check that the returned comment URL contains the correct `OWNER/REPO` and PR number before proceeding.

2. **Resolve** using [scripts/resolve-pr-thread](../scripts/resolve-pr-thread):
```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/resolve-pr-thread" THREAD_ID
```

### PR comments and review bodies

These cannot be resolved via GitHub's API. Reply with a top-level PR comment referencing the original:

```bash
gh pr comment PR_NUMBER --body "REPLY_TEXT"
```

Include enough quoted context in the reply so the reader can follow which comment is being addressed without scrolling.

## 8. Verify

**Re-fetch first, wait second.** A re-fetch is one GraphQL call; a wait is minutes. The reverse order pays the full timeout even when the reviewer already responded, and pays it again when the reviewer never will.

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/get-pr-comments" PR_NUMBER
```

Route on what comes back:

| Re-fetch result | Action |
|-----------------|--------|
| New threads present | Loop from step 2. The reviewer already responded — no wait was needed at all. |
| Empty, and this round **pushed a fix** | One short settle window, then re-fetch once more. Read `references/verify-gate.md`. |
| Empty, and **nothing was pushed** | Conclude. There is no new commit for a bot to re-review. |

`review_threads` should be empty apart from `needs-human` items. PR comments and review bodies have no resolve mechanism, so they still appear in the output; confirm they were replied to by checking the PR conversation.

**If new threads remain**, check two stop conditions before looping. Both count across the **whole PR**, not the current invocation — a fresh `/sl-resolve-pr-feedback` call must not reset them. Three invocations of one round each is three rounds, and the reviewer cannot tell the difference.

### Stop condition 1 — round count

Read it off the branch rather than from memory, since memory ends when the invocation does. Every fix round leaves a commit from step 6:

```bash
BASE=$(gh pr view PR_NUMBER --json baseRefName -q .baseRefName)
git log --oneline "origin/$BASE..HEAD" --grep="Address PR review feedback (#PR_NUMBER)" | wc -l
```

This counter depends on step 6's commit subject staying exactly `Address PR review feedback (#PR_NUMBER)`. If that format changes, this breaks silently and the loop becomes unbounded again — change both together.

- **Fewer than 3**: repeat from step 2 for the remaining threads.
- **3 or more**: stop looping and hand back (see *Handing back* below).

### Stop condition 2 — zero-delta plateau

Using the identical-output flag recorded in step 5: when **two consecutive rounds** are zero-delta, the reviewer has moved from finding defects to polishing. Stop looping and hand back, even if the round count is under 3.

The cost is what justifies this, not the findings' quality. A one-line, zero-delta change still pays a full fetch, cluster, dispatch, validation, Codex gate, push, reply, resolve and settle window. The fixes stay cheap; the loop around them does not.

### Handing back

Do **not** reclassify the remaining findings as nits and decline them. They are usually correct, and this skill's stated default is to fix — a severity judgment on reviewer prose is exactly the call it refuses to make. What has run out is the value of the *loop*, not of the fixes.

So: apply any remaining findings in one batch, reply and resolve their threads, and conclude **without** re-entering the wait. Then surface the pattern for the user to decide on: "Multiple rounds of feedback on [area/theme] — here's what we've fixed so far, what keeps appearing, and whether any of it changed behaviour." For anything genuinely unresolved, use the `needs-human` escalation pattern and leave those threads open.

## 9. Summary

Present a concise summary of all work done. Group by verdict, one line per item describing *what was done* not just *where*. This is the primary output the user sees.

Format:

```
Resolved N of M new items on PR #NUMBER:

Fixed (count): [brief description of each fix]
Fixed differently (count): [what was changed and why the approach differed]
Replied (count): [what questions were answered]
Not addressing (count): [what was skipped and why]
Declined (count): [what was declined and the harm cited]

Validation: [one line -- e.g., "bun test passed (893/893)" or "bun test passed with pre-existing failure in X noted"; omit when no code changes were committed]
Codex gate: [one line -- "approved", "N finding(s) addressed, M noted", or a skip reason such as "skipped (codex CLI not installed)"]
Reviewer wait: [one line, only when the step-8 gate timed out or fell back to the settle-window]
```

Three reporting rules the format alone does not carry:

- **Omit the `Codex gate` line entirely when no fix was pushed**, so the summary never implies a review that did not happen.
- **Omit the `Reviewer wait` line when the gate confirmed quiescence or no fix was pushed**, so it never implies quiescence it did not reach.
- **Never count Codex findings in the verdict tallies.** They carry no thread ID and belong only on the `Codex gate` line; counting them misreports how much reviewer feedback was addressed, which is the number the user actually reads.

**If this round has any `needs-human` verdict, or step 2 found a pending decision from a previous run**, read `references/summary.md` and follow it for those blocks. Most rounds have neither and can stop here.
