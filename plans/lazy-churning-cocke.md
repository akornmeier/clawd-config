# Plan: Fix Element Disambiguation + Observer Issue Collection

Two related but independent fixes for the CLI browser agent.

---

## Problem 1: Search Button Disambiguation (Proximity-Based Resolution)

**Root cause**: `findNodeByTarget()` in `snapshot-parser.ts:321` does depth-first search and returns the **first** match. When there are two "Search" buttons (header + form), it always picks whichever appears first in the tree, ignoring that the agent just typed into a form input.

### Solution: Track last interaction ref, prefer same-ancestor matches

**Files to modify:**

1. **`packages/cli/src/adapters/snapshot-parser.ts`**
   - Add `findAllNodesByTarget()` — returns ALL matching nodes with their refs
   - Add `getAncestorPath(nodes, ref)` — returns the chain of ancestor refs from root to the given ref
   - Add `findClosestRefByTarget(nodes, target, contextRef)` — finds all matches, scores by shared ancestor depth with `contextRef`, returns deepest-shared-ancestor match

2. **`packages/cli/src/adapters/mcp-client.ts`**
   - Add `lastInteractionRef: string | null` field to `PlaywrightMCPClient`
   - After `clickElement()`, `fillElement()`, `hoverElement()` — store the ref used as `lastInteractionRef`
   - In `takeSnapshot()` target resolution (line 419): use `findClosestRefByTarget()` when `lastInteractionRef` exists, fall back to `findRefByTarget()` when no context

**How it works:**
```
Agent fills searchbox ref=15 (inside form ref=10)
  → lastInteractionRef = "15"

Agent clicks button "Search"
  → findAllNodesByTarget finds: ref=5 (header), ref=16 (form ref=10)
  → getAncestorPath("15") = [root, main:4, form:10, searchbox:15]
  → getAncestorPath("5")  = [root, banner:1, button:5] — shared depth: 0
  → getAncestorPath("16") = [root, main:4, form:10, button:16] — shared depth: 2 (main + form)
  → Picks ref=16 (deeper shared ancestor = closer proximity)
```

---

## Problem 2: Observer Not Collecting Accessibility Issues

**Root cause**: Observer is injected once at `scan-browser.ts:794`. Navigations during journeys destroy `window.__oculisObserver`. No re-injection. `journeyViolations` (line 798) is never populated.

### Solution: Auto-setup ObserverLifecycleManager (fixture pattern)

Create a self-managing `ObserverLifecycleManager` class that acts as an automatic worker-scoped fixture. Once created and passed to the agent, it transparently handles inject/collect/re-inject — no manual callback wiring needed.

**New file:**

1. **`packages/core/src/services/browser/observer-lifecycle-manager.ts`**

```typescript
export interface ObserverLifecycleManager {
  /** One-time setup — injects observer into current page */
  setup(adapter: PlaywrightMCPAdapter): Promise<void>;
  /** Collect + preserve issues before navigation destroys page context */
  beforeNavigation(adapter: PlaywrightMCPAdapter): Promise<void>;
  /** Re-inject observer if page context was destroyed */
  afterAction(adapter: PlaywrightMCPAdapter): Promise<void>;
  /** Return all accumulated issues across the entire session */
  collectAll(adapter: PlaywrightMCPAdapter): Promise<BrowserIssue[]>;
  /** Cleanup observer */
  teardown(adapter: PlaywrightMCPAdapter): Promise<void>;
}
```

Implementation stores `BrowserIssue[]` internally, calls `observerInjector.collectIssues()` before navigations, checks `observerInjector.isActive()` after actions, and re-injects when needed.

**Files to modify:**

2. **`packages/core/src/services/browser/llm-reasoning-agent.ts`**
   - Add optional `observerManager?: ObserverLifecycleManager` to constructor
   - In `executeJourney()`:
     - Call `observerManager.setup()` at the start of the loop
     - Before navigate/click actions: call `observerManager.beforeNavigation()`
     - After every action: call `observerManager.afterAction()`
   - Expose `observerManager.collectAll()` in the journey result (or via getter)

3. **`packages/core/src/services/browser/playwright-step-executor.ts`** (cached mode)
   - Same pattern: accept optional `ObserverLifecycleManager`, auto-invoke during step execution

4. **`packages/cli/src/commands/scan-browser.ts`**
   - Create the manager once: `const observerManager = createObserverLifecycleManager(observerInjector)`
   - Pass to agent: `new DefaultLLMReasoningAgent(llmAdapter, null, observerManager)`
   - After journey: `const journeyViolations = await observerManager.collectAll(adapter)`
   - Remove manual observer inject at line 794 (manager handles it)

5. **`packages/core/src/index.ts`** — export new types/factory

**Why this is better than callback wiring:**
- Observer lifecycle is encapsulated — consumers just create it and pass it
- Works identically for agent mode and cached mode
- "Auto" — once set up, no manual intervention needed
- Mirrors Playwright Test's `{ scope: 'worker', auto: true }` semantics

---

## Implementation Order

1. **Snapshot parser proximity functions** — pure functions, easy to unit test
2. **MCP client interaction tracking** — wire up `lastInteractionRef`
3. **ObserverLifecycleManager** — new class in core + tests
4. **Wire manager into agent + step executor** — accept as dependency, auto-invoke
5. **Update scan-browser.ts** — create manager, pass to agent, collect at end

## Verification

1. Build: `pnpm build:packages`
2. Run existing tests: `pnpm test`
3. Run lint/format: `pnpm lint && pnpm format`
4. Manual test: `pnpm --filter @oculis/cli start -- scan https://www.namecheap.com --journey "Search for a domain" --llm-provider ollama --no-headless --verbose`
   - Verify agent clicks correct search button after filling input
   - Verify accessibility issues are reported in output
