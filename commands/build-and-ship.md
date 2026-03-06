---
description: Build, review, commit, create PR, handle review loop, and notify when ready
argument-hint: [path-to-plan]
model: opus
hooks:
  Stop:
    - hooks:
        - type: command
          command: >-
            uv run $HOME/.claude/hooks/validators/build_ship_stop_gate.py
---

# Build and Ship

Implement a plan, review it locally, commit and push to GitHub, create a PR, handle the review loop, and notify the user when the PR is ready for their approval.

## Variables

PATH_TO_PLAN: $ARGUMENTS

## Hard Constraints

- **NEVER** approve or merge PRs — no `gh pr merge`, no `gh pr review --approve`
- **NEVER** use `git add -A` or `git add .`
- **NEVER** force push
- The pipeline stops at "PR ready for your review" and notifies the human
- Only the human approves and merges on GitHub

## Workflow

If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user to provide it.

Read the plan at `PATH_TO_PLAN`. Extract the `Build-and-Ship Configuration` section and the `Step by Step Tasks` / `Team Members` sections. Execute all 5 phases in order.

---

## Phase 1: Implementation

Execute the plan's tasks using subagents.

### Steps

1. Read the plan file and parse:
   - `Step by Step Tasks` — each task with its ID, dependencies, assigned agent, and parallel flag
   - `Team Members` — agent types and roles
   - `Build-and-Ship Configuration` — git, review, and notification settings
2. Create tasks with `TaskCreate` for each step in the plan
3. Set dependencies with `TaskUpdate` + `addBlockedBy` based on each task's `Depends On` field
4. Deploy implementation subagents per the plan's agent assignments:
   - Use `run_in_background: true` for tasks marked `Parallel: true`
   - Use the `subagent_type` from the plan's `Agent Type` field
   - Provide each agent with its task description, relevant files, and full context
5. Wait for background agents with `TaskOutput(block: true)`
6. Mark tasks completed as agents finish with `TaskUpdate(status: "completed")`
7. Continue deploying newly unblocked tasks until all implementation tasks are done

### Error Handling
- If a subagent fails, retry the task once
- If still fails, report the failure and continue with remaining tasks

---

## Phase 2: Local Pre-flight Review

Run `code-review-simplify` on all changed files before committing.

### Steps

1. Get changed files: run `git diff --name-only` via Bash
2. Dispatch the `code-review-simplify` agent with the changed file list:
   ```
   Agent({
     description: "Pre-flight code review",
     prompt: "Review and simplify the following changed files: <file list>. These changes implement: <plan objective>.",
     subagent_type: "code-review-simplify"
   })
   ```
3. If result is **NEEDS_FIXES**:
   - Dispatch the appropriate builder agent to apply fixes
   - Re-run `code-review-simplify`
   - Maximum 3 rounds
   - If issues remain after 3 rounds, report them but proceed
4. If result is **PASS**: proceed to Phase 3

---

## Phase 3: Git Operations

Stage, commit, push, and create PR using the `git-ops` agent.

### Steps

1. Get the list of changed files: `git diff --name-only` (include both staged and unstaged)
2. Extract from the plan's `Build-and-Ship Configuration`:
   - `Branch Name` → feature branch
   - `Base Branch` → PR target
   - `Commit Prefix` → conventional commit type
   - `Reviewers` → GitHub usernames
3. Dispatch the `git-ops` agent:
   ```
   Agent({
     description: "Git commit and PR creation",
     prompt: "Perform git operations with the following configuration:
       files: <changed file list>
       branch_name: <Branch Name from config>
       base_branch: <Base Branch from config>
       commit_message: '<Commit Prefix>(<plan-scope>): <plan objective summary>'
       pr_title: '<Commit Prefix>(<plan-scope>): <plan objective summary>'
       pr_body: '## Summary\n<plan objective>\n\n## Changes\n<bullet list of changes>\n\n## Acceptance Criteria\n<from plan>'
       reviewers: <Reviewers from config>",
     subagent_type: "git-ops"
   })
   ```
4. Capture the agent's output: `PR_NUMBER`, `PR_URL`, `BRANCH`, `COMMIT_SHA`
5. **Error handling**:
   - Push conflict → agent handles via `git pull --rebase` then retry
   - PR already exists → agent returns existing PR info

