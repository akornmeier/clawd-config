# Plan: Oculis Studio — Collaborative Journey Builder

## Context

Oculis Studio is a hosted web application at `studio.oculis.dev` where users collaborate with an LLM to build accessibility test journeys through a chat interface and live cloud browser viewport. The user explicitly pivoted from a CLI-only approach: "the CLI greatly limits our audience of users. We want this to be approachable and simple to use."

A full design process produced 4 spec files (`specs/oculis-studio-{prd,clarification,ux-spec,build-prompts}.md`) with 17 self-contained build prompts. This plan organizes those prompts into phased, parallelizable work with team orchestration.

## Objective

Implement the complete Oculis Studio web application — from Nuxt 3 project scaffold through cloud browser sessions, chat-based journey building, and WCAG 2.1 AA accessibility polish. On completion, a user can sign in, enter a URL, build a 5-step journey through chat, and download a YAML file that replays via `oculis scan:browser --mode cached`.

## Problem Statement

QA engineers and accessibility leads struggle to create reliable accessibility test journeys because the autonomous CLI agent is slow (~5min for 8 steps), wastes time on LLM reasoning, and produces low-quality cached steps. Studio replaces this with a human-in-the-loop pattern: conversational, visual, and fast (~60s for 5 steps).

## Solution Approach

Three-layer architecture:
1. **Nuxt 3 web app** (`apps/studio`) — Landing, auth, dashboard, builder UI. Deploys to Vercel/CF Pages.
2. **Convex** (managed) — Real-time database for users, journeys, settings.
3. **Fly.io Session VMs** (`packages/session-service`) — Per-session cloud browsers with Chromium, WebSocket streaming, LLM proxy.

The session VM reuses existing CLI infrastructure (`PlaywrightMCPClient`, `createLLMAdapter()`, `parseSnapshotResponse()`, `buildSemanticTargetFromRef()`, `CachedStepSchema`) — no new browser control or LLM adapter code needed.

## Relevant Files

### Existing Files to Reuse

- `packages/cli/src/adapters/mcp-client.ts` — `PlaywrightMCPClient` for browser control on session VM
- `packages/cli/src/adapters/llm-factory.ts` — `createLLMAdapter()` multi-provider factory
- `packages/cli/src/adapters/snapshot-parser.ts` — `parseSnapshotResponse()`, `buildSemanticTargetFromRef()`, `findNodeByRef()`
- `packages/core/src/schemas/browser-agent-schema.ts` — `CachedStepSchema`, `CachedJourneySchema`, `SemanticTargetSchema`
- `packages/core/src/services/browser/llm-reasoning-agent.ts` — `AGENT_SYSTEM_PROMPT` as basis for Studio's adapted prompt
- `packages/cli/src/types/llm-options.ts` — `LLMProvider`, `LLMOptions`, `DEFAULT_MODELS`
- `packages/browser/src/assets/tokens.css` — Full Oculis design token system (copy into Studio)
- `packages/browser/src/assets/main.css` — Tailwind 4.x `@theme` directive pattern + NuxtUI `--ui-*` mapping
- `packages/browser/src/assets/fonts.css` — Fontsource variable font imports

### Monorepo Config to Modify

- `pnpm-workspace.yaml` — Add `apps/*` to workspace packages
- `turbo.json` — Add Convex `generate` task
- `package.json` (root) — Add `dev:studio` convenience script

### New Files to Create

**`apps/studio/`** — Nuxt 3 application:
- `nuxt.config.ts`, `package.json`, `tsconfig.json`
- `assets/tokens.css`, `assets/main.css`, `assets/fonts.css` (copied from browser extension)
- `layouts/default.vue` (collapsible sidebar)
- `pages/index.vue` (landing / chat prompt / builder — single page, multiple states)
- `pages/journeys.vue` (saved journeys list + detail)
- `components/builder/BrowserViewport.vue`
- `components/builder/ChatPanel.vue`
- `components/builder/StepList.vue`
- `components/settings/SettingsDrawer.vue`
- `components/onboarding/OnboardingSlides.vue`
- `composables/useStudioSession.ts` (WebSocket lifecycle)
- `composables/useCurrentUser.ts` (Clerk → Convex user)
- `server/api/sessions/create.post.ts` (Fly Machines provisioning)
- `server/api/sessions/[id]/stop.post.ts`
- `server/api/webhooks/clerk.post.ts` (user sync)
- `middleware/auth.ts`

