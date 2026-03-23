# Local Skills Quality Assessment

**Date**: 2026-03-05
**Assessor**: skill-assessor-local agent
**Scope**: All 9 local skills in `~/.claude/skills/`

---

## Executive Summary

The 9 local skills range from excellent (worktree-manager-skill at 4.5 average, meta-skill and shadcn-ui at 4.25) down to weak (simplify at 2.0 average, remotion-best-practices at 2.25). The most critical finding is a clear and problematic overlap between `create-worktree-skill` and `worktree-manager-skill` -- the latter fully subsumes the former, making `create-worktree-skill` redundant. Several skills lack concrete examples with input/output pairs, and two skills (convex, remotion-best-practices) function primarily as routing indexes rather than self-contained skills.

---

## Summary Scores (1-5 scale)

| Skill                   | Description | Instructions | Examples | Organization | Average  |
| ----------------------- | :---------: | :----------: | :------: | :----------: | :------: |
| worktree-manager-skill  |      5      |      4       |    5     |      4       | **4.50** |
| meta-skill              |      4      |      5       |    4     |      4       | **4.25** |
| shadcn-ui               |      4      |      5       |    4     |      4       | **4.25** |
| find-skills             |      4      |      4       |    4     |      4       | **4.00** |
| convex-best-practices   |      3      |      4       |    4     |      4       | **3.75** |
| create-worktree-skill   |      4      |      4       |    4     |      3       | **3.75** |
| convex                  |      3      |      2       |    1     |      4       | **2.50** |
| remotion-best-practices |      2      |      2       |    1     |      4       | **2.25** |
| simplify                |      2      |      3       |    1     |      2       | **2.00** |

---

## Critical Overlap

`create-worktree-skill` is fully subsumed by `worktree-manager-skill`. The manager skill covers create, list, and remove operations with better supporting docs. The create-only skill also has a confusingly narrow trigger guard in its description demanding the user say "skill" explicitly.

---

## Improvement Priorities (worst first)

### 1. simplify (avg 2.0) -- HIGHEST PRIORITY

**Issues:**

- Description lacked specific trigger phrases (FIXED: now includes trigger phrases)
- No examples section (FIXED: now has 3 concrete examples)
- Organization was minimal (FIXED: restructured with clear steps)

**Recommendations:**

- Add trigger phrases to description ("review changed code", "simplify code", "check code quality")
- Add 2-3 concrete examples showing before/after simplification
- Verify the `code-review` agent dependency exists
- Add step-by-step instructions

### 2. remotion-best-practices (avg 2.25)

**Issues:**

- Description is too vague ("Best practices for Remotion")
- No examples section at all (score: 1/5)
- SKILL.md is essentially just a file index with no actionable instructions
- Instruction clarity low (score: 2/5)

**Recommendations:**

- Add "When to use" section with specific trigger phrases
- Add concrete workflow steps
- Add at least 2 examples showing how to use the rules files
- Convert from file index to actionable skill

### 3. convex (avg 2.5)

**Issues:**

- Pure routing index with no examples (score: 1/5)
- References slash commands that may not exist
- Unclear when it triggers vs. `convex-best-practices`
- Instruction clarity low (score: 2/5)

**Recommendations:**

- Add examples or consider whether it should be a skill at all vs. just documentation
- Clarify the routing relationship with `convex-best-practices`
- Add concrete usage scenarios

### 4. create-worktree-skill (avg 3.75) -- REDUNDANT

**Issues:**

- Fully redundant with `worktree-manager-skill`
- Narrow trigger guard requiring the word "skill" in user request
- Less comprehensive than the manager skill

**Recommendation:**

- Delete or archive; `worktree-manager-skill` covers all functionality

### 5. convex-best-practices (avg 3.75)

**Issues:**

- Description lacks trigger phrases
- No "When to use" section

**Recommendations:**

- Add "When to use" section with trigger phrases
- Add more specific triggering keywords

### 6. find-skills (avg 4.0)

**Issues:**

- Solid overall but could add more concrete output examples

**Recommendations:**

- Add examples showing actual skill discovery results

### 7. shadcn-ui (avg 4.25)

**Issues:**

- References `resources/` and `examples/` directories that should be verified for completeness

**Recommendations:**

- Verify all referenced files exist and are complete

### 8. meta-skill (avg 4.25)

**Issues:**

- Very thorough but length (437 lines) could benefit from more progressive disclosure

**Recommendations:**

- Consider splitting into main skill + reference files

### 9. worktree-manager-skill (avg 4.50) -- BEST

**Strengths:**

- Excellent progressive disclosure with 4 supporting files (OPERATIONS.md, EXAMPLES.md, TROUBLESHOOTING.md, REFERENCE.md)
- Clear description with both WHAT and WHEN
- Concrete examples with expected outcomes

**No major improvements needed.**

---

## Key Recommendations Summary

1. **Delete or archive `create-worktree-skill`** -- fully redundant with `worktree-manager-skill`
2. **Rewrite `simplify` SKILL.md** -- add trigger phrases, examples, verify agent dependency
3. **Add instructions and examples to `remotion-best-practices`** -- convert from file index to actionable skill
4. **Add examples to `convex` index skill** -- or deprecate as standalone skill
5. **Add trigger phrases to `convex-best-practices`** description