---

## Phase 4: PR Review Loop

Wait for CI, poll for review comments, fix actionable ones, and reply.

### Step 4.1: Wait for CI

Run `gh pr checks <PR_NUMBER> --watch` with a 10-minute timeout.

### Step 4.2: Poll for Review Comments

Dispatch the `pr-review-monitor` agent:
```
Agent({
  description: "Monitor PR for reviews",
  prompt: "Monitor PR #<PR_NUMBER> in <owner/repo> for review comments.
    timeout_minutes: 15
    poll_interval_seconds: 60
    known_comment_ids: []",
  subagent_type: "pr-review-monitor"
})
```

### Step 4.3: Triage Comments

When the monitor returns comments, categorize each thread (reuse `/pr-fix` Step 2 logic):
- **actionable** — Requests a specific code change → fix it
- **question** — Needs human judgment → SKIP (note for report)
- **resolved** — Already addressed → SKIP
- **praise** — Positive feedback → SKIP
- **informational** — FYI/context → SKIP

### Step 4.4: Fix Actionable Comments

For each actionable comment:
1. Deploy builder subagent with:
   - The review comment text (verbatim)
   - File path and line range
   - Diff context
   - Instruction: "Address this PR review comment precisely"
2. Use `run_in_background: true` for comments on different files
3. Wait for all builders to complete

### Step 4.5: Re-run Local Review

Dispatch `code-review-simplify` on the fix changes (same as Phase 2).

### Step 4.6: Commit and Push Fixes

Dispatch `git-ops` agent for fix commits:
- Stage only the changed fix files
- Commit message: `fix(<scope>): address PR review comments`
- Push to the same branch

### Step 4.7: Reply on PR

For each addressed comment, dispatch a Haiku agent to reply:
```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments/{comment_id}/replies -f body="Addressed — <1-sentence summary>"
```
Use the LAST comment ID in each thread for the reply endpoint.

### Step 4.8: Re-poll

- Dispatch `pr-review-monitor` again with updated `known_comment_ids`
- Repeat Steps 4.3-4.7 for new comments
- Maximum 3 rounds total
- **Exit conditions**:
  - No new actionable comments → success
  - 3 rounds exhausted → report remaining issues
  - All CI checks passing → success

### Error Handling
- GitHub API rate limit → exponential backoff (60s → 120s → 240s)
- No reviewers respond in 15 min → proceed with notification that review is pending
- Fix causes new comments → track seen IDs, max 3 rounds total

---

## Phase 5: Notification

Notify the user that the PR is ready for THEIR review and approval.

### Step 5.1: macOS Desktop Notification

```bash
osascript -e 'display notification "PR #<PR_NUMBER> ready for YOUR review: <PR_URL>" with title "Build & Ship Complete" sound name "Glass"'
```

### Step 5.2: SMS Notification

```bash
uv run $HOME/.claude/hooks/utils/sms/twilio_sms.py --to "$NOTIFICATION_PHONE" --message "PR #<PR_NUMBER> ready for YOUR review: <PR_URL>"
```

Read `NOTIFICATION_PHONE` from the plan's `Build-and-Ship Configuration` → `Notification Phone`. If it references `$NOTIFICATION_PHONE`, read from environment.

### Step 5.3: IMPORTANT

Do NOT approve or merge the PR. The notification tells the human to review and approve it themselves.

### Step 5.4: Final Report

Present this report to the conversation:

```
## Build & Ship Complete

**PR**: #[number] — [title]
**Branch**: [branch] → [base]
**URL**: [url]

### Implementation Summary
- [N] tasks completed
- [N] files changed ([+added] / [-removed])

### Review Summary
- Local pre-flight: PASS (round [N])
- GitHub reviews: [N] comments addressed across [N] rounds
- Remaining issues: [none | list]

### Status: AWAITING_HUMAN_APPROVAL | NEEDS_HUMAN_REVIEW
(PR is never auto-merged — human must approve and merge on GitHub)
```

Use `AWAITING_HUMAN_APPROVAL` when all reviews are addressed and CI passes.
Use `NEEDS_HUMAN_REVIEW` when there are remaining questions or unresolved comments.
