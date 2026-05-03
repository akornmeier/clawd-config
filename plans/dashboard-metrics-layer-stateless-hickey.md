# Plan: Dashboard Metrics Layer — Phase 0+1 (Convex layer)

**Slug:** `dashboard-metrics-layer`
**Upstream:** `docs/brainstorms/2026-05-02-dashboard-metrics-layer-requirements.md`
**Anchor:** *Right primitives, even if slow.* No LLM in scoring chain, no placeholders, no vibe scores.

## Context

The dashboard mockup needs vocabulary that does not exist in the schema today (`warmth`, `repair`, `latency`, `initiation`, `archetype`). The ideation doc (`docs/ideation/2026-05-02-dashboard-metrics-layer.md`) recommended Idea 1 — a four-layer pyramid: per-message signals → per-relationship rollups → per-user rollups → population aggregates. The brainstorm locked in 7 user stories and 24 acceptance criteria.

This plan covers **Phase 0 + Phase 1** of the recommended sequencing: schema, deterministic extractors, rollup writers, archetype scoring function, and crons. **Out of scope:** the one-shot backfill action (Phase 2), dashboard UI / read path (Phase 2), F1–F4 then-vs-now surface (Phase 2). Phase 2 will be planned separately once Phase 0+1 is live and writing rows.

The deliverable of this plan is a Convex schema and pipeline integration where every new analysis produces durable per-message signal rows, per-relationship rollups, per-user rollups, and (nightly) population aggregates — with archetype assignment running deterministically against a hand-authored 8-archetype taxonomy. No frontend changes.

## Locked decisions (from /brainstorm + clarifying Qs)

