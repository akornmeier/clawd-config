# Plan: Simplify PlaywrightStepExecutor to use refs directly

## Problem
The step executor currently resolves semantic targets to `ElementHandle` objects, then passes them through `adapter.click(element)` / `adapter.fill(element, value)` etc. These adapter methods internally call `resolveElement()` again, extracting `element.selector` (which IS a ref string like `"e5"`) before making the MCP call. This is an unnecessary layer of indirection.

The two-phase resolution logic (strict polling + relaxed fallback) is sound, but the action dispatch should use `*ByRef()` methods directly once a ref is resolved.

## Changes

### File 1: `packages/core/src/services/browser/playwright-step-executor.ts`

**1. Replace `resolveTarget() → ElementHandle` with `resolveRef() → string`**

Same two-phase polling structure, but return `element.selector` (the ref) instead of the full ElementHandle.

```typescript
private async resolveRef(target: SemanticTargetSchemaType): Promise<string> {
  // Same polling + relaxed fallback logic
  // findElement returns ElementHandle | null
  // Extract element.selector (the ref string) on success
  // Throw ElementNotFoundError on failure
}
```

**2. Update action methods to use `*ByRef()`**

- `executeClick`: `const ref = await this.resolveRef(step.target)` → `adapter.clickByRef(ref)`
- `executeFill`: `const ref = await this.resolveRef(step.target)` → `adapter.fillByRef(ref, step.value)`
- `executeHover`: `const ref = await this.resolveRef(step.target)` → `adapter.hoverByRef(ref)`
- `executePress`: When `step.target` exists, resolve ref → `adapter.pressByRef(step.value, ref)`. Without target, `adapter.pressByRef(step.value)` (no ref, sends key to focused element)

**3. Remove `ElementHandle` import** (no longer needed)

**4. Keep `tryStrictMatch` and `tryRelaxedMatch`** but change return type from `ElementHandle | null` to `string | null` (extracting `.selector` from the found element).

### File 2: `packages/core/test/services/browser/playwright-step-executor.test.ts`

**1. Add `*ByRef` mocks to `createMockAdapter()`**
```typescript
clickByRef: vi.fn().mockResolvedValue({ success: true }),
fillByRef: vi.fn().mockResolvedValue({ success: true }),
hoverByRef: vi.fn().mockResolvedValue({ success: true }),
pressByRef: vi.fn().mockResolvedValue({ success: true }),
```

**2. Update action test assertions**
- Click tests: assert `clickByRef` called with ref string instead of `click` with element
- Fill tests: assert `fillByRef` called with ref + value
- Hover tests: assert `hoverByRef` called with ref
- Press tests: assert `pressByRef` called with key + ref (when target exists)
- Keep `findElement` assertions where they verify resolution logic

**3. Update mock findElement default return** to use a ref-like selector:
```typescript
findElement: vi.fn().mockResolvedValue({
  _id: 'element-1',
  selector: 'e1',  // ref format (was '[aria-label="Test"]')
  accessibleName: 'Test',
  role: 'button',
}),
```

## What stays the same
- Two-phase resolution structure (strict polling, relaxed fallback after timeout)
- `ElementNotFoundError` class and its constructor
- Journey execution logic (`executeJourney`, `executeStep`)
- Observer lifecycle integration
- Screenshot-on-failure behavior
- `calculateTimeout` logic
- Navigate, wait, screenshot actions (don't use element resolution)

## Verification
1. `pnpm --filter @oculis/core build` - confirm compilation
2. `pnpm --filter @oculis/core test` - all tests pass
3. `pnpm lint` - no lint errors
4. `pnpm format:check` - formatting clean
