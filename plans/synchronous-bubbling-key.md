# Plan: Replace PlaywrightMCPClient with @playwright/mcp

## Summary
Replace the hand-rolled `PlaywrightMCPClient` (~800 lines of custom Playwright wrapper) with the official `@playwright/mcp` package. This fixes the root cause of missing textboxes in diagnostics/healing — the new implementation gets accessibility data directly from Playwright's MCP server which correctly returns the full accessibility tree with proper ARIA roles.

## Files to Change

| File | Action | Why |
|---|---|---|
| `packages/cli/package.json` | Modify | Add `@playwright/mcp` + `@modelcontextprotocol/sdk` deps |
| `packages/cli/src/adapters/snapshot-parser.ts` | **Create** | Parse YAML snapshot text → structured nodes with refs |
| `packages/cli/test/adapters/snapshot-parser.test.ts` | **Create** | Tests for parser |
| `packages/cli/src/adapters/mcp-client.ts` | **Rewrite** | Replace PlaywrightMCPClient with @playwright/mcp-backed impl |
| `packages/cli/test/adapters/mcp-client.test.ts` | Update | Align with new implementation |
| `packages/cli/src/commands/scan-browser.ts` | Modify | Fix `onStepFailed` (line 867) to use `pageContext.interactiveElements` instead of top-level-only `accessibilityTree.map()` |

**NOT changed:** All core package files (`playwright-mcp-adapter.ts`, `playwright-step-executor.ts`, `llm-reasoning-agent.ts`, etc.) — they depend on the `MCPClient.call()` interface which we preserve.

## Steps

### 1. Install dependencies
```bash
pnpm --filter @oculis/cli add @playwright/mcp @modelcontextprotocol/sdk
```

### 2. Create `snapshot-parser.ts`
**File:** `packages/cli/src/adapters/snapshot-parser.ts`

Parse the `browser_snapshot` text response. The format is:
```
### Page state
- Page URL: https://example.com
- Page Title: Example
- Page Snapshot:
```yaml
- form [ref=e1]:
  - textbox "Name" [ref=e2]
  - textbox "Email" [required] [ref=e3]
  - button "Submit" [ref=e6]
```

Functions to implement:
- `parseSnapshotResponse(text: string): ParsedSnapshot` — extract url, title, tree nodes
- `flattenInteractiveNodes(nodes: SnapshotNode[]): SnapshotNode[]` — recursively collect interactive-role nodes
- `findRefByTarget(nodes: SnapshotNode[], target: {accessibleName?, role?, visibleText?}): string | null` — match SemanticTarget → ref
- `findNodeByRef(nodes: SnapshotNode[], ref: string): SnapshotNode | null` — look up node for element description

### 3. Create `snapshot-parser.test.ts`
**File:** `packages/cli/test/adapters/snapshot-parser.test.ts`

Test with realistic snapshot text including nested forms with textboxes, comboboxes, etc. Test matching logic, edge cases (empty tree, missing names, duplicate roles).

### 4. Rewrite `PlaywrightMCPClient`
**File:** `packages/cli/src/adapters/mcp-client.ts`

Key changes:
- **`connect()`**: Use `createConnection()` from `@playwright/mcp` + `InMemoryTransport` from `@modelcontextprotocol/sdk` for in-process communication
- **`call('take_snapshot', args)`**: Call `browser_snapshot`, parse response with `parseSnapshotResponse()`, cache the parsed snapshot. If `args` has semantic target fields, resolve to ref using `findRefByTarget()` and return `ElementInfo`
- **`call('click', {selector})`**: `selector` is actually a ref. Call `browser_click({element: description, ref})`
- **`call('fill', {selector, value})`**: Call `browser_type({element: description, ref, text: value})`
- **`call('hover', {selector})`**: Call `browser_hover({element: description, ref})`
- **`call('press_key', {key})`**: Call `browser_press_key({key})`
- **`call('navigate_page', {url})`**: Call `browser_navigate({url})`
- **`call('take_screenshot')`**: Call `browser_take_screenshot`, extract base64 image from response
- **`call('evaluate_script', {script})`**: Call `browser_evaluate({code: script})`
- Cache `lastSnapshot` so action calls can look up element descriptions by ref
- `getInteractiveElements()` removed entirely — the snapshot parser extracts them from the YAML

### 5. Fix `onStepFailed` in scan-browser.ts
**File:** `packages/cli/src/commands/scan-browser.ts` lines 858-871

Replace:
```typescript
const pageContext = await adapter!.getPageContext();
const accessibilityTree = await adapter!.getAccessibilityTree();
// ...
interactiveElements: accessibilityTree.map(node => ({
  role: node.role,
  name: node.name,
})),
```

With:
```typescript
const pageContext = await adapter!.getPageContext();
// pageContext.interactiveElements now has ALL elements from the full a11y tree
const healResult = await healingService.healStep({
  failedStep: result.step,
  stepIndex: index,
  errorMessage: result.error ?? 'Unknown error',
  pageContext: {
    url: pageContext.url,
    title: pageContext.title,
    interactiveElements: pageContext.interactiveElements.map(el => ({
      role: el.role,
      name: el.name,
    })),
  },
  recentSteps: cachedJourney.steps.slice(Math.max(0, index - 2), index),
});
```

### 6. Update tests, build, lint, verify
- Update `packages/cli/test/adapters/mcp-client.test.ts`
- `pnpm build:packages && pnpm lint && pnpm format && pnpm test`

## Key Design Decisions

1. **In-process transport** — Use `InMemoryTransport.createLinkedPair()` to talk to `@playwright/mcp` without network overhead. The server runs in the same Node.js process.

2. **Preserve `MCPClient.call()` interface** — The new client translates our tool names to Playwright MCP tool names. Core code is untouched.

3. **`selector` field stores ref** — `ElementHandle.selector` now contains the snapshot ref (e.g., `"e6"`). This is a transparent change since the adapter passes it back to `click({selector})` which the new client translates to `browser_click({ref})`.

4. **Cached snapshot for action calls** — After `take_snapshot`, the parsed tree is cached. When `click`/`fill`/`hover` are called, the client looks up the element description from the cached tree to satisfy `browser_click`'s `element` parameter.

## Verification
1. `pnpm build:packages` — compiles
2. `pnpm lint && pnpm format` — clean
3. `pnpm test` — all tests pass
4. Manual: `npx oculis scan-browser --url https://www.namecheap.com --journey "search for a domain name" --verbose` — verify textbox appears in diagnostics
