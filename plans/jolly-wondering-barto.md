# Plan: Register batching + accurate cost estimation

## Context

The register accumulation stage makes **one LLM call per session** sequentially (143 calls for 143 sessions). Each call re-sends the ~1,830-token system prompt + growing register JSON. This is the primary latency and cost bottleneck.

The cost estimator is off by ~10-20x because it:
- Ignores fixed per-call overhead (system prompt, few-shot examples)
- Models the register as a single `0.6x` multiplier instead of N sequential LLM calls
- Uses hardcoded pricing that drifts from actual OpenRouter rates

This plan addresses three things:
1. **Batch register sessions** to reduce LLM call count by ~5x
2. **Fetch live pricing from OpenRouter** so estimates stay accurate automatically
3. **Fix the cost estimator** to model what actually happens

---

## Part 1: Batch register accumulation

### Current behavior (`pattern-register.ts:255-303`)
```
for each session (1..N):
  updateRegisterLocal(register, session)
  callLLM(register + session) → refined register
  pruneRegister(register)
```
143 sessions = 143 sequential Sonnet calls.

### New behavior
```
for each batch of REGISTER_BATCH_SIZE sessions:
  for each session in batch:
    updateRegisterLocal(register, session)
  callLLM(register + [batch of summaries]) → refined register
  pruneRegister(register)
```
143 sessions / 5 per batch = 29 calls (5x reduction).

### Changes

**`packages/pipeline/src/llm/pattern-register.ts`**
- Add `batchSize` to `RegisterConfig` interface, default to `parseInt(process.env.REGISTER_BATCH_SIZE ?? '5')`
- Refactor the `for` loop to iterate in chunks of `batchSize`
- Apply `updateRegisterLocal` for each session in the batch before the LLM call
- Pass all batch summaries in a single `callLLM` invocation

**`packages/pipeline/src/llm/prompts/register-update.ts`**
- Update `buildRegisterUpdateUserMessage` to accept an array of session summaries instead of a single one
- Change the user message format from `## NEW SESSION SUMMARY (N of M)` to `## NEW SESSION SUMMARIES (batch X-Y of M)` with each summary labeled
- Keep existing single-session signature working (pass `[summary]` internally) to avoid breaking existing tests

**`packages/pipeline/src/cli.ts`**
- Add `--register-batch-size <n>` CLI option (default: `process.env.REGISTER_BATCH_SIZE ?? '5'`)
- Pass `batchSize` through to `accumulateRegister` config

### Env var
- `REGISTER_BATCH_SIZE` — controls how many session summaries are sent per register LLM call. Default `5`. Set higher (10-15) for faster runs with less LLM refinement granularity, or `1` for original behavior.

---

## Part 2: Live pricing from OpenRouter API

### OpenRouter endpoint
`GET https://openrouter.ai/api/v1/models` returns a `data` array where each model has:
```json
{
  "id": "anthropic/claude-sonnet-4.6",
  "pricing": {
    "prompt": "0.000003",    // $/token (string)
    "completion": "0.000015"  // $/token (string)
  }
}
```
Auth: `Authorization: Bearer <OPENROUTER_API_KEY>` (same key we already have).

### New file: `packages/pipeline/src/llm/pricing-cache.ts`

```ts
interface CachedPricing {
  models: Record<string, { input: number; output: number }>; // $/1K tokens
  fetchedAt: number; // Date.now()
}
```

- `fetchModelPricing(apiKey: string): Promise<CachedPricing>` — calls `/api/v1/models`, filters to models matching `anthropic/`, `google/`, `openai/`, extracts `pricing.prompt` and `pricing.completion`, converts from per-token strings to per-1K-token numbers
- `getCachedPricing(apiKey: string): Promise<CachedPricing>` — returns cached data if < 4 hours old, otherwise fetches fresh
- Module-level `let cache: CachedPricing | null` for in-process caching
- File-based cache at `~/.cache/validating/pricing.json` for cross-process persistence (survives CLI restarts)
- Graceful fallback: if the fetch fails (network error, no API key), fall back to hardcoded `MODEL_COSTS` from `client.ts`

### Changes to `client.ts`
- `estimateCost()` accepts an optional `CachedPricing` parameter. If provided, looks up model pricing from cache instead of hardcoded `MODEL_COSTS`. Falls back to `MODEL_COSTS` for unknown models.
- Export `MODEL_COSTS` as the fallback (already exported).

### Changes to `cost-estimate.ts`
- Import `getCachedPricing` and use live pricing instead of hardcoded `MODEL_PRICING`
- Convert from per-1K-token (cache format) to per-MTok (estimator format) at usage site