**`apps/studio/convex/`** — Convex backend:
- `schema.ts` (users, journeys, settings tables)
- `users.ts` (getByClerkId, upsert)
- `journeys.ts` (list, get, create, update, remove)
- `settings.ts` (get, update)
- `http.ts` (Clerk webhook handler)

**`packages/session-service/`** — Cloud browser session VM:
- `package.json`, `tsconfig.json`, `Dockerfile`, `fly.toml`
- `src/index.ts` (entry point)
- `src/ws-server.ts` (WebSocket server + protocol handler)
- `src/session-manager.ts` (Chromium lifecycle + screenshot loop)
- `src/studio-llm-service.ts` (LLM wrapper with Studio system prompt)
- `src/cdp-highlighter.ts` (element highlighting via CDP overlay)
- `src/orchestrator.ts` (full message→snapshot→LLM→highlight→confirm→execute→record flow)
- `src/journey-saver.ts` (assemble YAML, validate against CachedJourneySchema)
- `src/health.ts` (HTTP health check)

## Implementation Phases

### Phase 0: Monorepo Infrastructure
Update workspace config, Turborepo, and create shared WebSocket protocol types. Everything else depends on this.

### Phase 1: Foundation + Auth (Build Prompts 1, 3, 4)
Scaffold the Nuxt 3 project, copy design tokens, configure Convex schema, integrate Clerk auth, build landing page.

### Phase 2: Layout + Static Pages (Build Prompts 2, 5, 6, 15, 16)
Build the layout shell with collapsible sidebar, chat prompt entry point, journeys page, settings drawer, onboarding slides. All frontend-only, no session service dependency.

### Phase 3: Session Service (Build Prompts 7, 8) — PARALLEL with Phase 2
Build the cloud browser service package: WebSocket server, Chromium lifecycle, screenshot streaming, Fly.io config, and Nuxt API provisioning routes.

### Phase 4: Builder UI Components (Build Prompts 9, 10, 11, 13)
Build the three builder panels (viewport, chat, step list) as components with mock data. Element highlighting composable.

### Phase 5: LLM + Orchestration (Build Prompts 12, 14)
Wire everything together: StudioLLMService, system prompt, the full orchestration state machine, save flow, and client-side composable connecting WebSocket messages to Vue state.

### Phase 6: Accessibility Polish (Build Prompt 17)
WCAG 2.1 AA audit with axe-core, keyboard navigation, reduced motion, ARIA live regions, color contrast verification.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members.

### Team Members

- Builder
  - Name: infra-builder
  - Role: Monorepo config changes, auth wiring, Dockerfile/Fly.io config
  - Agent Type: builder
  - Resume: true

- Builder
  - Name: nuxt-frontend
  - Role: All Nuxt 3 pages, Vue components, NuxtUI integration, design tokens, composables
  - Agent Type: nuxt-ui-builder
  - Resume: true

- Builder
  - Name: convex-backend
  - Role: Convex schema, mutations, queries, webhook handlers
  - Agent Type: tdd-builder
  - Resume: true

- Builder
  - Name: session-service
  - Role: Session service package — WebSocket server, browser manager, screenshot stream, health check
  - Agent Type: tdd-builder
  - Resume: true

- Builder
  - Name: llm-orchestrator
  - Role: StudioLLMService, system prompt, orchestrator state machine, journey saver
  - Agent Type: tdd-builder
  - Resume: true

