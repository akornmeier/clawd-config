# Specialized Claude Code Agents for Stached & Oculis

## Core Pattern: Self-Validating Agents

The true power of this approach is **self-validating agents** - agents that cannot complete work without passing their own quality gates. This creates a closed loop where the agent is responsible for both doing work AND verifying it meets standards.

```
┌─────────────────────────────────────────────────────────────┐
│  SELF-VALIDATING AGENT PATTERN                              │
│                                                             │
│  Agent Definition (.md file)                                │
│  ├── System Prompt: What the agent does                     │
│  ├── PreToolUse Hooks: Gates BEFORE action                  │
│  │   └── TDD enforcer: Can't write impl without test        │
│  ├── PostToolUse Hooks: Validates AFTER action              │
│  │   └── Lint/Type validators: Can't complete with errors   │
│  └── Stop Hooks: Final gate BEFORE completion               │
│      └── Coverage validator: Can't stop without 80%         │
│                                                             │
│  Result: Agent keeps working until ALL gates pass           │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

```
~/.claude/                     # User-level (shared)
├── agents/
│   ├── ts-builder.md          # Self-validating TypeScript builder
│   ├── tdd-builder.md         # TDD-enforced builder (PreToolUse gates)
│   ├── ts-validator.md        # Read-only verification agent
│   ├── turborepo-runner.md    # Monorepo orchestration
│   └── coverage-checker.md    # Coverage validation
├── hooks/
│   └── validators/
│       ├── tdd_enforcer.py        # PreToolUse: blocks impl without test
│       ├── oxlint_validator.py    # PostToolUse: blocks on lint errors
│       ├── tsc_validator.py       # PostToolUse: blocks on type errors
│       ├── coverage_validator.py  # Stop: blocks if coverage < threshold
│       └── session_start_tdd.py   # SessionStart: resets TDD state
└── data/
    └── tdd_session_state.json     # Tracks test modifications per session

~/code/stached/.claude/agents/     # Stached-specific
├── convex-builder.md              # Self-validating Convex specialist
├── article-parser.md              # Content extraction agent
└── extension-builder.md           # WXT browser extension agent

~/code/oculis/.claude/agents/      # Oculis-specific
├── axe-specialist.md              # Self-validating a11y expert
├── adapter-guide.md               # DI/Adapter pattern guidance
└── tdd-builder.md                 # Strict TDD-enforced builder
```

## Implementation Steps

### Phase 1: TDD Enforcement Hook (PreToolUse Gate)

**1.1 Create `~/.claude/hooks/validators/tdd_enforcer.py`**

A PreToolUse hook that blocks implementation file writes until the corresponding test file has been modified in this session.

```python
# Pseudocode
def check_tdd_compliance(file_path):
    if is_test_file(file_path):
        add_to_session_state(file_path)
        return ALLOW

    if is_impl_file(file_path):
        matching_test = find_matching_test(file_path)
        if matching_test in session_state["test_files_modified"]:
            return ALLOW
        else:
            return BLOCK("Write test first: " + matching_test)
```

**Test file matching patterns:**
```
src/foo.ts → src/foo.test.ts, src/foo.spec.ts, __tests__/foo.test.ts
src/components/Bar.tsx → src/components/Bar.test.tsx
```

**1.2 Create `~/.claude/hooks/validators/session_start_tdd.py`**
- SessionStart hook that clears `tdd_session_state.json`
- Ensures each session starts fresh

### Phase 2: Code Quality Validators (PostToolUse Gates)

**2.1 Create `~/.claude/hooks/validators/oxlint_validator.py`**
- Run `pnpm exec oxlint` on .ts/.tsx files after Write/Edit
- Return `{"decision": "block", "reason": "..."}` on lint errors
- Agent cannot proceed until lint passes

**2.2 Create `~/.claude/hooks/validators/tsc_validator.py`**
- Run `npx tsc --noEmit` after Write/Edit
- Block on type errors with extracted messages
- Agent cannot proceed until types pass

### Phase 3: Coverage Validator (Stop Gate)

**3.1 Create `~/.claude/hooks/validators/coverage_validator.py`**
- Stop hook that runs `pnpm test:coverage`
- Parses coverage report for modified files
- Blocks completion if coverage < 80%
- Agent keeps working until coverage threshold met

### Phase 4: Self-Validating Agents

**4.1 Create `~/.claude/agents/tdd-builder.md`**

The flagship self-validating agent:

```yaml
---
name: tdd-builder
description: TDD-enforced TypeScript builder. Cannot write implementation code without test. Cannot complete with lint/type errors. Cannot stop without 80% coverage.
model: opus
color: cyan
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit"
      hooks:
        - type: command
          command: uv run ~/.claude/hooks/validators/tdd_enforcer.py
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: uv run ~/.claude/hooks/validators/oxlint_validator.py
        - type: command
          command: uv run ~/.claude/hooks/validators/tsc_validator.py
  Stop:
    - hooks:
        - type: command
          command: uv run ~/.claude/hooks/validators/coverage_validator.py
