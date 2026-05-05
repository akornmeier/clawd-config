# Code search for a Rust monorepo — Voyage recommendation

## Use `voyage-code-3`

For a code-search feature, `voyage-code-3` is the right pick. It is Voyage's code-specialist model, trained on source code rather than general prose, and it consistently beats general-purpose models on code retrieval benchmarks. Rust is well-represented in code embedding training distributions, so you get the domain advantage out of the box — no fine-tuning needed.

Skip `voyage-4-large` here. It is the strongest *general* model, but on code-vs-code and natural-language-query-vs-code retrieval, the domain-tuned `voyage-code-3` wins. Pick `voyage-4-large` only if your corpus is mostly prose (READMEs, design docs, RFCs) with code as a minority.

Specs that matter for a Rust monorepo:

- **Context length: 32K tokens.** Long enough to embed whole files, but for retrieval quality you still want function- or block-level chunks. Whole-file embeddings dilute the signal — a query about one function competes against everything else in the file. Chunk by syntactic unit (function, impl block, module) rather than fixed token windows.
- **Default dimension: 1024.**

## Dimensions — probably don't worry, but here's the knob

Default 1024 is the right starting point. `voyage-code-3` is **Matryoshka**, so you can truncate to 256, 512, or extend to 2048 without re-embedding — just slice the leading N dims and renormalize. The leading 256 dims typically retain ~95% of full-1024 quality.

Worry about dimensions only if:

- **Pinecone storage cost is real** (millions of vectors). Drop to 512 or 256 — measure recall on your queries, not on a benchmark.
- **You want max recall and storage is cheap.** Try 2048; usually marginal gain over 1024 for code.

For a typical monorepo (under ~1M chunks), stay at 1024.

## The thing you didn't ask about: `input_type`

This is the #1 silent bug with Voyage. The API takes an `input_type` parameter that prepends a different prompt under the hood:

- `input_type="document"` when you embed code chunks for the index
- `input_type="query"` when you embed the user's search string

Mixing them — or leaving it `None` — drifts queries and documents apart in the vector space. Top-k looks fine on obvious queries ("parse JSON") and silently fails on harder ones ("retry logic with exponential backoff in the http client"). Always set it. Both sides.

## Other knobs worth knowing

- **Metric:** Voyage embeddings are L2-normalized, so cosine ≡ dot product. Use `metric=cosine` (or dot) on your Pinecone index — they rank identically.
- **Quantization:** `output_dtype="int8"` cuts storage 4× with a small recall hit. Pinecone supports int8 natively. Worth it past ~5M vectors; otherwise stay on float.
- **Pinecone integration:** `voyage-code-3` is not an integrated Pinecone embedder, so you embed client-side and upsert vectors to a **standard** index. The Pinecone MCP `search-records` tool won't work for queries — use the SDK or `pc index query` with a pre-embedded vector.

TL;DR: `voyage-code-3`, 1024 dims, cosine metric, always set `input_type`, chunk by function not file.
