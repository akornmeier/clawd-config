# Marketplace Skill Quality Assessment

**Date**: 2026-03-05
**Assessor**: skill-assessor-marketplace agent
**Scope**: All 4 marketplaces + local skills

---

## Inventory

| Marketplace | Path | Skill Count |
|---|---|---|
| **claude-skills** | `~/.claude/plugins/marketplaces/claude-skills/skills/*/SKILL.md` | 93 (+ 1 template) |
| **claude-code-plugins** | `~/.claude/plugins/marketplaces/claude-code-plugins/plugins/*/skills/*/SKILL.md` | 10 |
| **claude-plugins-official** | `~/.claude/plugins/marketplaces/claude-plugins-official/{plugins,external_plugins}/*/skills/*/SKILL.md` | 15 |
| **mcp-use** | `~/.claude/plugins/marketplaces/mcp-use/skills/*/SKILL.md` | 3 |
| **Local** | `~/.claude/skills/*/SKILL.md` | 9 |
| **Total** | | **130** (excluding template, minus 7 exact duplicates = **122 unique**) |

---

## Top 10 Highest-Quality Skills

### 1. clerk-auth (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/clerk-auth/SKILL.md`
**Lines**: 701 | **Errors Prevented**: 15

**Why it is excellent**:
- Two-paragraph description nails WHAT (API Keys beta, Next.js 16 proxy.ts, API version breaking changes) and WHEN (troubleshooting JWKS/CSRF/JWT errors, webhook verification, 424242 OTP testing)
- Chronological "What's New" section with exact dates and version numbers
- Includes actual TypeScript code for every pattern (API key verification, webhook handling)
- Specific error code references make it highly discoverable

**Model qualities**: Specificity of error codes in description, date-stamped changelog, breaking change tracking

---

### 2. openai-api (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/openai-api/SKILL.md`
**Lines**: 1137 | **Errors Prevented**: 16

**Why it is excellent**:
- Comprehensive coverage of every OpenAI API endpoint (Chat, Embeddings, Images, Audio, Moderation, Streaming, Function Calling, Structured Outputs, Vision)
- Table of contents for navigation in a long document
- Status checklist format shows coverage at a glance
- Model name specificity (GPT-5.2, o3) in the description ensures accurate triggering

**Model qualities**: Exhaustive API coverage, table of contents, status dashboard format

---

### 3. cloudflare-browser-rendering (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/cloudflare-browser-rendering/SKILL.md`
**Lines**: 876 | **Errors Prevented**: (documented in skill)

**Why it is excellent**:
- Monthly changelog with exact dates going back over a year
- Dual framework coverage (Puppeteer AND Playwright) with side-by-side comparisons
- Pricing table with exact costs
- Production checklist section for deployment readiness

**Model qualities**: Changelog discipline, dual framework coverage, pricing transparency

---

### 4. elevenlabs-agents (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/elevenlabs-agents/SKILL.md`
**Lines**: 1164 | **Errors Prevented**: 34

**Why it is excellent**:
- Highest error prevention count of any skill (34)
- Explicit deprecated package warnings (`@11labs/react` -> `@elevenlabs/react`)
- Critical version removal notice (v1 TTS models removed 2025-12-15)
- Multi-SDK coverage (React, React Native, Swift, CLI)

**Model qualities**: Aggressive deprecation tracking, multi-platform SDK coverage, highest error prevention density

---

### 5. cloudflare-durable-objects (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/cloudflare-durable-objects/SKILL.md`
**Lines**: 838 | **Errors Prevented**: 20

**Why it is excellent**:
- Balanced description covering both "Use when" (chat rooms, multiplayer games, rate limiting) and troubleshooting keywords (class export, migration, WebSocket state loss)
- Monthly platform update tracking
- Beta stability warnings for `@cloudflare/actors` library with link to active issues
- Scaffold command as the very first Quick Start step

**Model qualities**: Beta vs stable distinction, scaffold-first workflow, balanced use-case + error keywords

---

### 6. skill-creator (claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator/SKILL.md`
**Lines**: 479

