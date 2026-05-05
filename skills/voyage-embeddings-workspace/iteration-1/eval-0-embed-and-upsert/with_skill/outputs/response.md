# Embedding `/tmp/sample_code.py` into `code-corpus-voyage` (namespace `pono`)

You're in the happy path for this skill — Python code, standard Pinecone index, single namespace. Use the `embed_and_upsert.py` script that ships with the `voyage-embeddings` skill. It handles batching, stable IDs, and retry-with-backoff for you.

## What's about to happen

1. **Read the file.** The script treats one file as one record. For a small `sample_code.py` that's fine; for a large repo you'd pre-chunk (function-level) before passing in.
2. **Embed with `voyage-code-3`.** This is the right model for source code — domain-tuned, beats general models on code retrieval. Default 1024 dims, cosine-friendly (Voyage vectors are L2-normalized).
3. **`input_type="document"`.** Critical for retrieval quality. The script defaults to `document`, which is correct here because you're upserting (not searching). Mismatching `document`/`query` between ingest and search is the #1 silent bug with Voyage — don't override it.
4. **Stable record ID = `sha256(text)[:16]`.** Re-running the command overwrites in place rather than duplicating. Idempotent by design.
5. **Upsert into `code-corpus-voyage` / namespace `pono`.** Batches of 100, with exponential backoff (1s, 2s, 4s, 8s) on transient failures.

## Prerequisites (one-time)

- `VOYAGE_API_KEY` and `PINECONE_API_KEY` set in `~/.claude/settings.local.json` under the `env` block. The skill assumes these are already there. If you get an auth error, add them and restart the session.
- Deps installed: `pip install voyageai pinecone`
- Index `code-corpus-voyage` already exists as a **standard** (non-integrated) index, dim=1024, metric=cosine. If it doesn't, create it first:
  ```bash
  pc index create-serverless --name code-corpus-voyage --dimension 1024 --metric cosine --cloud aws --region us-east-1
  ```

## The command

```bash
python ~/.claude/skills/voyage-embeddings/scripts/embed_and_upsert.py \
  --index code-corpus-voyage \
  --namespace pono \
  --model voyage-code-3 \
  --file /tmp/sample_code.py
```

That's it. You'll see `embedded 1/1` and `upserted 1/1 into pono`, then `done — 1 records in <N>s`.

## Verifying it worked

The Pinecone MCP `search-records` tool won't work here — that's for **integrated** indexes only, and `code-corpus-voyage` is standard (you're embedding client-side). To sanity-check, query with the Pinecone CLI or SDK using a Voyage-embedded query vector with `input_type="query"`:

```bash
pc index describe-index-stats --name code-corpus-voyage
# Should show namespace 'pono' with vector_count >= 1
```

## Heads-ups

- **One file = one record.** If `sample_code.py` is large (>32K tokens), Voyage will reject it. Pre-chunk by function before re-running.
- **Don't change `--input-type`.** It defaults to `document` for a reason. Only override to `query` for ad-hoc test searches.
- **Re-runs are safe.** Same file content → same ID → overwrite, not duplicate.
