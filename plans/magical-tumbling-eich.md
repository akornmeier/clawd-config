# Plan: CEO Board Meeting System for Pi

## Context

We're building a board meeting deliberation system on top of **Pi** (a terminal coding harness). The system simulates a CEO running a strategic board meeting with AI advisors, each bringing a distinct strategic lens. The CEO agent (Opus) orchestrates debate among board member agents (Sonnet), driven by a **brief** that frames a business decision. The meeting produces a final **memo** with the decision, SVG diagrams, and a TTS summary.

**Current state:** 3 of 9 agents exist (CEO, Compounder, Contrarian - the latter two need polish). No Pi extension exists yet. Skills (SVG, TTS) are provided by the user.

## Scope

### 1. Create 6 Missing Board Member Agents

Each follows the Compounder template structure. All agents use `anthropic/claude-sonnet-4-6`.

**Files to create:**
- `.pi/ceo-agents/agents/revenue.md`
- `.pi/ceo-agents/agents/product-strategist.md`
- `.pi/ceo-agents/agents/technical-architect.md`
- `.pi/ceo-agents/agents/customer-oracle.md`
- `.pi/ceo-agents/agents/market-strategist.md`
- `.pi/ceo-agents/agents/moonshot.md`

**Agent design - each agent needs:**
- Frontmatter (name, expertise path, skills with SVG, model, domain)
- Purpose statement
- Variables (objective function, time horizons, core bias, risk tolerance, default stance)
- Instructions (expertise block, skills block, runtime context)
- Temperament (5 traits)
- How This Role Thinks (4 questions)
- Reasoning Patterns (2 example quotes)
- Decision-Making Heuristics (5-7 heuristics)
- Questions You Press On (5-7)
- Evidence Standard
- Natural Tension Partners (with specific reasons)
- Red Lines (4)
- Role Checklist table
- Workflow (standardized 5-step)
- Report format

**Agent tension map (who naturally opposes whom):**
| Agent | Primary Tension | Secondary Tension |
|-------|----------------|-------------------|
| Revenue | Compounder (short vs long-term) | Customer Oracle (extraction vs trust) |
| Product Strategist | Technical Architect (ideal vs feasible) | Moonshot (incremental vs radical) |
| Technical Architect | Moonshot (pragmatic vs ambitious) | Revenue (quality vs speed) |
| Customer Oracle | Revenue (user advocacy vs extraction) | Market Strategist (current users vs market trends) |
| Market Strategist | Compounder (market moves vs retention) | Customer Oracle (trends vs current users) |
| Moonshot | Compounder (disruption vs stability) | Technical Architect (vision vs reality) |
| Contrarian | Everyone (by design) | N/A |
| Compounder | Revenue, Moonshot | Market Strategist |

### 2. Polish Existing Agents

**`.pi/ceo-agents/agents/contrarian.md`:**
- Fill in placeholder Red Lines (currently just "Red Line #1-4")
- Fill in Role Checklist (all say "needed")
- Fill in Natural Tension Partners with specific agents and reasons
- Fix typo: "trutch-seeking" -> "truth-seeking", "hole plan" -> "whole plan"
- Fix OBJECTIVE_FUNCTION: says "Maximize the probability of catastrophic error" - should be "Minimize" or "Surface"

**`.pi/ceo-agents/agents/compounder.md`:**
- Fix typos: "Heiristics" -> "Heuristics", "retension" -> "retention", "Parrtners" -> "Partners", "thiis" -> "this", "ans" -> "and"
- Update Natural Tension Partners to reference actual board member names

**`.pi/ceo-agents/agents/ceo.md`:**
- Fix typo: "EXPPERTISE_BLOCK" -> "EXPERTISE_BLOCK", "wrtie" -> "write"

### 3. Create Expertise Scratch Pad Files

Each agent gets an empty scratch pad for runtime notes:
- `.pi/ceo-agents/expertise/compounder-scratch-pad.md` (already referenced)
- `.pi/ceo-agents/expertise/contrarian-scratch-pad.md`
- `.pi/ceo-agents/expertise/revenue-scratch-pad.md`
- `.pi/ceo-agents/expertise/product-strategist-scratch-pad.md`
- `.pi/ceo-agents/expertise/technical-architect-scratch-pad.md`
- `.pi/ceo-agents/expertise/customer-oracle-scratch-pad.md`
- `.pi/ceo-agents/expertise/market-strategist-scratch-pad.md`
- `.pi/ceo-agents/expertise/moonshot-scratch-pad.md`

