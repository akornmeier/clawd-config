---
name: strategy-awareness
description: A strategic governance skill — not a memory feature. Maintains a living strategy document at ~/.claude/strategy.md (or user-chosen path). Auto-fires when the conversation surfaces strategic substance — customer signals, market signals, decisions, focus shifts, wins, hypotheses, new offers, or learnings. Captures the moment to the right named section, dates it, and reflects conflicts against the user's existing Decisions and Don't-Do list. On first run, runs a 6-question setup flow to bootstrap the file. Manual triggers include "run strategy setup", "show my strategy", "show me my strategy overview", "visualize my strategy", "edit my strategy", "what's my strategy on X", and "update my strategy". When the user says "show my strategy" or "strategy overview" or asks to visually edit, generate the interactive visualization HTML and open it in the browser (see VISUALIZE mode below). Do NOT use this skill for personal preferences (oat milk, name, voice tone) — those belong in Claude's general memory or ~/.claude/CLAUDE.md. Use this only for strategic state that governs decisions.
---

# Strategy & Awareness Skill

A strategic governance layer for Claude. Reads the user's living strategy doc, updates the right section when something strategic comes up, and surfaces conflicts with existing strategy in real time.

This is **not** a memory feature. It's a governance feature. Claude memory recalls *"the user mentioned dashboards before."* This skill says *"the user explicitly decided not to build dashboards this quarter on April 22 — surface that conflict."*

---

## What this skill is FOR

✅ Strategic decisions ("we're pivoting", "I'm killing the agency offering")
✅ Customer signals that point at strategy ("3 customers asked for Slack")
✅ Market signals (competitor moves, new tools, industry shifts)
✅ Wins and metrics that mark progress
✅ Active hypotheses and bets
✅ Open strategic questions
✅ Focus shifts ("now focused on enterprise")
✅ Don't-Do entries ("explicitly not building X")

## What this skill is NOT for

❌ Personal preferences ("I'm vegetarian", "I prefer dark mode") → Claude general memory
❌ Voice/tone rules → ~/.claude/CLAUDE.md (project-level) or general memory
❌ Project-specific config ("this codebase uses pnpm") → project's CLAUDE.md
❌ Trivia ("I had a coffee", "today is Tuesday")
❌ One-off tasks or todos → not strategic state, don't log

If unsure: ask "would this still matter in 6 months when I look back?" If yes → log. If no → skip.

---

## File location

Default: `~/.claude/strategy.md`

Configurable during setup. Common alternatives:
- `~/Desktop/strategy.md` (visible)
- `~/Brain/strategy.md` (if user has a personal brain repo)

A one-line pointer is added to `~/.claude/CLAUDE.md` so every Claude session knows the file exists:

```
## Strategy
My living strategy document is at <path>. Use the strategy-awareness skill to read, update, or reflect on it.
```

---

## The five modes

### MODE 1 — SETUP (first run only)

**Triggered when:**
- Strategy file doesn't exist at the configured path, OR
- User says "run strategy setup", "set up my strategy", or installs the skill.

**Steps:**

1. Check if the strategy file already exists. If yes, skip to other modes.
2. Run the 6-question setup flow, one question at a time, waiting for each answer:
   1. *What's the name of your business, role, or project?*
   2. *In one sentence — what do you do, and for whom?*
   3. *What's your single biggest focus right now (next 30–90 days)?*
   4. *Who is your primary customer or audience?*
   5. *Name 1–2 things you're explicitly NOT doing right now (your Don't-Do list).*
   6. *Where should I save your strategy file? (default: ~/.claude/strategy.md)*
3. Generate the starter file from `templates/strategy-template.md`, populated with the answers.
4. Append the pointer line to `~/.claude/CLAUDE.md` under a `## Strategy` heading. Create the file if missing. Never overwrite existing content.
5. Confirm in one line: *"Strategy file created at <path>. I'll keep it updated as we work."*

### MODE 2 — CAPTURE (most common, auto-fires)

**Triggered when conversation contains strategic substance.** Strict filtering — see "What this skill is NOT for" above.

**Strong triggers:**
- *Customer signals* — "a user said", "we keep hearing", "they're complaining about", "X churned because"
- *Market signals* — competitor news, new tools, pricing moves, industry shifts
- *Strategic decisions* — "I decided", "we're pivoting", "moving away from", "doubling down on", "killing"
- *Wins / metrics* — "we hit", "MRR is at", "subs crossed", "we landed"
- *New offers / products* — launches, pricing changes, packaging
- *Learnings* — "turns out", "I realized", "we got this wrong"
- *Focus shifts* — "now focused on", "this quarter we're"
- *Hypotheses* — "I think X will", "my bet is", "the theory is"