---

# TDD Builder

You are a disciplined engineering agent that follows strict TDD workflow.

## Workflow

1. **Write failing test first** - You CANNOT write implementation until test exists
2. **Implement minimal code** - Make the test pass
3. **Verify quality** - Lint and type errors block you automatically
4. **Check coverage** - You cannot complete until 80% coverage met

## If Blocked

- PreToolUse blocks → Write the test file first
- PostToolUse blocks → Fix the lint/type errors
- Stop blocks → Add more tests to reach coverage threshold
```

**4.2 Create `~/.claude/agents/ts-builder.md`**

Standard builder without TDD enforcement (for non-TDD work):

```yaml
---
name: ts-builder
description: TypeScript builder with quality validation. Use for general implementation work without strict TDD requirements.
model: opus
color: blue
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: uv run ~/.claude/hooks/validators/oxlint_validator.py
        - type: command
          command: uv run ~/.claude/hooks/validators/tsc_validator.py
---
```

**4.3 Create `~/.claude/agents/ts-validator.md`**

Read-only verification agent:

```yaml
---
name: ts-validator
description: Validates code quality, tests, and coverage without modifications. Use after builder to verify work.
model: sonnet
color: yellow
disallowedTools: Write, Edit, MultiEdit, NotebookEdit
---
```

**4.4 Create `~/.claude/agents/turborepo-runner.md`**

Monorepo operations:

```yaml
---
name: turborepo-runner
description: Orchestrates Turborepo commands. Use for building, testing, or linting across monorepo packages.
model: sonnet
color: green
tools: Bash, Read, Glob
---
```

**4.5 Create `~/.claude/agents/coverage-checker.md`**

Lightweight coverage validation:

```yaml
---
name: coverage-checker
description: Validates test coverage meets threshold. Use to check coverage after tests pass.
model: haiku
color: purple
disallowedTools: Write, Edit
---
```

### Phase 5: Stached-Specific Self-Validating Agents

**5.1 Create `~/code/stached/.claude/agents/convex-builder.md`**

```yaml
---
name: convex-builder
description: Self-validating Convex backend specialist. Validates Convex schemas and functions on every write.
model: opus
color: cyan
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: pnpm --filter @stache/convex type-check
        - type: command
          command: pnpm exec oxlint
---

# Convex Builder

Domain expertise:
- Convex functions (query, mutation, action)
- Schema design with validators
- Clerk auth integration
- File storage patterns
```

**5.2 Create `~/code/stached/.claude/agents/article-parser.md`**
- Domain knowledge: Mozilla Readability, HTML sanitization, metadata extraction

**5.3 Create `~/code/stached/.claude/agents/extension-builder.md`**
- Domain knowledge: WXT framework, Manifest V3, content scripts, browser APIs

### Phase 6: Oculis-Specific Self-Validating Agents

**6.1 Create `~/code/oculis/.claude/agents/axe-specialist.md`**

```yaml
---
name: axe-specialist
description: Self-validating accessibility testing expert. Validates WCAG compliance on every write.
model: opus
color: purple
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: pnpm exec oxlint
        - type: command
          command: turbo run lint
---

# Accessibility Specialist

