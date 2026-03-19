---
description: Full design process - PRD → Clarification → UX Spec → Copy & Visual Design → Build Prompts → Documentation
argument-hint: <feature idea or description>
model: opus
---

# Design Command

Transform a rough feature idea into comprehensive, build-ready specifications through a 6-stage design process that produces professional UI, compelling copy, psychologically-informed UX, and documentation that stays in sync with the code.

## Variables

FEATURE_IDEA: $ARGUMENTS
OUTPUT_DIR: `specs/`

## Process Overview

```
Stage 1: PRD-Lite             → specs/<name>-prd.md
Stage 2: PRD-Clarifier        → specs/<name>-clarification.md
Stage 3: PRD-to-UX            → specs/<name>-ux-spec.md
Stage 4: Copy & Visual Design → specs/<name>-copy-design.md
Stage 5: UX-to-Prompts        → specs/<name>-build-prompts.md
Stage 6: Documentation Sync   → specs/<name>-docs.md
```

## Instructions

- If no `FEATURE_IDEA` is provided, use AskUserQuestion to gather it
- Execute all 6 stages IN ORDER - do not skip stages
- Write outputs to files in `OUTPUT_DIR` - do not output long content to conversation
- Generate a kebab-case name from the feature idea for file naming
- After completion, provide instructions for `/plan_w_team` or `/build`

---

# Stage 1: MVP to Demo PRD Generator

## Role

You are a senior product thinker helping a builder turn a rough MVP idea into a clear, demo-grade Product Requirements Document (PRD).

Your goal is decision clarity, not enterprise ceremony.

## Input Analysis

The user has provided: `FEATURE_IDEA`

You must infer missing details, but:
- Clearly label assumptions
- Avoid overengineering
- Optimize for a believable demo, not production scale

## PRD Output Structure (Write to `specs/<name>-prd.md`)

### 1. One-Sentence Problem

Write a sharp problem statement in this format:

> [User] struggles to [do X] because [reason], resulting in [impact].

If multiple problems exist, pick the single most demo-worthy one.

### 2. Demo Goal (What Success Looks Like)

Describe:
- What must work for this demo to be considered successful
- What outcome the demo should clearly communicate

Optionally include:
- Non-Goals (what is intentionally out of scope)

### 3. Target User (Role-Based)

Define one primary user role.

Include:
- Role / context
- Skill level
- Key constraint (time, knowledge, access, etc.)

Avoid personas or demographics.

### 4. Core Use Case (Happy Path)

Describe the single most important end-to-end flow.

Include:
- Start condition
- Step-by-step flow (numbered)
- End condition

If this flow works, the demo works.

### 5. Functional Decisions (What It Must Do)

List only required functional capabilities.

Use this table:

| ID | Function | Notes |
|----|----------|-------|

Rules:
- Phrase as capabilities, not implementation
- No "nice-to-haves"
- Keep the list tight

### 6. UX Decisions (What the Experience Is Like)

Explicitly define UX assumptions so nothing is left implicit.

#### 6.1 Entry Point
- How the user starts
- What they see first

#### 6.2 Inputs
What the user provides (if anything).

#### 6.3 Outputs
What the user receives and in what form.

#### 6.4 Feedback & States
How the system communicates:
- Loading
- Success
- Failure
- Partial results

#### 6.5 Errors (Minimum Viable Handling)
What happens when:
- Input is invalid
- The system fails
- The user does nothing

### 7. Data & Logic (At a Glance)

#### 7.1 Inputs
Where data comes from: User, API, Static/mocked, Generated

#### 7.2 Processing
High-level logic only (no architecture diagrams).
Example: Input → transform → output

#### 7.3 Outputs
Where results go: UI only, Temporarily stored, Logged

### 8. Brand & Design Context

**IMPORTANT**: Before finalizing the PRD, search the codebase for:
- Existing design tokens, themes, or style guides
- Brand assets (logos, colors, typography)
- Component libraries or UI patterns in use
- Related features that should inform consistency

