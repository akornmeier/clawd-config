---
name: od-design-shape
description: Reshape a token-style DESIGN.md (e.g. one with `## Tokens — Colors`, `Quick Start`, `Similar Brands` sections) into Open Design's strict 9-section schema from CONTRIBUTING.md, ready to drop into `design-systems/<slug>/DESIGN.md` of the open-design repo. Use whenever the user wants to convert, reshape, normalize, port, refit, or rewrite a DESIGN.md / design-system markdown into the Open Design format, or is preparing to contribute a new design system to the open-design repo. Trigger on phrases like "convert this DESIGN.md", "reshape this design system", "OD 9-section schema", "open-design design system", "make this fit Open Design", "shape this into the OD format", or any mention of `design-systems/` contribution. Also trigger when the user references both a DESIGN.md file and the open-design (or open design) repo, even without explicit conversion language.
---

# od-design-shape

Reshape a token-style `DESIGN.md` into Open Design's **strict 9-section schema** as defined in `CONTRIBUTING.md` of the open-design repo. The schema is what skill bodies grep for at runtime, so the headings — count, ordering, exact wording — are contractual.

## When to use

- The user has a DESIGN.md authored in a token-table style (sections like `## Tokens — Colors`, `## Components`, `## Quick Start`, `## Similar Brands`) and wants it normalized.
- The user is preparing to add a new design system under `design-systems/<slug>/` in the open-design repo.
- The user references both a DESIGN.md and the open-design repo and wants the file reshaped to fit.

If the input already uses the strict 9-section schema (numbered H2s `## 1. …` through `## 9. …` with the exact CONTRIBUTING titles), tell the user it's already conformant and stop — don't restructure for the sake of restructuring.

## The output schema

The output MUST have these nine H2s in this exact order, numbered, with these exact titles:

```
## 1. Visual Theme & Atmosphere
## 2. Color
## 3. Typography
## 4. Spacing & Grid
## 5. Layout & Composition
## 6. Components
## 7. Motion & Interaction
## 8. Voice & Brand
## 9. Anti-patterns
```

Plus a single H1 and a metadata blockquote at the very top:

```markdown
# Design System Inspired by <Brand>

> Category: <Category from existing list, or new>
> One-line summary that shows in the picker preview.
```

### Why these exact headings matter

`CONTRIBUTING.md` calls out: *"All 9 sections present. Empty section bodies are fine for hard-to-find data (e.g. motion tokens), but the headings have to be there or the prompt grep breaks."* Skill prompt bodies in the daemon literally `grep` for these headings to splice the right slice into a system prompt. Get the wording wrong and the picker still works, but downstream prompts silently miss the section.

## Section mapping (typical token-style input → 9-section output)

