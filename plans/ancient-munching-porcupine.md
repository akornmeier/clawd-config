# Qualifying Conversation: Relationship Context Onboarding

## Context

The pipeline currently assumes a romantic-partner lens for all analyses — the taxonomy (`taxonomy.ts`) uses Gottman frameworks, attachment theory, and "bids for connection" language designed for couples. When a user uploads a conversation with their **mother**, the models misapply these frameworks: labeling normal adult-child independence as `avoidant_attachment`, casual check-ins as `assertive_communication`, and silence as `stonewalling_gottman`. This produces misleading analysis.

**Goal:** Add a conversational onboarding step between conversation selection and pipeline processing. An LLM asks 2-4 qualifying questions to establish relationship context, then that context flows through the entire pipeline to calibrate pattern detection, narrative framing, and output tone.

---

## Design

### 1. RelationshipContext Type

Define a shared type used across web, Convex, and pipeline:

```ts
interface RelationshipContext {
  relationshipType: 'romantic_partner' | 'parent_child' | 'sibling' | 'friend' | 'coworker' | 'other';
  userRole?: string;          // e.g. "adult child", "younger sibling"
  otherRole?: string;         // e.g. "mother", "older brother"
  cadence?: 'daily' | 'weekly' | 'occasional' | 'sporadic';
  userIntent?: 'general' | 'specific_concern' | 'curiosity' | 'growth';
  intentDetail?: string;      // free-text if specific_concern
  rawTranscript?: string[];   // the qualifying Q&A messages for audit
}
```

### 2. Qualifying Conversation UI (New Component)

**New file:** `packages/web/components/upload/QualifyingChat.tsx`

A lightweight chat interface that:
- Receives a `ConversationMeta` (contact name, message count, date range) from the selector
- Uses an LLM (haiku) to generate 2-4 contextual questions
- Infers relationship type from the contact name + message sample, then **confirms** with the user
- Collects intent ("What are you curious about?")
- Outputs a `RelationshipContext` object
- Has a "Skip — just analyze it" escape hatch that uses defaults

**LLM-driven conversation (haiku generates all phrasing dynamically):**

The component sends the contact metadata (name, message count, date range, avg frequency) to haiku with a system prompt that instructs it to:
- Infer the relationship from the contact name and stats
- Ask 2-4 natural qualifying questions in a warm, conversational tone
- Use a structured tool-call schema to signal when it has enough info to emit a `RelationshipContext`
- Keep it to 3-4 exchanges max

The LLM manages the flow — it decides when it has enough context and emits a structured `RelationshipContext` via tool use. The UI renders each LLM message as a chat bubble and each user response as a text input (with optional quick-reply chips for common answers like "Yes", "My mother", "Just curious").

**Typical flow:**
1. LLM: "I see 948 messages with 'Mom' over about 18 months — looks like you two text pretty regularly. Is this your mother?"
2. User: "Yeah"
3. LLM: "Got it! Anything in particular you're curious about, or just want a general picture of how you two communicate?"
4. User: "General picture"
5. LLM emits `RelationshipContext` via tool call → UI transitions to payment

### 3. Upload Flow Integration

**Modified file:** `packages/web/app/dashboard/upload/page.tsx`

Add a new step to the upload state machine:

```
'upload' → 'selecting' → 'qualifying' → 'payment'
                              ↑ NEW
```

- After `ConversationSelector` completes (user picks conversations), transition to `qualifying` step
- `QualifyingChat` renders with the selected conversation metadata
- On completion, store `RelationshipContext` in component state alongside selections
- Pass context forward to payment and eventually to the pipeline job

### 4. Convex Schema Update

**Modified file:** `convex/schema.ts`

Add `relationshipContext` field to the `analyses` table:

```ts
relationshipContext: v.optional(v.object({
  relationshipType: v.string(),
  userRole: v.optional(v.string()),
  otherRole: v.optional(v.string()),
  cadence: v.optional(v.string()),
  userIntent: v.optional(v.string()),
  intentDetail: v.optional(v.string()),
})),
```

### 5. Pipeline Server — Accept Context

**Modified file:** `packages/pipeline/src/server.ts`

Extend `JobRequest` to accept `relationshipContext`:

```ts
interface JobRequest {
  // ... existing fields
  relationshipContext?: RelationshipContext;
}
```

Pass it through `runPipeline()` to all prompt-building functions.

### 6. Prompt Injection — The Core Change

