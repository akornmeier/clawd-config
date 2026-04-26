> Source: https://code.claude.com/docs/en/sub-agents
> Snapshot: 2026-04-25
> Local cache for Claude Code agent reference. Re-fetch when behavior changes.

# Create custom subagents

> Create and use specialized AI subagents in Claude Code for task-specific workflows and improved context management.

Subagents are specialized AI assistants that handle specific types of tasks. Use one when a side task would flood your main conversation with search results, logs, or file contents you won't reference again: the subagent does that work in its own context and returns only the summary. Define a custom subagent when you keep spawning the same kind of worker with the same instructions.

Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions. When Claude encounters a task that matches a subagent's description, it delegates to that subagent, which works independently and returns results.

Subagents help you:

* **Preserve context** by keeping exploration and implementation out of your main conversation
* **Enforce constraints** by limiting which tools a subagent can use
* **Reuse configurations** across projects with user-level subagents
* **Specialize behavior** with focused system prompts for specific domains
* **Control costs** by routing tasks to faster, cheaper models like Haiku

## Built-in subagents

Claude Code includes built-in subagents that Claude automatically uses when appropriate. Each inherits the parent conversation's permissions with additional tool restrictions.

**Explore** — Fast read-only agent optimized for searching and analyzing codebases.
- Model: Haiku
- Tools: Read-only (denied Write/Edit)
- Thoroughness levels: `quick`, `medium`, `very thorough`

**Plan** — Research agent used during plan mode to gather context.
- Model: Inherits from main conversation
- Tools: Read-only

**General-purpose** — Capable agent for complex, multi-step tasks.
- Model: Inherits
- Tools: All tools

Other helpers: `statusline-setup` (Sonnet, when running `/statusline`), Claude Code Guide (Haiku, for questions about Claude Code).

## Quickstart: create your first subagent

Subagents are defined in Markdown files with YAML frontmatter. Create them via `/agents` or by adding files directly.

Walkthrough using `/agents`:

1. Run `/agents` in Claude Code
2. Switch to **Library** → **Create new agent** → **Personal**
3. Select **Generate with Claude** and describe the subagent
4. Select tools (deselect everything except read-only for a reviewer)
5. Pick a model (Sonnet for code analysis)
6. Choose a color
7. Configure memory (User scope = persistent at `~/.claude/agent-memory/`)
8. Press `s` or Enter to save

## Configure subagents

### Use the `/agents` command

Opens a tabbed interface. The **Running** tab shows live subagents and lets you open or stop them. The **Library** tab lets you view, create, edit, and delete subagents.

To list all configured subagents from the CLI: `claude agents`.

### Choose the subagent scope

Subagents are Markdown files with YAML frontmatter. Higher-priority locations win when names collide.

| Location                     | Scope                   | Priority    |
| :--------------------------- | :---------------------- | :---------- |
| Managed settings             | Organization-wide       | 1 (highest) |
| `--agents` CLI flag          | Current session         | 2           |
| `.claude/agents/`            | Current project         | 3           |
| `~/.claude/agents/`          | All your projects       | 4           |
| Plugin's `agents/` directory | Where plugin is enabled | 5 (lowest)  |

**CLI-defined subagents** as JSON:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

The `--agents` flag accepts the same frontmatter fields as file-based subagents.

### Write subagent files

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

The frontmatter defines metadata and configuration. The body becomes the system prompt. Subagents receive only this system prompt (plus basic environment details), not the full Claude Code system prompt.

A subagent starts in the main conversation's current working directory. `cd` does not persist between Bash calls. Use `isolation: worktree` for an isolated copy of the repo.

#### Supported frontmatter fields

| Field             | Required | Description                                                                                                                                                                                                                                          |
| :---------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`            | Yes      | Unique identifier using lowercase letters and hyphens                                                                                                                                                                                                |
| `description`     | Yes      | When Claude should delegate to this subagent                                                                                                                                                                                                         |
| `tools`           | No       | Tools the subagent can use. Inherits all tools if omitted                                                                                                                                                                                            |
| `disallowedTools` | No       | Tools to deny, removed from inherited or specified list                                                                                                                                                                                              |
| `model`           | No       | Model: `sonnet`, `opus`, `haiku`, full ID (e.g. `claude-opus-4-7`), or `inherit`. Defaults to `inherit`                                                                                                                                              |
| `permissionMode`  | No       | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, or `plan`                                                                                                                                                                          |
| `maxTurns`        | No       | Maximum agentic turns before the subagent stops                                                                                                                                                                                                      |
| `skills`          | No       | Skills to inject into context at startup                                                                                                                                                                                                             |
| `mcpServers`      | No       | MCP servers available to this subagent                                                                                                                                                                                                               |
| `hooks`           | No       | Lifecycle hooks scoped to this subagent                                                                                                                                                                                                              |
| `memory`          | No       | Persistent memory scope: `user`, `project`, or `local`                                                                                                                                                                                               |
| `background`      | No       | Set to `true` to always run as a background task                                                                                                                                                                                                     |
| `effort`          | No       | Effort level: `low`, `medium`, `high`, `xhigh`, `max`                                                                                                                                                                                                |
| `isolation`       | No       | Set to `worktree` for an isolated git worktree                                                                                                                                                                                                       |
| `color`           | No       | `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, or `cyan`                                                                                                                                                                              |
| `initialPrompt`   | No       | Auto-submitted as first user turn when running as main session agent                                                                                                                                                                                 |

### Choose a model

The `model` field accepts:
- Alias: `sonnet`, `opus`, `haiku`
- Full model ID: e.g. `claude-opus-4-7`, `claude-sonnet-4-6`
- `inherit`: same model as main conversation

