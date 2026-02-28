# Plan: Wire Journey Persistence (localStorage + Auto-download)

## Context

When a user clicks "Complete Journey", the server generates YAML and sends a `journey_saved` message with `{ name, yamlContent }`. The client composable receives this but only creates a system text message — the YAML content is dropped. The `useJourneySaver` composable has `handleJourneySaved(name, yamlContent)` and `downloadYaml()` but they're never called. The journeys page uses hardcoded mock data. Convex client is not yet wired in Nuxt, so we'll use localStorage as the persistence layer.

## Changes

### 1. Expose journey_saved data from session composable

**File:** `apps/studio/composables/useStudioSession.ts`

- Add a reactive ref: `const lastSavedJourney = ref<{ name: string; yamlContent: string } | null>(null)`
- In the `journey_saved` case, set `lastSavedJourney.value = { name: msg.name, yamlContent: msg.yamlContent }`
- Export `lastSavedJourney` in the return object

### 2. Update useJourneySaver to persist to localStorage

**File:** `apps/studio/composables/useJourneySaver.ts`

- In `handleJourneySaved()`, after storing in refs, also persist to localStorage:
  - Read existing journeys array from `localStorage.getItem('oculis-journeys')`
  - Append `{ name, yamlContent, url, stepCount, updatedAt: Date.now() }`
  - Write back to localStorage
- Accept `url` and `stepCount` as additional params so we can store them
- Auto-trigger `downloadYaml()` after saving

### 3. Wire builder.vue to call journeySaver on journey_saved

**File:** `apps/studio/pages/builder.vue`

- Replace the existing message-matching watcher with a direct watch on `session.lastSavedJourney`
- When it changes, call `journeySaver.handleJourneySaved(name, yamlContent, submittedUrl, session.steps.value.length)`

### 4. Update journeys page to read from localStorage

**File:** `apps/studio/pages/journeys.vue`

- Replace hardcoded mock data with `JSON.parse(localStorage.getItem('oculis-journeys') || '[]')`
- Add a unique `_id` to each journey (use `crypto.randomUUID()` or timestamp at save time)
- Keep the delete functionality working by writing back to localStorage

## Files to Modify

1. `apps/studio/composables/useStudioSession.ts` — expose lastSavedJourney ref
2. `apps/studio/composables/useJourneySaver.ts` — persist to localStorage + auto-download
3. `apps/studio/pages/builder.vue` — wire lastSavedJourney → journeySaver
4. `apps/studio/pages/journeys.vue` — read from localStorage instead of mock data

## Verification

1. `pnpm --filter studio lint && pnpm --filter studio format` — code quality
2. Manual: start session → record steps → "Complete Journey" → YAML file downloads → navigate to journeys page → journey appears in list
3. Manual: refresh journeys page → journey persists (localStorage)
4. Manual: delete journey → removed from list and localStorage