**Modified files:**
- `packages/pipeline/src/llm/prompts/session-summary.ts`
- `packages/pipeline/src/llm/prompts/register-update.ts`
- `packages/pipeline/src/llm/prompts/snapshot.ts`
- `packages/pipeline/src/llm/prompts/walkthrough.ts`

Each `buildXxxSystemPrompt()` function gains an optional `context?: RelationshipContext` parameter. When provided, a `## RELATIONSHIP CONTEXT` section is injected into the system prompt:

```
## RELATIONSHIP CONTEXT
This conversation is between an adult child and their mother.
- Relationship type: parent-child
- User's role: adult child
- Communication cadence: daily

Calibrate your analysis for this relationship type:
- Patterns like brief responses, logistical coordination, and independent decision-making are NORMATIVE in adult parent-child relationships, not signs of avoidance or disengagement.
- The Gottman "bids" framework was designed for romantic partners; apply it with appropriate adjustment for family dynamics.
- Power dynamics in parent-child relationships have a developmental context (e.g., parental authority shifting to peer-like respect over time).
- "Stonewalling" in a parent-child context may simply reflect generational communication differences, not emotional withdrawal.
```

The calibration text is generated dynamically based on `relationshipType` — a `buildRelationshipCalibration(context)` helper function returns the appropriate guidance per type.

### 7. Taxonomy Calibration Helper

**New file:** `packages/pipeline/src/llm/relationship-calibration.ts`

Contains `buildRelationshipCalibration(context: RelationshipContext): string` that returns relationship-type-specific guidance injected into prompts. This keeps the taxonomy itself universal but adjusts how models interpret patterns per relationship type.

### 8. CLI Support

**Modified file:** `packages/pipeline/src/cli.ts`

Add `--relationship-type` and `--user-role` CLI flags for local runs, constructing a `RelationshipContext` that flows into the prompt builders.

---

## Files to Create
| File | Purpose |
|------|---------|
| `packages/web/components/upload/QualifyingChat.tsx` | Chat UI component |
| `packages/pipeline/src/llm/relationship-calibration.ts` | Calibration text per relationship type |
| `packages/pipeline/src/types/relationship-context.ts` | Shared `RelationshipContext` type |

## Files to Modify
| File | Change |
|------|--------|
| `packages/web/app/dashboard/upload/page.tsx` | Add `qualifying` step to state machine |
| `convex/schema.ts` | Add `relationshipContext` to `analyses` table |
| `packages/pipeline/src/server.ts` | Accept `relationshipContext` in `JobRequest`, pass through pipeline |
| `packages/pipeline/src/cli.ts` | Add `--relationship-type` / `--user-role` flags |
| `packages/pipeline/src/llm/prompts/session-summary.ts` | Accept + inject context |
| `packages/pipeline/src/llm/prompts/register-update.ts` | Accept + inject context |
| `packages/pipeline/src/llm/prompts/snapshot.ts` | Accept + inject context |
| `packages/pipeline/src/llm/prompts/walkthrough.ts` | Accept + inject context |
| `packages/pipeline/src/llm/session-summaries.ts` | Thread context through to prompt builder |
| `packages/pipeline/src/llm/pattern-register.ts` | Thread context through to prompt builder |
| `packages/pipeline/src/llm/snapshot.ts` | Thread context through to prompt builder |
| `packages/pipeline/src/llm/walkthrough.ts` | Thread context through to prompt builder |

## Build Sequence
1. **Types first** — `relationship-context.ts` (shared type)
2. **Calibration helper** — `relationship-calibration.ts`
3. **Prompt injection** — modify all 4 prompt builders
4. **Pipeline threading** — wire context through `session-summaries.ts`, `pattern-register.ts`, `snapshot.ts`, `walkthrough.ts`, `server.ts`, `cli.ts`
5. **Convex schema** — add field to `analyses` table
6. **UI component** — `QualifyingChat.tsx`
7. **Upload flow** — integrate into `upload/page.tsx`

## Verification
1. **Pipeline CLI** — Run `pnpm pipeline analyze <file> --relationship-type parent_child --user-role "adult child"` and verify prompt injection in verbose output
2. **Prompt content** — Add a `--dry-run` check that prints the system prompt with context section visible
3. **UI flow** — Manual test: upload → select conversation → qualifying chat appears → answer questions → context stored → payment step
4. **Regression** — Run pipeline without context (no flags) → behavior unchanged, all existing tests pass
5. **Lint + format** — `pnpm lint && pnpm format`
6. **Tests** — `pnpm test` from root
