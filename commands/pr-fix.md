---
description: Review and address PR comments by dispatching parallel builder agents
argument-hint: <PR#>
model: opus
---

# PR Fix

Address review comments on a pull request by orchestrating parallel builder agents. Fetch comments, triage into tasks, dispatch builders, commit, push, and reply on each addressed comment.

## Variables

PR_NUMBER: $ARGUMENTS

## Instructions

- If no `PR_NUMBER` is provided, STOP and ask the user to provide it.
- You are an orchestrator. You NEVER write code directly. You dispatch agents to do the work.
- Use `TaskCreate`, `TaskUpdate`, `TaskList`, `TaskGet` to manage the work.
- Use `Task` to deploy agents. Use `run_in_background: true` for parallel execution.
- Always provide builders with full context: the comment text, file path, line range, and surrounding diff.
- **Autonomous mode**: All agents MUST be dispatched with `mode: "bypassPermissions"` so they can run gh CLI, git, and file operations without prompting. This flow is designed to run end-to-end without user intervention.

## Workflow

Execute these steps in order. Do not skip steps.

### Step 1: Fetch PR Data (Haiku agent)

Launch a **Haiku** agent (`mode: "bypassPermissions"`) to gather all PR review comment data. The agent should run these `gh` commands and return structured results:

```
gh pr view PR_NUMBER --json number,title,headRefName,baseRefName,url,headRefOid
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments
gh api repos/{owner}/{repo}/pulls/PR_NUMBER/reviews
```

The agent should return:

- PR metadata: number, title, head branch, base branch, URL, head SHA
- All review comments with: id, author, body, path, line/original_line, diff_hunk, in_reply_to_id, created_at
- Group threaded comments (replies grouped under their parent by in_reply_to_id)
- Review-level comments (from reviews endpoint, the top-level review body)

**Important**: Derive `{owner}/{repo}` from the git remote, not hardcoded.

### Step 2: Triage & Plan (Sonnet agent)

Launch a **Sonnet** agent (`mode: "bypassPermissions"`) with ALL the data from Step 1. The agent should:

**2a. Categorize each comment thread:**

- **actionable** - Requests a specific code change (bug fix, refactor, style, missing handling, etc.)
- **question** - Asks a question requiring human judgment - SKIP
- **resolved** - Already addressed in a subsequent commit or marked resolved - SKIP
- **praise** - Positive feedback, acknowledgment - SKIP
- **informational** - FYI, context, explanation - SKIP

**2b. For each actionable comment, produce a task entry:**

- `taskId`: Sequential number (1, 2, 3...)
- `commentIds`: Array of PR comment IDs in this thread (for replying later)
- `file`: File path
- `lineRange`: Approximate line range from the diff_hunk
- `description`: Clear, specific description of what code change is needed
- `diffContext`: The relevant diff_hunk for context
- `dependsOn`: Array of taskIds this depends on (empty if independent)

**2c. Dependency rules:**

- Two tasks touching the SAME file: make them sequential (second depends on first)
- Two tasks touching DIFFERENT files: can run in parallel
- If a comment references another comment's change, make it dependent

**2d. Return the complete triage plan as structured data:**

- List of actionable tasks (with all fields above)
- List of skipped comments (with id, author, reason for skipping)

### Step 3: Create Tasks

Using the triage plan from Step 2:

1. Call `TaskCreate` for each actionable task. Include in the description:
   - The review comment text (verbatim)
   - The file path and line range
   - The diff context
   - Clear instruction of what change to make
2. Call `TaskUpdate` with `addBlockedBy` to set dependencies between tasks
3. Identify parallel groups: tasks with no unresolved dependencies can run together

### Step 4: Execute (Builder agents)

Deploy builder agents (`mode: "bypassPermissions"`) to address the comments:

1. **Identify ready tasks**: Tasks with no pending `blockedBy` dependencies
2. **Launch builders in parallel**: For all ready tasks, launch **builder** agents simultaneously using `run_in_background: true`
   - Each builder gets a prompt containing:
     - The PR context (title, branch)
     - The specific review comment text
     - The file path and line range
     - The diff context
     - Instruction: "Address this PR review comment. Read the file, understand the context, and make the requested change. Be precise - only change what the comment asks for."
3. **Wait for completion**: Use `TaskOutput` with `block: true` to wait for background agents
4. **Mark complete**: `TaskUpdate` each task to `completed`
5. **Launch next wave**: Check `TaskList` for newly unblocked tasks, repeat from step 1
6. Continue until all tasks are completed

### Step 5: Review & Simplify

After ALL builders complete, dispatch the `code-review` agent (`mode: "bypassPermissions"`) to review and simplify the changed code:

1. Get the list of changed files with `git diff --name-only`
2. Launch the `code-review` agent with the changed file list and context that these are PR comment fixes
3. If the agent reports **NEEDS_FIXES**: apply the fixes before proceeding
4. If the agent reports **PASS**: proceed to commit

### Step 6: Commit & Push

Automatically commit and push the fixes to the PR branch:

1. Stage the changed files: `git add <list of changed files>` (stage specific files, never `git add -A`)
2. Commit with message: `fix: address PR review comments`
3. Push to the PR branch: `git push origin HEAD`

### Step 7: Reply on PR (Haiku agents in parallel)

After the commit is pushed:

For each addressed comment, launch a parallel **Haiku** agent (`mode: "bypassPermissions"`) to:

1. Read the git diff for the specific file that was changed (`git diff HEAD~1 -- <filepath>`)
2. Post a reply on the PR comment using:
   ```
   gh api repos/{owner}/{repo}/pulls/PR_NUMBER/comments/{comment_id}/replies -f body="<reply>"
   ```
3. The reply should be brief and professional:
   - Format: `Addressed in <commit-sha-short> — <1-sentence summary of what was changed>`
   - Example: `Addressed in a1b2c3d — Renamed variable to use camelCase and extracted the validation into a helper function.`

**Important**: Use the LAST comment ID in each thread (the most recent comment) for the reply endpoint.

### Step 8: Summary

After all steps complete, present this report:

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
| 2 | path/to/other.ts:L88 | @author: "missing null check" | Added null guard |

### Skipped ([N] comments)
| # | Author | Reason |
|---|--------|--------|
| 1 | @author | Question — needs human response |
| 2 | @author | Already resolved |
```
