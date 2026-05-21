---
name: wrap-up
description: Captures session summaries to Pinecone (Bucket 01 — Memory). At the end of a Claude session, generates a structured summary of what was discussed, what was decided, what was built, and saves it both as a dated markdown log and as an embedded vector in the user's personal Pinecone index. Trigger when user says "wrap up", "save this session", "summarize and save", "end session", "log this", or at natural session-end moments after substantial work is done. Requires Pinecone MCP server connected, or PINECONE_API_KEY env var if using the bundled Python script. Do NOT trigger for trivial sessions or quick one-question chats — only when there's strategic substance worth recalling later.
---

# Wrap-up Skill (Bucket 01 — Memory)

Captures session summaries to Pinecone for long-term semantic recall. The diary.

---

## Prerequisites

The user must have ONE of these configured:

1. **Pinecone MCP server** (recommended) — connected via Claude Code's MCP config. Check by listing available MCP tools that start with `pinecone`.
2. **Pinecone Python SDK + API key** — `pip install pinecone-client`, plus `PINECONE_API_KEY` in env.

Index name lives at `~/.claude/memory-config.json`:
```json
{
  "personal_index": "personal-memory",
  "embedding_model": "llama-text-embed-v2",
  "dimension": 1024
}
```

If config is missing, run setup first (see `setup/pinecone-setup.md` in the package).

---

## When to fire

✅ User says: *"wrap up"*, *"save this session"*, *"summarize and save"*, *"log this session"*, *"end session"*
✅ User says variants of: *"that's all for today"*, *"thanks, we're done"* — and the session had real substance
✅ After completing a significant piece of work, the skill MAY proactively offer: *"Want me to wrap this session up for memory?"*

❌ Do NOT fire for short chats, troubleshooting one-liners, or sessions with no strategic substance.

---

## Steps

### 1. Generate the summary

Use this exact structure:

```markdown
# Session — {{YYYY-MM-DD HH:MM}}

## Topic
{{ONE_LINE — what this session was about}}

## What we worked on
- {{specific outcomes, files touched, decisions debated}}
- ...

## Decisions made
- {{actual decisions, not deliberations}}

## Key insights
- {{learnings, "ah-ha" moments, customer signals heard}}

## Open items / Next steps
- {{what's still pending}}
- ...

## Tags
{{comma-separated topical tags — e.g. memory-system, deck-rebuild, strategy-skill}}
```

Be specific. *"We worked on the SuperSkills deck"* beats *"we did some stuff."* Quote actual user phrasing where possible.

Keep the summary under 600 words. This is a recall index, not a verbatim transcript.

### 2. Save the markdown log

Append (or create) to `~/.claude/sessions/YYYY-MM-DD.md`. If the file exists for today, append the new session under a `---` divider.

### 3. Embed and upsert to Pinecone

**If Pinecone MCP is available**, use the MCP tools:
- Tool: `pinecone-upsert-vector` (or equivalent for the connected MCP)
- Body: the full summary text
- Metadata:
  ```json
  {
    "date": "YYYY-MM-DD",
    "topic": "<topic line>",
    "tags": ["tag1", "tag2"],
    "type": "session-summary"
  }
  ```
- ID: `session-YYYY-MM-DD-HHMM` (deterministic so re-runs upsert, don't duplicate)

**If using the bundled script**, run:
```bash
python3 ~/.claude/skills/wrap-up/upsert.py --summary-file ~/.claude/sessions/YYYY-MM-DD.md --tags "tag1,tag2"
```

### 4. Confirm in one line

> *"Saved to memory archive — ID `session-2026-04-26-1530`. Search it via the recall skill."*

---

## Rules

- **Strategic substance only.** No log for trivial exchanges.
- **Specifics beat summaries.** Name the file paths, the decisions, the customer quotes.
- **Decisions vs deliberations.** Capture what was decided, not the back-and-forth getting there (unless the user asks for verbose mode).
- **Keep it under 600 words.** Recall doesn't need verbatim — it needs a hook.
- **Tags matter.** Tag with the topic, the project, the relevant bucket — these are the filters that make recall fast.
- **Deterministic IDs.** `session-YYYY-MM-DD-HHMM` so accidental re-runs upsert (overwrite) instead of creating duplicates.

---

## Pairing

This skill writes to Pinecone. The `recall` skill reads from it. The `strategy-awareness` skill operates independently on `~/.claude/strategy.md` — but if the wrap-up captures a strategic decision, mention it: *"This session contained 2 strategic decisions — they should also be in your strategy.md via the strategy-awareness skill. Want me to verify?"*
