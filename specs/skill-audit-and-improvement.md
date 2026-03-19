# Plan: Skill Audit, Improvement & Performance Measurement

## Task Description

Conduct a comprehensive audit of all skills available in the `~/.claude/` configuration directory. Catalog every skill by source, read and assess each, then use the `/skill-creator` skill's improvement and evaluation workflow to improve existing skills and measure their performance with quantitative benchmarks.

## Objective

When complete, we will have:

1. A full inventory of every skill in the configuration, organized by source
2. Quality assessments and improvement recommendations for each skill
3. Measurable performance baselines (triggering accuracy, output quality) for priority skills
4. Improved versions of underperforming skills with before/after benchmarks

## Problem Statement

With 100+ skills installed across 4 plugin marketplaces and 3 local skill directories, there is no visibility into:

- Which skills are high-quality vs. poorly written
- Whether skill descriptions trigger accurately (precision and recall)
- Which skills overlap or conflict with each other
- Whether local custom skills follow best practices

## Solution Approach

Use a phased approach: first catalog all skills (automated scan), then assess quality (human + agent review), then use the `skill-creator` skill's eval/benchmark infrastructure to run performance tests on priority skills. Improve underperformers using the skill-creator's iterative improvement loop.

## Relevant Files

Use these files to complete the task:

**Local Skills (user-authored, highest priority for improvement):**

- `~/.claude/skills/create-worktree-skill/SKILL.md` — Worktree creation skill, delegates to slash command
- `~/.claude/skills/meta-skill/SKILL.md` — Skill creation helper, includes docs/ references
- `~/.claude/skills/worktree-manager-skill/SKILL.md` — Comprehensive worktree lifecycle manager with 4 reference files

**Marketplace Skills (claude-skills — ~90 skills):**

- `~/.claude/plugins/marketplaces/claude-skills/skills/*/SKILL.md` — Large collection of domain-specific skills

**Marketplace Skills (claude-code-plugins — 10 skills):**

- `~/.claude/plugins/marketplaces/claude-code-plugins/plugins/*/skills/*/SKILL.md` — Plugin development, frontend-design, migrations

**Marketplace Skills (claude-plugins-official — 15 skills):**

- `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/*/skills/*/SKILL.md` — Official Anthropic plugin skills
- `~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/*/skills/*/SKILL.md` — Third-party official skills

**Marketplace Skills (mcp-use — 3 skills):**

- `~/.claude/plugins/marketplaces/mcp-use/skills/*/SKILL.md` — MCP builder and app builder skills

**Skill Creator (evaluation infrastructure):**

- `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md` — Main skill-creator skill
- Eval viewer, grader agents, benchmark scripts referenced within

### New Files

- `specs/skill-inventory.md` — Complete skill inventory with metadata
- `specs/skill-assessment-report.md` — Quality assessment results
- `<skill-name>-workspace/` directories — Per-skill eval results (created by skill-creator workflow)

## Implementation Phases

### Phase 1: Discovery & Inventory

Scan all skill directories, extract YAML frontmatter (name, description), catalog by source, identify duplicates and overlaps.

### Phase 2: Quality Assessment

Read each skill's SKILL.md body. Assess against best practices: description quality (triggering effectiveness), instruction clarity, progressive disclosure usage, example coverage, reference file organization.

### Phase 3: Performance Measurement & Improvement

For priority skills (local skills first, then underperformers), use the `/skill-creator` workflow to:

- Generate trigger eval queries
- Run description optimization
- Create test cases and run eval benchmarks
- Iterate on improvements

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to do the building, validating, testing, deploying, and other tasks.

### Team Members

- Builder
  - Name: skill-scanner
  - Role: Scan all skill directories, extract frontmatter, and produce the skill inventory document
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: skill-assessor-local
  - Role: Deep-read all 3 local skills and assess quality against best practices, produce assessment with improvement recommendations
  - Agent Type: scout-report-suggest
  - Resume: true