Document findings:
- Design system location (if any)
- Key brand colors/fonts
- Existing component patterns to reuse
- Consistency requirements with other features

### 9. User Psychology & Motivation Drivers

Apply marketing psychology mental models to understand what drives the target user. This analysis shapes everything downstream — UX decisions, copy, visual hierarchy, and interaction patterns.

**Analyze using these lenses:**

#### 9.1 Jobs to Be Done
What "job" is the user hiring this product to do? Frame the answer as an outcome, not a feature. Example: "Spend less time on reports" not "Generate reports."

#### 9.2 Primary Psychological Drivers
Identify 2-3 psychological principles most relevant to this user and product. Choose from:

- **Loss aversion** — Are users trying to avoid losing something (time, money, status)?
- **Social proof** — Do users need reassurance that others use/trust this?
- **Endowment effect** — Can we let them "own" something early (free trial, customization)?
- **Goal-gradient** — Is there a completion journey that accelerates motivation?
- **Status-quo bias** — Are we asking them to change behavior? How do we reduce that friction?
- **Reciprocity** — Can we give value before asking for commitment?
- **Scarcity/urgency** — Is there genuine time pressure or limited availability?
- **Authority** — Does credibility or expertise matter in this domain?
- **IKEA effect** — Does user investment in setup increase perceived value?

For each selected driver, write:
- Why it applies to this user/context
- How it should influence the UX and copy

#### 9.3 Behavioral Model (BJ Fogg)
For the primary action you want users to take:
- **Motivation**: What makes them want to do this?
- **Ability**: What makes it easy or hard?
- **Prompt**: What triggers them at the right moment?

Identify the weakest of the three — that's where design effort should focus.

#### 9.4 Friction & Hesitation Map
List the moments where a user might hesitate, bail, or feel uncertain:

| Moment | Likely Feeling | Psychological Principle to Apply |
|--------|---------------|----------------------------------|
| [e.g., First seeing the pricing] | [e.g., Sticker shock] | [e.g., Anchoring — show value first, Mental accounting — frame as $/day] |

This map feeds directly into Stage 3 (Cognitive Load pass) and Stage 4 (copy).

---

# Stage 2: PRD Clarification

After writing the PRD, systematically clarify ambiguities through structured questioning.

## Create Tracking Document

Write to `specs/<name>-clarification.md`:

```markdown
# PRD Clarification Session

**Source PRD**: <name>-prd.md
**Session Started**: [date/time]
**Depth Selected**: [pending]
**Progress**: 0/[total]

---

## Session Log
```

## Ask Depth Preference

Use AskUserQuestion:

```json
{
  "questions": [{
    "question": "What depth of PRD analysis would you like?",
    "header": "Depth",
    "multiSelect": false,
    "options": [
      {"label": "Quick (5 questions)", "description": "Rapid surface-level review of critical ambiguities only"},
      {"label": "Medium (10 questions)", "description": "Balanced analysis covering key requirement areas"},
      {"label": "Long (20 questions)", "description": "Comprehensive review with detailed exploration"},
      {"label": "Ultralong (35 questions)", "description": "Exhaustive deep-dive leaving no stone unturned"}
    ]
  }]
}
```

## Questioning Strategy

Prioritize questions by impact:
1. **Critical Path Items**: Requirements blocking other features
2. **High-Ambiguity Areas**: Vague language, missing acceptance criteria
3. **Integration Points**: Interfaces with external systems
4. **Edge Cases**: Error handling, boundary conditions
5. **Non-Functional Requirements**: Performance, accessibility gaps
6. **User Journey Gaps**: Missing steps, undefined user states

## Question Quality Standards

Each question MUST be:
- **Specific**: Reference exact sections from the PRD
- **Actionable**: Answer directly informs a requirement update
- **Non-leading**: Avoid suggesting the "right" answer
- **Singular**: One clear question per turn

Use AskUserQuestion with 2-4 options for EVERY question.

Update the tracking document after EACH answer.

---

# Stage 3: PRD to UX Specification

Transform the clarified PRD into UX foundations through **7 forced designer mindset passes**.