Resolution order:
1. `CLAUDE_CODE_SUBAGENT_MODEL` environment variable
2. Per-invocation `model` parameter
3. Subagent definition's `model` frontmatter
4. Main conversation's model

### Control subagent capabilities

#### Available tools

By default, subagents inherit all tools. Restrict with `tools` (allowlist) or `disallowedTools` (denylist):

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
---
```

```yaml
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit
---
```

If both are set, `disallowedTools` is applied first.

#### Restrict which subagents can be spawned

When an agent runs as the main thread with `claude --agent`, restrict spawnable subagents:

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

#### Scope MCP servers to a subagent

```yaml
---
name: browser-tester
description: Tests features in a real browser using Playwright
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github
---
```

#### Permission modes

| Mode                | Behavior                                                                  |
| :------------------ | :------------------------------------------------------------------------ |
| `default`           | Standard permission checking with prompts                                 |
| `acceptEdits`       | Auto-accept file edits and common filesystem commands                     |
| `auto`              | Background classifier reviews commands and protected-directory writes    |
| `dontAsk`           | Auto-deny permission prompts (explicitly allowed tools still work)       |
| `bypassPermissions` | Skip permission prompts                                                   |
| `plan`              | Plan mode (read-only exploration)                                         |

If parent uses `bypassPermissions` or `acceptEdits`, this takes precedence and cannot be overridden.

#### Preload skills into subagents

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---
```

The full content of each skill is injected into the subagent's context at startup.

#### Enable persistent memory

```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---
```

| Scope     | Location                                      |
| :-------- | :-------------------------------------------- |
| `user`    | `~/.claude/agent-memory/<name-of-agent>/`     |
| `project` | `.claude/agent-memory/<name-of-agent>/`       |
| `local`   | `.claude/agent-memory-local/<name-of-agent>/` |

When memory is enabled, Read/Write/Edit are auto-enabled and the first 200 lines or 25KB of `MEMORY.md` are loaded into the system prompt.

#### Conditional rules with hooks

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---
```

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b' > /dev/null; then
  echo "Blocked: Only SELECT queries are allowed" >&2
  exit 2
fi

exit 0
```

#### Disable specific subagents

```json
{
  "permissions": {
    "deny": ["Agent(Explore)", "Agent(my-custom-agent)"]
  }
}
```

Or via CLI: `claude --disallowedTools "Agent(Explore)"`.

### Define hooks for subagents

Two ways:
1. In the subagent's frontmatter (run only while subagent is active)
2. In `settings.json` (run in main session on `SubagentStart` / `SubagentStop`)

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

Project-level hooks for subagent lifecycle:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db-connection.sh" }
        ]
      }
    ]
  }
}
```

## Work with subagents

### Automatic delegation

Claude delegates based on the task description, the `description` field, and current context. Include phrases like "use proactively" to encourage delegation.

### Invoke subagents explicitly

Three patterns:

* **Natural language**: name the subagent in your prompt
  ```
  Use the test-runner subagent to fix failing tests
  ```

* **@-mention**: guarantees the subagent runs
  ```
  @"code-reviewer (agent)" look at the auth changes
  ```

* **Session-wide**: `claude --agent code-reviewer`

To make it the default for a project, set `agent` in `.claude/settings.json`:

```json
{ "agent": "code-reviewer" }
```

### Foreground vs background

* **Foreground**: blocks main conversation; permission prompts and clarifying questions pass through
* **Background**: runs concurrently; permissions pre-approved upfront, then auto-denied for anything not pre-approved

Press **Ctrl+B** to background a running task. Set `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` to disable.

### Common patterns

**Isolate high-volume operations**: keep verbose output (test runs, doc fetches, log processing) in the subagent's context.

**Run parallel research**: spawn multiple subagents for independent investigations.

**Chain subagents**: ask Claude to use subagents in sequence.

### Choose between subagents and main conversation

Use the **main conversation** when:
* Frequent back-and-forth needed
* Multiple phases share significant context
* Quick targeted change
* Latency matters

Use **subagents** when:
* Verbose output not needed in main context
* Tool restrictions or permissions need enforcement
* Self-contained work that returns a summary

> Subagents cannot spawn other subagents. Use Skills or chain from main conversation.

### Resume subagents

Each invocation creates a new instance with fresh context. Resume to continue an existing subagent's work — it retains full conversation history, tool calls, results, and reasoning.

Subagent transcripts persist in `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`.

## Fork the current conversation

A fork is a subagent that inherits the entire conversation so far instead of starting fresh. Enable with `CLAUDE_CODE_FORK_SUBAGENT=1`. Use for:
- Side tasks needing too much background to re-explain
- Trying multiple approaches in parallel from the same starting point

```
/fork draft unit tests for the parser changes so far
```

|                         | Fork                             | Named subagent                                         |
| :---------------------- | :------------------------------- | :----------------------------------------------------- |
| Context                 | Full conversation history        | Fresh context with the prompt you pass                 |
| System prompt and tools | Same as main session             | From subagent's definition file                        |
| Model                   | Same as main session             | From subagent's `model` field                          |
| Permissions             | Prompts surface in your terminal | Pre-approved before launch, then auto-denied          |
| Prompt cache            | Shared with main session         | Separate cache                                         |

## Example subagents

### Code reviewer

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Data scientist

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly
```

## Best practices

* **Design focused subagents**: each should excel at one specific task
* **Write detailed descriptions**: Claude uses the description to decide when to delegate
* **Limit tool access**: grant only necessary permissions
* **Check into version control**: share project subagents with your team
