# Escalation Formats

Read this reference when step 9's summary has to carry an escalation — any `needs-human` verdict this round, or a pending decision detected in step 2 from a previous run. The ordinary summary format lives inline in step 9; only these two blocks are here, because most rounds have neither.

## needs-human decisions

These are rare but high-signal. Each `needs-human` agent returns a `decision_context` field with a structured analysis: what the reviewer said, what the agent investigated, why it needs a decision, concrete options with tradeoffs, and the agent's lean if it has one.

Present the `decision_context` directly -- it is already structured for the user to read and decide quickly:

```
Needs your input (count):

1. [decision_context from the agent -- includes quoted feedback,
   investigation findings, why it needs a decision, options with
   tradeoffs, and the agent's recommendation if any]
```

The `needs-human` threads already have a natural-sounding acknowledgment reply posted and remain open on the PR.

## Pending from a previous run

Threads detected in step 2 as already responded to but still unresolved. Surface them after the new work:

```
Still pending from a previous run (count):

1. [Thread path:line] -- [brief description of what's pending]
   Previous reply: [link to the existing reply]
   [Re-present the decision options if the original context is available,
   or summarize what was asked]
```

If there are only pending decisions and no new work was done, the summary is just the pending items.

## Asking

Ask about all pending decisions -- both new `needs-human` and previous-run pending -- together, in one blocking question rather than several.

Use `AskUserQuestion` (call `ToolSearch` with `select:AskUserQuestion` first if its schema isn't loaded) to present the decisions and wait for the user's response. After they decide, process the remaining items: fix the code, compose the reply, post it, and resolve the thread.

Fall back to presenting the decisions in the summary output and waiting in conversation only if it is unavailable or the call errors. Never silently skip. If the user doesn't respond, the items remain open on the PR for later handling.