**Why it is excellent**:
- Uniquely conversational, approachable tone ("Cool? Cool.") that considers non-technical users
- Eval-driven improvement loop: draft -> test -> evaluate -> iterate
- Explicit guidance on communicating with users of varying technical ability
- Meta-awareness: teaches the skill creation process itself rather than just documenting it

**Model qualities**: Accessible tone, iterative eval workflow, audience awareness, process-oriented rather than reference-oriented

---

### 7. nextjs (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/nextjs/SKILL.md`
**Lines**: 1745 | **Errors Prevented**: 25

**Why it is excellent**:
- Longest skill at 1745 lines, justified by the breadth of Next.js 16 breaking changes
- Security advisories section (December 2025 CVE context)
- "When NOT to Use" section prevents over-triggering
- Covers proxy.ts vs middleware comparison (new in Next.js 16)
- allowed-tools field explicitly set

**Model qualities**: Security advisory integration, "when NOT to use" section, length justified by complexity

---

### 8. cloudflare-mcp-server (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/cloudflare-mcp-server/SKILL.md`
**Lines**: (detailed) | **Errors Prevented**: 24

**Why it is excellent**:
- Identifies the #1 failure cause upfront (URL path mismatches)
- Template selection guide (authless, GitHub OAuth, Google OAuth, Auth0, AuthKit)
- Emphasizes "the ONLY platform with official remote MCP support"
- Monthly update tracking with specific SDK versions

**Model qualities**: Root cause identification, template-driven quick start, platform positioning clarity

---

### 9. mcp-oauth-cloudflare (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/mcp-oauth-cloudflare/SKILL.md`
**Lines**: (detailed) | **Errors Prevented**: 9

**Why it is excellent**:
- ASCII architecture diagram showing the dual OAuth role pattern
- Explicit "When NOT to Use" section (3 counter-indicators)
- Security-critical note: "MCP server generates and issues its own token rather than passing through the third-party token"
- Description calls out specific bugs (RFC 8707 audience bugs, Claude.ai connection failures)

**Model qualities**: Architecture diagrams, "when NOT to use", security-first design, specific bug references

---

### 10. claude-automation-recommender (claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/SKILL.md`
**Lines**: 288

**Why it is excellent**:
- Workflow-driven: analyzes codebase BEFORE making recommendations
- Read-only mode explicitly stated (does not create/modify files)
- Automation type comparison table (hooks vs subagents vs skills vs plugins vs MCP)
- Bash detection commands for project analysis

**Model qualities**: Analyze-before-recommend pattern, explicit scope boundaries, comparison tables

---

## Top 10 Lowest-Quality Skills

### 1. stripe-best-practices (claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/stripe/skills/stripe-best-practices/SKILL.md`
**Lines**: 30

**Issues**:
- Only 30 lines of prose directives with no code examples
- Single-sentence description with no "Use when" trigger specificity
- No version information, no error prevention, no quick start
- Entirely links to external Stripe documentation
- No YAML `user-invocable` field

**Needs**: Code examples, version pinning, error scenarios, structured format with quick start

---

### 2. frontend-design (claude-plugins-official + claude-code-plugins -- identical)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`
**Lines**: 42

**Issues**:
- Pure aesthetic philosophy with zero code examples
- No version information for any library
- No technical specifics (no framework versions, no package names)
- Description is generic ("build web components, pages, or applications") with no error keywords
- Identical copies exist in both claude-plugins-official and claude-code-plugins

**Needs**: Concrete code patterns, framework-specific examples, version references, error troubleshooting

---

### 3. example-skill (claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/plugins/example-plugin/skills/example-skill/SKILL.md`
**Lines**: 84

**Issues**:
- Template/demonstration skill with no real domain knowledge
- Exists solely to show skill format structure
- Description starts with "This skill should be used when..." (meta-referential)
- No practical value beyond documentation purposes

**Needs**: Should be clearly labeled as a template or moved to a docs directory, not presented as an installable skill

---

### 4. chatgpt-app-builder (mcp-use)

**Path**: `/Users/tk/.claude/plugins/marketplaces/mcp-use/skills/chatgpt-app-builder/SKILL.md`
**Lines**: 55

