# Wrap Up Session

End-of-session capture. Use the **wrap-up skill** to summarize what was discussed in this session, save it as a dated markdown log to `~/.claude/sessions/`, and upsert it as an embedded vector to my personal Pinecone index for long-term semantic recall.

Optional context from the user: `$ARGUMENTS`

Steps:

1. Generate a structured summary using the format defined in the wrap-up skill (Topic, What we worked on, Decisions made, Key insights, Open items / Next steps, Tags).
2. Be specific. Quote actual decisions and customer signals where possible. Keep the summary under 600 words.
3. Save to `~/.claude/sessions/YYYY-MM-DD.md` (append if file exists for today).
4. Embed and upsert to Pinecone using my existing setup at `~/.claude/pinecone_memory.py` (or the Pinecone MCP if available). Use a deterministic ID like `session-YYYY-MM-DD-HHMM` so re-runs upsert instead of duplicate.
5. Confirm in one line: *"Saved to memory archive — ID `session-YYYY-MM-DD-HHMM`. Search via `/recall`."*

Do NOT fire if this session had no real substance.
