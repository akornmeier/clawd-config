---
name: od-design-shape
description: Reshape a token-style DESIGN.md into Open Design's strict 9-section schema (the one in CONTRIBUTING.md of the open-design repo).
user-invokable: true
args:
  - name: input
    description: Path to the source DESIGN.md (e.g. ~/Downloads/foo/DESIGN.md)
    required: true
  - name: output
    description: Output path (default - design-systems/<slug>/DESIGN.md if in open-design repo, else next to input)
    required: false
  - name: slug
    description: ASCII-dashed slug for the brand (e.g. general-intelligence)
    required: false
---

Invoke the `od-design-shape` skill to reshape `$input` into the Open Design 9-section schema and write it to `$output`.

Read the SKILL.md at `~/.claude/skills/od-design-shape/SKILL.md` and follow its workflow:

1. Read `$input`.
2. If the file already uses the strict 9-section schema (`## 1. Visual Theme & Atmosphere` through `## 9. Anti-patterns`, exact wording), tell the user and stop.
3. Confirm metadata with the user — slug (if not provided), category, one-line summary, output path (if not provided).
4. Apply the section mapping from the skill body to produce the reshaped DESIGN.md.
5. Write to `$output` (or the negotiated default).
6. Verify against the quality bar in the skill body and report what was kept, dropped, and thin.
