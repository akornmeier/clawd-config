# Pinecone Architecture

Canonical structure for the Pinecone project shared across repos and Claude Code skills.
Source of truth for index/namespace/schema decisions. Skills read `~/.claude/memory-config.json` for the machine-readable form.

## Indexes

| Index | Purpose | Namespace = | Writers |
|---|---|---|---|
| `personal-memory` | Session summaries, decisions, learnings | repo name (or `_global` for cross-cutting) | `wrap-up`, `recall` |
| `code-corpus` | Code embeddings (function/class/module level) | repo name | code ingest skill (e.g. `graphify`) |
| `project-docs` | READMEs, specs, plans, ADRs, CLAUDE.md | repo name | doc ingest skill |
| `<source>-memory` | One per knowledge source (Hormozi, Karpathy, etc.) | source default | bulk ingest |

All indexes use `llama-text-embed-v2` (1024 dim, cosine) on AWS `us-east-1`. Embed-on-write means records carry plain text in `chunk_text`; Pinecone embeds server-side.

## Namespaces

`namespace = repo name` for everything project-scoped. Use the repo's directory name (e.g. `pono`, not `tk/pono`). Reserved: `_global` for memory not tied to one repo.

Why per-repo namespaces:
- Wipe one repo cleanly: `delete --namespace=foo`
- One repo's churn doesn't affect another's recall ranking
- Free — Pinecone serverless bills per read/write, not per namespace

## Metadata schemas

Defined in `~/.claude/memory-config.json` under `metadata_schemas`. Required fields must be present on every record. Skills that write must conform; skills that read can filter on any field.

Field discipline matters: if `wrap-up` writes `created_at` and another skill writes `timestamp`, recall silently misses half the data. The config file is the contract.

## Adding a new bucket

1. Add the index name to `memory-config.json` (top-level key like `code_index`).
2. Add a `metadata_schemas.<bucket>` block with required + optional fields.
3. Create the index with `mcp__plugin_pinecone_pinecone__create-index-for-model` using the same embedding model unless you have a reason to diverge.
4. Document the namespace convention here.

## Adding a new repo

No setup needed. First upsert into a new namespace creates it. Just make sure the writer normalizes the repo name (lowercase directory basename) so reads find it.

## Lifecycle ops

- **Delete a repo's data across all buckets:** delete namespace `<repo>` from `personal-memory`, `code-corpus`, `project-docs`.
- **Reindex a repo's code:** delete namespace `<repo>` from `code-corpus`, re-run code ingest.
- **Full reset of a bucket:** delete the index, recreate via `create-index-for-model`.

## Skills that touch this

- `wrap-up` — writes session summaries to `personal-memory`.
- `recall` — reads `personal-memory` and any `knowledge_indexes` listed in config.
- `graphify` — produces knowledge graphs; can ingest into `code-corpus` and/or `project-docs` per repo.

When writing a new skill that touches Pinecone, read `memory-config.json` to discover indexes — never hardcode names.
