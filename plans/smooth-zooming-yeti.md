# Plan: Integrate Playwright MCP into Session-Service for Ref-Based Targeting

> **Team-orchestrated plan saved to**: `specs/integrate-mcp-session-service.md`
> Use `/build specs/integrate-mcp-session-service.md` to execute with team orchestration.

## Context

The session-service's `PlaywrightSnapshotAdapter` uses unreliable `getByRole()` targeting. The CLI already solved this with `@playwright/mcp` ref-based targeting. This plan aligns the session-service with the CLI's proven approach by sharing `BrowserContext` via `createConnection(config, contextGetter)`.

## Verification

1. `pnpm build:packages` — compilation succeeds
2. `pnpm test` — all tests pass (shared, CLI, session-service)
3. `pnpm lint && pnpm format` — clean