- Builder
  - Name: a11y-auditor
  - Role: WCAG 2.1 AA audit, keyboard nav, reduced motion, ARIA, color contrast
  - Agent Type: axe-specialist
  - Resume: true

- Validator
  - Name: final-validator
  - Role: Full build, test, lint, format validation across all packages
  - Agent Type: ts-validator
  - Resume: false

## Step by Step Tasks

### 1. Update monorepo workspace config
- **Task ID**: workspace-config
- **Depends On**: none
- **Assigned To**: infra-builder
- **Agent Type**: builder
- **Parallel**: true (with task 2)
- Add `apps/*` to `pnpm-workspace.yaml`
- Add `dev:studio` script to root `package.json`
- Update `turbo.json` if needed for Convex generate task

### 2. Create shared WebSocket protocol types
- **Task ID**: ws-protocol-types
- **Depends On**: none
- **Assigned To**: convex-backend
- **Agent Type**: tdd-builder
- **Parallel**: true (with task 1)
- Add `StudioClientMessage` and `StudioServerMessage` discriminated union types to `packages/shared/src/`
- Add Zod schemas for all message types
- Export from `@oculis/shared`

### 3. Scaffold Nuxt 3 project
- **Task ID**: nuxt-scaffold
- **Depends On**: workspace-config
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: false
- Create `apps/studio` with Nuxt 3, NuxtUI, Tailwind CSS 4.x, TypeScript
- Configure `nuxt.config.ts` with modules
- Copy design tokens from `packages/browser/src/assets/` (tokens.css, main.css, fonts.css)
- Install fonts: Plus Jakarta Sans, Inter, JetBrains Mono, OpenDyslexic
- Map Oculis tokens to NuxtUI `--ui-*` CSS variables
- Dark mode default
- Verify the project builds and dev server starts

### 4. Configure Convex schema and initial mutations
- **Task ID**: convex-schema
- **Depends On**: nuxt-scaffold
- **Assigned To**: convex-backend
- **Agent Type**: tdd-builder
- **Parallel**: true (with task 5)
- Create `apps/studio/convex/schema.ts` with users, journeys, settings tables
- Create `convex/users.ts` (getByClerkId, upsert mutations)
- Create `convex/journeys.ts` (list, get, create, update, remove)
- Create `convex/settings.ts` (get, update)
- Add Convex Nuxt plugin

### 5. Integrate Clerk auth + landing page
- **Task ID**: clerk-auth
- **Depends On**: nuxt-scaffold
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with task 4)
- Install and configure `nuxt-clerk` module
- Create auth middleware protecting `/journeys` routes
- Create Clerk webhook endpoint for user sync (`server/api/webhooks/clerk.post.ts`)
- Build landing page: minimal hero with Oculis logo, headline, "Get Started" CTA
- Redirect authenticated users past landing to chat prompt
- Create `useCurrentUser` composable (Clerk → Convex user lookup)

### 6. Build layout shell with collapsible sidebar
- **Task ID**: layout-shell
- **Depends On**: clerk-auth
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: false
- Create `layouts/default.vue` with collapsible sidebar (64px collapsed, 200px expanded)
- Sidebar items: Home (chat bubble icon), Journeys (folder icon), Settings (gear icon)
- Collapse state in localStorage, smooth animation, keyboard shortcut Cmd+B
- Tooltips on collapsed items
- Active item highlighting

### 7. Build chat prompt entry point
- **Task ID**: chat-prompt
- **Depends On**: layout-shell
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 8, 9, 10)
- Centered full-screen URL input: "Enter a URL to start building..."
- URL validation (auto-prefix https://)
- Loading state with Ora-style spinner
- CSS transition to builder layout on session start
- The chat input repositions from center to bottom of chat panel

### 8. Build onboarding slides
- **Task ID**: onboarding-slides
- **Depends On**: layout-shell
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 7, 9, 10)
- 3 full-screen slides with CSS animations (Remotion deferred to later)
- Slide navigation: arrows, dots, keyboard (Left/Right, Escape to skip)
- Skip link always visible
- Alt text on every visual
- localStorage flag `oculis_onboarding_complete` to show once
- Reduced motion fallback: static illustrations

