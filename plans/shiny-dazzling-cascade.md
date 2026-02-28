# Plan: Delete Legacy .js Test Files + Remove Shadow DOM Feature Detection

## Context

After Phase 3 migration (Mocha/Karma → Vitest/Playwright), 420+ old `.js` test files remain alongside their `.test.ts` replacements. They cause **30,728 lint errors** (mostly `no-undef` and `func-names` from oxlint processing Mocha globals). Additionally, ~60 `.test.ts` files conditionally skip shadow DOM tests via `shadowSupport.v1` checks — unnecessary since Playwright + Chrome always supports Shadow DOM v1.

## Task 1: Delete Legacy .js Test Files

**Safe to delete (fully replaced by `test/browser/`):**
- `test/checks/**/*.js` — all files
- `test/commons/**/*.js` — all files
- `test/core/**/*.js` — all files
- `test/rule-matches/**/*.js` — all files

**Safe to delete (replaced by `test/unit/`):**
- `test/integration/virtual-rules/*.js` — all 47 files
- `test/test-locales.js`
- `test/test-virtual-rules.js`
- `test/test-rule-help-version.js`

**NOT deleting (still active):**
- `test/integration/full/**/*.js` — loaded by HTML pages in WebDriver pipeline
- `test/integration/no-ui-reporter.js`, `test/integration/adapter.js`
- `test/act-rules/`, `test/aria-practices/`, `test/get-webdriver.js`
- `test/node/node.js`, `test/node/jsdom.js`

**Config cleanup after deletion:**
- `oxlint.json` — remove the `test/**/*.js` override block (mocha env, assert/sinon globals) since remaining `.js` test files are in `integration/full/` which has its own needs
  - Actually: keep the override but audit if it still applies to remaining `.js` files in `integration/full/`. Those still use Mocha globals, so the override may need to stay but could be narrowed.

### Steps
1. `git rm` all `.js` files in `test/checks/`, `test/commons/`, `test/core/`, `test/rule-matches/`
2. `git rm` all `.js` files in `test/integration/virtual-rules/`
3. `git rm test/test-locales.js test/test-virtual-rules.js test/test-rule-help-version.js`
4. Narrow the oxlint.json `test/**/*.js` override glob to `test/integration/**/*.js` (only remaining Mocha .js files)
5. Run `pnpm lint` and verify error count drops dramatically

## Task 2: Remove Shadow DOM Feature Detection Guards

Since Playwright + Chrome always has `attachShadow`, simplify all shadow DOM conditional patterns in `.test.ts` files.

### Patterns to transform

| Pattern | Transform |
|---|---|
| `(shadowSupport.v1 ? it : xit)('name', fn)` | `it('name', fn)` |
| `const shadowTest = shadowSupport.v1 ? it : xit;` then `shadowTest(...)` | Remove variable, use `it(...)` |
| `if (shadowSupport.v1) { it(...) }` or `if (shadowSupportV1) { it(...) }` | Remove `if` wrapper, keep `it()` |
| `if (shadowSupport.v1) { describe(...) }` | Remove `if` wrapper, keep `describe()` |
| `describe.skipIf(!shadowSupported)(...)` | `describe(...)` |
| `const testSuite = shadowSupported ? describe : describe.skip;` | Remove variable, use `describe(...)` |
| `if (shadowSupport.v1)` inside test body | Remove `if`, keep assertions |
| Inline `typeof document.body.attachShadow === 'function'` | Remove, always true |

### v0 tests (dead code — Shadow DOM v0 removed from Chrome 2018)
- `test/browser/core/utils/flattened-tree.test.ts` — `if (shadowSupport.v0) { describe(...) }` → **delete entire block**
- `test/browser/commons/dom/find-up.test.ts` — `(shadowSupport.v0 ? it : xit)(...)` → **delete these test cases**
- `test/browser/core/utils/flattened-tree.test.ts` — `if (shadowSupport.undefined) { describe(...) }` → **delete entire block**

### testutils.ts cleanup
- Remove the `shadowSupport` export entirely (lines 77-97)
- Remove `shadowSupport` from any re-exports or type declarations

### Steps
1. Remove `shadowSupport` from `testutils.ts`
2. In each `.test.ts` file: remove `shadowSupport` imports and conditional guards per the transform table above
3. Delete v0 and `undefined` shadow DOM test blocks entirely
4. Run `pnpm lint` and `pnpm test` to verify

## Files to modify

**Delete (~475 files):**
- `test/checks/**/*.js`, `test/commons/**/*.js`, `test/core/**/*.js`, `test/rule-matches/**/*.js`
- `test/integration/virtual-rules/*.js`
- `test/test-locales.js`, `test/test-virtual-rules.js`, `test/test-rule-help-version.js`

**Edit (~60 .test.ts files + testutils.ts + oxlint.json):**
- `test/testutils.ts` — remove `shadowSupport` export
- `oxlint.json` — narrow test override glob
- ~60 `.test.ts` files in `test/browser/` — remove shadow DOM conditional guards

## Verification

1. `pnpm lint` — errors should drop from ~31k to a much smaller number
2. `pnpm test` — all tests should pass
3. `pnpm format` — check formatting
4. Grep for `shadowSupport` to confirm no remaining references
5. Grep for `xit` to confirm no remaining Mocha-isms from shadow guards