**Core principle:** UX foundations come BEFORE visual specifications. Mental models, information architecture, and cognitive load analysis prevent "pretty but unusable" designs. But unlike previous versions of this process, we DO complete the visual design — Pass 7 establishes the full design language so the build phase produces professional, polished results.

## Write to `specs/<name>-ux-spec.md`

### Pass 1: User Intent & Mental Model Alignment

**Designer mindset:** "What does the user think is happening?"

**Force these questions:**
- What does the user believe this system does?
- What are they trying to accomplish in one sentence?
- What wrong mental models are likely?

**Cross-reference** the psychology drivers from PRD Section 9 — especially the Jobs to Be Done and Friction Map. The mental model analysis here should build on that foundation.

**Output:**
```markdown
## Pass 1: Mental Model

**Primary user intent:** [One sentence]

**Likely misconceptions:**
- [Misconception 1]
- [Misconception 2]

**UX principle to reinforce/correct:** [Specific principle]
```

### Pass 2: Information Architecture

**Designer mindset:** "What exists, and how is it organized?"

**Actions:**
1. Enumerate ALL concepts the user will encounter
2. Group into logical buckets
3. Classify each as: Primary / Secondary / Hidden (progressive)

**Output:**
```markdown
## Pass 2: Information Architecture

**All user-visible concepts:**
- [Concept 1]
- [Concept 2]

**Grouped structure:**

### [Group Name]
- [Concept]: [Primary/Secondary/Hidden]
- Rationale: [One sentence]
```

### Pass 3: Affordances & Action Clarity

**Designer mindset:** "What actions are obvious without explanation?"

**Force explicit decisions:**
- What is clickable?
- What looks editable?
- What looks like output (read-only)?

**Output:**
```markdown
## Pass 3: Affordances

| Action | Visual/Interaction Signal |
|--------|--------------------------|
| [Action] | [What makes it obvious] |

**Affordance rules:**
- If user sees X, they should assume Y
```

### Pass 4: Cognitive Load & Decision Minimization

**Designer mindset:** "Where will the user hesitate?"

**Pull in the Friction & Hesitation Map** from PRD Section 9.4. Each friction point identified there should have a concrete UX resolution here.

**Identify:**
- Moments of choice (decisions required)
- Moments of uncertainty (unclear what to do)
- Moments of waiting (system processing)

**Apply:**
- Collapse decisions (fewer choices)
- Delay complexity (progressive disclosure)
- Introduce defaults (reduce decision burden)
- Apply relevant psychology (anchoring for pricing, goal-gradient for onboarding, etc.)

**Output:**
```markdown
## Pass 4: Cognitive Load

**Friction points:**
| Moment | Type | Psychology Applied | Simplification |
|--------|------|-------------------|----------------|
| [Where] | Choice/Uncertainty/Waiting | [Principle from PRD §9] | [How to reduce] |

**Defaults introduced:**
- [Default 1]: [Rationale]
```

### Pass 5: State Design & Feedback

**Designer mindset:** "How does the system talk back?"

**For EACH major element, enumerate states:**
- Empty
- Loading
- Success
- Partial (incomplete data)
- Error

**Output:**
```markdown
## Pass 5: State Design

### [Element/Screen]
| State | User Sees | User Understands | User Can Do |
|-------|-----------|------------------|-------------|
| Empty | | | |
| Loading | | | |
| Success | | | |
| Partial | | | |
| Error | | | |
```

### Pass 6: Flow Integrity Check

**Designer mindset:** "Does this feel inevitable?"

**Sanity check:**
- Where could users get lost?
- Where would a first-time user fail?
- What must be visible vs can be implied?

**Output:**
```markdown
## Pass 6: Flow Integrity

**Flow risks:**
| Risk | Where | Mitigation |
|------|-------|------------|
| [Risk] | [Location] | [Guardrail/Nudge] |

**Visibility decisions:**
- Must be visible: [List]
- Can be implied: [List]

**UX constraints:** [Hard rules for visual phase]
```

### Pass 7: Visual Design Language

