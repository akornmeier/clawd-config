# Skills health check — 2026-07-25

Run via `meta-skill` → `workflows/audit-skills.md`. Mechanical scan by
`scripts/scan.py`, then one grader per flagged skill against
`references/skill-review-rubric.md`.

**Coverage.** 21 skills scanned, 0 broken, **8 graded**, 13 scanned only. The 13
are not a clean bill of health — the scan proves only the absence of *mechanical*
defects. Rubric dimensions 3 (progressive disclosure), 5 (single source of truth)
and 7 (scope) are unproven for them, and this run's own results show those are
exactly the dimensions that fail most often.

Baseline before this run: 68 directory entries, 46 dangling symlinks, 1 orphaned
gitlink. Those are already removed (`19fa9d5`, `d02b7cb`).

## Pick what to plan

- [ ] **graphify** — 62 KB forced on every trigger, mostly inline Python duplicating its own shipped CLI
- [ ] **emil-design-eng** — fully duplicated by `motion-design-skill`; recommend deletion
- [ ] **voyage-embeddings** — description cannot return "no"; fires on any embedding question
- [ ] **diagram-design** — colour tokens forked three ways, so the advertised first-run gate is dead code
- [ ] **thermo-nuclear-code-quality-review** — seven rules restated up to eight times; cannot auto-fire
- [ ] **review-animations** — `disable-model-invocation` makes it unreachable from natural language
- [ ] **motion-design-skill** — compound asks load 74% of the bundle; duplicated recipes across references
- [ ] **sl-resolve-pr-feedback** — three references sit two hops out; a documented live failure mode

## Summary

| # | Skill | Forced | Fails | Effort |
|---|---|---|---|---|
| 1 | graphify | 1426 L / 62.3 KB | 6 of 7 | large |
| 2 | emil-design-eng | 679 L / 26.7 KB | 6 of 7 | small (delete) |
| 3 | voyage-embeddings | 177 L / 11.8 KB | 6 of 7 | small |
| 4 | diagram-design | 507 L / 24.0 KB | 4 of 7 | medium |
| 5 | thermo-nuclear-code-quality-review | 192 L / 12.1 KB | 4 of 7 | small |
| 6 | review-animations | 113 L / 7.9 KB | 4 of 7 | small |
| 7 | motion-design-skill | 179 L / 12.8 KB | 3 of 7 | medium |
| 8 | sl-resolve-pr-feedback | 53 L / 3.1 KB | 2 of 7 | small |

## Cross-cutting findings

**Two skills can never fire from their descriptions.** `review-animations` and
`thermo-nuclear-code-quality-review` both set `disable-model-invocation: true`,
which removes them from the model's skill list entirely. Both also carry
carefully written trigger phrasing that is dead on arrival — `thermo-nuclear`
names four synonyms that can never match. Whichever half is intended, the other
is wrong. The scanner now reports this flag directly; before this run it reported
only the symptom.

**One duplicate pair.** `emil-design-eng` (679 lines, single file) and
`motion-design-skill` (179 lines routing to 6 references) are the same capability
from the same source, and both descriptions open with nearly identical wording,
so they race on every prompt. Two graders reached this independently, and I
verified it separately: 9 of 10 distinctive `emil` terms already appear in the
`motion` bundle. The sole exception is an `animations.dev` course link — one line
if wanted.

**Duplication is the most common failure.** Dimension 5 failed in 7 of 8 graded
skills. Dimension 3 failed in 6 of 8. Dimensions 2 and 6 mostly passed. The
pattern is not oversized routers — it is the same idea restated in two to eight
places inside otherwise reasonable files.

## Findings

### 1. graphify — 1426 L / 62.3 KB forced, 6 fails, large

62 KB on every trigger, 100% of it forced; the only other bundled file is a 5-byte
version stamp. A `/graphify explain` run uses about 2% of what it loads.

- Description fires on "any question about a codebase, documents, or project content" — a stranger can never say no. `trigger: /graphify` is a non-standard field the loader ignores.
- 31 inline Python heredocs re-implement subcommands the shipped `graphify` CLI already provides — two implementations free to drift.
- Graph-loading preamble restated 11 times across Steps 4–7c.
- Three jobs in one skill: build, query, and environment setup (`hook install`, `claude install`, `--mcp`, `--watch`).

Top edits: replace heredocs with CLI calls (~700 lines / 35 KB); split query/path/explain into a `graphify-query` skill gated on `graphify-out/graph.json`; rewrite the description with a not-for clause.

### 2. emil-design-eng — 679 L / 26.7 KB forced, 6 fails, small

Recommend deletion. Every idea is also in `motion-design-skill`, which does the
same job in 179 forced lines with real progressive disclosure. Internally it also
repeats itself: `scale(0.97)` on `:active` three times, transitions-beat-keyframes
three times, the Review Format table restating the Review Checklist.

Also: an "Initial Response" gate forces a canned greeting and forbids acting until
asked again — actively harmful when the skill fires mid-task.

Top edit: delete the skill and its symlink; port the `animations.dev` link into
`motion-design-skill`'s Credit section if wanted.