**Steps:**

1. Read the strategy file at the configured path.
2. Identify the section the new info belongs to (see Section Map below).
3. Append a one-line dated entry. Format: `- 2026-04-26 — <one line summary>`
4. Update the `Last updated:` line at the top of the file.
5. **Reflect (this is the unique value):**
   - **Conflict?** Compare the new entry against `## Don't-Do List`, recent `## Decisions Log`, and `## Current Focus`. If conflict, surface it: *"Heads up — this contradicts your Don't-Do (no dashboard rebuild). Hold the line, or update Don't-Do?"*
   - **Pattern?** Check if 3+ similar entries exist in the same section. If yes: *"This is the 4th customer signal pointing to dashboards. Want me to elevate to Current Focus?"*
   - **Neutral?** Skip the reflection — just confirm.
6. Confirm in one line: *"Logged to Customer Insights."*

### MODE 3 — REFLECT (the governance moment)

**This is the mode that earns the skill its seat.** Triggered when the user is currently working on or proposing something that existing strategy could inform.

**Examples that should trigger Reflect:**
- *"Let's add a [feature]"* — check Don't-Do
- *"I want to launch [offer]"* — check Active Offers, Don't-Do, Customer / Audience
- *"Should I take this sponsor / client / deal"* — check Don't-Do, Current Focus
- *"What should I build next"* — check Customer Insights, Hypotheses, Open Questions
- *"Help me write [strategic doc — pricing page, sales page, video script]"* — pull from Active Offers, Customer / Audience, Voice Rules

**Steps:**

1. Read the strategy file.
2. Surface the directly-relevant sections by name. Quote the specific lines.
3. Cite explicitly with dates and section names: *"Your Don't-Do says no dashboard rebuild this quarter (logged April 22). Your Customer Insights show 4 dashboard requests in 30 days. You said you'd revisit at 5. Currently at 4."*
4. Let the user decide. Do NOT auto-update the file in Reflect mode — only surface.

### MODE 4 — QUERY (explicit, text response)

**Triggered when** user asks "what's my strategy on X", "what do I think about Y", "what's my current focus", "show my Don't-Do list", *and is happy with a text answer*.

**Steps:**

1. Read the strategy file.
2. Return the relevant section(s) verbatim.
3. Add 2–3 sentences synthesizing the implications and any tensions you notice.

### MODE 5 — VISUALIZE (interactive HTML view + edit)

**Triggered when** user says *"show my strategy"*, *"show me my strategy overview"*, *"visualize my strategy"*, *"edit my strategy"*, *"open the strategy view"*, or any variant suggesting they want to **see** the strategy interactively rather than read a text dump.

**What this mode does:** generates a styled interactive HTML representation of the user's strategy file at `~/.claude/strategy-view.html`, opens it in their default browser, and lets them edit visually — click X to mark items for deletion, type to add new items, edit inline. When they click "Apply changes," the page produces a structured Claude prompt (auto-copied to clipboard) that the user pastes back, and this skill applies the diff to `~/.claude/strategy.md`.

**Steps:**

1. **Read the strategy file** at the configured path (default `~/.claude/strategy.md`).
2. **Parse the markdown into a structured object** with this shape:
   ```json
   {
     "title": "Acme — Strategy & Awareness",
     "lastUpdated": "2026-04-26",
     "sections": [
       {
         "id": "north-star",
         "name": "North Star",
         "type": "paragraph",
         "content": "Help entrepreneurs..."
       },
       {
         "id": "current-focus",
         "name": "Current Focus",
         "type": "list",
         "items": [
           { "id": "...", "date": null, "text": "SuperSkills launch (April 28)" }
         ]
       },
       {
         "id": "decisions-log",
         "name": "Decisions Log",
         "type": "list",
         "items": [
           { "id": "...", "date": "2026-04-25", "text": "Decided: Pinecone alone..." }
         ]
       }
     ]
   }
   ```
   Each item gets a stable `id` derived from a hash of section+text so updates are deterministic.
3. **Read the visualization template** at `~/.claude/skills/strategy-awareness/strategy-view-template.html` (installed alongside the skill).
4. **Inject the parsed JSON** into the template by replacing the marker `/* {{STRATEGY_JSON}} */` inside the template's `<script>` block with the actual JSON.
5. **Write the result** to `~/.claude/strategy-view.html`.
6. **Open it in the default browser** with `open ~/.claude/strategy-view.html` (macOS) or platform equivalent.
7. **Confirm in one line:** *"Strategy view opened in browser. Edit visually, then paste the diff back here when ready."*