**Designer mindset:** "What does professional look like for this product?"

This pass transforms the UX structure into a concrete visual system. The goal is a design that looks intentional, cohesive, and professional — not generic or template-like.

**Step 1: Establish Design Direction**

Consider the product's personality from the PRD:
- Is this a tool (efficient, clean) or an experience (expressive, delightful)?
- Who is the audience — developers, consumers, enterprise, creative professionals?
- What existing design system or component library is in the codebase (from PRD Section 8)?

Choose a design stance:
- **Minimal/functional**: Clean lines, generous whitespace, type-driven hierarchy (dashboards, dev tools, SaaS)
- **Warm/approachable**: Rounded corners, softer colors, friendly illustrations (consumer, onboarding)
- **Bold/editorial**: Strong typography, high contrast, dramatic spacing (marketing, landing pages)
- **Dense/professional**: Compact layouts, data-rich, clear grid structure (enterprise, analytics)

**Step 2: Define the Visual System**

```markdown
## Pass 7: Visual Design Language

**Design stance:** [Minimal/Warm/Bold/Dense] — [one sentence rationale]

### Color System
- **Background**: [specific value — e.g., zinc-950 for dark, white for light]
- **Surface/Card**: [e.g., zinc-900/zinc-50]
- **Primary accent**: [one color with specific usage — e.g., blue-500 for CTAs and active states]
- **Secondary accent**: [if needed — e.g., emerald-500 for success states]
- **Text hierarchy**: [e.g., zinc-100 primary, zinc-400 secondary, zinc-500 tertiary]
- **Borders**: [e.g., zinc-800 subtle, zinc-700 prominent]
- **Mode**: [Dark/Light/Both] — [rationale tied to audience]

### Typography
- **Font family**: [e.g., Geist Sans for UI, Geist Mono for code/data]
- **Scale**: Define sizes for: page title, section header, card title, body, caption, label
- **Weight usage**: [e.g., medium for headings, regular for body, semibold for emphasis only]

### Spacing & Layout
- **Content width**: [e.g., max-w-6xl centered, full-width with sidebar]
- **Grid approach**: [e.g., 12-col grid, CSS grid with named areas, flex-based]
- **Spacing rhythm**: [e.g., 4px base unit — 8, 16, 24, 32, 48]
- **Card/section padding**: [specific values]
- **Density**: [comfortable/compact/spacious]

### Component Patterns
- **Buttons**: [style — e.g., filled primary, ghost secondary, no outlines]
- **Cards**: [e.g., subtle border, no shadow, 8px radius]
- **Inputs**: [e.g., bordered, filled background, minimal]
- **Navigation**: [e.g., sidebar, top bar, tabs]
- **Feedback**: [e.g., toast notifications, inline alerts]
- **Empty states**: [e.g., centered illustration + action, or minimal text + CTA]

### Interaction & Motion
- **Transitions**: [e.g., 150ms ease-out for hovers, 200ms for reveals]
- **Hover states**: [e.g., background lightens, subtle scale, underline]
- **Loading patterns**: [e.g., skeleton screens, pulsing dots, progress bar]

### Design Constraints (Non-Negotiable)
- Every interactive element needs visible focus states (accessibility)
- Maintain consistent border-radius across all components
- Text contrast ratios meet WCAG AA minimum
- No more than 2 font weights per page section
- Stick to the spacing scale — no arbitrary pixel values
```

**Step 3: Reference Checks**

If using shadcn/ui or an existing component library (from PRD Section 8):
- Note which components map to the design system
- Specify any customization needed to match the visual language
- Prefer using the `/shadcn-ui` and `/ui-ux-pro-max` skills during the build phase

If the codebase has existing design patterns:
- Document how this design language extends (not contradicts) them

---

# Stage 4: Copy & Visual Design

Write all user-facing copy informed by the psychology drivers (PRD Section 9) and the visual design language (UX Spec Pass 7). Copy is not decoration — it's a core part of the UX. Every word should earn its place.

## Write to `specs/<name>-copy-design.md`