- Builder
  - Name: skill-assessor-marketplace
  - Role: Scan marketplace skills (description + first 50 lines of each), identify top 10 highest-quality and top 10 needing improvement
  - Agent Type: scout-report-suggest
  - Resume: true

- Builder
  - Name: skill-improver
  - Role: Use /skill-creator workflow to improve one skill at a time — generate evals, run benchmarks, iterate
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: eval-runner
  - Role: Execute skill-creator eval runs (with-skill and baseline) for each skill being tested
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: description-optimizer
  - Role: Run the skill-creator description optimization loop (run_loop.py) for skills with poor triggering
  - Agent Type: builder
  - Resume: true

- Validator
  - Name: skill-validator
  - Role: Validate improved skills meet quality criteria and benchmarks show improvement
  - Agent Type: validator
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Scan All Skill Directories and Build Inventory

- **Task ID**: scan-skills
- **Depends On**: none
- **Assigned To**: skill-scanner
- **Agent Type**: builder
- **Parallel**: false
- Scan these 5 skill source directories:
  - `~/.claude/skills/` (local)
  - `~/.claude/plugins/marketplaces/claude-skills/skills/`
  - `~/.claude/plugins/marketplaces/claude-code-plugins/plugins/*/skills/*/`
  - `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/*/skills/*/` and `external_plugins/*/skills/*/`
  - `~/.claude/plugins/marketplaces/mcp-use/skills/`
- For each skill, extract: name, description, source, path, line count, has-examples (y/n), has-references (y/n), allowed-tools
- Identify duplicate skill names across sources
- Save inventory to `specs/skill-inventory.md` as a categorized table

### 2. Assess Local Skills Quality

- **Task ID**: assess-local
- **Depends On**: scan-skills
- **Assigned To**: skill-assessor-local
- **Agent Type**: scout-report-suggest
- **Parallel**: true (can run parallel with assess-marketplace)
- Deep read all 3 local skills: create-worktree-skill, meta-skill, worktree-manager-skill
- Assess each against these criteria:
  - Description: Does it include both WHAT and WHEN? Is it specific enough for triggering?
  - Instructions: Clear numbered steps? Actionable language?
  - Examples: Are there 2+ concrete examples?
  - Progressive disclosure: Is content split appropriately?
  - Overlap: Does it conflict with other skills?
- Score each skill 1-5 on: Description Quality, Instruction Clarity, Example Coverage, Organization
- Produce ranked list of improvement priorities
- Save to `specs/skill-assessment-local.md`

### 3. Assess Marketplace Skills Quality

- **Task ID**: assess-marketplace
- **Depends On**: scan-skills
- **Assigned To**: skill-assessor-marketplace
- **Agent Type**: scout-report-suggest
- **Parallel**: true (can run parallel with assess-local)
- Sample all marketplace skills (read description + first section of each SKILL.md)
- Identify the top 10 highest-quality skills (to use as exemplars)
- Identify the top 10 lowest-quality skills (candidates for improvement)
- Flag any skills that overlap with local skills
- Save to `specs/skill-assessment-marketplace.md`

### 4. Prioritize Skills for Improvement

- **Task ID**: prioritize
- **Depends On**: assess-local, assess-marketplace
- **Assigned To**: Team Lead (you)
- **Agent Type**: N/A (orchestrator decision)
- **Parallel**: false
- Review both assessment reports
- Select 3-5 skills to improve, prioritizing:
  1. Local skills (user-authored, most impactful)
  2. Skills with poor descriptions (triggering failures)
  3. Skills with missing examples or unclear instructions
- Present prioritized list to user for approval before proceeding

### 5. Improve Priority Skill #1 (using /skill-creator workflow)

