# Code Review & Simplify Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a globally-available agent that combines code review and simplification into a single pre-validation step in the development workflow, replacing the need to invoke separate review and simplify passes.

**Architecture:** A new agent (`code-review-simplify`) that reads changed code via git diff, performs confidence-scored code review (bugs, quality, patterns), then applies safe simplifications. It slots into the workflow between builder completion and the validate stage. An accompanying skill (`simplify`) is updated to orchestrate invoking this agent automatically.

**Tech Stack:** Markdown agent definition, Python hook validator (optional), existing git/grep/read tooling.

---

## Context & Design Decisions

### Current Workflow Gap

Today the development pipeline is:

```
builder → (manual review) → validator → coverage-checker
```

There is no automated step that reviews code quality AND simplifies before validation. The `code-simplifier` agent from pr-review-toolkit exists but is plugin-scoped and separate from the `code-reviewer` agent. The local `simplify` skill exists but is a simple prompt without structured review.

### Proposed Workflow

```
builder → code-review-simplify agent → validator → coverage-checker
```

The new agent:
1. **Reviews** changed code with confidence-scored findings (only reports issues ≥80 confidence)
2. **Simplifies** code that passes review (or after issues are addressed)
3. Operates on **git diff scope** — only touches recently changed files
4. Is **globally available** as both an agent (for team/subagent dispatch) and through the existing `simplify` skill (for interactive use)

### Key Design Choices

- **Combined agent** rather than chaining two agents — reduces context window waste and latency
- **Confidence scoring** from superpowers code-reviewer pattern — avoids noise
- **Git-diff scoped** — doesn't review the entire codebase, only changes
- **Can write** — unlike pure validators, this agent applies simplifications directly
- **PostToolUse hooks** for linting — catches any regressions from simplification edits

---

## Task 1: Create the Agent Definition

**Files:**
- Create: `agents/code-review-simplify.md`

**Step 1: Write the agent definition file**

```markdown
---
name: code-review-simplify
description: |
  Use this agent after code has been written or modified and before validation.
  Combines code review (bug detection, quality analysis, pattern adherence) with
  code simplification (clarity, consistency, maintainability). Operates on git
  diff scope — only reviews and simplifies recently changed files. Automatically
  triggered by the simplify skill or manually dispatched as a pre-validation step.
model: sonnet
color: purple
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/ruff_validator.py
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/oxlint_validator.py
---

# Code Review & Simplify Agent

## Purpose

You are a combined code reviewer and simplification specialist. You operate as a
pre-validation gate in the development workflow. Your job is to catch issues AND
improve code quality before the validate stage runs.

## Workflow

### Phase 1: Scope Discovery

1. Run `git diff --name-only HEAD~1` (or `git diff --name-only` for unstaged changes)
   to identify recently changed files
2. If invoked with specific file paths, use those instead
3. Filter to only code files (skip configs, lockfiles, generated files)

### Phase 2: Code Review

For each changed file:

1. Read the full file content
2. Read the diff hunks to understand what changed
3. Review changes against these criteria:
   - **Bugs & Logic Errors**: Off-by-one, null derefs, race conditions, missing error handling
   - **Security**: Injection, XSS, secrets in code, unsafe deserialization
   - **Performance**: Unnecessary allocations, N+1 queries, missing memoization
   - **Project Patterns**: Adherence to CLAUDE.md standards and existing codebase conventions
   - **Code Quality**: Dead code, unused imports, overly complex logic

4. Score each finding 0-100 confidence
5. **Only report findings with confidence ≥ 80**

### Phase 3: Simplification

After review (and only if no Critical issues block it):

1. Apply simplifications to the changed code:
   - Reduce unnecessary complexity and nesting
   - Eliminate redundant code and abstractions
   - Improve variable and function naming for clarity
   - Consolidate related logic
   - Remove unnecessary comments describing obvious code
   - Avoid nested ternaries — prefer switch/if-else
   - Choose clarity over brevity

2. **Preserve all functionality** — never change what code does, only how it does it
3. **Stay scoped** — only touch files identified in Phase 1

### Phase 4: Report

Output a structured report:

```
## Code Review & Simplify Report

### Review Findings

**Critical** (must fix before proceeding):
- [ ] `file:line` — [description] (confidence: XX)

**Important** (should fix):
- [ ] `file:line` — [description] (confidence: XX)

**Suggestions** (nice to have):
- [ ] `file:line` — [description] (confidence: XX)

### Simplifications Applied

- `file:line-range` — [what was simplified and why]

### Files Reviewed
- [file1] — N findings, M simplifications
- [file2] — N findings, M simplifications

### Status: PASS | NEEDS_FIXES
```

## Rules

- If Critical findings exist, report them but do NOT apply simplifications — the code
  needs fixes first. Set status to NEEDS_FIXES.
- If only Important/Suggestions exist, apply simplifications and set status to PASS.
- Never add features, refactor architecture, or expand scope.
- Never add comments, docstrings, or type annotations to code you didn't change.
- Respect existing abstractions — don't collapse them unless clearly redundant.
- Run lint/format checks are handled by PostToolUse hooks automatically.
```

**Step 2: Verify the file was created correctly**

Run: `cat agents/code-review-simplify.md | head -5`
Expected: Shows the YAML frontmatter starting with `---`