| Source section | Target section | Notes |
|---|---|---|
| H1 + theme intro paragraph | §1 Visual Theme & Atmosphere | Lead with the atmosphere prose. End with a `**Key Characteristics:**` bullet list distilling palette + typographic + depth signature. |
| `## Imagery` | §1 Visual Theme & Atmosphere | Fold into the same prose — imagery is part of atmosphere. |
| `## Tokens — Colors` table | §2 Color | Re-group by **role**, not by source table order. Keep every hex. Suggested groups below. |
| Agent Prompt Guide → "Quick Color Reference" | §2 Color → optional `### Quick Reference` subsection | Preserves the at-a-glance role map. |
| `## Tokens — Typography` (per-font details + Type Scale) | §3 Typography | Keep font families with fallbacks. Keep the type scale table. Add a `### Principles` bullet list capturing the weight + letter-spacing rules. |
| `## Tokens — Spacing & Shapes` (base unit, density, Spacing Scale, Border Radius, Shadows) | §4 Spacing & Grid | Spacing scale + border radius + base unit + density live here. **Shadows do NOT live here** — they go into §6 Components and §7 if they encode interaction feedback. |
| `## Layout` (page structure, hero, columns, max-width) | §5 Layout & Composition | Plus the `Layout` subkeys from `Tokens — Spacing & Shapes` (section gap, card padding, element gap). |
| `## Components` | §6 Components | One sub-block per component. Carry over background, text color, border, radius, padding, shadow, role. Group naturally (Buttons, Cards, Inputs, Navigation, Badges) if there are enough to warrant grouping. |
| `## Elevation` | §6 Components or §1 atmosphere | If it lists per-component shadow stacks, fold the values into each component in §6. The shadow philosophy (one-line summary) stays in §1. |
| `## Agent Prompt Guide` → "Example Component Prompts" | §6 Components → optional `### Example Component Prompts` subsection | Keeps the agent-facing prompts useful without inventing a 10th section. |
| Hover/focus states + `backdrop-filter` mentions in Components | §7 Motion & Interaction | Distill into prose: hover behavior, focus rings, blur usage, transition feel. If source has nothing concrete, write one sentence acknowledging that and stop — do not invent motion specs the brand never made. |
| Theme paragraph tone words ("calm authority", "advanced technology") + `## Similar Brands` | §8 Voice & Brand | Tone bullets first, then a `### Adjacent Brands` list. |
| `## Do's and Don'ts` → Don't list | §9 Anti-patterns | Direct mapping. Drop the Do list (or fold into §1 / §6 prose only if it adds something §1/§6 don't already say). |
| `## Quick Start` (CSS variables, Tailwind v4) | **DROP** | Derivative of tokens already captured in §2/§3/§4. The bundled systems don't carry these blocks. |

Anything left over that doesn't fit one of these mappings: ask the user before adding a 10th section. The schema is fixed; the answer is almost always "fold or drop", not "extend".

## Per-section guidance

### §1 Visual Theme & Atmosphere

Three to five paragraphs of prose evoking the atmosphere. Talk about palette philosophy, typographic identity, depth handling, imagery posture. Close with a `**Key Characteristics:**` bullet list — this is the section that downstream prompts most heavily lean on, so make the bullets concrete (specific hexes, specific weights, specific radii).

### §2 Color

Re-group the source color table by role. Suggested headings (use whichever apply):

- `### Background Surfaces`
- `### Text & Content`
- `### Brand & Accent`
- `### Status Colors` (only if present)
- `### Border & Divider`
- `### Overlay` (only if present)

Each entry: `**Name** (\`#hex\`): role description.` Keep every hex from the source — never paraphrase a color away.

If the source includes a "Quick Color Reference" (common in Agent Prompt Guide), reproduce it as a `### Quick Reference` subsection at the top.

OKLch values are nice-to-have for accent colors per CONTRIBUTING.md but are NOT required. Don't fabricate them — only include if the source has them.

### §3 Typography

```
### Font Family
- **Primary**: '<font>', <fallback stack>
- **Monospace**: '<mono>', <fallback stack>
- **OpenType Features**: <if specified>

### Hierarchy
| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
| ... |

### Principles
- One bullet per non-obvious rule (signature weight, tracking ramps with size, OpenType is identity-bearing, etc.)
```

### §4 Spacing & Grid

Spacing scale table. Border radius table. Base unit and density up top. Don't duplicate layout-level spacing (section gap, card padding, element gap) — those go in §5.

### §5 Layout & Composition

Prose covering page structure (hero, max-width, columns), section rhythm (gaps, alternating backgrounds), navigation posture. Include the layout-level spacing values (section gap, card padding, element gap) as a short bullet list.

### §6 Components

One sub-block per component. Preserve the source's component naming. Each block:

```
### <Component Name>
**Role:** <one line>

- Background: …
- Text: …
- Border: …
- Radius: …
- Padding: …
- Shadow: … (if present)
```

If the source has only 4-6 components, list them flat. If it has 10+, group under `### Buttons`, `### Cards & Containers`, `### Inputs & Forms`, `### Navigation`, `### Badges & Pills`.

### §7 Motion & Interaction

Token-style sources rarely carry explicit motion specs. What you can usually salvage:

