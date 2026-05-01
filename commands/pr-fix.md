---
description: Review and address PR comments by dispatching parallel builder agents
argument-hint: <PR#>
model: opus
---

# PR Fix

Address review comments on a pull request. Fetch comments, triage, dispatch parallel builders for independent fixes, commit, push, and reply.

## Variables

PR_NUMBER: $ARGUMENTS

## Instructions

- If no `PR_NUMBER` is provided, STOP and ask the user to provide it.
- You are an orchestrator. You NEVER write code directly. You dispatch agents to do the work.
- Always provide builders with full context: the comment text, file path, line range, and surrounding diff.
- **Autonomous mode**: All agents MUST be dispatched with `mode: "bypassPermissions"` so they can run gh CLI, git, and file operations without prompting. This flow is designed to run end-to-end without user intervention.

## Workflow

### Step 1: Fetch, Triage & Plan (Sonnet agent)

Launch a single **Sonnet** agent (`mode: "bypassPermissions"`) that fetches all PR data AND triages it in one pass. The agent should:

**1a. Fetch PR data** using `gh` CLI:

```
gh pr view PR_NUMBER --json number,title,headRefName,baseRefName,url,headRefOid
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/reviews
```

Derive `{owner}/{repo}` from `git remote get-url origin`, not hardcoded.

**1b. Categorize each comment thread:**

- **actionable** — Requests a specific code change (bug fix, refactor, style, missing handling, etc.)
- **question** — Asks a question requiring human judgment → SKIP
- **resolved** — Already addressed or marked resolved → SKIP
- **praise** — Positive feedback → SKIP
- **informational** — FYI, context → SKIP

**1c. For each actionable comment, produce a task:**

- `commentIds`: Array of PR comment IDs in this thread (for replying later)
- `file`: File path
- `lineRange`: Approximate line range from the diff_hunk
- `description`: Clear, specific description of what code change is needed
- `diffContext`: The relevant diff_hunk

**1d. Group tasks for parallel execution:**

- Tasks touching DIFFERENT files → can run in parallel
- Tasks touching the SAME file → must be sequential (group them together as one task with multiple changes)
- If a comment references another comment's change → combine into same group

**1e. Return structured data:**

- PR metadata (number, title, head branch, base branch, URL, head SHA)
- Parallel groups: each group is an array of tasks that a single builder will handle
- Skipped comments (id, author, reason)

### Step 2: Execute (Builder agents in parallel)

Dispatch builder agents for all parallel groups simultaneously:

1. For each parallel group, launch a **builder** agent (`mode: "bypassPermissions"`, `run_in_background: true`)
   - Each builder gets:
     - PR context (title, branch)
     - All tasks in its group (comment text, file path, line range, diff context)
     - Instruction: "Address these PR review comments. Read each file, understand the context, and make the requested changes. Be precise — only change what the comments ask for. Reach for engineering skills when triggered: use `tdd` to write a regression test before fixing a reported bug, `diagnose` when a bug's root cause isn't obvious, and `zoom-out` if you're unfamiliar with the area of code."
   - If a group has multiple tasks (same-file comments), the builder handles them sequentially
2. Wait for all builders to complete

### Step 3: Review (conditional)

Check the scope of changes:

1. Run `git diff --stat` to see what changed
2. **If 3+ files changed OR 50+ lines changed**: dispatch the `code-review` agent (`mode: "bypassPermissions"`) to review the changes. If it reports fixes needed, apply them.
3. **If fewer changes**: skip the review — the builders' targeted edits are low-risk.

### Step 4: Commit, Push & Reply

Do this step yourself (no agent needed):

1. Stage changed files: `git add <specific files>` (never `git add -A`)
2. Commit: `fix: address PR review comments`
3. Push: `git push origin HEAD`
4. Get the commit SHA: `git rev-parse --short HEAD`

Then launch parallel **Haiku** agents (`mode: "bypassPermissions"`, `run_in_background: true`) to reply on each addressed comment:

- Use the LAST comment ID in each thread for the reply endpoint
- Reply format: `Addressed in <sha> — <1-sentence summary>`
- Command: `gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments/{comment_id}/replies -f body="<reply>"`

### Step 5: Summary

Present this report:

```
## PR Fix Complete

**PR**: #[number] — [title]
**Branch**: [branch]
**URL**: [url]
**Commit**: [sha]

### Addressed ([N] comments)
| # | File | Comment | Change Made |
|---|------|---------|-------------|
| 1 | path/to/file.ts:L42 | @author: "use camelCase here" | Renamed variable |

### Skipped ([N] comments)
| # | Author | Reason |
|---|--------|--------|
| 1 | @author | Question — needs human response |
```
