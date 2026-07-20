# Image Generation

Fill or update the embedded images in an existing plan `.html` file.

## Backend Check (do this first)

Run `[ -n "$OPENAI_API_KEY" ] && echo gpt-image || echo diagram-design`.

- `gpt-image` → follow this file as written (scripts below).
- `diagram-design` → the `diagram-design` skill is the backend instead. Invoke it via the Skill tool, ask it for one diagram per `{{...IMAGE` slot using that slot's subject, and inline the resulting SVG directly into the slot's `<figure>` (replace the `<!-- {{...IMAGE: ...}} -->` comment with the `<svg>` element; keep the `<figcaption>`). No PNGs, no `IMAGES_OUTPUT_DIR`. Skip the rest of this file except the shared rules, which still apply, plus these three:
  - **Colors come from the plan, not the skin.** Have the SVG reference the plan's own custom properties — `fill="var(--accent)"`, `stroke="var(--ink)"` — never diagram-design's hardcoded hexes. Inline SVG resolves `var()` against the page, so this is what keeps the synced visual identity.
  - **Define the roles it needs in `:root`.** diagram-design assumes `--bg`, `--ink`, `--muted`, `--soft`, `--accent`, `--accent-tint`. An undeclared var silently renders as no fill. Add any missing ones to the plan's `:root` before embedding.
  - **No font `<link>`.** The plan must stay self-contained, so diagram-design's Google Fonts line is out. Use fallback stacks: `'Geist', ui-sans-serif, system-ui, sans-serif` and `'Geist Mono', ui-monospace, monospace`.

Pick the sub-workflow based on the incoming `USER_PROMPT`:

| Sub-workflow | When to call it |
| --- | --- |
| Create | The prompt asks to generate, fill, or add the plan's images from scratch (empty `{{...IMAGE` slots) |
| Update | The prompt asks to change, refine, regenerate, or replace images that already exist in the plan |

Scripts (run with `uv run`, needs `OPENAI_API_KEY`):
- Create image: `uv run scripts/generate_gpt_image.py "<prompt>" <output.png> --size 1536x1024 --quality high`
- Edit image: `uv run scripts/edit_gpt_image.py "<instruction>" <output.png> <input.png> --size 1536x1024 --quality high`

Shared rules for every image prompt:
- always generate in wide format (`--size 1536x1024`) at high quality (`--quality high`)
- convey the one or two core ideas of that section for a professional software engineer
- match the plan's synced visual identity (professional, focused, minimal)
- keep total words shown in the image under 10
- save images to `IMAGES_OUTPUT_DIR` (create it if missing)

## Create

1. Find slots - Grep the plan for `{{...IMAGE` placeholders (hero + per-phase). Each comment names the intended subject.
2. Write prompts - For each slot, write a prompt following the shared rules above.
3. Generate - Run `generate_gpt_image.py` once per slot, writing to `IMAGES_OUTPUT_DIR`.
4. Embed - Replace each `<!-- {{...IMAGE: ...}} -->` placeholder with `<img src="<plan-name>/<file>.png" alt="...">`, keeping the existing `<figure>`/`<figcaption>`.
5. Report - List the images generated and the slots filled.

## Update

1. Identify targets - From the `USER_PROMPT`, determine which embedded `<img>` images to change.
2. Write instruction - Write an edit instruction describing the change, following the shared rules above.
3. Edit - Run `edit_gpt_image.py` with the existing PNG as input, overwriting it (the script backs up the original first).
4. Verify embed - Confirm the `<img>` still points at the updated file; update `src`/`alt`/`<figcaption>` if the change warrants it.
5. Report - List the images updated and what changed.