**Step 3: Commit**

```bash
git add agents/code-review-simplify.md
git commit -m "feat: add code-review-simplify agent"
```

---

## Task 2: Update the Simplify Skill to Orchestrate the Agent

**Files:**
- Modify: `~/.agents/skills/simplify/SKILL.md`

The existing simplify skill is a standalone prompt. Update it to invoke the new agent and serve as the user-facing entry point.

**Step 1: Read the current skill**

Run: `cat ~/.agents/skills/simplify/SKILL.md`

**Step 2: Update the skill to orchestrate the agent**

Replace the full content of `~/.agents/skills/simplify/SKILL.md` with:

```markdown
---
name: simplify
description: Review changed code for reuse, quality, and efficiency, then fix any issues found.
---

# Simplify

Review and simplify recently modified code. Combines code review with simplification.

## Instructions

When this skill is invoked:

1. **Determine scope** — Check git status for changed files:
   - Unstaged changes: `git diff --name-only`
   - Staged changes: `git diff --cached --name-only`
   - Last commit: `git diff --name-only HEAD~1`
   - Use whichever has changes (prefer unstaged > staged > last commit)

2. **Dispatch the agent** — Launch the `code-review-simplify` agent with:
   - The list of changed files
   - Any specific focus area the user mentioned
   - Instructions to review AND simplify

3. **Report results** — Surface the agent's report to the user:
   - If NEEDS_FIXES: highlight critical issues that need manual attention
   - If PASS: summarize simplifications applied

4. **Verify** — After simplifications, run:
   - `pnpm lint` (or project-appropriate lint command)
   - `pnpm test` (if tests exist)
   - Confirm no regressions

## Usage

- `/simplify` — Review and simplify all recent changes
- `/simplify src/auth/` — Focus on specific directory
- `/simplify --review-only` — Skip simplification, just review
```

**Step 3: Verify the update**

Run: `cat ~/.agents/skills/simplify/SKILL.md | head -5`
Expected: Updated frontmatter with new description

**Step 4: Commit**

```bash
git add ~/.agents/skills/simplify/SKILL.md
git commit -m "feat: update simplify skill to orchestrate code-review-simplify agent"
```

---

## Task 3: Wire Into Development Workflow Documentation

**Files:**
- Modify: `CLAUDE.md` (in the project root, if workflow documentation exists there)

**Step 1: Read current CLAUDE.md**

Run: `cat ~/CLAUDE.md`

**Step 2: Add the pre-validation step to task completion checklist**

Add a new checklist item in the "Task Completion" section, inserted before the lint/test checks:

```markdown
## Task Completion

- [ ] After code is complete, run `/simplify` to review and simplify changed code.
- [ ] After code is complete, please run lint and format checks to ensure code quality. (examples: `pnpm lint`, `pnpm format`)
- [ ] Before completing a task, you must run all tests from root of the project w/ a coverage check. (examples: `pnpm test:coverage`, `pnpm test`)
```

**Step 3: Verify the change**

Run: `grep -A 5 "Task Completion" ~/CLAUDE.md`
Expected: Shows the new `/simplify` checklist item first

**Step 4: Commit**

```bash
git add ~/CLAUDE.md
git commit -m "docs: add simplify step to task completion checklist"
```

---

## Task 4: Test the Agent End-to-End

**Step 1: Create a test file with intentional issues**

Create a temporary test file with common issues the agent should catch:

```typescript
// /tmp/test-review.ts
const unusedVar = "hello";

export const processData = (data: any) => {
  if (data) {
    if (data.items) {
      if (data.items.length > 0) {
        const result = data.items.map((item: any) => {
          // transform the item
          return { ...item, processed: true };
        });
        return result;
      } else {
        return [];
      }
    } else {
      return [];
    }
  } else {
    return [];
  }
};
```

**Step 2: Stage the file and invoke the agent**

```bash
git add /tmp/test-review.ts
```

Then invoke the simplify skill or directly dispatch the agent to review it.

**Step 3: Verify expected findings**

Expected review findings:
- `any` type usage (confidence ≥80)
- Excessive nesting (confidence ≥80)
- Unused variable (confidence ≥80)

Expected simplifications:
- Early returns to flatten nesting
- Remove unused variable

**Step 4: Clean up test file**

```bash
rm /tmp/test-review.ts
```

---

## Task 5: Verify Integration with Team Workflow

**Step 1: Verify agent is discoverable**

Run: `ls agents/code-review-simplify.md`
Expected: File exists

**Step 2: Verify skill symlink works**

Run: `ls -la skills/simplify`
Expected: Symlink to `../../.agents/skills/simplify`

**Step 3: Verify the agent appears in agent listing**

Launch a new Claude Code session and check that `code-review-simplify` appears as an available subagent type.

**Step 4: Commit any remaining changes**

```bash
git add -A
git commit -m "test: verify code-review-simplify agent integration"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Create agent definition | `agents/code-review-simplify.md` |
| 2 | Update simplify skill | `~/.agents/skills/simplify/SKILL.md` |
| 3 | Wire into CLAUDE.md workflow | `~/CLAUDE.md` |
| 4 | End-to-end testing | Temp test file |
| 5 | Integration verification | Existing files |
