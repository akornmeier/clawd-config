# Recall

Semantic search across past memories and reference knowledge. Use the **recall skill** to query Pinecone for relevant past sessions, decisions, customer signals, or expert references.

The user's query: `$ARGUMENTS`

Steps:

1. If no query was provided, ask: *"What do you want me to search for?"*
2. Determine the right Pinecone index:
   - "we", "I decided", "last session" → personal index (e.g. `los-angeles`)
   - Named expert (Hormozi, Karpathy, etc.) → matching knowledge index
   - "my videos", "transcripts" → `jack-youtube` (or matching)
   - "Skool members", "the community" → `skool-community`
   - Ambiguous → ask which index
3. Run the search via `~/.claude/pinecone_memory.py query "<query>" --top-k 5` or via the Pinecone MCP if available.
4. Format results with date, source ID, and similarity score:
   ```
   1. **2026-04-22** — Topic line
      > "relevant excerpt"
      *Source: session-... · score: 0.87*
   ```
5. End with a 2-line synthesis of the pattern across hits.
6. If scores are weak (< 0.65 cosine), say so honestly. Don't fabricate confidence.
