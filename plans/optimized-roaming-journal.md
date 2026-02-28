# Plan: Redesign Action Proposal UI with Buttons

## Context
The current action proposal UI renders as a plain centered system message: `Proposed: click on "Search Wikipedia" (searchbox). Confirm? (yes/no)`. Users must type "yes" or "no" in the chat input, which is non-obvious. The user wants interactive buttons and a "Complete Journey" option visible at the point of each proposal.

## Design

**Proposal card layout:**
```
┌─────────────────────────────────────────┐
│ [Proposed Step]  (offset badge)         │
│                                         │
│ click on "Search Wikipedia" (searchbox) │
│ Confirm?                                │
│                                         │
│       [ Yes ]  [ No ]                   │
│       Complete Journey                  │
└─────────────────────────────────────────┘
```

- "Proposed Step" = `UBadge` with `variant="subtle"`, `color="primary"`, top-left
- Description text = `action on "name" (role)` (+ `= "value"` if present)
- "Confirm?" on its own line
- Yes / No = `UButton` side by side, primary/neutral
- "Complete Journey" = text link button centered below, muted color
- Only the **last** proposal shows interactive buttons when `hasPendingProposal` is true
- Past proposals render as static text (no buttons)

## Files to Modify

### 1. `apps/studio/components/builder/ChatPanel.vue`

**Extend ChatMessage interface:**
```ts
export interface ProposalData {
  action: string
  accessibleName: string
  role: string
  value?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  proposal?: ProposalData  // NEW - present for propose_action messages
}
```

**Add new props and emits:**
```ts
interface Props {
  messages: ChatMessage[]
  isStreaming: boolean
  hasPendingProposal: boolean  // NEW
  fontFamily?: 'mono' | 'sans' | 'system' | 'dyslexic'
}

const emit = defineEmits<{
  send: [content: string]
  confirm: []           // NEW
  reject: []            // NEW
  'complete-journey': [] // NEW
}>()
```

**Template changes:**
- In the `v-for` message loop, check if `msg.proposal` exists
- If proposal AND it's the last message AND `hasPendingProposal`: render interactive card
- Otherwise if proposal but not active: render static description text (system style)
- Add the card HTML with badge, description, buttons
- Wire button clicks to emit confirm/reject/complete-journey

**Styles:**
- `.chat-panel__proposal` card styling (left-aligned like assistant, with border)
- `.chat-panel__proposal-badge` for the "Proposed Step" tag
- `.chat-panel__proposal-text` for description
- `.chat-panel__proposal-actions` for button row
- `.chat-panel__proposal-complete` for the link button

### 2. `apps/studio/composables/useStudioSession.ts`

**Change `propose_action` handler** (line 141-147):
```ts
case 'propose_action': {
  hasPendingProposal.value = true;
  const desc = `${msg.action} on "${msg.target.accessibleName}" (${msg.target.role})${msg.value ? ` = "${msg.value}"` : ''}`;
  messages.value = [
    ...messages.value,
    {
      id: nextMessageId(),
      role: 'system',
      content: desc,
      proposal: {
        action: msg.action,
        accessibleName: msg.target.accessibleName,
        role: msg.target.role,
        value: msg.value,
      },
    },
  ];
  break;
}
```

### 3. `apps/studio/pages/builder.vue`

**Update ChatPanel usage:**
```vue
<BuilderChatPanel
  :messages="session.messages.value"
  :is-streaming="session.isStreaming.value"
  :has-pending-proposal="session.hasPendingProposal.value"
  @send="handleChatSend"
  @confirm="session.confirmAction()"
  @reject="session.rejectAction()"
  @complete-journey="handleCompleteJourney"
/>
```

**Remove text-based yes/no routing** from `handleChatSend` — the `if (session.hasPendingProposal.value)` block can be removed entirely since buttons handle it now. Text input during a pending proposal will act as an implicit rejection (new user message, same as current orchestrator behavior).

**Add `handleCompleteJourney`:**
```ts
function handleCompleteJourney() {
  session.rejectAction()  // dismiss the pending proposal
  const name = `journey-${Date.now()}`
  session.saveJourney(name)
}
```

## Verification
1. `pnpm build` — confirm studio builds without errors
2. `pnpm --filter @oculis/session-service test` — confirm backend tests still pass
3. `pnpm lint && pnpm format` — no lint/format issues
4. Manual: start studio, connect to a URL, ask the LLM to do something, verify the proposal card renders with badge + buttons, verify Yes/No/Complete Journey work
