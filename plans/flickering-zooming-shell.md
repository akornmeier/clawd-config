# Fix: Accessibility scanning, cache validation, and agent verification

## Problem Summary

Three issues from the CLI scan log:

1. **CRITICAL: Zero accessibility violations** — `browser_evaluate` MCP call uses wrong parameter name (`expression` instead of `function`) and wrong format (bare statements instead of arrow functions). ALL evaluate calls silently fail, breaking observer injection, axe-core scanning, and URL retrieval.

2. **Cache validation errors** — `take_snapshot` actions get recorded in `executedSteps` and fail schema validation when saving to cache (schema only allows: navigate, click, fill, press, hover, wait, screenshot).

3. **Agent declares "done" without verification** — When the LLM decides the journey is complete, the agent returns success immediately without checking the actual page state.

---

## Fix 1: `browser_evaluate` parameter + format (CRITICAL)

**File**: `packages/cli/src/adapters/mcp-client.ts` — `evaluateScript()` method (~line 568)

**Root cause**: Line 577 passes `{ expression: script }` to `browser_evaluate`. The Playwright MCP `browser_evaluate` tool expects `{ function: "() => { ... }" }` — an arrow function string.

**Change**: Wrap all scripts in `() => { ... }` and use `function` parameter name:

```typescript
// Playwright MCP browser_evaluate expects `function` param with arrow function format
const fn = `() => { ${script} }`;
const text = await this.callMcpTool('browser_evaluate', { function: fn });
```

**Why `() => { script }` works for all callers**:
- Scripts with `return`: `return x` → `() => { return x }` — returns value
- Statement blocks (`if/return`): `if (...) { return true; } return false;` → `() => { ... }` — works
- IIFE observer script: `(function() { ... })();` → `() => { ... }` — returns `undefined` but caller only checks truthy (fallback handles it)
- axe-core injection: side-effect-only, return type is `void`
- Async scripts: `return (async () => { ... })();` → `() => { return (async () => { ... })(); }` — works

**Test update**: `packages/cli/test/adapters/mcp-client.test.ts`
- Line 382: Change expected arg from `{ expression: '21 + 21' }` to `{ function: '() => { 21 + 21 }' }`

---

## Fix 2: Filter `take_snapshot` from cached steps

**File**: `packages/cli/src/commands/scan-browser.ts` — `onAfterAction` callback (~line 960)

**Root cause**: `onAfterAction` records ALL successful actions into `executedSteps`, including `take_snapshot`. Cache validation rejects these.

**Change**: Add guard before pushing to `executedSteps`:

```typescript
// Record step for cache — skip agent-only actions that aren't valid cached steps
if (result.success && action.action !== 'take_snapshot' && action.action !== 'done') {
    executedSteps.push({ ... });
}
```

No test changes needed — the existing tests don't cover agent-mode caching directly.

---

## Fix 3: Agent verification before completing journey

**File**: `packages/core/src/services/browser/llm-reasoning-agent.ts`

**Approach**: When the LLM decides "done", take an accessibility tree snapshot and ask the LLM to verify the goal was achieved. Make this opt-in via constructor option to avoid breaking existing tests (~18 tests return "done").

### a) Add options to constructor:

```typescript
export interface AgentOptions {
    /** Whether to verify completion with a snapshot before accepting "done" (default: false) */
    verifyCompletion?: boolean;
}

constructor(
    llm: LLMAdapter,
    contextExtractor?: DefaultPageContextExtractor | null,
    observerManager?: ObserverLifecycleManager,
    options?: AgentOptions
)
```

### b) Add private verification method:

```typescript
private async verifyCompletion(
    goal: string,
    adapter: PlaywrightMCPAdapter,
    history: ActionHistory
): Promise<{ confirmed: boolean; reasoning: string }>
```

Takes a snapshot, asks LLM: "Does the current page state confirm the goal has been achieved?"

### c) Update `executeJourney()` done handling (line 496):

When `verifyCompletion` is enabled and the LLM says "done":
1. Call `verifyCompletion()`
2. If confirmed → return success
3. If not confirmed → log, add to history, continue loop

### d) Enable in CLI (scan-browser.ts ~line 942):

```typescript
const agent = new DefaultLLMReasoningAgent(
    llmAdapter as LLMAdapter,
    null,
    observerManager,
    { verifyCompletion: true }
);
```

**Test updates**: `packages/core/test/services/browser/llm-reasoning-agent.test.ts`
- Existing tests: No changes needed (default is `verifyCompletion: false`)
- New tests: Create agent with `{ verifyCompletion: true }` and test:
  - Verification confirmed → journey passes
  - Verification rejected → loop continues with history entry

---

## Files Modified

| File | Change |
|------|--------|
| `packages/cli/src/adapters/mcp-client.ts` | Fix `browser_evaluate` param name + arrow fn wrapping |
| `packages/cli/test/adapters/mcp-client.test.ts` | Update expected `browser_evaluate` arguments |
| `packages/cli/src/commands/scan-browser.ts` | Filter `take_snapshot`/`done` from cached steps, enable verification |
| `packages/core/src/services/browser/llm-reasoning-agent.ts` | Add verification step, `AgentOptions` type |
| `packages/core/test/services/browser/llm-reasoning-agent.test.ts` | Add verification tests |

---

## Verification

1. `pnpm build:packages`
2. `pnpm test`
3. `pnpm lint`
4. `pnpm format`
