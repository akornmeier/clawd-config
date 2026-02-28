# Plan: Enrich semantic targets at recording time

## Context

When the LLM agent executes a journey and records steps to YAML cache, `buildSemanticTargetFromRef()` only captures `{accessibleName, role}`. When the page has multiple elements sharing the same name and role (e.g., two "Search" buttons — one in the header, one in the hero), cached replay picks the first match, which may be wrong.

The previous fix (Phase 0 fallback-first in `resolveRef`) addresses this for steps that have already been corrected. This change prevents the ambiguity from ever being recorded by enriching targets upfront with `spatialHint` (landmark context) and disambiguating information.

## Approach

Enrich `buildSemanticTargetFromRef()` to derive spatial context from the accessibility tree's ancestor path. When the ref's name+role is ambiguous (multiple elements match), also record landmark-based `spatialHint`.

## Changes

### 1. Enrich `buildSemanticTargetFromRef` — `packages/cli/src/adapters/snapshot-parser.ts`

**Current** (lines 318-328): Returns only `{accessibleName, role}`.

**New behavior**:
1. Find the node by ref (existing)
2. Use `getAncestorPath()` (already exists at line 382) to get the ancestor chain
3. Walk ancestors to find the nearest landmark role (`banner`, `navigation`, `main`, `form`, `search`, `region`, `complementary`, `contentinfo`)
4. Use `findAllRefsByTarget()` (already exists at line 352) to check if `name + role` is ambiguous (>1 match)
5. If ambiguous, set `spatialHint` from the landmark context (e.g., "in the main content", "in the header")
6. Return the enriched `SemanticTargetSchemaType`

**Return type change**: `{ accessibleName?: string; role?: string }` → `SemanticTargetSchemaType` (which already has `spatialHint`, `visibleText`, `fallbackSelectors` fields)

**Reuse existing utilities**:
- `getAncestorPath()` from the same file
- `findAllRefsByTarget()` from the same file
- Landmark label logic similar to `getLandmarkLabel()` in `element-formatter.ts` (inline a simple version to avoid cross-module dependency)

### 2. Update call site — `packages/cli/src/commands/scan-browser.ts`

**Lines 1086-1101**: The call site already stores the derived target. Since the return type now includes `spatialHint`, no structural change needed — just ensure the type annotation matches.

### 3. Tests — `packages/cli/test/adapters/snapshot-parser.test.ts`

Add tests for the enriched `buildSemanticTargetFromRef`:
- Returns `spatialHint` when name+role is ambiguous (two "Search" buttons in different landmarks)
- Does NOT add `spatialHint` when name+role is unique (no ambiguity)
- Returns null when ref not found (existing behavior preserved)
- Handles elements with no landmark ancestor gracefully

## Files to modify

| File | Change |
|------|--------|
| `packages/cli/src/adapters/snapshot-parser.ts` | Enrich `buildSemanticTargetFromRef()` with spatialHint for ambiguous targets |
| `packages/cli/src/commands/scan-browser.ts` | Update type annotation at call site (~line 1090) |
| `packages/cli/test/adapters/snapshot-parser.test.ts` | Add tests for enriched target derivation |

## Verification

1. Run `pnpm --filter @oculis/cli build` to verify compilation
2. Run `pnpm --filter @oculis/cli test` to verify all tests pass
3. Run `pnpm build:packages && pnpm test` for full suite
4. Run `pnpm lint && pnpm format`
