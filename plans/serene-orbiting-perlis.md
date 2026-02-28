# Session Resume & "Session Ended" Action Card

## Context

When a session times out, the user sees two plain-text system messages ("Session closed due to inactivity" and "Session disconnected.") with no way to resume. This is a poor experience — especially for screen reader users who get no structured announcement. We need a rich action card that clearly communicates the session ended, shows a session key, and provides a one-click resume button.

**V1 scope**: "Resume" creates a fresh session at the same URL (not true reconnection to an existing browser). The code is structured so true persistence-based resume can be added later.

## Changes

### 1. Protocol — add `session_ended` message type

**File**: `packages/shared/src/studio-protocol.ts`

Add `SessionEndedSchema` to the `StudioServerMessageSchema` union:

```typescript
const SessionEndedSchema = z.object({
  type: z.literal('session_ended'),
  sessionId: z.string(),
  reason: z.enum(['idle_timeout', 'max_duration', 'user_ended', 'error']),
  message: z.string(),
  url: z.string().optional(),
});
```

### 2. Backend — generate session ID, send `session_ended`

**File**: `apps/studio/server/api/sessions/create.post.ts`
- Generate `sessionId` via `crypto.randomUUID()`
- Embed in JWT payload: `jwt.sign({ sub: 'session', url, sessionId }, ...)`
- Return `sessionId` in the HTTP response

**File**: `packages/session-service/src/ws-server.ts`
- Extract `sessionId` and `url` from decoded JWT payload on connection
- Store on `WsServerHandle` for external access
- **Idle timeout handler** (line ~54): send `{ type: 'session_ended', sessionId, reason: 'idle_timeout', message, url }` instead of the current `status` message
- **Max duration handler** (line ~125): same pattern with `reason: 'max_duration'`

### 3. Frontend types — extend `ChatMessage`

**File**: `apps/studio/components/builder/ChatPanel.vue` (lines 21-34)

Add `SessionEndedData` interface and optional field on `ChatMessage`:

```typescript
export interface SessionEndedData {
  sessionId: string;
  reason: 'idle_timeout' | 'max_duration' | 'user_ended' | 'error';
  url?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  proposal?: ProposalData;
  sessionEnded?: SessionEndedData;  // NEW
}
```

### 4. Composable — handle `session_ended`, add `resume()`

**File**: `apps/studio/composables/useStudioSession.ts`

- Add `sessionId` and `sessionUrl` refs
- Capture `sessionId` from HTTP response in `connect()`
- Add `session_ended` case to `handleMessage()` switch — creates a message with `sessionEnded` data
- **Change `disconnect()`**: do NOT clear `messages`/`steps` (so the card stays visible); insert a `session_ended` message for user-initiated disconnects
- Add `resetState()` helper (clears messages, steps, IDs) — called at the start of `connect()`
- WS `close` handler: only add disconnect message if no `session_ended` message already exists (avoids duplicates)
- New `resume()` method: calls `connect()` with the stored `sessionUrl`
- Expose `sessionId`, `sessionUrl`, `resume` in the public interface

### 5. New component — `SessionEndedCard.vue`

**File**: `apps/studio/components/builder/SessionEndedCard.vue` (NEW)

Follows DecisionCard patterns exactly (BEM naming, design tokens, entry animation).

| Element | Detail |
|---------|--------|
| Container | `role="alert"`, amber accent border (`--oculis-serious`) |
| Header | Icon (clock/timer/stop/alert per reason) + "Session Ended" title |
| Message | Reason text from server |
| Session ID | `<code>` element + copy-to-clipboard button |
| Actions | "Resume Session" (primary, auto-focused) + "New Session" (ghost) |
| A11y | `role="alert"` for immediate SR announcement, descriptive `aria-label` on all buttons |

**Props**: `sessionId`, `reason`, `message`, `url?`
**Emits**: `resume`, `new-session`

### 6. ChatMessages — add `session-ended` slot

**File**: `apps/studio/components/builder/ChatMessages.vue`

In the `v-for` rendering, add a check for `msg.sessionEnded` before falling through to regular system message rendering. Uses a named `#session-ended` slot (same pattern as the default slot for DecisionCard).

### 7. Builder page — wire resume flow

**File**: `apps/studio/pages/builder.vue`

- Add `handleResume()` — calls `session.resume()`
- Add `handleNewSession()` — resets `submittedUrl`/`urlInput`, transitions to idle
- Change `handleEndSession()` — calls `session.disconnect()` but does NOT clear `submittedUrl`
- Wire `SessionEndedCard` into the `#session-ended` slot of `ChatMessages`

## Implementation order

1. `packages/shared/src/studio-protocol.ts` — new schema
2. `apps/studio/server/api/sessions/create.post.ts` — sessionId generation
3. `packages/session-service/src/ws-server.ts` — extract sessionId, send `session_ended`
4. Build: `pnpm build:packages`
5. `apps/studio/components/builder/ChatPanel.vue` — type extensions
6. `apps/studio/composables/useStudioSession.ts` — composable changes
7. `apps/studio/components/builder/SessionEndedCard.vue` — new component
8. `apps/studio/components/builder/ChatMessages.vue` — add slot
9. `apps/studio/pages/builder.vue` — wire everything

## Verification

1. `pnpm build:packages` — all packages compile
2. `pnpm test` — existing tests pass + new tests for:
   - `session_ended` schema parsing in shared package
   - WS server sends `session_ended` on idle timeout / max duration (ws-server.test.ts)
   - Studio system prompt tests still pass (studio-system-prompt.test.ts)
3. `pnpm lint && pnpm format` — clean
4. Manual: connect to a session, let it timeout → card appears with session ID and Resume button → click Resume → new session starts at the same URL