### 4. Build Pi Extension: Board Meeting Orchestrator

**File:** `.pi/ceo-agents/extensions/board-meeting.ts`

This TypeScript extension implements the meeting orchestration:

**Custom Tools registered for the CEO:**
- `converse(to: string | string[], message: string)` - Routes CEO messages to board members
  - Spawns board member LLM sessions (one per member) using Pi SDK's `createAgentSession`
  - Board members respond in parallel (all see the full conversation log)
  - Each member's agent .md is injected as system prompt with template variables resolved
  - Appends all messages to a JSONL conversation log
  - Returns all responses + constraint state (elapsed time, budget spent)
- `end_deliberation(message: string)` - Final round, Contrarian goes last
  - Broadcasts closing prompt to all members
  - Enforces Contrarian-last ordering
  - Returns all final statements

**Meeting State Management:**
- Track elapsed wall-clock time (min 3min, max 10min)
- Track real API cost via token counts (min $3, max $10)
- Expose constraints in every `converse()` response so CEO can pace the meeting
- Store conversation log as JSONL at `{deliberations_dir}/{session_id}/conversation.jsonl`

**Template Variable Resolution:**
- Read YAML config at startup
- For each agent .md, resolve: `{{EXPERTISE_BLOCK}}`, `{{SKILLS_BLOCK}}`, `{{DELIBERATION_DIR}}`, `{{CONVERSATION_LOG}}`
- For CEO: also resolve `{{SESSION_ID}}`, `{{BRIEF_CONTENT}}`, `{{BOARD_MEMBERS}}`, `{{MEMO_PATH}}`, `{{MIN_TIME}}`, `{{MAX_TIME}}`, `{{MIN_BUDGET}}`, `{{MAX_BUDGET}}`

**Board Member Session Management:**
- Each board member gets a persistent Pi SDK session for the duration of the meeting
- System prompt = their agent .md with variables resolved
- On `converse()`: send the CEO's message + full conversation log to each targeted member
- Collect responses in parallel, append to log, return to CEO

**Note:** The exact sub-agent spawning mechanism depends on Pi SDK capabilities. If `createAgentSession` supports injecting system prompts from .md files, we use that. Otherwise, we may need to use Pi's RPC mode or direct Anthropic API calls. Will verify during implementation with SDK docs.

### 5. Wire Up Skills

User has existing SVG and TTS skills. We need to:
- Get the skill files from the user and place them in `skills/svg-generate/SKILL.md` and `skills/tts-eleven/SKILL.md`
- Ensure all board member agents reference the SVG skill in their frontmatter
- Ensure CEO references both SVG and TTS skills

### 6. Create Output Directories

- `.pi/ceo-agents/deliberations/` - conversation logs per session
- `.pi/ceo-agents/memos/` - final CEO memos with SVGs and audio

## Build Sequence

1. **Polish existing agents** (CEO, Contrarian, Compounder) - fix typos, fill placeholders
2. **Create 6 new agents** - can be done in parallel
3. **Create expertise scratch pad files** - trivial, do alongside agents
4. **Build the Pi extension** - the core orchestration logic
5. **Wire up skills** - get files from user, place in correct locations
6. **Test end-to-end** - load a brief, run a meeting, verify memo output

## Verification

1. All 9 agent .md files parse correctly (valid YAML frontmatter, no template syntax errors)
2. Pi extension loads without errors (`pi -e .pi/ceo-agents/extensions/board-meeting.ts`)
3. `converse("all", "...")` spawns all board members and returns responses
4. Budget and time tracking report accurate numbers
5. Conversation log JSONL is well-formed
6. CEO can call `end_deliberation()` and Contrarian speaks last
7. CEO writes memo with SVG diagrams and TTS summary

## Open Questions

- **Skills location:** User needs to provide existing SVG and TTS skill files
- **Pi SDK sub-agents:** Need to verify `createAgentSession` API supports custom system prompts. Fallback: use direct Anthropic API calls within the extension.
- **Domain config:** The `domain: []` field needs a convention for how domain docs are referenced and loaded