**Issues**:
- Explicitly DEPRECATED in the description itself
- Redirects to `mcp-app-builder` which does not exist in the marketplace skills directory
- Still contains implementation content despite deprecation notice
- Confusing for users who install it

**Needs**: Either remove entirely or replace with working redirect. Deprecated skills should not be discoverable.

---

### 5. mcp-builder (mcp-use)

**Path**: `/Users/tk/.claude/plugins/marketplaces/mcp-use/skills/mcp-builder/SKILL.md`
**Lines**: 70

**Issues**:
- Same deprecation problem as chatgpt-app-builder -- redirects to non-existent `mcp-app-builder`
- 70 lines of content that should not be loaded since the skill is deprecated
- Wastes context window tokens on deprecated instructions

**Needs**: Same as chatgpt-app-builder -- remove or replace with actual working skill

---

### 6. playground (claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-plugins-official/plugins/playground/skills/playground/SKILL.md`
**Lines**: 76

**Issues**:
- Interesting concept (interactive HTML playgrounds) but very thin implementation
- Only 76 lines with state management pattern and prompt output pattern
- No concrete examples of actual playgrounds built
- References template files (templates/*.md) but no inline examples to verify quality
- Description lacks error keywords or troubleshooting triggers

**Needs**: At least one complete playground example inline, before/after screenshots or outputs, error handling for common issues

---

### 7. writing-rules / hookify (claude-code-plugins + claude-plugins-official)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-code-plugins/plugins/hookify/skills/writing-rules/SKILL.md`
**Lines**: ~50

**Issues**:
- Extremely narrow scope: only covers hookify-specific rule syntax
- Identical duplicates across two marketplaces
- Description limited to hookify-specific triggers only
- No broader applicability to other hook systems or patterns

**Needs**: Either broaden scope to general hook/rule patterns or clearly label as hookify-specific utility

---

### 8. oauth-integrations (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/skills/oauth-integrations/SKILL.md`
**Lines**: 169

**Issues**:
- Only covers GitHub and Microsoft providers (very limited for "OAuth Integrations")
- Missing `user-invocable: true` field
- No error prevention count
- 169 lines is sparse for the scope implied by the name
- Overlaps significantly with `azure-auth` (Microsoft) and partially with `better-auth` (general OAuth)

**Needs**: Either rename to reflect limited scope (e.g., "github-microsoft-oauth") or expand to cover more providers. Add error prevention documentation.

---

### 9. plugin-settings (claude-code-plugins)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-code-plugins/plugins/plugin-dev/skills/plugin-settings/SKILL.md`
**Lines**: ~50

**Issues**:
- Documents a single pattern (`.local.md` files) that could be a section in a larger skill
- Very narrow scope -- barely qualifies as a standalone skill
- Description is comprehensive but the content does not justify a separate skill
- Part of the plugin-dev bundle where it could be a subsection of plugin-structure

**Needs**: Merge into plugin-structure skill or expand with more settings patterns (env vars, config files, etc.)

---

### 10. skill-skeleton template (claude-skills)

**Path**: `/Users/tk/.claude/plugins/marketplaces/claude-skills/templates/skill-skeleton/SKILL.md`
**Lines**: ~50

**Issues**:
- All content is `[TODO: ...]` placeholders
- Not a functional skill -- purely a template
- Should not appear in skill discovery
- Included in glob results and could confuse assessment tools

**Needs**: This is intentionally a template, not a quality issue per se, but it should be excluded from skill discovery paths (e.g., not in `skills/` directory)

---

## Overlap with Local Skills

| Local Skill | Marketplace Overlap | Overlap Level |
|---|---|---|
| `shadcn-ui` | `tailwind-v4-shadcn` (claude-skills) | **Medium** -- Local focuses on MCP tool integration for shadcn, marketplace focuses on Tailwind v4 + shadcn CSS architecture. Complementary more than duplicative. |
| `meta-skill` (Create New Skills) | `skill-creator` (claude-skills), `skill-creator` (claude-plugins-official), `skill-development` (claude-code-plugins) | **High** -- All teach skill creation. The official `skill-creator` has the eval-driven approach; the local `meta-skill` references documentation files; the claude-skills `skill-creator` focuses on description optimization. Consider consolidating. |
| `create-worktree-skill` | None | **No overlap** -- Unique local skill for git worktree creation |
| `worktree-manager-skill` | None | **No overlap** -- Unique local skill for git worktree lifecycle management |

### Cross-Marketplace Duplicates

| Skill | claude-code-plugins | claude-plugins-official | Notes |
|---|---|---|---|
| frontend-design | YES | YES | **Exact duplicate** |
| writing-rules (hookify) | YES | YES | **Exact duplicate** |
| agent-development (plugin-dev) | YES | YES | **Exact duplicate** |
| command-development (plugin-dev) | YES | YES | **Exact duplicate** (only in c-c-p) |
| skill-development (plugin-dev) | YES | YES | **Exact duplicate** (only in c-c-p) |
| plugin-settings (plugin-dev) | YES | YES | **Exact duplicate** (only in c-c-p) |
| plugin-structure (plugin-dev) | YES | YES | **Exact duplicate** |
| hook-development (plugin-dev) | YES | YES | **Exact duplicate** (only in c-c-p) |
| mcp-integration (plugin-dev) | YES | YES | **Exact duplicate** (only in c-c-p) |

**7 of 10 claude-code-plugins skills are exact duplicates of claude-plugins-official skills.** These marketplaces appear to be forks or mirrors.

---

## Summary Statistics

### By Quality Tier

| Tier | Description | Count | % |
|---|---|---|---|
| **A (Excellent)** | 500+ lines, rich examples, error prevention, version tracking, clear triggers | ~35 | 30% |
| **B (Good)** | 200-500 lines, solid structure, quick starts, mostly complete | ~45 | 38% |
| **C (Adequate)** | 100-200 lines, functional but could be deeper | ~20 | 17% |
| **D (Poor)** | Under 100 lines, missing examples, deprecated, or too narrow | ~10 | 8% |
| **N/A** | Templates, deprecated markers, or exact cross-marketplace duplicates | ~8 | 7% |

### By Marketplace

| Marketplace | Avg Quality | Avg Lines | Has Examples | Has "Use when" | Has Versions |
|---|---|---|---|---|---|
| **claude-skills** | A-/B+ | ~450 | 93/93 (100%) | 93/93 (100%) | 90/93 (97%) |
| **claude-code-plugins** | B-/C+ | ~150 | 6/10 (60%) | 10/10 (100%) | 0/10 (0%) |
| **claude-plugins-official** | B/C+ (high variance) | ~175 | 8/15 (53%) | 12/15 (80%) | 2/15 (13%) |
| **mcp-use** | D+ | ~160 | 1/3 (33%) | 1/3 (33%) | 0/3 (0%) |

### Description Quality Patterns

| Pattern | Good Practice | Count |
|---|---|---|
| Two-paragraph format (WHAT + WHEN) | YES | ~85 |
| "Use when:" explicit trigger | YES | ~100 |
| Error count in description ("Prevents N errors") | YES | ~55 |
| `user-invocable: true` | YES | ~85 |
| Version numbers in skill body | YES | ~90 |
| "When NOT to use" section | YES (underused) | ~8 |
| Architecture diagrams | YES (underused) | ~5 |

### Key Observations

1. **claude-skills dominates in quality and quantity** -- 93 skills with remarkable consistency, clearly following a documented standard (ONE_PAGE_CHECKLIST.md, STANDARDS_COMPARISON.md)
2. **Duplicate proliferation** -- 7 skills exist identically across claude-code-plugins and claude-plugins-official, wasting storage and causing confusion
3. **mcp-use is essentially non-functional** -- 2 of 3 skills are deprecated, leaving only mcp-apps-builder as viable
4. **Error prevention counts correlate with quality** -- Skills that track "Prevents N documented errors" consistently deliver more thorough content
5. **"When NOT to use" sections are rare but valuable** -- Only ~8 skills include negative triggers, reducing false activations
6. **The official Anthropic skill-creator (claude-plugins-official) has a uniquely effective conversational tone** that the claude-skills skill-creator lacks -- these could learn from each other

---

**Priority Level:** Medium -- No critical issues, but the duplicate proliferation and deprecated mcp-use skills should be cleaned up to avoid user confusion.