**When the user pastes back a diff** (it'll be a structured block starting with `Apply these changes to ~/.claude/strategy.md:`), parse the operations:
- `DELETE — section: <name>, text: <line>` → remove that line from the section
- `ADD — section: <name>, text: <line>` → append to that section with today's date
- `EDIT — section: <name>, from: <old>, to: <new>` → replace the line

Apply all operations to `~/.claude/strategy.md` using surgical edits. Update `Last updated:` to today. Confirm: *"Applied {{n}} changes. Want me to regenerate the view?"*

**Edit conflicts** with existing rules (Don't-Do violations, etc.) should still be surfaced before applying — same Reflect logic as Capture mode.

---

## Section Map

The skill expects this section structure in `strategy.md`. If a section is missing, ask before creating.

| User says / context | Section to update |
|---|---|
| Customer feedback, user quotes, support themes | `## Customer Insights` |
| Competitor move, new tool, market shift | `## Market Signals` |
| Strategic decision (pivot, kill, ship, redirect) | `## Decisions Log` |
| New theory or bet | `## Hypotheses` |
| Concrete win, metric, milestone | `## Wins` |
| Open strategic question | `## Open Questions` |
| Focus shift | `## Current Focus` (also log change in `## Decisions Log`) |
| New product / offer launched or changed | `## Active Offers / Products` |
| New "explicitly not doing X" rule | `## Don't-Do List` |
| Outdated content the user wants removed | `## Archive` (move, never delete) |

---

## Editing rules

- **Surgical edits only.** Never reformat, never reorder existing sections, never delete a section the user didn't ask to remove.
- **Date everything new.** ISO format: `YYYY-MM-DD`.
- **One line per entry.** If something needs more than a line, ask if it should be its own document.
- **Most recent on top.** New entries go at the top of their section, not the bottom — easier to read recent state.
- **Promote with permission.** When 3+ similar entries pile up in `## Customer Insights`, ask before elevating to `## Decisions Log` or `## Current Focus`.
- **Never silently delete.** If something is moot, suggest moving to `## Archive`.
- **Don't load the whole file into a response.** Read it, summarize the relevant slice.
- **Preserve user language.** When capturing customer feedback, quote them — don't paraphrase.
- **No trivia.** Strategic relevance only.

---

## Examples in the wild

| User says | Mode | Skill action |
|---|---|---|
| *"Three customers asked for Slack integration this week."* | CAPTURE | Append to `## Customer Insights` with date. Reflect: pattern check. |
| *"I'm pivoting toward enterprise."* | CAPTURE | Update `## Current Focus`. Log the pivot in `## Decisions Log`. Surface SMB-customer conflict if relevant. |
| *"We just hit $100K MRR."* | CAPTURE | Append to `## Wins`. |
| *"Let's add a dashboard feature."* | REFLECT | Don't update. Cite Don't-Do entry. Cite Customer Insight count. Let user decide. |
| *"Help me write the SuperSkills launch email."* | REFLECT | Pull `## Active Offers`, `## Customer / Audience`, `## Voice Rules`. Surface. |
| *"What's my pricing strategy right now?"* | QUERY | Return `## Active Offers` + relevant `## Decisions Log` entries verbatim, plus 2-line synthesis. |
| *"Show my open questions."* | QUERY | Return `## Open Questions` verbatim. |
| *"Run strategy setup."* | SETUP | Six questions. Generate file. Add pointer to CLAUDE.md. |
| *"I'm vegetarian."* | (none) | DO NOT use this skill. That's a personal preference for Claude general memory. |
| *"This codebase uses pnpm not npm."* | (none) | DO NOT use this skill. That belongs in the project's CLAUDE.md. |

---

## Don't

- Don't capture personal preferences, voice rules, or project-specific config — those have their own homes.
- Don't push opinions unsolicited. Reflect what's there, suggest, let the user decide.
- Don't create new sections without asking.
- Don't update during trivial conversation.
- Don't paraphrase user quotes when capturing customer feedback.
- Don't delete the Archive — it's history.
- Don't auto-update during REFLECT mode — only surface.
- Don't load the whole file into context. Read it, use the relevant slice.

---

## How this differs from Claude's general memory

| | Claude memory | `CLAUDE.md` | This skill |
|---|---|---|---|
| **Job** | Recall facts | Always-on context | Govern decisions |
| **Structure** | Flat list | Whatever you write | Named sections |
| **Conflict detection** | None | None | Yes, on every capture |
| **Auditability** | Opaque | Open file | Open file |
| **Promotion logic** | None | None | 3+ insights → ask to elevate |
| **Best for** | Preferences, voice | Always-loaded rules | Strategic state |

Use the right tool for the job. This skill earns its seat only when strategy drift is a real problem — typically when you're making 3+ strategic decisions a month.
