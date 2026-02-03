# Browser Extension PRD-Lite

## Problem Statement

Pocket shutdown (July 2025) creates urgency. Users need frictionless article saving without context-switching. Extension is P2 Critical - primary capture mechanism for ongoing use.

**User Need**: "Save articles instantly while browsing, without losing reading flow."

---

## User Personas

| Persona | Behavior | Primary Need |
|---------|----------|--------------|
| Power Reader | 10+ articles/day, heavy tags | Quick save + keyboard shortcuts |
| Casual Saver | 2-3/week, minimal org | One-click, zero friction |
| Researcher | Systematic collection | Folder/tag organization, offline |

---

## Core User Flows

### Primary: Popup Save
```
Click icon → Popup (300x400px) → Shows metadata preview →
Optional: select tags → Click "Save" → Success (auto-close 1.5s)
```

### Secondary: Context Menu
```
Right-click → "Save to Stache" → Toast confirmation → Auto-dismiss
```

### States
- Loading metadata | Ready | Saving | Success | Already saved | Offline | Error | Unauthenticated

### Success State Branding
Animated Stache logo with rotating taglines:
- "Nice stache"
- "The stache grows"
- "Stached for later"
- "Another one for the stache"
- "Stache it away"

Logo animation: Whimsical bounce/wiggle on success (CSS keyframes, ~1s)

---

## Feature Requirements

### Must-Have (MVP)

| ID | Feature |
|----|---------|
| M1 | One-click save with metadata preview |
| M2 | Searchable tag multi-select |
| M3 | Inline tag creation |
| M4 | Context menu "Save to Stache" |
| M5 | Clerk auth (web app redirect) |
| M6 | Offline queue (IndexedDB) |
| M7 | Chrome Web Store submission |
| M8 | Firefox Add-ons submission |
| M9 | Keyboard shortcut (Cmd/Ctrl+Shift+S) |
| M10 | Settings panel (auto-close toggle) |
| M11 | "Already saved" detection with tag merge |
| M12 | Animated success state (logo + rotating taglines) |
| M13 | Clipboard bridge (grant paste permission to web app) |
| M14 | Deep link to saved article in success state |

### Nice-to-Have (Post-MVP)

| ID | Feature |
|----|---------|
| N1 | Folder selection |
| N2 | Library tab in popup |
| N3 | Content extraction in extension (Readability.js) |
| N4 | Dark mode (system preference default) |
| N5 | Safari support |
| N6 | Sound effects (subtle save confirmation sfx) |
| N7 | Save streak counter (gamification) |
| N8 | Easter eggs for power users |

---

## Technical Constraints

| Constraint | Implication |
|------------|-------------|
| **WXT framework** | Confirmed. Single codebase for Chrome + Firefox, Vite-based, TypeScript, Manifest V3 |
| 300x400px popup | Fixed dimensions |
| `chrome.storage.session` | Tokens persist during session only |
| Convex in service worker | Background save mutations |
| `activeTab` permission | Minimal permission scope |

### Permissions
```json
{
  "permissions": ["activeTab", "storage", "contextMenus", "clipboardRead", "clipboardWrite"],
  "host_permissions": ["https://*.stache.app/*"]
}
```
Note: Clipboard permissions enable paste-to-save in web app without repeated permission prompts.

---

## Design Philosophy

**Tight web app coupling**: Extension is a companion to the web app, not standalone.
- Share auth state seamlessly (Clerk tokens)
- Clipboard permissions: Extension can grant clipboard access for web app paste-to-save
- Deep links: Success state links directly to article in web app
- Consistent branding and component styling

**Polish over utility**: Since core function is simple (save URL), invest in delightful touches:
- Whimsical animations (logo bounce, smooth transitions)
- Personality through copy (taglines, micro-interactions)
- Surprise elements (Easter eggs for power users?)
- Sound feedback option (subtle save confirmation sfx)

---

## Non-Goals

- Reading in extension (save-only)
- Full library management (no delete/archive)
- Content script on all sites
- Mobile browser support
- Safari (post-MVP)

---

## Architecture

```
apps/extension/
├── src/
│   ├── entrypoints/
│   │   ├── popup/           # React popup UI
│   │   ├── background.ts    # Service worker (Convex, offline queue)
│   │   └── content.ts       # Optional content script
│   ├── lib/
│   │   ├── convex.ts        # Client setup
│   │   ├── auth.ts          # Clerk tokens
│   │   ├── offline-queue.ts # IndexedDB queue
│   │   └── metadata.ts      # Page metadata
│   └── components/          # ShadCN subset
├── wxt.config.ts
└── package.json
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Save success rate | >95% |
| Time to save | <2s |
| Offline queue recovery | 100% |
| Store rating | >4.0 stars |

---

## Decisions

### Product Decisions (resolved)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Duplicate URL handling | **Update existing** - merge new tags, update metadata |
| 2 | Post-save behavior | **User preference** - settings toggle, default auto-close |
| 3 | Content extraction | **Backend extraction** - extension sends URL, Convex parses |
| 4 | Tag/folder defaults | Cache with 5min TTL, background refresh |

### Technical Decisions

| # | Decision | Choice |
|---|----------|--------|
| 5 | Offline queue | IndexedDB (larger capacity) |
| 6 | Retry logic | Exponential backoff (1s, 2s, 4s, 8s, max 5) |
| 7 | Metadata fallbacks | Graceful degrade (title=document.title) |

---

## Key Files to Integrate With

- `packages/convex/convex/articles.ts` - `articles.create` mutation
- `packages/convex/convex/parseArticle.ts` - `parseUrl` action for metadata
- `apps/web/src/components/features/dialogs/SaveArticleDialog.tsx` - Reference UI patterns

---

## Verification

1. Extension loads in Chrome/Firefox dev mode
2. Auth flow: sign in → token stored → saves work
3. Save flow: click → metadata preview → save → success
4. Offline: airplane mode → save → queue shows → reconnect → syncs
5. Context menu: right-click → save → toast
6. Duplicate: save same URL twice → expected behavior