- **Task ID**: improve-skill-1
- **Depends On**: prioritize
- **Assigned To**: skill-improver
- **Agent Type**: builder
- **Parallel**: false
- Invoke the `/skill-creator` skill in "improve existing skill" mode
- Follow the skill-creator workflow:
  1. Write 2-3 realistic test prompts
  2. Save to `<skill-name>-workspace/evals/evals.json`
  3. Spawn with-skill and baseline runs
  4. Draft assertions while runs execute
  5. Grade results, aggregate benchmark, launch eval viewer
  6. Collect user feedback
  7. Improve skill based on feedback
  8. Repeat until satisfied

### 6. Run Description Optimization for Priority Skill #1

- **Task ID**: optimize-desc-1
- **Depends On**: improve-skill-1
- **Assigned To**: description-optimizer
- **Agent Type**: builder
- **Parallel**: false
- Generate 20 trigger eval queries (10 should-trigger, 10 should-not-trigger)
- Present to user for review via HTML template
- Run `scripts.run_loop` with `--max-iterations 5`
- Apply best_description to SKILL.md
- Report before/after trigger accuracy scores

### 7. Improve Priority Skills #2-N (repeat pattern)

- **Task ID**: improve-remaining
- **Depends On**: optimize-desc-1
- **Assigned To**: skill-improver (resumed)
- **Agent Type**: builder
- **Parallel**: false
- Repeat steps 5-6 for each remaining priority skill
- Each gets its own workspace directory
- Track cumulative improvement metrics

### 8. Review & Simplify

- **Task ID**: review-simplify
- **Depends On**: improve-remaining
- **Assigned To**: Team Lead (you)
- **Agent Type**: code-review
- **Parallel**: false
- Get the list of changed files with `git diff --name-only`
- Dispatch the `code-review` agent with the changed file list
- If NEEDS_FIXES: apply fixes before proceeding to validation
- If PASS: proceed to final validation

### 9. Final Validation & Summary Report

- **Task ID**: validate-all
- **Depends On**: review-simplify
- **Assigned To**: skill-validator
- **Agent Type**: validator
- **Parallel**: false
- Verify each improved skill:
  - YAML frontmatter is valid
  - Description includes WHAT + WHEN
  - Instructions have numbered steps
  - Examples section exists with 2+ examples
  - No broken file references
- Compile final report with:
  - Skills improved (before/after descriptions)
  - Benchmark scores (trigger accuracy, output quality)
  - Remaining improvement backlog
- Save to `specs/skill-improvement-report.md`

## Acceptance Criteria

- [ ] Complete inventory of all skills exists in `specs/skill-inventory.md`
- [ ] Quality assessment completed for all local skills and sampled marketplace skills
- [ ] At least 3 skills improved with measurable before/after benchmarks
- [ ] Description optimization run on at least 1 skill with trigger accuracy data
- [ ] All improved skills pass YAML validation and best practices checklist
- [ ] Final summary report saved to `specs/skill-improvement-report.md`

## Validation Commands

Execute these commands to validate the task is complete:

- `ls specs/skill-inventory.md specs/skill-assessment-local.md specs/skill-assessment-marketplace.md specs/skill-improvement-report.md` — Verify all report files exist
- `head -5 ~/.claude/skills/*/SKILL.md` — Verify local skills have valid YAML frontmatter
- `grep -c "description:" ~/.claude/skills/*/SKILL.md` — Verify descriptions exist in all local skills
- `wc -l specs/skill-inventory.md` — Verify inventory is substantive (should be 100+ lines)

## Notes

- The skill-creator's `eval-viewer/generate_review.py` requires Python. Verify Python is available before running.
- The description optimization loop uses `claude -p` via subprocess — requires the Claude CLI to be available.
- Marketplace skills are read-only (installed via git). Improvements to marketplace skills should be documented as recommendations, not applied directly.
- Local skills (~/.claude/skills/) are the primary candidates for direct improvement.
- The `create-worktree-skill` and `worktree-manager-skill` appear to have overlapping functionality — this should be assessed and potentially consolidated.