| Decision | Choice | Source |
|---|---|---|
| Plan scope | Phase 0 + Phase 1 (no backfill, no UI) | Clarifying Q |
| Archetype taxonomy | 8 new archetypes per ideation (`THE_ANCHOR`, `THE_BRIDGER`, `THE_SENTINEL`, `THE_KINDLER`, `THE_HARMONIZER`, `THE_PROVIDER`, `THE_WANDERER`, `THE_WITNESS`) | Clarifying Q |
| Partial-vector scoring | 6-tuple `axisProfile`, scorer ignores null user-axes | Clarifying Q (requirements OQ #1 → option b) |
| Scoring metric (OQ #3) | **Cosine similarity** with masked-axis dot product. Weighted Manhattan deferred to v2 if archetype assignments feel "too directional" in practice. | Planner |
| Tie-break order (OQ #4) | Source-array order of the `ARCHETYPES` const, top-down: `ANCHOR, BRIDGER, SENTINEL, KINDLER, HARMONIZER, PROVIDER, WANDERER, WITNESS`. Encoded as the array literal — no `Object.keys()` or insertion-order assumptions. | Planner |
| Snapshot dedup (OQ #7) | **No dedup for v1.** Append every snapshot. Storage cost (~one row per analysis-completion + one per nightly cron) is negligible vs. history fidelity. Revisit in v2 if `relationshipRollups` row count exceeds 10⁵ per active user. | Planner |
| Repair-success heuristic (OQ #6) | Ship with the "next 3 messages from counterpart show warmer scores than prior 3" heuristic. Document the heuristic in the extractor and emit `repairSucceeded: null` when fewer than 3 follow-up messages exist. Labeled validation set is a v1.5 concern. | Planner |
| F1–F4 N-days (OQ #5) | Out of scope (Phase 2). Plan default of **N=30 days** when Phase 2 is written. | Planner — deferred |
| Backfill blast radius (OQ #8) | Out of scope. Phase 2 plan must include a write-unit estimate before greenlighting. | Deferred |
| `axisProfile` numbers (OQ #2) | The 8 archetype `axisProfile` 6-tuples will land as **deliberately-marked placeholder values** in this plan's Phase 1, with `// TODO(design+data): real axis profile` comments. The scoring function and schema work end-to-end against placeholders; rotating real numbers in is a const-only edit (no migration). Authorship is a Phase 2 prerequisite, not a Phase 0+1 blocker. | Planner |

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ packages/pipeline/src/signals/  (NEW — pure deterministic)     │
│   initiation.ts • latency.ts • warmth.ts • repair.ts          │
│   index.ts (extractAllSignals)                                 │
└──────────────────────────┬─────────────────────────────────────┘
                           │ (called from cli.ts after Stage 3)
                           ▼
┌────────────────────────────────────────────────────────────────┐
│ Convex tables (NEW)                                            │
│   messageSignals          ← bulk-inserted at pipeline end      │
│        ↓ rollup writer (synchronous, post-metadata)            │
│   relationshipRollups     ← append-only snapshot               │
│        ↓ nightly cron `dailyUserRecompute`                     │
│   userRollups             ← append-only, archetype assigned    │
│        ↓ nightly cron `dailyPopulationRecompute`               │
│   populationAxisAggregates ← k-anonymous, sampleN ≥ 50        │
└────────────────────────────────────────────────────────────────┘

packages/shared/src/archetypes.ts   ← 8-archetype const + scoreArchetype()
                                      cosine similarity, masked nulls
```

## File-level plan

### Phase 0 — Schema + extractor scaffolding

**0.1 Schema (`convex/schema.ts`).** Append four tables to the existing `defineSchema`:

- `messageSignals` — fields: `analysisId` (Id<'analyses'>), `userId` (Id<'users'>), `contactId` (optional Id<'contacts'>), `messageIndex` (number), `ts` (number), `sender` (`'participant_a' | 'participant_b'`), `initiated` (boolean), `latencyMs` (optional number), `warmth0to100` (number), `repairAttempt` (boolean), `repairSucceeded` (optional boolean). Indexes: `by_analysis`, `by_contact_ts`, `by_user_ts`, `by_analysis_messageIndex` (for AC 5.3 idempotency lookups).
- `relationshipRollups` — `userId`, `contactId`, `computedAt`, `windowDays`, `axis6` (object with all six axis names, all optional float64), `latencyMedianMs`, `latencyMinMs`, `latencyMaxMs`, `warmthBaselineDeg`, `warmthMaxContact`, `warmthMinContact`, `initiationRatePct`, `repairTendency` (string union), `repairMedianTimeMs`, `snapshotKind` (`'rolling90d' | 'allTime' | 'milestone'`). Index: `by_user_contact_computed`.
- `userRollups` — `userId`, `computedAt`, `windowDays`, `axis6` (six optional float64s — curiosity/presence are `null` in v1, AC 5.4), `archetypeSlug` (optional string), `archetypeScores` (optional object), `snapshotKind`. Index: `by_user_computed`.
- `populationAxisAggregates` — `axis` (string), `p25`, `p50`, `p75`, `p90`, `sampleN`, `computedAt`, `cohortKey` (defaults to `'all_users'`). Index: `by_cohort_axis_computed`. Per AC 2.4: **no `userId` references at any point**.

Match existing style: `v.id('users')`, `v.optional(v.float64())`, `.index('by_user', ['userId'])`. Mirror the `pipelineEvents` append-only pattern (`convex/schema.ts`).

**0.2 CI guard (`scripts/check-no-llm-in-signals.sh`).** Mirror `scripts/check-no-voyage-in-pipeline.sh`. Recursively grep `packages/pipeline/src/signals/` for `openai|anthropic|@ai-sdk|llm-clients|voyage`; exit 1 on match. Wire into `package.json` script `check:no-llm-in-signals` and into the existing CI lint step.

**0.3 Extractor module — `packages/pipeline/src/signals/`.** Each file is pure, deterministic, takes `Message[]` (and optionally precomputed metadata), returns `MessageSignalRow[]`. No I/O, no LLM imports.

- `latency.ts` — reuses `computeResponseLatency`'s loop pattern from `packages/pipeline/src/metadata/session-metadata.ts:9-36` but emits per-message rather than collapsing. Returns `latencyMs | null` per message (null for the very first message and for self-replies — same sender twice).
- `initiation.ts` — emits `initiated: true` for the first message of each session and the first message of each new calendar day. Reuses session boundaries from `SegmentationResult`.
- `warmth.ts` — calls `analyzeSentiment(text)` per-message from `packages/pipeline/src/metadata/sentiment.ts` (already returns the VADER-compound + repair/escalation/affection overlays), then maps the compound score from `[-1, 1]` to `[0, 100]` via `Math.round(((compound + 1) / 2) * 100)`. **Reuse**, do not re-implement, the existing lexicons (`REPAIR_PHRASES`, `AFFECTION_TERMS`, `ESCALATION_PHRASES` in `metadata/sentiment.ts`).
- `repair.ts` — emits `repairAttempt: true` when message text contains a `REPAIR_PHRASES` token. For `repairSucceeded`: scan the next 3 messages from the *counterpart* (skipping same-sender follow-ups); if their mean `warmth0to100` exceeds the prior-3-counterpart-message mean, return `true`; else `false`; if fewer than 3 follow-up counterpart messages exist, return `null`.
- `index.ts` — `extractAllSignals(sessions: Session[], analysis: { _id, userId, contactId? }): MessageSignalRow[]`. Composes the four extractors with a shared per-message position counter so `messageIndex` is monotonically increasing across the entire analysis.

**0.4 Pipeline integration (`packages/pipeline/src/cli.ts:444`-region).** After the existing Stage 3 (Metadata) call to `computeAllSessionMetadata(...)`, add a Stage 3.5: `extractAllSignals(...)`. Write the result to a stage output file (matches the existing `writeStageOutput` pattern). Bulk-write to Convex via a new `internalMutation` in `convex/messageSignals.ts`:

- `convex/messageSignals.ts` (NEW) — exports `bulkUpsert` (`internalMutation`) that takes the array of signal rows and inserts them with idempotent `(analysisId, messageIndex)` lookup (per AC 5.3). The existing pipeline → Convex bridge in this codebase uses the same pattern (see how `analysisResults` lands in pipeline-completion).

**0.5 Tests (`packages/pipeline/tests/signals.test.ts`).** Vitest. Per AC 1.3, run each extractor twice on a fixture and assert byte-identical output. Per AC 1.2, assert `warmth0to100` is the documented deterministic function (no Math.random spy hits). Property test: shuffle the lexicon arrays in test setup and confirm output is unchanged (lexicons are sets, not order-dependent).

### Phase 1 — Rollup writers, archetype const, crons

**1.1 Archetype taxonomy + scoring (`packages/shared/src/archetypes.ts`, NEW).**

```ts
export type Axis6 = {
  initiate: number | null;
  repair: number | null;
  warmth: number | null;
  curiosity: number | null;  // null in v1
  presence: number | null;   // null in v1
  latency: number | null;
};

export type Archetype = {
  slug: string;
  displayName: string;
  tagline: string;
  narrativeTemplate: string; // mustache, filled with user numbers per AC 4.5
  axisProfile: Axis6;        // 6-tuple, all numbers (TODO real values)
};

// Tie-break: source-order top-down (AC 4.3).
export const ARCHETYPES: readonly Archetype[] = [
  { slug: 'THE_ANCHOR',     /* TODO(design+data): real axis profile */ ... },
  { slug: 'THE_BRIDGER',    ... },
  { slug: 'THE_SENTINEL',   ... },
  { slug: 'THE_KINDLER',    ... },
  { slug: 'THE_HARMONIZER', ... },
  { slug: 'THE_PROVIDER',   ... },
  { slug: 'THE_WANDERER',   ... },
  { slug: 'THE_WITNESS',    ... },
] as const;

export function scoreArchetype(userVector: Axis6): {
  slug: string;
  scores: Record<string, number>;
};
```

`scoreArchetype` computes cosine similarity per archetype using only the axes where `userVector[axis]` is non-null (the masked subset). Returns the full `scores` map (per AC 4.2 — stored on `userRollups.archetypeScores` for explainability) and the winning slug. Tie-break (within 0.02 of next): pick the lower index in `ARCHETYPES`.

Re-export through `packages/shared/src/index.ts`. The existing legacy `packages/web/lib/archetypes.ts` (display-only Anchor/Spark/Bridge/Mirror/Guardian/Explorer/Lighthouse + Weaver/Catalyst/Sage/Sentinel) is **left untouched** in this plan — it powers the existing walkthrough archetype card surface. Phase 2 (UI) is where we'll reconcile / migrate. Calling out so a future reader doesn't trip on the dual-archetype-set transient state.

**1.2 Rollup writer (`convex/internal/rollups.ts`, NEW).** Two `internalMutation`s:

- `writeRelationshipRollup({ userId, contactId, windowDays, snapshotKind })` — reads `messageSignals` via `by_contact_ts` for the (user, contact, window), computes the axis6 + latency/warmth/repair/initiation derived stats, inserts a new `relationshipRollups` row (append-only per AC 5.2). Pure read+insert; never updates an existing row.
- `writeUserRollup({ userId, windowDays, snapshotKind })` — reads the user's most-recent `relationshipRollups` snapshot per contact via `by_user_contact_computed`, aggregates each axis as the recent-message-count-weighted mean across contacts, calls `scoreArchetype(axis6)`, inserts a new `userRollups` row with `archetypeSlug` and `archetypeScores`. **Curiosity and presence are written as `null`** (AC 5.4 — distinguishes "not yet computed" from zero).

**1.3 Pipeline-completion hook.** In the existing pipeline-completion landing path (the place that writes `analysisResults`), append calls to:
1. `internal.messageSignals.bulkUpsert` (already added in 0.4)
2. `internal.rollups.writeRelationshipRollup` (for the analysis's contact, if `analyses.contactId` is set)
3. `internal.rollups.writeUserRollup` (for the analysis's user)

Idempotency: re-running the pipeline for the same analysis will overwrite the same `(analysisId, messageIndex)` rows in `messageSignals` (AC 5.3) and append fresh snapshot rows downstream (intended — snapshots are append-only, AC 5.2).

**1.4 Crons (`convex/crons.ts`).** Append two daily handlers, mirror the existing `cleanupExpiredSharedDecks` pattern:

- `dailyRelationshipRecompute` (UTC 02:00) — scan `relationshipRollups` for `(userId, contactId)` pairs whose latest `computedAt` is > 24h old AND has new `messageSignals` since that snapshot; call `writeRelationshipRollup` for each. Skip pairs with no new signals (storage discipline). Implemented in `convex/internal/dailyRecompute.ts`.
- `dailyPopulationRecompute` (UTC 03:00) — read all users' most-recent `userRollups`, compute per-axis quartiles (`p25/p50/p75/p90`), but **only emit a `populationAxisAggregates` row if `sampleN >= 50`** (AC 2.1). `cohortKey: 'all_users'`. The cron rebuilds the table from current `userRollups` each night (AC 6.3 — naturally drops deleted users).

**1.5 Anti-vibe trace test (`convex/tests/rollupTrace.test.ts`, NEW).** Property-style test (per requirements doc "Notes for the planner"): seed a fixture with N messages → run extractors → run rollup writers → sample one rendered axis value from `userRollups.axis6.warmth` → walk it backward through the rollup chain → assert it terminates at one or more `messageSignals` rows whose `analysisId` belongs to the user. Enforces AC 1.4 ("any rendered axis traces to messageSignals"). Without this test, "right primitives" is unenforceable.

**1.6 Schema migration story.** Convex schema changes are additive (new tables, new indexes; no existing field touched). Deploy via the existing `pnpm convex deploy` flow. No data migration needed; backfill of historical analyses is explicitly Phase 2.

## Critical files

**Read-only references (existing):**
- `convex/schema.ts` — append four tables here
- `convex/crons.ts` — append two cron registrations here
- `convex/internal.ts` — match the `cleanupExpiredSharedDecks` style for new internal mutations
- `packages/pipeline/src/cli.ts:444` — pipeline integration point (after Stage 3 metadata)
- `packages/pipeline/src/metadata/session-metadata.ts:9-36` — `computeResponseLatency` to reuse
- `packages/pipeline/src/metadata/sentiment.ts` — `analyzeSentiment`, `REPAIR_PHRASES`, `AFFECTION_TERMS`, `ESCALATION_PHRASES` to reuse
- `packages/pipeline/src/parsers/types.ts` — `Message`, `Session` types
- `scripts/check-no-voyage-in-pipeline.sh` — template for the new CI guard

**New files:**
- `packages/pipeline/src/signals/{initiation,latency,warmth,repair,index}.ts`
- `convex/messageSignals.ts` (with `bulkUpsert`)
- `convex/internal/rollups.ts` (with `writeRelationshipRollup`, `writeUserRollup`)
- `convex/internal/dailyRecompute.ts` (cron handlers)
- `packages/shared/src/archetypes.ts`
- `scripts/check-no-llm-in-signals.sh`
- `packages/pipeline/tests/signals.test.ts`
- `convex/tests/rollupTrace.test.ts`

**Modified:**
- `convex/schema.ts` — four new table defs
- `convex/crons.ts` — two new cron registrations
- `packages/shared/src/index.ts` — re-export `archetypes`
- `packages/pipeline/src/cli.ts` — Stage 3.5 invocation + bulk write
- The pipeline-completion landing path (the place that writes `analysisResults`) — add three internal mutation calls
- Root `package.json` — `check:no-llm-in-signals` script + CI hook

## Verification

End-to-end (each step is a hard yes/no):

1. **Schema deploys.** `pnpm convex deploy` succeeds; the four new tables are visible in the Convex dashboard with the indexes named in 0.1.
2. **CI guard works.** `scripts/check-no-llm-in-signals.sh` exits 0 on the clean tree; intentionally add an `import OpenAI from 'openai'` to `packages/pipeline/src/signals/warmth.ts` and confirm it exits 1. Revert.
3. **Extractor unit tests pass** — `pnpm vitest run packages/pipeline/tests/signals.test.ts`. Includes the AC 1.3 idempotency check (run extractor twice → byte-equal output).
4. **Live pipeline writes signals.** Run `pnpm pipeline analyze fixtures/<thread>.json` against an existing test fixture. Confirm via Convex dashboard that `messageSignals` has exactly `messageCount` rows for that `analysisId` (AC 1.1) and that no row has a placeholder/synthetic warmth (AC 1.2 — sample 5 rows by hand and recompute by hand).
5. **Rollup writers fire on completion.** After the pipeline run in step 4, confirm one new `relationshipRollups` row and one new `userRollups` row exist for the user. `userRollups.axis6.curiosity` and `.presence` are `null`; the other four axes are populated.
6. **Archetype scoring is idempotent (AC 4.4).** Run `writeUserRollup` twice with no new signals between calls — both inserts produce the same `archetypeSlug`. Two new rows (snapshot pattern), identical archetype.
7. **Anti-vibe trace test passes** — `pnpm vitest run convex/tests/rollupTrace.test.ts`. Sampled axis value walks back to `messageSignals` rows.
8. **Cron N≥50 floor** — manually invoke `dailyPopulationRecompute` against a seeded test environment with 49 users → assert zero `populationAxisAggregates` rows (AC 2.1, AC 2.3 empty-state precondition). Add a 50th user → re-run → assert exactly 6 rows (one per axis), each with `sampleN === 50`. Curiosity and presence rows are still emitted but with whatever the `null`-handling policy is — *open implementation question, see below.*
9. **Population aggregate carries no PII** — read the entire `populationAxisAggregates` table and `grep -i userid` on the JSON dump → zero matches (AC 2.4, AC 6.1).

## Open implementation questions (resolve during build, not before)

These do not block the plan but the implementer should make and document the choice:

- **Population aggregate behavior for null axes.** When an axis is `null` for all users (curiosity/presence in v1), should `dailyPopulationRecompute` skip the row entirely or emit a row with `sampleN: 0`? Recommendation: **skip** — keeps "no row exists" as the single signal for "not yet baselineable", avoids divide-by-zero in any downstream consumer. Document in the cron's source.
- **`messageSignals.bulkUpsert` chunk size.** Convex has per-mutation write limits. For analyses with > ~1000 messages, the bulk insert may need to chunk. Implement with a default chunk of 500; tune with the first real backfill in Phase 2.
- **Window definition for "rolling90d".** The exact wall-clock semantics — anchored to `analysis.completedAt` or to "now"? Recommendation: anchor to `now` for nightly cron writes and to `analysis.completedAt` for pipeline-completion writes. Document.
- **`writeRelationshipRollup` skip-if-no-signals.** The cron should NOT write a snapshot if no new `messageSignals` exist since the previous one (storage discipline). The pipeline-completion path SHOULD always write (the analysis is fresh evidence). Implement as a `since: number` parameter that the cron passes and the pipeline path omits.

## Phase 2 prerequisites (for future planner — not for this plan)

Capturing so the next plan does not re-derive:

- Author the eight `axisProfile` 6-tuples (OQ #2) with design + data partnership before the dashboard renders archetype cards meaningfully. Until then, the const ships with TODO-marked placeholders and `userRollups.archetypeSlug` is technically populated but should not be surfaced to users.
- Decide F1–F4 N-days threshold (OQ #5; planner default = 30).
- Decide backfill write-unit budget (OQ #8) before invoking the one-shot backfill action.
- Build the dashboard read path: radar (with curiosity/presence in "loading" state per AC 1.5), archetype card (mustache template per AC 4.5), relationship cards, population overlay (with "building baseline" empty state per AC 2.3 when no aggregate row exists).
- Decide whether `walkthrough.ts:417-447` rhythm-card aggregation reads from `relationshipRollups` instead of recomputing (out-of-scope for both Phase 0+1 and Phase 2 dashboard wiring; surgical refactor for v1.5).