### 9. Build journeys page
- **Task ID**: journeys-page
- **Depends On**: layout-shell, convex-schema
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 7, 8, 10)
- Journey list from Convex real-time query
- Journey cards: name, URL, step count, relative time
- Detail view: step list, Download YAML button, Continue Building button, Delete with confirmation
- Empty state with guidance

### 10. Build settings drawer
- **Task ID**: settings-drawer
- **Depends On**: layout-shell, convex-schema
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 7, 8, 9)
- NuxtUI USlideover from right edge
- LLM provider toggle (Default / Custom) + provider dropdown + API key input
- Chat font selector (Mono, Sans, System, Dyslexic) with live preview
- Theme toggle (Dark/Light)
- Auto-save to Convex (debounced 500ms)
- API key never displayed in plaintext after entry

### 11. Scaffold session-service package
- **Task ID**: session-service-scaffold
- **Depends On**: ws-protocol-types
- **Assigned To**: session-service
- **Agent Type**: tdd-builder
- **Parallel**: true (runs alongside Phase 2 frontend tasks)
- Create `packages/session-service/` with package.json, tsconfig.json
- Dependencies: `@oculis/cli`, `@oculis/core`, `@oculis/shared`, `ws`, `playwright`
- Entry point `src/index.ts`
- Health check endpoint `src/health.ts`

### 12. Build WebSocket server and protocol handler
- **Task ID**: ws-server
- **Depends On**: session-service-scaffold
- **Assigned To**: session-service
- **Agent Type**: tdd-builder
- **Parallel**: false
- `src/ws-server.ts`: WebSocket server using `ws`
- JWT authentication on connection
- Parse incoming StudioClientMessage, dispatch to handler
- Emit StudioServerMessage (binary for screenshots, JSON text for rest)
- Idle timeout tracking (10min), max duration (30min)

### 13. Build browser session manager with screenshot loop
- **Task ID**: browser-manager
- **Depends On**: ws-server
- **Assigned To**: session-service
- **Agent Type**: tdd-builder
- **Parallel**: false
- `src/session-manager.ts`: Wraps PlaywrightMCPClient
- Launch Chromium, navigate to URL
- Screenshot loop: CDP Page.captureScreenshot → JPEG → binary WS frame
- Adaptive frame rate: 4fps active, 1fps idle
- Frame deduplication via hash comparison
- Graceful shutdown: close browser, close WS, exit process

### 14. Create Dockerfile and Fly.io config
- **Task ID**: fly-config
- **Depends On**: session-service-scaffold
- **Assigned To**: infra-builder
- **Agent Type**: builder
- **Parallel**: true (with tasks 12, 13)
- `Dockerfile`: Multi-stage build with `mcr.microsoft.com/playwright:v1.50.0-noble` base
- `fly.toml`: Machine config, auto-stop after 35min
- Document local dev mode (local Playwright, no Fly VM)

### 15. Build session provisioning API routes
- **Task ID**: session-api
- **Depends On**: nuxt-scaffold, session-service-scaffold
- **Assigned To**: session-service
- **Agent Type**: tdd-builder
- **Parallel**: true (with tasks 12, 13)
- `server/api/sessions/create.post.ts`: Clerk-authenticated, reads user LLM settings from Convex, calls Fly Machines API, generates JWT, returns {machineId, wsUrl, token}
- `server/api/sessions/[id]/stop.post.ts`: Stops Fly Machine
- Rate limit: 1 concurrent session per user

### 16. Build browser viewport component
- **Task ID**: browser-viewport
- **Depends On**: layout-shell
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 17, 18)
- `components/builder/BrowserViewport.vue`
- Receives binary WS frames, renders via `<img>` with blob URLs
- Revoke previous blob URL on each new frame
- Maintain aspect ratio, center if wider
- Resizable divider between viewport and chat (drag + keyboard arrows)
- Min widths: 300px viewport, 300px chat
- Persist split ratio in localStorage
- View-only: pointer-events: none on img, cursor: default
- `role="img"`, dynamic `aria-label`

