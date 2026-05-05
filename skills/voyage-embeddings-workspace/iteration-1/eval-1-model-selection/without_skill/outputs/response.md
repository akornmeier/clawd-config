# Voyage model recommendation for Rust code search

**Use `voyage-code-3`.** It's Voyage's code-specialized embedding model and the right default for any code search feature. On Voyage's own retrieval benchmarks it materially outperforms general-purpose models (including OpenAI's `text-embedding-3-large`) on code tasks — typically by double-digit percentage points on code-to-code and natural-language-to-code retrieval. For a Rust monorepo specifically, that gap matters: code embeddings need to capture identifier semantics, syntactic structure, and cross-language idioms in ways general text models don't.

Don't reach for `voyage-3` / `voyage-3-large` here. They're stronger than `voyage-code-3` on prose, but weaker on code. And don't use the domain models (`voyage-finance-2`, `voyage-law-2`) — wrong domain.

## Dimensions: yes, think about it, but it's not scary

`voyage-code-3` supports **Matryoshka embeddings** — you can request 256, 512, 1024, or 2048 dimensions from the same model. Quality degrades gracefully as you shrink.

Practical guidance:

- **Default to 1024.** Best quality/cost balance. Matches what most vector DBs are tuned for.
- **2048** if you want maximum recall and storage/latency aren't constraints (large monorepo, infrequent queries, willing to pay).
- **512 or 256** if you're indexing millions of chunks and storage/RAM dominates cost — quality loss is small (single-digit percentage points typically).
- It also supports **int8 and binary quantization**, which can cut storage 4x–32x with minor recall loss. Worth benchmarking once you have a working baseline.

Pick a dimension on day one and stick with it — re-embedding a monorepo is annoying.

## Things you didn't ask but should know

1. **Chunking matters more than the model.** Don't embed whole files. Chunk by function/impl block, ideally with tree-sitter for Rust. Include the function signature plus a few lines of surrounding context (module path, doc comment). Bad chunking will tank retrieval no matter what model you use.

2. **Input types.** Voyage's API takes an `input_type` parameter (`"query"` vs `"document"`). Use `"document"` when indexing and `"query"` at search time — it asymmetrically tunes the embeddings and noticeably improves retrieval. Easy to forget.

3. **Context window.** `voyage-code-3` supports 32K tokens per input, so you have room, but longer inputs dilute the signal. Keep chunks focused.

4. **Hybrid search beats pure vector search for code.** Combine `voyage-code-3` with BM25/ripgrep-style lexical search and rerank. Identifier matches (`fn parse_config`) often need exact-match recall that dense embeddings miss. Voyage also offers `rerank-2` if you want a second-stage reranker.

5. **Cost.** Code-3 is priced per million tokens — cheap for indexing a monorepo once, but watch query volume if this is user-facing.
