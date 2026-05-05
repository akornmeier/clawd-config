# Migrating `code-corpus` from `llama-text-embed-v2` to `voyage-code-3`

The safe path is **parallel run, then swap** — never mutate the existing index. `llama-text-embed-v2` is integrated (Pinecone embeds server-side); `voyage-code-3` is a third-party model, so the new index must be **standard** (you embed client-side and push vectors). Different index types, different dimensions — they cannot coexist in one index.

## Plan

### 1. Pre-flight checks

- Confirm `VOYAGE_API_KEY` and `PINECONE_API_KEY` are in the `env` block of `~/.claude/settings.local.json`. Restart the Claude Code session if you just added them.
- `pip install -U voyageai pinecone`
- List the 8 namespaces on the existing index so you can mirror them exactly:
  ```bash
  pc index describe --name code-corpus
  ```

### 2. Create the new standard index

```bash
pc index create-serverless \
  --name code-corpus-voyage \
  --dimension 1024 \
  --metric cosine \
  --cloud aws \
  --region us-east-1
```

Why these values: `voyage-code-3` returns 1024-dim vectors by default, Voyage embeddings are L2-normalized so `cosine` is the safe metric, and matching the existing region keeps query latency comparable.

### 3. Re-ingest each namespace

Use `~/.claude/skills/voyage-embeddings/scripts/embed_and_upsert.py` per repo. The script handles batching (128 for Voyage, 100 for Pinecone), exponential-backoff retries, stable sha256 IDs (idempotent re-runs), and defaults to `input_type="document"` — which is what you want for upserts.

```bash
python ~/.claude/skills/voyage-embeddings/scripts/embed_and_upsert.py \
  --index code-corpus-voyage \
  --namespace repo-1 \
  --model voyage-code-3 \
  --file path/to/file1.py --file path/to/file2.py
```

Loop this for each of the 8 repos, mirroring the existing namespace names. The script's chunking is naive (one record per file). For ~50k records you almost certainly want function-level chunks — use `graphify` to produce those, then point `--file` at the chunk artifacts. Don't reuse llama-era IDs; let sha256 regenerate them.

### 4. Verify before swapping

Three checks, in order:

1. **Counts match.** `pc index describe-index-stats --name code-corpus-voyage` — vector counts per namespace should roughly match the old index (allow drift if you re-chunked).
2. **Sanity query.** Pick 5–10 real queries you've actually used. Embed each one with `input_type="query"` (not `document` — this is the #1 silent bug) and compare top-10 hits between old and new indexes side-by-side. Querying voyage-code-3 means SDK or `pc index query` with a vector — the Pinecone MCP `search-records` tool only works on integrated indexes.
3. **Eyeball quality.** Voyage should win on code-specific queries (function names, API call patterns). If it doesn't — stop. Either chunking is wrong or `input_type` is mismatched somewhere.

### 5. Swap over

Once verified:

- Update `~/.claude/memory-config.json`: set `code_index` to `code-corpus-voyage` and `embedding_model` to `voyage-code-3`.
- Update the `graphify` skill's ingest path to call `embed_and_upsert.py` for the code-corpus bucket.
- Run for a few days against the new index while the old one stays alive as a fallback.

### 6. Decommission

After ~1 week of clean operation with nothing reading from the old index:

```bash
pc index delete --name code-corpus
```

## Why parallel-run, not in-place

Dimension/metric mismatches between writes and existing vectors corrupt an index irrecoverably. Index type also can't be mutated — integrated and standard are different objects in Pinecone. Parallel run lets you bail out cheaply, keeps existing tools working during migration, and gives you a real apples-to-apples comparison rather than a leap of faith.

## Cost estimate

50k records × ~500 tokens avg = ~25M tokens. At voyage-code-3 pricing this is roughly **$1–4** in embedding cost, plus ~200MB of Pinecone storage (~$0.07/month). The big cost is your time on chunking and verification — not the API.
