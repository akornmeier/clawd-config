# Clipboard URL Detection for Article Saving

## Goal
Reduce friction + improve discovery for saving articles via clipboard URL detection.

## User Experience

### Toast on App Focus
1. App reads clipboard on mount + window focus
2. Valid URL detected → fetch light metadata (title, favicon)
3. Show toast (bottom-right):
   ```
   ┌──────────────────────────────────────────────────┐
   │ 🌐  Why AI Needs Better Memory Systems           │
   │     techcrunch.com                    [Save] [✕] │
   └──────────────────────────────────────────────────┘
   ```
4. "Save" → opens SaveArticleDialog pre-filled
5. Dismiss → URL added to session blocklist (no re-prompt until refresh)

### Dialog Pre-fill
- SaveArticleDialog reads clipboard on open
- Pre-fills URL field if valid URL found

## Implementation

### New Files
- `hooks/useClipboardUrl.ts` - clipboard read, validation, blocklist, metadata fetch
- `components/features/articles/ClipboardArticleToast.tsx` - toast UI

### Modified Files
- `routes/app/articles.index.tsx` - mount hook, render toast
- `components/features/articles/SaveArticleDialog.tsx` - pre-fill from clipboard

### URL Validation (fail-fast)
```ts
function isLikelyUrl(text: string): boolean {
  if (text.length > 2048) return false
  if (!/^https?:\/\//i.test(text)) return false
  if (/[\n\t]/.test(text)) return false
  try { new URL(text); return true } catch { return false }
}
```

### Toast Behavior
- Slide-up animation (motion/react)
- Auto-dismiss: 8s, pause on hover
- Loading: show URL + skeleton title, populate when fetch completes
- Fallback: URL-only if fetch fails/slow (3s timeout)

### Session Blocklist
- React context, `Set<string>` of dismissed URLs
- Clears on page refresh

### Edge Cases
- URL already saved → don't show toast (check via query)
- Skip localhost, file://, data:, known non-article domains
- Permission denied → silent no-op
- Only show on main articles list (not reading view)

## Testing

### Vitest
- `isLikelyUrl` validation logic
- `useClipboardUrl` hook behavior
- Metadata caching

### Storybook
- Toast states: loading, with-title, url-only
- Dismiss + auto-dismiss behavior
- Save button interaction

### Playwright
- Toast appears with mocked clipboard URL
- Dismiss prevents re-show for same URL
- Save opens dialog pre-filled
- Dialog pre-fills from clipboard

### Manual Verification
1. Copy URL → open app → toast with title + favicon
2. Dismiss → refocus → no toast for same URL
3. Refresh → refocus → toast reappears
4. Copy non-URL → no toast
5. Deny permission → no errors
6. Save via toast → article in list

## Unresolved Questions
None - all requirements clarified during brainstorming.