- **Hover states** mentioned in component descriptions (color shifts, opacity steps).
- **Backdrop blur** values (`backdrop-filter: blur(Npx)`).
- **Focus shadows / focus rings** if components specify them.
- **Shadow as feedback** — when a card lifts on interaction.

Write one or two paragraphs distilling whatever is present. If the source is genuinely silent, write a single short sentence: *"Source DESIGN.md does not specify motion tokens."* and leave it. CONTRIBUTING.md says empty bodies are fine — don't fabricate.

### §8 Voice & Brand

Tone bullets distilled from the theme paragraph (e.g. *calm authority, advanced technology, restrained elegance*). Then `### Adjacent Brands` — a bullet list of similar brands with one-line "what they share".

### §9 Anti-patterns

Map the source's Don't list directly. One bullet per anti-pattern. Keep the *why* if the source explained it.

## Workflow

1. **Read the input file.** Get its full contents.
2. **Detect already-conformant.** If H2s match the strict 9-section schema verbatim, stop and tell the user.
3. **Confirm metadata.** Pull brand name from H1, but ask the user for:
   - **Slug** (ASCII, dashed — `general-intelligence` not `generalintelligence`).
   - **Category** — list the existing ones (`AI & LLM`, `Developer Tools`, `Productivity & SaaS`, `Backend & Data`, `Design & Creative`, `Fintech & Crypto`, `E-Commerce & Retail`, `Media & Consumer`, `Automotive`) and let them pick or propose new.
   - **One-line summary** (≤80 chars, shows in picker preview).
   - **Output path** — default `design-systems/<slug>/DESIGN.md` if working in the open-design repo, else alongside the input.
4. **Reshape** following the section mapping above. Use `Write` to create the output file.
5. **Verify.** Re-read your output and check:
   - All nine H2s present, numbered, exact titles.
   - H1 starts with `Design System Inspired by `.
   - Blockquote has both `> Category:` and a one-line summary.
   - No fabricated hexes, weights, sizes, or motion specs.
   - Slug is ASCII-dashed (CONTRIBUTING merge bar item 5).
6. **Report.** Tell the user what you produced, what got dropped (e.g. "Quick Start CSS/Tailwind blocks dropped — derivative of §2/§3/§4"), and what was thin (e.g. "§7 Motion & Interaction has only one sentence — source had no motion specs").

## Quality bar (mirrors CONTRIBUTING merge bar)

1. **All 9 sections present.** Numbered, exact wording, in order.
2. **Hex codes are real.** Carry over every hex from source verbatim. Never invent or guess.
3. **No marketing fluff.** A brand tagline is not a design token — cut it.
4. **ASCII slug.** Dotted brands get dashed (`x.ai` → `x-ai`).
5. **Don't expand the schema.** No 10th section. If something doesn't fit, fold it or drop it.
6. **Don't shrink the schema.** All 9 headings present even if a body is one line.

## Common mistakes to avoid

- **Renaming sections.** "Color Palette & Roles" is the bundled-imports style; it is NOT the CONTRIBUTING schema. Use `## 2. Color`.
- **Adding "Agent Prompt Guide" as section 10.** Fold its content into §2 (color quickref) and §6 (example prompts).
- **Keeping "Quick Start" CSS/Tailwind blocks.** They're derivative — drop them.
- **Inventing motion specs to fill §7.** A one-sentence acknowledgment that the source is silent is the correct output.
- **Reordering numbered sections.** The numbers are part of the schema, not annotations.
- **Skipping the H1 boilerplate prefix.** It must be `# Design System Inspired by <Brand>` — the loader strips that prefix to derive the picker label.

## Reference: existing categories

`AI & LLM` · `Developer Tools` · `Productivity & SaaS` · `Backend & Data` · `Design & Creative` · `Fintech & Crypto` · `E-Commerce & Retail` · `Media & Consumer` · `Automotive`

Pick the closest match. Only invent a new category if none of these fit, and tell the user you're doing so.
