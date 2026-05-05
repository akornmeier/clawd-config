# Embedding Python code with Voyage AI and storing in Pinecone

Here's the walkthrough. You'll use **`voyage-code-3`** (Voyage's code-specialized model) to embed the file, then upsert into your existing `code-corpus-voyage` index under the `pono` namespace.

## Prerequisites

1. **API keys** in your environment:
   ```bash
   export VOYAGE_API_KEY="..."
   export PINECONE_API_KEY="..."
   ```
2. **SDKs installed:**
   ```bash
   pip install voyageai pinecone
   ```
3. **Index assumption:** `code-corpus-voyage` already exists as a *standard* (non-integrated) index, with dimension matching `voyage-code-3` (default 1024). If it's an integrated index with its own embedding model, this approach won't apply — you'd upsert raw text instead.

## What the script does

1. Read `/tmp/sample_code.py`.
2. Embed it with `voyage-code-3` using `input_type="document"` (correct for indexed content; use `"query"` only at search time).
3. Upsert into Pinecone with the file path as the record ID, namespace `pono`, and the source code in metadata for retrieval.

## The script

Save this as `/tmp/embed_and_upsert.py`:

```python
import os
import voyageai
from pinecone import Pinecone

FILE_PATH = "/tmp/sample_code.py"
INDEX_NAME = "code-corpus-voyage"
NAMESPACE = "pono"
MODEL = "voyage-code-3"

# Read source
with open(FILE_PATH, "r") as f:
    code = f.read()

# Embed with Voyage
vo = voyageai.Client()  # reads VOYAGE_API_KEY
result = vo.embed(
    texts=[code],
    model=MODEL,
    input_type="document",
)
embedding = result.embeddings[0]

# Upsert to Pinecone
pc = Pinecone()  # reads PINECONE_API_KEY
index = pc.Index(INDEX_NAME)

index.upsert(
    vectors=[
        {
            "id": FILE_PATH,
            "values": embedding,
            "metadata": {
                "path": FILE_PATH,
                "language": "python",
                "text": code,
            },
        }
    ],
    namespace=NAMESPACE,
)

print(f"Upserted {FILE_PATH} → {INDEX_NAME}/{NAMESPACE}")
```

## Run it

```bash
python /tmp/embed_and_upsert.py
```

## Notes & gotchas

- **Token limit:** `voyage-code-3` accepts up to 32K tokens per input. If `sample_code.py` exceeds that, chunk it (e.g., by function or fixed-size windows) and upsert each chunk with a suffixed ID like `sample_code.py#0`, `#1`, etc.
- **Dimension mismatch:** if your index was created at a non-default dimension (256, 512, 1024, or 2048 are supported by `voyage-code-3` via the `output_dimension` param), pass `output_dimension=<N>` to `vo.embed()` to match.
- **At query time**, re-embed the query string with the same model but `input_type="query"`, then call `index.query(vector=..., namespace="pono", top_k=...)`.
- **Verify** with `index.describe_index_stats()` — you should see the new vector count under the `pono` namespace.