### Step 1: Messaging Strategy

Before writing any copy, define the messaging foundation:

```markdown
# Copy & Visual Design: [Project Name]

## Messaging Strategy

### Voice & Tone
- **Formality**: [Casual / Professional-friendly / Formal]
- **Personality**: [e.g., Confident and direct / Warm and encouraging / Technical and precise]
- **Point of view**: [e.g., "We help you..." / "You can..." / Direct imperative "Build..."]

### Core Value Proposition
[One sentence that captures what this product does for the user, written in user language]

### Psychological Levers (from PRD §9)
For each driver identified in the PRD, define how copy will activate it:

| Driver | Copy Strategy | Example |
|--------|--------------|---------|
| [e.g., Loss aversion] | [e.g., Frame inaction as costly] | [e.g., "Stop losing 4 hours/week to manual reports"] |
| [e.g., Social proof] | [e.g., Show adoption numbers] | [e.g., "Join 2,400 teams already shipping faster"] |
| [e.g., Goal-gradient] | [e.g., Progress language] | [e.g., "You're 2 steps from your first deploy"] |
```

### Step 2: Page-Level Copy

Write copy for every screen/page identified in the UX spec. For each:

```markdown
### [Screen/Page Name]

**Purpose**: [What this screen accomplishes in the user journey]
**User's mindset arriving here**: [What they're thinking/feeling — reference Friction Map]

#### Headline
- Primary: [The headline]
- Rationale: [Why this works — connect to psychology driver]

#### Subheadline
[1-2 sentences expanding on the headline]

#### Body Copy
[Section-by-section copy, organized to match the UX spec's information architecture]

#### CTAs
- Primary: [Button text] — [What it communicates]
- Secondary: [If applicable]
```

### Step 3: Microcopy & State Messages

Write copy for every state identified in UX Spec Pass 5:

```markdown
## Microcopy

### Empty States
| Element | Message | Action |
|---------|---------|--------|
| [e.g., Dashboard on first visit] | [e.g., "No projects yet. Create one to get started."] | [e.g., "Create Project" button] |

### Loading States
| Element | Message |
|---------|---------|
| [e.g., Data processing] | [e.g., "Crunching your numbers..."] |

### Success Messages
| Action | Message |
|--------|---------|
| [e.g., Project created] | [e.g., "Project created. You're ready to go."] |

### Error Messages
| Error | Message | Recovery Action |
|-------|---------|-----------------|
| [e.g., Invalid input] | [e.g., "That email doesn't look right. Check the format and try again."] | [e.g., Focus on field, show format hint] |

### Tooltips & Help Text
| Element | Text |
|---------|------|
| [e.g., API key field] | [e.g., "Find this in Settings → API Keys. We never store it in plain text."] |
```

### Step 4: Copy Quality Checklist

Before finalizing, verify every piece of copy against these standards (drawn from the `/copywriting` skill):

- [ ] **Clarity over cleverness** — Would a first-time user understand this instantly?
- [ ] **Benefits over features** — Does copy describe outcomes, not mechanisms?
- [ ] **Specificity over vagueness** — No "streamline," "optimize," "innovative," "seamlessly"
- [ ] **Active voice** — "We generate your report" not "Your report is generated"
- [ ] **No orphan CTAs** — Every call-to-action tells users what they get ("Start Free Trial" not "Submit")
- [ ] **Psychology alignment** — Does the copy activate the drivers identified in PRD Section 9?
- [ ] **State coverage** — Is there copy for empty, loading, success, error, and edge cases?
- [ ] **Consistent voice** — Does the tone match across all screens?

---

# Stage 5: UX Spec to Build-Order Prompts

Transform the UX spec, copy, and visual design into sequential, self-contained prompts for implementation.

## Write to `specs/<name>-build-prompts.md`

## Build Order Strategy

Generate prompts in this order:

| Phase | What to Include | Why First |
|-------|-----------------|-----------|
| **1. Foundation** | Design tokens, shared types, base styles from Pass 7 | Everything depends on these |
| **2. Layout Shell** | Page structure, navigation, panels | Container for all features |
| **3. Core Components** | Primary UI elements with their copy | Building blocks |
| **4. Interactions** | Drag-drop, connections, pickers | Depend on components |
| **5. States & Feedback** | Empty, loading, error, success — with microcopy from Stage 4 | Refinement layer |
| **6. Polish** | Animations, responsive, edge cases | Final layer |
| **7. Documentation** | README, code comments, CONTRIBUTING updates from Stage 6 | Docs stay in sync |

## Prompt Structure Template

Each prompt follows this structure:

```markdown
## [Feature Name]

### Context
[What this feature is and where it fits]

### Visual Design
[Relevant specs from Pass 7 — colors, spacing, component patterns]
[Reference the design stance and how this element embodies it]

### Copy
[Exact copy from Stage 4 for this element — headlines, labels, microcopy, state messages]
[Do NOT use placeholder text like "Lorem ipsum" or "Title goes here"]

### Requirements
- [Specific behavior/appearance requirement]
- [Include specs: dimensions, colors, states]

### States
- Default: [description + copy]
- Empty: [description + copy from Stage 4 microcopy]
- Loading: [description + copy]
- Error: [description + copy]
- [Other states]

### Interactions
- [How user interacts]
- [Keyboard support if applicable]

### Design Skills to Use
[Reference relevant skills for the builder: /shadcn-ui, /ui-ux-pro-max, /frontend-design]

### Constraints
- [Technical or design constraints]
- [What NOT to include]
```

## Self-Containment Rules

Each prompt MUST:
- Include enough context to understand in isolation
- Include all visual specs relevant to that feature (from Pass 7)
- Include all exact copy for that feature (from Stage 4)
- Include all states that feature can be in
- Include all interactions for that feature

Each prompt MUST NOT:
- Reference "see previous prompt"
- Assume knowledge from other prompts
- Leave specs vague ("appropriate styling")
- Use placeholder copy — all text must be final copy from Stage 4

## Output Format

```markdown
# Build-Order Prompts: [Project Name]

## Overview
[1-2 sentence summary]

## Design System Summary
[Condensed version of Pass 7 visual design language — the builder needs this as reference]

## Build Sequence
1. [Prompt name] - [brief description]
2. [Prompt name] - [brief description]
...

---

## Prompt 1: [Feature Name]
[Full self-contained prompt]

---

## Prompt 2: [Feature Name]
[Full self-contained prompt]
```

---

# Stage 6: Documentation Sync

Audit existing documentation and produce exact text patches so docs stay aligned with the feature being built. Documentation drifts from code when updates happen as an afterthought — this stage prevents that by treating docs as a first-class deliverable, written alongside the design rather than months later.

**Writing quality gate:** Apply the `/writing-clearly-and-concisely` skill to all prose produced in this stage. Every sentence should pass Strunk's core rules — active voice, positive form, concrete language, no needless words. Documentation that reads like filler ("This feature provides a streamlined way to optimize your workflow") undermines trust. Say what the thing does, for whom, and stop.

## Write to `specs/<name>-docs.md`

### Step 1: Documentation Audit

Search the codebase for existing documentation that the new feature affects:

- **README.md** — Does the project overview, setup instructions, or feature list need updating?
- **CONTRIBUTING.md** — Do contribution guidelines, development setup, or architecture notes need changes?
- **API documentation** — Are there new endpoints, changed parameters, or deprecated routes?
- **Code comments** — Which files from the build prompts (Stage 5) will need JSDoc, docstrings, or inline explanations?
- **Configuration docs** — Are there new environment variables, config files, or feature flags to document?
- **CHANGELOG** — Does the project maintain one? Draft the entry.

For each doc file found, record:
- Current state (what it says now)
- What needs changing and why (tied to a specific PRD requirement or build prompt)

If a doc file doesn't exist but should (e.g., no README for a new package), flag it for creation.

### Step 2: Documentation Patches

For each file identified in Step 1, write the exact text to insert, replace, or append. Use this format:

```markdown
### [File Path]

**Action**: [Insert after line X / Replace section Y / Append to end / Create new file]
**Reason**: [Which PRD requirement or build prompt drives this change]

#### Current Text
> [Existing text being replaced, or "N/A — new section"]

#### Updated Text
[Exact replacement copy, written with /writing-clearly-and-concisely applied]
```

Rules for writing patches:
- **Say what it does, not what it is.** "Generates a PDF report from the dashboard data" beats "A PDF report generation feature."
- **Match the existing doc's voice.** If the README is terse and technical, don't add marketing fluff. If it's friendly and tutorial-style, match that.
- **One idea per paragraph.** Don't bury setup instructions inside a feature description.
- **Omit needless words.** Cut "In order to," "It should be noted that," "basically," "simply." If removing a word doesn't change the meaning, remove it.
- **Use active voice.** "Run `npm start` to launch the dev server" not "The dev server can be launched by running `npm start`."
- **Be specific.** "Requires Node.js 20+" not "Requires a recent version of Node.js."

### Step 3: Code Comment Specifications

For each component or module from the build prompts (Stage 5), specify where code comments belong and what they should say. Focus on the non-obvious — comments should explain *why*, not *what*.

```markdown
## Code Comments

### [Component/Module Name]
**File**: [Expected file path from build prompts]

| Location | Comment | Why Needed |
|----------|---------|------------|
| [e.g., Function signature] | [e.g., "Debounces input to avoid excess API calls during rapid typing"] | [e.g., Not obvious from the 300ms delay constant alone] |
| [e.g., Config constant] | [e.g., "Max 50 items — API pagination limit, not a UX choice"] | [e.g., Prevents future dev from changing it thinking it's arbitrary] |
```

Skip comments for self-evident code. A function called `calculateTotalPrice(items)` doesn't need a comment saying "Calculates the total price." Reserve comments for:
- **Business rules** that aren't obvious from the code
- **Constraints** imposed by external systems (API limits, browser quirks, legal requirements)
- **Non-obvious decisions** where a future developer might reasonably change the code and break something

### Step 4: Documentation Quality Checklist

Before finalizing, verify all documentation against these standards:

- [ ] **Accurate** — Every statement matches the PRD and build prompts. No aspirational claims about unbuilt features.
- [ ] **Complete** — All new environment variables, endpoints, commands, and configuration options are documented.
- [ ] **Concise** — No sentence can be shortened without losing meaning. No paragraph repeats what another already said.
- [ ] **Active voice** — "Run X" not "X should be run." "The function returns Y" not "Y is returned by the function."
- [ ] **Concrete** — Version numbers, command examples, file paths. No "appropriate value" or "as needed."
- [ ] **Consistent** — Terminology matches the codebase. If the code calls it a "workspace," the docs don't call it a "project."
- [ ] **Scannable** — Headers, bullet points, and code blocks break up walls of text. A developer skimming finds what they need.

---

# Completion

After all 6 stages, present the summary:

```
Design Process Complete

Files created:
- specs/<name>-prd.md
- specs/<name>-clarification.md
- specs/<name>-ux-spec.md
- specs/<name>-copy-design.md
- specs/<name>-build-prompts.md
- specs/<name>-docs.md
```

## Approval Gate

Use AskUserQuestion to present the next step:

```json
{
  "questions": [{
    "question": "Design is complete. Ready to create an implementation plan with /plan_w_team?",
    "header": "Next Step",
    "multiSelect": false,
    "options": [
      {"label": "Create plan now (Recommended)", "description": "Auto-invoke /plan_w_team with the build-prompts spec"},
      {"label": "Review specs first", "description": "I want to review the spec files before proceeding"},
      {"label": "Done for now", "description": "Stop here — I'll plan manually later"}
    ]
  }]
}
```

### If "Create plan now":
Invoke the Skill tool with: `skill: "plan_w_team", args: "specs/<name>-build-prompts.md"`

### If "Review specs first":
List the file paths and stop.

### If "Done for now":
List the file paths and stop.