### Changes to `pricing.ts` (and `packages/web/lib/pricing.ts`)
- Import and use live pricing for `BALANCED_PRICING` values
- Since `pricing.ts` is called at CLI interactive time (user is present), the 4-hour cache ensures at most one API call per session

---

## Part 3: Fix the cost estimator

### Problem summary
The estimator models stages as simple multipliers of total text tokens. The actual pipeline makes **N calls per session** for the register stage, each with ~1,830 tokens of fixed system prompt overhead, plus the summary and few-shot overhead for the summaries stage.

### Changes to `cost-estimate.ts`

**Replace `estimateStageTokens` with per-call modeling:**

1. **Summaries stage**: `sessionCount * (SYSTEM_PROMPT_OVERHEAD + FEW_SHOT_OVERHEAD + avgSessionTokens + OUTPUT_TOKENS_PER_SUMMARY)`
   - `SYSTEM_PROMPT_OVERHEAD = 1830` (taxonomy + guardrails)
   - `FEW_SHOT_OVERHEAD = 1075` (3 examples from bank)
   - `avgSessionTokens = totalTextTokens / sessionCount`
   - `OUTPUT_TOKENS_PER_SUMMARY = 400`

2. **Register stage**: `ceil(sessionCount / REGISTER_BATCH_SIZE) * (SYSTEM_PROMPT_OVERHEAD + avgRegisterSize + batchSummaryTokens + OUTPUT_TOKENS_PER_REGISTER)`
   - `SYSTEM_PROMPT_OVERHEAD = 1830`
   - `avgRegisterSize = 500` (starts empty, grows to ~2000 token budget, average ~500)
   - `batchSummaryTokens = REGISTER_BATCH_SIZE * OUTPUT_TOKENS_PER_SUMMARY` (each summary is ~400 tokens)
   - `OUTPUT_TOKENS_PER_REGISTER = 2000` (full register JSON output)
   - Number of calls = `ceil(sessionCount / batchSize)` instead of 1

3. **Other stages** (episodes, snapshot, walkthrough): Keep multiplier approach but add `SYSTEM_PROMPT_OVERHEAD` per call (these are single-call stages, so add once)

4. **Input/output split**: Model per-stage instead of global 75/25. Each stage now computes input and output tokens separately based on the per-call model above.

**New function signature:**
```ts
export function estimateCosts(
  sessions: Session[],
  metadata: SessionMetadata[],
  options?: { registerBatchSize?: number; pricing?: CachedPricing }
): CostEstimate
```

### Changes to `pricing.ts`
- Replace `estimateBaseCost` with a version that uses the same per-call model
- Accept `registerBatchSize` parameter (default from env var)
- The `AVG_CHARS_PER_MESSAGE = 50` stays (pricing.ts doesn't have access to actual text), but add the fixed overhead per session

### Changes to `cli.ts`
- Pass `registerBatchSize` and `CachedPricing` to `estimateCosts()` for dry-run
- Fetch pricing early (before interactive prompts) so it's cached for both the conversation selector and the pipeline run

---

## Files to modify/create

| File | Action |
|---|---|
| `packages/pipeline/src/llm/pricing-cache.ts` | **New** — OpenRouter pricing fetch + cache |
| `packages/pipeline/src/llm/pattern-register.ts` | Batch the accumulation loop |
| `packages/pipeline/src/llm/prompts/register-update.ts` | Support batched session summaries in user message |
| `packages/pipeline/src/llm/client.ts` | `estimateCost()` accepts optional live pricing |
| `packages/pipeline/src/validation/cost-estimate.ts` | Per-call token modeling, live pricing, batch size param |
| `packages/pipeline/src/validation/pricing.ts` | Per-call overhead, batch size, live pricing |
| `packages/pipeline/src/cli.ts` | `--register-batch-size` flag, pricing fetch, wire through |
| `packages/pipeline/tests/register.test.ts` | Update tests for batched behavior |
| `packages/pipeline/tests/cost-estimate.test.ts` | Update expected values, test per-call model |
| `packages/pipeline/tests/pricing.test.ts` | Update expected values |

---

## Verification

1. `REGISTER_BATCH_SIZE=1 pnpm --filter pipeline test` — all tests pass (backward compat)
2. `pnpm --filter pipeline test` — all tests pass with default batch size 5
3. `pnpm lint` — clean
4. `pnpm test` — full suite passes
5. Manual: `npx tsx src/cli.ts analyze <file> --dry-run` — verify cost report shows realistic numbers (compare against actual run costs from previous pipeline runs)
6. Manual: verify `~/.cache/validating/pricing.json` is created after first run with API key
