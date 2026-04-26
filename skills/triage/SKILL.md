---
name: triage
description: Use whenever the user wants to address PR review comments, work through reviewer feedback (CodeRabbit, Copilot, human reviewers), respond to review suggestions, or resolve open review threads on the current branch's pull request. Auto-detects the PR from the current branch, fetches both conversation and inline review comments in parallel, groups them by file and theme, proposes concrete fixes, applies edits directly in the main agent (sub-agents repeatedly hit Edit-permission blocks even with bypassPermissions), then commits, pushes, and replies to each comment with the resolving SHA. Trigger this even when the user just says "address the PR comments" or "fix the review feedback" without naming the skill.
---

# Triage PR Comments

End-to-end workflow for resolving PR review feedback on the current branch's pull request — from fetching comments to replying with the resolving commit SHA.

## Why this skill exists

Past `/pr-fix` runs lost time when dispatched builder sub-agents got blocked from `Edit` even under `bypassPermissions`. This skill keeps all writes (Edit, Write, git) in the main agent while still parallelizing the read-heavy phases (fetching comments, running checks). The result is comparable speed to a sub-agent fan-out, without the permission-retry tax.

If the user explicitly invokes `/pr-fix`, defer to that — they've chosen the parallel-agent flow on purpose.

## Workflow

### 1. Discover the PR from the current branch

```bash
gh pr view --json number,headRefName,baseRefName,url,title,isDraft,state
```

If no PR is found, stop and report it — don't fabricate a number. If the PR is closed/merged, confirm with the user before continuing.

### 2. Fetch all comment sources in parallel

Issue these as parallel Bash calls in a single message — they're independent:

- `gh pr view <N> --json comments,reviews,reviewThreads` — top-level conversation, review summaries, and thread resolution state
- `gh api repos/{owner}/{repo}/pulls/<N>/comments --paginate` — inline file/line review comments (this is where most actionable feedback lives)
- `gh pr diff <N>` — diff context, used for grouping comments to changed regions
- `gh pr checks <N>` — failing checks often correspond to the same issues reviewers are flagging

Skip resolved review threads. Focus on unresolved feedback and outdated-but-unaddressed comments.

### 3. Group, dedupe, and propose

Build a structured plan. For each group, capture:

- **Files / lines** affected
- **Comment(s)** consolidated — when CodeRabbit and a human flag the same line, treat them as one issue
- **Proposed fix** — a concrete change, not "consider refactoring." If a comment is a question or architectural pushback, mark it as **needs-discussion** and surface to the user instead of silently editing
- **Verification** — lint, targeted test, or just a re-read

Show the plan to the user as a compact table or numbered list before applying edits. Keep it scannable — the user should be able to spot a wrong call in seconds. Proceed unless they interrupt.

If the user invokes this skill in **plan-only** mode (e.g., "triage but don't apply yet"), stop here and output the structured plan as the final result.

### 4. Apply edits directly in the main agent

Use Edit/Write from the main agent. Do not dispatch sub-agents for edit work — they get blocked.

- Where edits are independent across files, batch the Edit calls in parallel within a single message.
- Where they're dependent (e.g., a rename in file A propagates to file B), sequence them.
- For purely mechanical fixes (trailing whitespace, lint autofixes), prefer running the formatter once over hand-editing each instance.

### 5. Verify before commit

Run in parallel where possible:

- Linters/formatters scoped to the changed files
- Targeted tests for the changed modules (full suite only if the user wants it or the change is broad)
- A re-read of each modified file to confirm the edit landed correctly

Never push red. If a check fails, fix it before committing.

### 6. Commit, push, reply

Default to **one bundled commit per triage run** with a message that names the themes addressed. If the PR convention is one commit per concern (check `git log` on the branch), follow that instead.

Use a HEREDOC commit message with the standard `Co-Authored-By` trailer. Stage specific files, not `git add -A`.

```bash
git push
```

Then reply to each comment with the resolving SHA. For inline review comments, reply on the thread:

```bash
gh api -X POST repos/{owner}/{repo}/pulls/<N>/comments/<COMMENT_ID>/replies \
  -f body="Fixed in <SHA>: <one-line summary>"
```

For top-level conversation comments, post one summary via `gh pr comment <N>` listing what each addressed group corresponds to which commit. Avoid spamming individual replies when one summary is clearer.

### 7. Re-check CI

After push, run `gh pr checks <N>` (use `--watch` only if checks are slow) and report status. If anything regressed, surface it immediately rather than declaring the run done.

## Speed strategy

This workflow is built to match `/pr-fix` parallel-agent speed via two mechanisms:

1. **Parallel Bash for reads** — fetching comments, diff, and checks happen concurrently in one message, not serially.
2. **Parallel Edit for independent writes** — when fixes touch unrelated files, batch the Edit calls in one message so they apply together.

The wall-clock difference vs. sub-agents is usually small for PRs under ~15 comments. Past sub-agent runs paid more in permission retries than they saved in parallelism.

## When NOT to use this skill

- "Just look at the PR" or "summarize the comments" — that's a read-only task; just run `gh pr view` and respond.
- The PR has unresolved architectural disagreements — flag those for the user; don't try to silently fix design debates.
- The user explicitly invoked `/pr-fix` — they've opted into the sub-agent flow.

## Output format

End every triage run with a brief summary the user can paste anywhere:

```
Triaged PR #<N>: <title>
- <N> comments addressed across <M> files
- Commit: <SHA> pushed to <branch>
- Replies posted to <K> threads
- CI: <status>
- Needs-discussion (not fixed): <list, or "none">
```
