# Form-Aware Spatial Understanding for LLM Web Agent

## Context

The LLM agent struggles with spatial form understanding. When a page has multiple forms (login, search, registration), the agent picks the wrong "Submit" button or targets a field in the wrong form. The accessibility tree shows structure through indentation, but forms are just another indentation level — easy for the LLM to miss.

Research into Stagehand, Agent-E, browser-use, and other web agent frameworks reveals that **no major project solves form scoping at the infrastructure level** — they all delegate it to the LLM. The ones that perform best reduce noise before the LLM sees the tree. Three strategies, shipped incrementally across PRs.

### Ideas borrowed from Stagehand

- **Aggressive tree pruning**: Collapse structural/generic single-child nodes, deduplicate static text matching parent names. Review our snapshot parser against these rules.
- **Scoped subtree snapshots**: When a `focusSelector` is provided, only process that subtree. Maps to Strategy 2.
- **Compound component hints**: Annotate complex widgets with sub-parts inline. Future work, not in this plan.

---

## Strategy 1: Annotate Form Boundaries in Tree Output

**Effort: Small | Impact: Immediate | PR: standalone**

### What changes

Modify `formatAccessibilityTree()` to wrap `form`/`search` nodes in prominent unicode boundary markers. Update the agent system prompt to explain these markers.

**Before:**
```yaml
- form "Login":
  - textbox "Email" [ref=e3]
  - textbox "Password" [ref=e4]
  - button "Sign in" [ref=e5]
```

**After:**
```yaml
━━ FORM: "Login" (login) ━━
  - textbox "Email" [ref=e3]
  - textbox "Password" [ref=e4]
  - button "Sign in" [ref=e5]
━━ END FORM ━━
```

### Files

| File | Change |
|------|--------|
| `packages/core/src/services/browser/llm-reasoning-agent.ts` | 1. Modify `formatAccessibilityTree()` (~line 396): when `node.role === 'form' \|\| node.role === 'search'`, emit `━━ FORM: "name" (purpose) ━━` header, recurse children indented, then emit `━━ END FORM ━━`. Infer purpose via simple heuristics (has password field → "login", has searchbox → "search", else use name or "form"). 2. Add `## Form Awareness` section to `AGENT_SYSTEM_PROMPT` explaining markers and instructing the LLM to prefer elements within the same form boundary. |
| `packages/core/test/services/browser/llm-reasoning-agent.test.ts` | Tests for `formatAccessibilityTree()` with form nodes (export the function or test indirectly via snapshot formatting). |

### Test cases

1. Named form emits `━━ FORM: "Login" (login) ━━` / `━━ END FORM ━━`
2. Unnamed form emits `━━ FORM (form) ━━` / `━━ END FORM ━━`
3. `search` role treated same as `form` role
4. Non-form landmarks (banner, nav, main) are NOT wrapped
5. Form purpose inference: password field → "login", searchbox → "search"
6. Nested content inside form preserves indentation
7. Form at deeper nesting levels gets correct indentation for its boundary lines

### Implementation notes

- `formatAccessibilityTree()` is currently a private function. Either export it for direct testing or add a thin wrapper.
- Reuse the purpose-inference pattern from `inferFormPurpose` in `page-context-extractor.ts` (lines 833-837) — look for password fields, search inputs in children.
- The unicode `━━` characters are chosen because they're visually distinct in monospace terminals and won't be confused with YAML syntax.

---

## Strategy 2: Form-Scoped Tree for Fill/Type Steps

**Effort: Medium | Impact: Big noise reduction | PR: after S1**

### What changes

When the agent or correction flow needs to reason about a form interaction, scope the accessibility tree to just that form's subtree instead of the full page.

### Files