### 3. voyage-embeddings — 177 L / 11.8 KB forced, 6 fails, small

- "Use even when the user doesn't say Voyage — many embedding questions are Voyage questions in disguise" makes "no" unreachable. Its own exclusion list is invisible until the 11.8 KB is already paid.
- Five ideas stated twice between `SKILL.md` and `references/models.md`.
- **Two broken references**: `~/.claude/settings.local.json` is cited three times but does not exist, and `VOYAGE_API_KEY` is set nowhere — "no extra wiring needed" is false and a real run dies at the env guard. The `pinecone-query` skill it routes to does not exist; the real one is the `pinecone:query` plugin skill.
- An 18-line dated personal decision journal ("should we migrate code-corpus?", status noted 2026-05-05) sits in forced context and belongs in `strategy.md`.

### 4. diagram-design — 507 L / 24.0 KB forced, 4 fails, medium

The flagship first-run style gate is dead code. §0 tests whether the accent
colour differs from `#b5523a`, but the real default in `style-guide.md` is
`#eb6c36`, so the test is always true and the gate never fires. Colours have
forked three ways across `SKILL.md`, `style-guide.md`, and a stale inversion rule.

`style-guide.md` claims sole ownership of colour ("SKILL.md say `accent`, not a
hex") while `SKILL.md` inlines 20 hex literals and duplicates four of its blocks
verbatim.

Two genuine dangling paths: `.impeccable.md` exists nowhere, and it routes to a
**wiretext** skill that is not installed.

### 5. thermo-nuclear-code-quality-review — 192 L / 12.1 KB forced, 4 fails, small

Seven rules restated up to eight times each. The 1000-line rule appears at lines
34–38, 81, 95, 120, 144, 163, 176 and 186. Four sections after "Non-Negotiable
Standards" are the same rules re-voiced as questions, then flags, then remedies,
then quotable phrases.

Deleting lines 71–153 and 183–192 plus standards 3–7 takes it from 192 lines to
about 60 — at which point progressive disclosure is moot rather than failed.

Frontmatter contradiction: four trigger synonyms that `disable-model-invocation`
guarantees can never match.

### 6. review-animations — 113 L / 7.9 KB forced, 4 fails, small

Cannot auto-fire (`disable-model-invocation: true`), and the description states
only what it does. Consequence: `improve-animations` ("audit the motion") is what
actually fires on "review the animations here" — the disambiguation is
one-directional, since both siblings name `review-animations` but it never claims
the diff-review scope itself.

All ten standards are restated in `STANDARDS.md`, several a third time in
"Aggressive Escalation Triggers" (itself the Ten Standards in imperative form).

### 7. motion-design-skill — 179 L / 12.8 KB forced, 3 fails, medium

The healthiest of the flagged set; its failures are refinement, not repair.
Routing rows are orthogonal facets, so a compound ask (Vue + Tailwind + swipe +
drawer — its own eval #1) matches 4 rows and loads 74% of the bundle. Four
Tailwind recipes are token-identical between `tailwind.md` and `components.md`.

Hygiene: `logs/` (1.5 MB, 23 files) and `.claude/data/sessions/` sit in the
working copy. Gitignored, so no context cost by default, but any directory-wide
scan reads them.

### 8. sl-resolve-pr-feedback — 53 L / 3.1 KB forced, 2 fails, small

Already a lean router; dimensions 1–4 and 7 pass cleanly. Two real findings:

- `codex-gate.md`, `verify-gate.md` and `summary.md` are two hops from `SKILL.md`, reachable only via `full-mode.md`. The skill's own `evals/README.md` documents "codex-gate.md is not being loaded" as a distinct failure cluster — a live risk, not a formality.
- `SKILL.md:31` claims "each reference is self-contained for that mode's flow", which is false for Targeted mode.

## Scanner limitations this run exposed

Recorded because the audit is only as good as its first tier.

1. **Second-hop and glob references are missed.** The scan claimed 40 of 61 `diagram-design` files were unreferenced; the true number is 0. All are linked from second-hop `type-*.md` files or matched by a documented `example-<type>.html` glob. Same error on `motion-design-skill` (27 claimed).
2. **Gitignored directories are walked.** `motion-design-skill/logs/` (1.5 MB) counted as 23 orphans. The scan should respect `.gitignore`.
3. **Fixed during this run:** `disable-model-invocation` now reported directly; nested `templates/SKILL.md` no longer excluded from bundled counts; `evals/` directories skipped like `evals.md`; the trigger regex now matches "Use this whenever".

Net effect of 1 and 2: the orphan check is the weakest signal the scanner
produces. Treat it as a prompt to look, never as a finding.

## Not graded (13)

`animation-vocabulary`, `apple-design`, `cmux`, `find-animation-opportunities`,
`find-skills`, `improve-animations`, `intent-layer`, `karpathy-guidelines`,
`meta-skill`, `od-design-shape`, `planf3`, `strategy-awareness`,
`worktree-manager-skill`.

Mechanically clean only. Given that dimension 5 failed in 7 of 8 graded skills, a
second pass over these is worth running before treating them as healthy.
