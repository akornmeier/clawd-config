# Plan: Session Service Entry Point

## Context

The session-service package (`packages/session-service/`) is a library that exports building blocks (WS server, SessionManager, Orchestrator, etc.) but has **no runnable entry point**. The Studio builder connects to `ws://localhost:8080` expecting a live session service, resulting in "Connection error" when it's not running.

We need to create a `main.ts` that wires all the adapters together and starts a WebSocket server that the Studio can connect to.

## Implementation

### 1. Add dependencies to `packages/session-service/package.json`

Add:
- `playwright` (browser control, screenshots, CDP, accessibility tree)
- `@anthropic-ai/sdk` (LLM streaming)

### 2. Create `src/adapters/playwright-browser-adapter.ts`

Implements `BrowserAdapter` interface using Playwright:
- `launch(url)` — launch chromium, create page, navigate to URL
- `captureScreenshot()` — `page.screenshot({ type: 'png' })`
- `close()` — close browser
- Exposes `page` and `browser` for use by other adapters

### 3. Create `src/adapters/playwright-snapshot-adapter.ts`

Implements `SnapshotAdapter` interface:
- `getAccessibilityTree()` — use `page.accessibility.snapshot()` to build a text tree with refs
- `executeAction(action, ref, value?)` — find element by ref, execute click/fill/select etc.

### 4. Create `src/adapters/playwright-cdp-adapter.ts`

Implements `CDPAdapter` interface:
- Get CDP session from Playwright page: `page.context().newCDPSession(page)`
- `send(method, params)` — forward to CDP session

### 5. Create `src/adapters/anthropic-llm-adapter.ts`

Implements `LLMAdapter` interface:
- Uses `@anthropic-ai/sdk` with `ANTHROPIC_API_KEY` env var
- `stream(messages, systemPrompt)` — async generator yielding text chunks from `client.messages.stream()`
- Model: `claude-sonnet-4-5-20250929` (fast, capable)

### 6. Create `src/main.ts` — the runnable entry point

Flow on startup:
1. Read env vars: `JWT_SECRET`, `SESSION_PORT`, `ANTHROPIC_API_KEY`
2. Start WS server on `SESSION_PORT` (default 8080)
3. Start health server on 8081

Flow on client connect:
1. WS server validates JWT, extracts `url` from token payload
2. Launch Playwright browser, navigate to URL
3. Wire up all adapters → SessionManager → Orchestrator
4. Start screenshot loop
5. Route incoming messages to `orchestrator.handleMessage()`

Flow on client disconnect:
1. Stop screenshot loop
2. Close browser
3. Reset state, ready for next connection

### 7. Update `tsup.config.ts`

Add `src/main.ts` as a second entry point so it gets compiled to `dist/main.js`.

### 8. Update `package.json` scripts

- Change `"start"` script from `node dist/index.js` to `node dist/main.js`
- Add `"dev:start"` script: `tsup && node dist/main.js` for quick local dev

### 9. Update `.env.sample` in studio

Add `ANTHROPIC_API_KEY=sk-ant-...` entry.

### 10. Modify `ws-server.ts` — expose decoded JWT payload

Small change: add optional `onConnection?: (payload: Record<string, unknown>) => void` to `WsServerOptions`. Call it in the upgrade handler after JWT verification so main.ts can extract the URL from the token.

## Files to Create
- `packages/session-service/src/adapters/playwright-browser-adapter.ts`
- `packages/session-service/src/adapters/playwright-snapshot-adapter.ts`
- `packages/session-service/src/adapters/playwright-cdp-adapter.ts`
- `packages/session-service/src/adapters/anthropic-llm-adapter.ts`
- `packages/session-service/src/main.ts`

## Files to Modify
- `packages/session-service/package.json` (add deps)
- `packages/session-service/tsup.config.ts` (add main.ts entry)
- `packages/session-service/src/ws-server.ts` (add onConnection callback)
- `apps/studio/.env.sample` (add ANTHROPIC_API_KEY)

## Verification

1. Build: `pnpm --filter @oculis/session-service build`
2. Start session service: `node packages/session-service/dist/main.js`
3. Start studio: `pnpm dev:studio`
4. Open browser → enter URL in builder → verify screenshot stream appears
5. Send a chat message → verify LLM response streams back
6. Run existing tests: `pnpm --filter @oculis/session-service test`
