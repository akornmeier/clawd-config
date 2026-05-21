---
name: recall
description: Semantic search across all stored memories and reference knowledge in Pinecone (Bucket 01 — Memory and Bucket 02 — Knowledge). Trigger when user asks "what did we decide about X", "what did we say about Y last month", "what does [expert] say about Z", "search my notes for X", "do we have anything on", "find that thing about", or any retrieval question about past content. Returns top 3-5 hits with date and source citations, then synthesizes a 2-line answer. Requires Pinecone MCP server connected, or PINECONE_API_KEY env var. Configured indexes live in ~/.claude/memory-config.json. Do NOT use this skill for current state queries (e.g. "what's my strategy on X right now") — that's the strategy-awareness skill's job.
---

# Recall Skill (Bucket 01 + 02 — Memory & Knowledge)

Semantic search across past conversations and reference knowledge.

---

## Prerequisites

Same as wrap-up — Pinecone MCP or Python SDK, plus a `~/.claude/memory-config.json` listing available indexes:

```json
{
  "personal_index": "personal-memory",
  "knowledge_indexes": [
    { "name": "your-youtube", "topic": "your video transcripts and scripts" },
    { "name": "skool-community", "topic": "Skool community posts and sentiment" },
    { "name": "hormozi", "topic": "Alex Hormozi books and podcasts" }
  ],
  "embedding_model": "llama-text-embed-v2"
}
```

---

## When to fire

✅ *"What did we decide about pricing last month?"* → personal index
✅ *"What did we say about churn?"* → personal index
✅ *"What does Hormozi say about pricing?"* → hormozi index
✅ *"Search my video transcripts for 'agent failure'"* → your-youtube index
✅ *"Do we have anything on dashboard requests?"* → personal index (likely Customer Insights)
✅ *"Find that thing we worked on about wrap-up skills"* → personal index

❌ Do NOT fire for current state queries:
- *"What's my current strategy?"* → use **strategy-awareness** (QUERY mode)
- *"What's on my Don't-Do list?"* → use **strategy-awareness**
- *"What am I working on right now?"* → use **strategy-awareness**

If unsure: current state lives in `strategy.md` (strategy-awareness handles it). Past conversations and reference material live in Pinecone (recall handles it).

---

## Steps

### 1. Determine the index

Read `~/.claude/memory-config.json`. Match the query to the right index:

| Query mentions | Index |
|---|---|
| "we", "I decided", "last session", "last month" | personal_index |
| Named expert (Hormozi, Karpathy, etc.) | matching knowledge index |
| "my videos", "my transcripts", "my channel" | your-youtube (or matching) |
| "the community", "Skool members" | skool-community |
| Ambiguous | Ask user which index |

### 2. Run the search

**With Pinecone MCP:**
- Tool: `pinecone-query-ids` or `pinecone-fetch-vectors` (depends on MCP)
- Embed the query, run top-K=5 search against the chosen index

**With bundled script:**
```bash
python3 ~/.claude/skills/recall/search.py --query "<query>" --index <index> --k 5
```

### 3. Format the response

```markdown
**Found {{n}} relevant entries in `{{index}}`:**

1. **{{date}}** — {{topic line}}
   > "{{relevant excerpt}}"
   *Source: session-{{id}} · score: 0.87*

2. **{{date}}** — ...

---

**Synthesis:** {{2-line summary of the pattern across hits}}
```

### 4. Cite honestly

- Always show the date.
- Always show the source ID.
- Show the similarity score for the top hit.
- If scores are weak (< 0.65 cosine), say so: *"Top result is a weak match — you might not have logged this yet."*
- If no results: don't fabricate. Say *"Nothing in `{{index}}` matches that. Want me to check another index?"*

---

## Rules

- **Date first.** Recency matters — always lead with the date.
- **Quote, don't paraphrase.** Show the actual stored text.
- **Cite the source ID** so the user can find the full session log if they want.
- **Acknowledge weak matches.** Never imply confidence the data doesn't support.
- **Suggest follow-ups.** If the answer is partial, suggest: *"Want me to check `hormozi` or `skool-community` too?"*
- **Don't load entire results into the response.** Top 5 with excerpts, not full session dumps.

---

## Pairing

- **Knows nothing about current state.** For current strategy, defer to `strategy-awareness`.
- **Reads what `wrap-up` writes.** If the user asks about something they did this week and recall finds nothing, suggest: *"This session might not be wrapped yet — want me to wrap it now?"*
- **Reference knowledge requires bulk ingest.** If a knowledge index returns nothing, the data probably isn't loaded. Reference `setup/bulk-ingest.md` in the package.