### 17. Build chat panel component
- **Task ID**: chat-panel
- **Depends On**: layout-shell
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 16, 18)
- `components/builder/ChatPanel.vue`
- Message types: user (right-aligned), assistant (left-aligned), system (centered, muted)
- Streaming text: reactive string appending tokens from assistant_chunk
- Ora-style spinner while thinking (sage green), reduced motion fallback
- Numbered options as inline text, not buttons
- Chat input: textarea, Enter to send, Shift+Enter for newline
- Configurable font from user settings
- Auto-scroll, pause if user scrolled up
- `role="log"`, `aria-live="polite"`

### 18. Build step list component
- **Task ID**: step-list
- **Depends On**: layout-shell
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: true (with tasks 16, 17)
- `components/builder/StepList.vue`
- Frameless list, fixed max-height 200px, overflow scroll
- CSS gradient mask at bottom (fade effect)
- Step items: action badge pill + concise description
- Click step → NuxtUI UPopover with full details
- Step count indicator above list
- Hidden scrollbar, keyboard navigable (Tab, arrows, Enter for popover)

### 19. Build StudioLLMService
- **Task ID**: llm-service
- **Depends On**: browser-manager
- **Assigned To**: llm-orchestrator
- **Agent Type**: tdd-builder
- **Parallel**: true (with task 20)
- `packages/session-service/src/studio-llm-service.ts`
- Wraps `createLLMAdapter()` from @oculis/cli
- Dual provider: user's BYOK key or Oculis default
- Streaming: emit assistant_chunk messages as tokens arrive
- Single LLM call per user message, no iteration loop
- Context: accessibility tree + current instruction + step summary (small window)

### 20. Build Studio system prompt
- **Task ID**: system-prompt
- **Depends On**: browser-manager
- **Assigned To**: llm-orchestrator
- **Agent Type**: tdd-builder
- **Parallel**: true (with task 19)
- `packages/session-service/src/prompts/studio-system-prompt.ts`
- Adapted from CLI agent's AGENT_SYSTEM_PROMPT for collaborative mode
- One action at a time, structured JSON output (action, target ref, value, reasoning)
- Confirmation detection: "yes/1/go ahead" = confirm, "no/2/skip" = reject
- Clarification with numbered options when ambiguous
- Never guess user-specific values

### 21. Build CDP element highlighter
- **Task ID**: cdp-highlighter
- **Depends On**: browser-manager
- **Assigned To**: session-service
- **Agent Type**: tdd-builder
- **Parallel**: true (with tasks 19, 20)
- `packages/session-service/src/cdp-highlighter.ts`
- Resolve ref (e.g. `e210`) to DOM nodeId via browser_evaluate
- Call CDP `Overlay.highlightNode` with amber config
- Auto-clear after 10s or on confirm/reject
- Bump screenshot rate to 4fps while highlight active
- Graceful fallback if element not found

### 22. Build journey builder orchestrator
- **Task ID**: orchestrator
- **Depends On**: llm-service, system-prompt, cdp-highlighter
- **Assigned To**: llm-orchestrator
- **Agent Type**: tdd-builder
- **Parallel**: false
- `packages/session-service/src/orchestrator.ts`
- Full flow: user_message → snapshot via MCP → parse → LLM call → stream response → propose_action → highlight → wait for confirm → execute via MCP → build CachedStep → validate against CachedStepSchema → step_recorded
- Uses `buildSemanticTargetFromRef()` for durable semantic targets
- Undo: remove last step, chat confirmation
- Save: assemble CachedJourney YAML, validate against CachedJourneySchema, send journey_saved