| File | Change |
|------|--------|
| `packages/core/src/services/browser/accessibility-tree-analyzer.ts` | Add `scopeTreeToForm(tree, targetRole, targetName)`: walk tree to find the element matching `{role, name}`, then walk up to find enclosing `form`/`search` ancestor, return that subtree. Fail-open: returns full tree if no form ancestor found. |
| `packages/core/src/services/browser/llm-reasoning-agent.ts` | In agent loop: after `take_snapshot`, if the current goal context suggests a form interaction (previous action was `fill`, or page context shows a form matching the goal keywords), pass the scoped tree to `formatAccessibilityTree()` instead of the full tree. Include a note "Showing form context only. Use take_snapshot for full page." |
| `packages/cli/src/commands/scan-browser/verification-orchestrator.ts` | In `extractNearbyElementsFlat()`: strengthen form-preference from +0.3 bonus to hard-filter. If ≥2 candidates share the target's form landmark, exclude candidates from other forms entirely. Fall back to full list if <2 same-form candidates. |
| Tests | Unit tests for `scopeTreeToForm()` with various tree structures. Tests for the hard-filter behavior in extraction. |

### Design consideration

- Scoping must fail-open. If the form can't be found (element moved, no `<form>` tag in SPA), return the full tree.
- The agent should be able to "zoom out" — the scoped view includes a note about using `take_snapshot` for the full page if the scoped view is insufficient.
- The correction flow hard-filter has a fallback: if filtering to same-form produces <2 candidates, revert to full list with the existing +0.3 bonus.

---

## Strategy 3: Composite `fill_form` Action

**Effort: Large | Impact: Eliminates the problem class | PR: after S1+S2**

### What changes

Add `fill_form` to the step schema. The LLM emits one decision for an entire form. The executor handles individual field interactions deterministically.

**New step shape:**
```yaml
- action: fill_form
  target:
    role: form
    accessibleName: "Login"
  fields:
    - role: textbox
      accessibleName: "Email"
      value: "user@example.com"
    - role: textbox
      accessibleName: "Password"
      value: "secret123"
  submit:
    role: button
    accessibleName: "Sign in"
  reasoning: "Filling the login form with credentials"
```

### Files

| File | Change |
|------|--------|
| `packages/core/src/schemas/browser-agent-schema.ts` | Add `'fill_form'` to action enum. Add optional `fields: z.array(z.object({ role, accessibleName, value }))` and `submit: SemanticTargetSchema.optional()` to `CachedStepSchema`. |
| `packages/core/src/services/browser/playwright-step-executor.ts` | Add `fill_form` case: resolve form by semantic target, iterate `fields` array (find each element by role+name within the form, fill value), then click `submit` element. Return per-field success/failure for diagnostics. |
| `packages/core/src/services/browser/llm-reasoning-agent.ts` | Update system prompt with `fill_form` action description and example. Update decision parsing to handle `fields` and `submit` in the JSON response. |
| `packages/core/src/services/browser/page-context-extractor.ts` | Already extracts form fields + submit button via `extractFormsFromTree()`. Wire structured form info into the user prompt when forms are present, so the LLM has the data to emit `fill_form`. |
| `packages/cli/src/commands/scan-browser/verification-orchestrator.ts` | When a `fill_form` step fails, expand it into individual `fill` + `click` steps for per-field correction. |
| Tests | Schema validation tests, executor tests with mocked adapter, agent decision parsing tests. |

### Design considerations

- **Backward compatibility**: `fill_form` is additive. Existing `fill`/`click` steps continue working.
- **Partial fill**: `fields` only includes fields to fill — others left alone.
- **Dynamic forms**: Forms that reveal fields progressively can't use `fill_form`. The agent falls back to individual steps.
- **Healing**: When `fill_form` fails, expand to individual steps. The correction flow handles each field separately.
- **YAML cache**: `fill_form` uses semantic targets for each field (same as regular steps), so it survives DOM changes via the existing healing path.

---

## Implementation Order

```
PR 1: Strategy 1 (form boundary annotations)     ← can ship and test independently
PR 2: Strategy 2 (form-scoped tree)               ← builds on S1's form detection
PR 3: Strategy 3 (composite fill_form action)      ← biggest change, after S1+S2 validated
```

Each PR is independently shippable and testable. S2 and S3 don't need to wait for production validation of prior strategies — they can be developed on the same branch — but the code dependencies flow S1 → S2 → S3.

---

## Verification

For each strategy:
1. `pnpm build:packages`
2. `pnpm test` (all packages)
3. `pnpm lint && pnpm format:check`
4. Manual testing with `oculis scan-browser` on a page with multiple forms