Domain expertise:
- WCAG 2.1 AA/AAA compliance
- axe-core rule configuration
- Custom accessibility rules
- Fingerprinting DOM elements
- ARIA patterns and anti-patterns
```

**6.2 Create `~/code/oculis/.claude/agents/adapter-guide.md`**
- Read-only architectural guidance for DI/Adapter patterns
- Reference existing adapters in packages/core/src/adapters/

**6.3 Create `~/code/oculis/.claude/agents/tdd-builder.md`**
- Copy of shared tdd-builder with oculis-specific validations

### Phase 7: Update Project Settings

**7.1 Stached `settings.local.json`**
Add hooks section while preserving existing permissions.

**7.2 Oculis `settings.json`**
Replace tdd-guard with new tdd_enforcer.py hook.

## Files to Create

| File | Lines | Purpose |
|------|-------|---------|
| **TDD Enforcement** |||
| `~/.claude/hooks/validators/tdd_enforcer.py` | ~120 | PreToolUse: blocks impl without test |
| `~/.claude/hooks/validators/session_start_tdd.py` | ~30 | SessionStart: resets TDD state |
| `~/.claude/hooks/validators/coverage_validator.py` | ~80 | Stop: blocks if coverage < 80% |
| **Code Quality Validators** |||
| `~/.claude/hooks/validators/oxlint_validator.py` | ~80 | PostToolUse: OXLint check |
| `~/.claude/hooks/validators/tsc_validator.py` | ~75 | PostToolUse: TypeScript check |
| **Shared Self-Validating Agents** |||
| `~/.claude/agents/tdd-builder.md` | ~70 | Flagship: TDD + lint + type + coverage gates |
| `~/.claude/agents/ts-builder.md` | ~50 | Standard: lint + type gates |
| `~/.claude/agents/ts-validator.md` | ~40 | Read-only verification |
| `~/.claude/agents/turborepo-runner.md` | ~35 | Monorepo commands |
| `~/.claude/agents/coverage-checker.md` | ~30 | Coverage validation |
| **Stached Self-Validating Agents** |||
| `~/code/stached/.claude/agents/convex-builder.md` | ~60 | Convex specialist with type-check gate |
| `~/code/stached/.claude/agents/article-parser.md` | ~40 | Content extraction |
| `~/code/stached/.claude/agents/extension-builder.md` | ~50 | WXT extension |
| **Oculis Self-Validating Agents** |||
| `~/code/oculis/.claude/agents/axe-specialist.md` | ~60 | A11y expert with lint gate |
| `~/code/oculis/.claude/agents/adapter-guide.md` | ~45 | Architecture guidance |
| `~/code/oculis/.claude/agents/tdd-builder.md` | ~70 | Strict TDD enforcement |

**Total: 16 files, ~935 lines**

## Self-Validation Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. SessionStart Hook                                        │
│     └─> session_start_tdd.py clears state                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Agent receives task                                      │
│     └─> "Implement feature X with tests"                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Agent tries to write implementation                      │
│     └─> PreToolUse: tdd_enforcer.py BLOCKS                  │
│     └─> "Write test first: src/X.test.ts"                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Agent writes test file                                   │
│     └─> PreToolUse: tdd_enforcer.py ALLOWS (it's a test)    │
│     └─> PostToolUse: oxlint/tsc run                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Agent writes implementation                              │
│     └─> PreToolUse: tdd_enforcer.py ALLOWS (test exists)    │
│     └─> PostToolUse: oxlint BLOCKS (lint error)             │
│     └─> Agent fixes lint error                              │
│     └─> PostToolUse: tsc BLOCKS (type error)                │
│     └─> Agent fixes type error                              │
│     └─> PostToolUse: ALL PASS                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Agent tries to complete                                  │
│     └─> Stop: coverage_validator.py BLOCKS (72% coverage)   │
│     └─> Agent adds more tests                               │
│     └─> Stop: coverage_validator.py ALLOWS (82% coverage)   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  7. Task complete                                            │
│     └─> All gates passed                                    │
│     └─> TDD workflow enforced                               │
│     └─> Code quality guaranteed                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Self-validating agents** - Agents cannot complete without passing ALL gates
2. **Three gate types**: PreToolUse (before), PostToolUse (after), Stop (completion)
3. **Closed loop** - Agent keeps working until all validations pass
4. **Session state for TDD** - Tracks test modifications within session
5. **User-level shared** - Core agents/hooks work across all projects
6. **Project-specific specialization** - Domain experts extend base patterns
7. **UV scripts** - Portable, no virtual env needed

## Verification

1. **Test TDD blocking**: Write `src/foo.ts` without test → BLOCKED
2. **Test TDD allowing**: Write `src/foo.test.ts` then `src/foo.ts` → ALLOWED
3. **Test lint blocking**: Write code with lint errors → BLOCKED until fixed
4. **Test type blocking**: Write code with type errors → BLOCKED until fixed
5. **Test coverage blocking**: Try to complete with 60% coverage → BLOCKED
6. **Test full workflow**: Complete feature with TDD → all gates pass