### 23. Wire client-side orchestration
- **Task ID**: client-orchestration
- **Depends On**: browser-viewport, chat-panel, step-list, orchestrator
- **Assigned To**: nuxt-frontend
- **Agent Type**: nuxt-ui-builder
- **Parallel**: false
- `composables/useStudioSession.ts`: WebSocket lifecycle, message routing
- Route screenshot frames → viewport, assistant_chunk → chat, propose_action → chat + highlight, step_recorded → step list
- Manage confirm/reject flow from chat input
- Connect chat prompt transition → builder layout
- `composables/useJourneySaver.ts`: On journey_saved, store YAML to Convex

### 24. WCAG 2.1 AA audit
- **Task ID**: a11y-audit
- **Depends On**: client-orchestration
- **Assigned To**: a11y-auditor
- **Agent Type**: axe-specialist
- **Parallel**: false
- Run axe-core against all pages
- Fix critical and serious violations
- Keyboard navigation: all elements reachable via Tab, visible focus rings
- Focus management: builder transition, settings drawer open/close
- Reduced motion: all animations respect prefers-reduced-motion
- ARIA: live regions on chat (polite), step list (polite), viewport (off)
- Color contrast: verify 4.5:1 ratio for all text/background combos
- Test at 200% zoom

### 25. Final validation
- **Task ID**: validate-all
- **Depends On**: a11y-audit
- **Assigned To**: final-validator
- **Agent Type**: ts-validator
- **Parallel**: false
- `pnpm build` (all packages including apps/studio and packages/session-service)
- `pnpm test` (all tests pass)
- `pnpm lint` (no lint errors)
- `pnpm format:check` (formatting OK)
- Verify Studio dev server starts cleanly
- Verify session-service builds and Docker image creates

## Acceptance Criteria

- Nuxt 3 app at `apps/studio` builds and serves with NuxtUI + Oculis design tokens
- Clerk auth works: sign in with GitHub/Google, user synced to Convex
- Collapsible sidebar navigates between Home, Journeys, Settings
- Chat prompt accepts URL, provisions cloud browser session via Fly Machines API
- Browser viewport renders live screenshot stream from session VM WebSocket
- Chat panel streams LLM responses with numbered options (1. Yes | 2. No)
- Confirming an action executes it via PlaywrightMCPClient and records a CachedStep
- Step list shows recorded steps with action badges, clickable for detail popovers
- Element highlighting visible in screenshot stream (amber CDP overlay)
- "save" in chat produces CachedJourney YAML stored in Convex
- YAML download works and validates against CachedJourneySchema
- "Continue Building" on a saved journey provisions new session with existing steps
- Settings drawer configures LLM provider (Default/BYOK), chat font, theme
- Onboarding slides shown once for new users
- All pages pass WCAG 2.1 AA (axe-core, keyboard nav, reduced motion, color contrast)
- All existing monorepo tests continue to pass

## Validation Commands

```bash
# Build all packages + apps
pnpm build

# Run all tests
pnpm test

# Lint
pnpm lint

# Format check
pnpm format:check

# Verify Studio dev server
pnpm --filter studio dev

# Verify session-service builds
pnpm --filter @oculis/session-service build

# Verify Docker image
cd packages/session-service && docker build -t oculis-session .
```

## Notes

- **External services**: Clerk and Convex require API keys configured in environment variables. Local development needs `.env` files with `CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `CONVEX_URL`, `CONVEX_DEPLOY_KEY`.
- **Fly.io**: Session provisioning requires `FLY_API_TOKEN`. For local dev, use a local Playwright instance instead of Fly VM.
- **Design token drift**: Tokens are copied from browser extension, not imported. A future `@oculis/design-tokens` shared package could prevent drift.
- **Remotion**: Deferred to a later phase. Onboarding uses CSS animations with static fallbacks.
- **Phase 1 scope**: No team/org management, billing, cloud replay, journey editing after save, or multi-tab recording.
- **Suggested commit prefix**: `feat(studio): ...` for the Nuxt app, `feat(session-service): ...` for the cloud browser package.
