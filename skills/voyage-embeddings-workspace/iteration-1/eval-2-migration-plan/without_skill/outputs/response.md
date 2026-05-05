# Migrating code-corpus from llama-text-embed-v2 to voyage-code-3

You cannot swap embedding models on an existing index — embeddings are tied to the model that produced them, and dimensions/spaces differ. The safe path is **build a parallel index, dual-write, verify, cut over, then retire the old one.** Treat it like a blue/green deploy.

## Key facts before you start

- `llama-text-embed-v2` is a Pinecone-hosted integrated model (default 1024 dim).
- `voyage-code-3` is **not** an integrated model in Pinecone — Voyage is a separate provider. You generate vectors via Voyage's API and upsert them yourself. It supports Matryoshka dims (256, 512, 1024, 2048) and `int8`/`binary` quantization. Default 1024 dim, float.
- Voyage requires a `VOYAGE_API_KEY`. Code corpus → use `input_type="document"` for upserts, `input_type="query"` at search time. That asymmetry matters for retrieval quality.

## Step-by-step plan

**1. Inventory the source.** `describe-index` and `describe-index-stats` on the current `code-corpus` index. Confirm record count (~50k), the 8 namespaces, and the schema (which field holds the text — that's the field you'll re-embed).

**2. Create the new index.** Since voyage-code-3 isn't integrated, create a **standard dense index**, not `create-index-for-model`. Pick dimension (1024 recommended unless storage is tight) and metric `cosine`. Name it `code-corpus-voyage` so you can run both in parallel.

**3. Backfill in batches per namespace.** For each of the 8 namespaces:
   - Page through records from the old index (`list` + `fetch`, or export).
   - Batch the text field into Voyage's `/v1/embeddings` endpoint. Voyage allows up to 128 texts per request and ~120k tokens — code chunks are usually small, so 128 is the practical cap. Use `model="voyage-code-3"`, `input_type="document"`.
   - Upsert vectors + original metadata into the new index under the same namespace name.
   - Add retries with exponential backoff (Voyage rate-limits per tier).
   - Track progress per namespace so you can resume on failure. ~50k records at 128/batch ≈ 400 API calls — should take well under an hour.

**4. Verify counts.** `describe-index-stats` on the new index. Each namespace's `vector_count` must match the source. Spot-check 5–10 IDs per namespace via `fetch` to confirm metadata round-tripped intact.

**5. Quality eval before cutover.** Pick 20–50 representative code queries you've run before. Query both indexes (remember: voyage-code-3 needs `input_type="query"` at search time). Compare top-10 results. Acceptance bar: voyage results should be at least as relevant as llama on the majority of queries — this is the whole point of the migration. If they're worse, stop and investigate (likely cause: forgot `input_type` asymmetry, or wrong text field embedded).

**6. Dual-write window (optional but recommended).** Before flipping reads, point your ingestion path at *both* indexes for a few days. Lets you roll back without data loss if voyage-code-3 underperforms in production.

**7. Cut over reads.** Flip your application's index name from `code-corpus` → `code-corpus-voyage`. Keep the old index live for 1–2 weeks as a rollback safety net.

**8. Retire.** Once you're confident, `delete-index` on the old `code-corpus`.

## Gotchas

- **Don't forget `input_type` at query time** — Voyage's biggest retrieval-quality footgun.
- **Costs:** you pay Voyage per token for embeddings *and* Pinecone storage for both indexes during the transition. Budget accordingly.
- **Re-embedding is one-way** — keep the source text in your records (or in the metadata) so you can re-embed again later if Voyage releases v4.
