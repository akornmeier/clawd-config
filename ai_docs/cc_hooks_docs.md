> Source: https://code.claude.com/docs/en/hooks
> Snapshot: 2026-04-25
> Local cache for Claude Code agent reference. Re-fetch when behavior changes.

# Hooks Reference

> Reference for Claude Code hook events, configuration schema, JSON input/output formats, exit codes, async hooks, HTTP hooks, prompt hooks, and MCP tool hooks.

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. Use this reference to look up event schemas, configuration options, JSON input/output formats, and advanced features like async hooks, HTTP hooks, and MCP tool hooks.

## Hook Lifecycle

Hooks fire at specific points during a Claude Code session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision.

Events fall into three cadences:
- **Once per session**: `SessionStart`, `SessionEnd`
- **Once per turn**: `UserPromptSubmit`, `Stop`, `StopFailure`
- **On every tool call**: `PreToolUse`, `PostToolUse`

| Event                 | When it fires                                                                                                                                          |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart`        | When a session begins or resumes                                                                                                                       |
| `UserPromptSubmit`    | When you submit a prompt, before Claude processes it                                                                                                   |
| `UserPromptExpansion` | When a user-typed command expands into a prompt, before it reaches Claude. Can block the expansion                                                     |
| `PreToolUse`          | Before a tool call executes. Can block it                                                                                                              |
| `PermissionRequest`   | When a permission dialog appears                                                                                                                       |
| `PermissionDenied`    | When a tool call is denied by the auto mode classifier. Return `{retry: true}` to tell the model it may retry the denied tool call                     |
| `PostToolUse`         | After a tool call succeeds                                                                                                                             |
| `PostToolUseFailure`  | After a tool call fails                                                                                                                                |
| `PostToolBatch`       | After a full batch of parallel tool calls resolves, before the next model call                                                                         |
| `Notification`        | When Claude Code sends a notification                                                                                                                  |
| `SubagentStart`       | When a subagent is spawned                                                                                                                             |
| `SubagentStop`        | When a subagent finishes                                                                                                                               |
| `TaskCreated`         | When a task is being created via `TaskCreate`                                                                                                          |
| `TaskCompleted`       | When a task is being marked as completed                                                                                                               |
| `Stop`                | When Claude finishes responding                                                                                                                        |
| `StopFailure`         | When the turn ends due to an API error. Output and exit code are ignored                                                                               |
| `TeammateIdle`        | When an agent team teammate is about to go idle                                                                                                       |
| `InstructionsLoaded`  | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context                                                                                   |
| `ConfigChange`        | When a configuration file changes during a session                                                                                                     |
| `CwdChanged`          | When the working directory changes                                                                                                                    |
| `FileChanged`         | When a watched file changes on disk                                                                                                                   |
| `WorktreeCreate`      | When a worktree is being created via `--worktree` or `isolation: "worktree"`                                                                           |
| `WorktreeRemove`      | When a worktree is being removed                                                                                                                      |
| `PreCompact`          | Before context compaction                                                                                                                              |
| `PostCompact`         | After context compaction completes                                                                                                                    |
| `Elicitation`         | When an MCP server requests user input during a tool call                                                                                              |
| `ElicitationResult`   | After a user responds to an MCP elicitation, before the response is sent back to the server                                                            |
| `SessionEnd`          | When a session terminates                                                                                                                              |

## Configuration

Hooks are defined in JSON settings files. The configuration has three levels of nesting:

1. Choose a hook event to respond to, like `PreToolUse` or `Stop`
2. Add a matcher group to filter when it fires, like "only for the Bash tool"
3. Define one or more hook handlers to run when matched

### Hook Locations

| Location                                     | Scope                         | Shareable                          |
| :------------------------------------------- | :---------------------------- | :--------------------------------- |
| `~/.claude/settings.json`                    | All your projects             | No, local to your machine          |
| `.claude/settings.json`                      | Single project                | Yes, can be committed to the repo  |
| `.claude/settings.local.json`                | Single project                | No, gitignored                     |
| Managed policy settings                      | Organization-wide             | Yes, admin-controlled              |
| Plugin `hooks/hooks.json`                    | When plugin is enabled        | Yes, bundled with the plugin       |
| Skill or agent frontmatter                   | While the component is active | Yes, defined in the component file |

### Matcher Patterns

The `matcher` field filters when hooks fire:

| Matcher value                       | Evaluated as                                          | Example                                                                                                            |
| :---------------------------------- | :---------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `"*"`, `""`, or omitted             | Match all                                             | fires on every occurrence of the event                                                                             |
| Only letters, digits, `_`, and `\|` | Exact string, or `\|`-separated list of exact strings | `Bash` matches only the Bash tool; `Edit\|Write` matches either tool exactly                                       |
| Contains any other character        | JavaScript regular expression                         | `^Notebook` matches any tool starting with Notebook; `mcp__memory__.*` matches every tool from the `memory` server |

Each event type matches on a different field:

| Event                                                                                      | What the matcher filters     | Example matcher values                                                                                                    |
| :----------------------------------------------------------------------------------------- | :--------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | tool name                    | `Bash`, `Edit\|Write`, `mcp__.*`                                                                                          |
| `SessionStart`                                                                             | how the session started      | `startup`, `resume`, `clear`, `compact`                                                                                   |
| `SessionEnd`                                                                               | why the session ended        | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`                                  |
| `Notification`                                                                             | notification type            | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`                                                  |
| `SubagentStart`                                                                            | agent type                   | `Bash`, `Explore`, `Plan`, or custom agent names                                                                          |
| `PreCompact`, `PostCompact`                                                                | what triggered compaction    | `manual`, `auto`                                                                                                          |
| `SubagentStop`                                                                             | agent type                   | same values as `SubagentStart`                                                                                            |
| `ConfigChange`                                                                             | configuration source         | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills`                                        |
| `CwdChanged`                                                                               | no matcher support           | always fires on every directory change                                                                                    |
| `FileChanged`                                                                              | literal filenames to watch   | `.envrc\|.env`                                                                                                            |
| `StopFailure`                                                                              | error type                   | `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` |
| `InstructionsLoaded`                                                                       | load reason                  | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`                                              |
| `UserPromptExpansion`                                                                      | command name                 | your skill or command names                                                                                               |
| `Elicitation`                                                                              | MCP server name              | your configured MCP server names                                                                                          |
| `ElicitationResult`                                                                        | MCP server name              | same values as `Elicitation`                                                                                              |
| `UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove` | no matcher support | always fires on every occurrence                                                                  |

### Hook Handler Fields

Each object in the inner `hooks` array is a hook handler: the shell command, HTTP endpoint, MCP tool, LLM prompt, or agent that runs when the matcher matches. There are five types:

* **Command hooks** (`type: "command"`): run a shell command
* **HTTP hooks** (`type: "http"`): send the event's JSON input as an HTTP POST request to a URL
* **MCP tool hooks** (`type: "mcp_tool"`): call a tool on an already-connected MCP server
* **Prompt hooks** (`type: "prompt"`): send a prompt to a Claude model for single-turn evaluation
* **Agent hooks** (`type: "agent"`): spawn a subagent that can use tools to verify conditions

#### Common Fields

| Field           | Required | Description                                                                                                                                                                                |
| :-------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `type`          | yes      | `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, or `"agent"`                                                                                                                              |
| `if`            | no       | Permission rule syntax to filter when this hook runs, such as `"Bash(git *)"` or `"Edit(*.ts)"`. Only evaluated on tool events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, and `PermissionDenied` |
| `timeout`       | no       | Seconds before canceling. Defaults: 600 for command, 30 for prompt, 60 for agent                                                                                                          |
| `statusMessage` | no       | Custom spinner message displayed while the hook runs                                                                                                                                       |
| `once`          | no       | If `true`, runs once per session then is removed. Only honored for hooks declared in skill frontmatter                                                                                     |

#### Command Hook Fields

| Field         | Required | Description                                                                                       |
| :------------ | :------- | :------------------------------------------------------------------------------------------------ |
| `command`     | yes      | Shell command to execute                                                                          |
| `async`       | no       | If `true`, runs in the background without blocking                                                |
| `asyncRewake` | no       | If `true`, runs in the background and wakes Claude on exit code 2. Implies `async`                |
| `shell`       | no       | Shell to use for this hook. Accepts `"bash"` (default) or `"powershell"`                          |

#### HTTP Hook Fields

| Field            | Required | Description                                                                                                                                |
| :--------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `url`            | yes      | URL to send the POST request to                                                                                                            |
| `headers`        | no       | Additional HTTP headers as key-value pairs. Values support environment variable interpolation using `$VAR_NAME` or `${VAR_NAME}` syntax    |
| `allowedEnvVars` | no       | List of environment variable names that may be interpolated into header values                                                             |

#### MCP Tool Hook Fields

| Field    | Required | Description                                                                                                                                 |
| :------- | :------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| `server` | yes      | Name of a configured MCP server. The server must already be connected; the hook never triggers an OAuth or connection flow                  |
| `tool`   | yes      | Name of the tool to call on that server                                                                                                     |
| `input`  | no       | Arguments passed to the tool. String values support `${path}` substitution from the hook's JSON input, such as `"${tool_input.file_path}"` |

#### Prompt and Agent Hook Fields

| Field    | Required | Description                                                          |
| :------- | :------- | :------------------------------------------------------------------- |
| `prompt` | yes      | Prompt text to send to the model. Use `$ARGUMENTS` as a placeholder  |
| `model`  | no       | Model to use for evaluation. Defaults to a fast model                |

### Reference Scripts by Path

Use environment variables to reference hook scripts:

* `$CLAUDE_PROJECT_DIR`: the project root
* `${CLAUDE_PLUGIN_ROOT}`: the plugin's installation directory
* `${CLAUDE_PLUGIN_DATA}`: the plugin's persistent data directory

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/check-style.sh"
          }
        ]
      }
    ]
  }
}
```

### Hooks in Skills and Agents

Hooks can be defined directly in skills and subagents using frontmatter:

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

### The `/hooks` Menu

Type `/hooks` in Claude Code to open a read-only browser for your configured hooks. The menu shows every hook event with a count of configured hooks, lets you drill into matchers, and shows the full details of each hook handler.

### Disable or Remove Hooks

To remove a hook, delete its entry from the settings JSON file.

To temporarily disable all hooks without removing them, set `"disableAllHooks": true` in your settings file:

```json
{
  "disableAllHooks": true
}
```

## Hook Input and Output

Command hooks receive JSON data via stdin and communicate results through exit codes, stdout, and stderr. HTTP hooks receive the same JSON as the POST request body and communicate results through the HTTP response body.

### Common Input Fields

| Field             | Description                                                                                                                                                          |
| :---------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `session_id`      | Current session identifier                                                                                                                                           |
| `transcript_path` | Path to conversation JSON                                                                                                                                            |
| `cwd`             | Current working directory when the hook is invoked                                                                                                                   |
| `permission_mode` | Current permission mode: `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, or `"bypassPermissions"`                                                    |
| `hook_event_name` | Name of the event that fired                                                                                                                                         |

When running with `--agent` or inside a subagent, two additional fields are included:

| Field        | Description                                                                                                |
| :----------- | :--------------------------------------------------------------------------------------------------------- |
| `agent_id`   | Unique identifier for the subagent. Present only when the hook fires inside a subagent call               |
| `agent_type` | Agent name (for example, `"Explore"` or `"security-reviewer"`)                                            |

### Exit Code Output

The exit code from your hook command tells Claude Code whether the action should proceed, be blocked, or be ignored.

**Exit 0** means success. Claude Code parses stdout for JSON output fields.

**Exit 2** means a blocking error. Claude Code ignores stdout and any JSON in it. Instead, stderr text is fed back to Claude as an error message.

**Any other exit code** is a non-blocking error for most hook events. The transcript shows a `<hook name> hook error` notice.

#### Exit Code 2 Behavior Per Event

| Hook event            | Can block? | What happens on exit 2                                                            |
| :-------------------- | :--------- | :-------------------------------------------------------------------------------- |
| `PreToolUse`          | Yes        | Blocks the tool call                                                              |
| `PermissionRequest`   | Yes        | Denies the permission                                                             |
| `UserPromptSubmit`    | Yes        | Blocks prompt processing and erases the prompt                                    |
| `UserPromptExpansion` | Yes        | Blocks the expansion                                                              |
| `Stop`                | Yes        | Prevents Claude from stopping, continues the conversation                         |
| `SubagentStop`        | Yes        | Prevents the subagent from stopping                                               |
| `TeammateIdle`        | Yes        | Prevents the teammate from going idle                                             |
| `TaskCreated`         | Yes        | Rolls back the task creation                                                      |
| `TaskCompleted`       | Yes        | Prevents the task from being marked as completed                                  |
| `ConfigChange`        | Yes        | Blocks the configuration change from taking effect (except `policy_settings`)     |
| `StopFailure`         | No         | Output and exit code are ignored                                                  |
| `PostToolUse`         | No         | Shows stderr to Claude (tool already ran)                                         |
| `PostToolUseFailure`  | No         | Shows stderr to Claude (tool already failed)                                      |
| `PostToolBatch`       | Yes        | Stops the agentic loop before the next model call                                 |
| `PermissionDenied`    | No         | Exit code and stderr are ignored. Use JSON `hookSpecificOutput.retry: true`       |
| `Notification`        | No         | Shows stderr to user only                                                         |
| `SubagentStart`       | No         | Shows stderr to user only                                                         |
| `SessionStart`        | No         | Shows stderr to user only                                                         |
| `SessionEnd`          | No         | Shows stderr to user only                                                         |
| `CwdChanged`          | No         | Shows stderr to user only                                                         |
| `FileChanged`         | No         | Shows stderr to user only                                                         |
| `PreCompact`          | Yes        | Blocks compaction                                                                 |
| `PostCompact`         | No         | Shows stderr to user only                                                         |
| `Elicitation`         | Yes        | Denies the elicitation                                                            |
| `ElicitationResult`   | Yes        | Blocks the response (action becomes decline)                                      |
| `WorktreeCreate`      | Yes        | Any non-zero exit code causes worktree creation to fail                           |
| `WorktreeRemove`      | No         | Failures are logged in debug mode only                                            |
| `InstructionsLoaded`  | No         | Exit code is ignored                                                              |

### HTTP Response Handling

HTTP hooks use HTTP status codes and response bodies instead of exit codes and stdout:

* **2xx with an empty body**: success, equivalent to exit code 0 with no output
* **2xx with a plain text body**: success, the text is added as context
* **2xx with a JSON body**: success, parsed using the same JSON output schema as command hooks
* **Non-2xx status**: non-blocking error, execution continues
* **Connection failure or timeout**: non-blocking error, execution continues

### JSON Output

Exit codes let you allow or block, but JSON output gives you finer-grained control. Exit 0 and print a JSON object to stdout.

```json
{
  "continue": false,
  "stopReason": "Build failed, fix errors before continuing"
}
```

| Field            | Default | Description                                                                       |
| :--------------- | :------ | :-------------------------------------------------------------------------------- |
| `continue`       | `true`  | If `false`, Claude stops processing entirely after the hook runs                  |
| `stopReason`     | none    | Message shown to the user when `continue` is `false`                              |
| `suppressOutput` | `false` | If `true`, omits stdout from the debug log                                        |
| `systemMessage`  | none    | Warning message shown to the user                                                 |

#### Decision Control

| Events                                                                                                                              | Decision pattern               | Key fields                                                                                                          |
| :---------------------------------------------------------------------------------------------------------------------------------- | :----------------------------- | :------------------------------------------------------------------------------------------------------------------ |
| UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact | Top-level `decision`           | `decision: "block"`, `reason`                                                                                       |
| TeammateIdle, TaskCreated, TaskCompleted                                                                                            | Exit code or `continue: false` | Exit code 2 blocks the action with stderr feedback                                                                  |
| PreToolUse                                                                                                                          | `hookSpecificOutput`           | `permissionDecision` (allow/deny/ask/defer), `permissionDecisionReason`                                             |
| PermissionRequest                                                                                                                   | `hookSpecificOutput`           | `decision.behavior` (allow/deny)                                                                                    |
| PermissionDenied                                                                                                                    | `hookSpecificOutput`           | `retry: true` tells the model it may retry the denied tool call                                                     |
| WorktreeCreate                                                                                                                      | path return                    | Command hook prints path on stdout; HTTP hook returns `hookSpecificOutput.worktreePath`                             |
| Elicitation                                                                                                                         | `hookSpecificOutput`           | `action` (accept/decline/cancel), `content` (form field values for accept)                                          |
| ElicitationResult                                                                                                                   | `hookSpecificOutput`           | `action` (accept/decline/cancel), `content` (form field values override)                                            |

## Hook Events

### SessionStart

Runs when Claude Code starts a new session or resumes an existing session. Useful for loading development context or setting up environment variables.

| Matcher   | When it fires                          |
| :-------- | :------------------------------------- |
| `startup` | New session                            |
| `resume`  | `--resume`, `--continue`, or `/resume` |
| `clear`   | `/clear`                               |
| `compact` | Auto or manual compaction              |

#### SessionStart Input

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../00893aaf-19fa-41d2-8238-13269b9b3ca0.jsonl",
  "cwd": "/Users/...",
  "hook_event_name": "SessionStart",
  "source": "startup",
  "model": "claude-sonnet-4-6"
}
```

#### SessionStart Decision Control

Any text your hook script prints to stdout is added as context for Claude:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "My additional context here"
  }
}
```

#### Persist Environment Variables

SessionStart hooks have access to the `CLAUDE_ENV_FILE` environment variable, which provides a file path where you can persist environment variables for subsequent Bash commands:

```bash
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

### UserPromptSubmit

Runs when the user submits a prompt, before Claude processes it. Use to add context, validate prompts, or block certain types of prompts.

#### UserPromptSubmit Input

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../00893aaf.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Write a function to calculate the factorial of a number"
}
```

#### UserPromptSubmit Decision Control

```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here",
    "sessionTitle": "My session title"
  }
}
```

### UserPromptExpansion

Runs when a user-typed slash command expands into a prompt before reaching Claude.

#### UserPromptExpansion Input

```json
{
  "session_id": "abc123",
  "hook_event_name": "UserPromptExpansion",
  "expansion_type": "slash_command",
  "command_name": "example-skill",
  "command_args": "arg1 arg2",
  "command_source": "plugin",
  "prompt": "/example-skill arg1 arg2"
}
```

### PreToolUse

Runs after Claude creates tool parameters and before processing the tool call. Matches on tool name: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `ExitPlanMode`, and any MCP tool names.

#### PreToolUse Input

```json
{
  "session_id": "abc123",
  "transcript_path": "/Users/.../00893aaf.jsonl",
  "cwd": "/Users/...",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

##### Bash Tool Input

| Field               | Type    | Example            | Description                                   |
| :------------------ | :------ | :----------------- | :-------------------------------------------- |
| `command`           | string  | `"npm test"`       | The shell command to execute                  |
| `description`       | string  | `"Run test suite"` | Optional description of what the command does |
| `timeout`           | number  | `120000`           | Optional timeout in milliseconds              |
| `run_in_background` | boolean | `false`            | Whether to run the command in background      |

##### Write Tool Input

| Field       | Type   | Example               | Description                        |
| :---------- | :----- | :-------------------- | :--------------------------------- |
| `file_path` | string | `"/path/to/file.txt"` | Absolute path to the file to write |
| `content`   | string | `"file content"`      | Content to write to the file       |

##### Edit Tool Input

| Field         | Type    | Example               | Description                        |
| :------------ | :------ | :-------------------- | :--------------------------------- |
| `file_path`   | string  | `"/path/to/file.txt"` | Absolute path to the file to edit  |
| `old_string`  | string  | `"original text"`     | Text to find and replace           |
| `new_string`  | string  | `"replacement text"`  | Replacement text                   |
| `replace_all` | boolean | `false`               | Whether to replace all occurrences |

##### Read Tool Input

| Field       | Type   | Example               | Description                                |
| :---------- | :----- | :-------------------- | :----------------------------------------- |
| `file_path` | string | `"/path/to/file.txt"` | Absolute path to the file to read          |
| `offset`    | number | `10`                  | Optional line number to start reading from |
| `limit`     | number | `50`                  | Optional number of lines to read           |

##### Glob Tool Input

| Field     | Type   | Example          | Description                                   |
| :-------- | :----- | :--------------- | :-------------------------------------------- |
| `pattern` | string | `"**/*.ts"`      | Glob pattern to match files against           |
| `path`    | string | `"/path/to/dir"` | Optional directory to search in               |

##### Grep Tool Input

| Field         | Type    | Example          | Description                                                     |
| :------------ | :------ | :--------------- | :-------------------------------------------------------------- |
| `pattern`     | string  | `"TODO.*fix"`    | Regular expression pattern to search for                        |
| `path`        | string  | `"/path/to/dir"` | Optional file or directory to search in                         |
| `glob`        | string  | `"*.ts"`         | Optional glob pattern to filter files                           |
| `output_mode` | string  | `"content"`      | `"content"`, `"files_with_matches"`, or `"count"`               |
| `-i`          | boolean | `true`           | Case insensitive search                                         |
| `multiline`   | boolean | `false`          | Enable multiline matching                                       |

##### WebFetch Tool Input

| Field    | Type   | Example                       | Description                          |
| :------- | :----- | :---------------------------- | :----------------------------------- |
| `url`    | string | `"https://example.com/api"`   | URL to fetch content from            |
| `prompt` | string | `"Extract the API endpoints"` | Prompt to run on the fetched content |

##### Agent Tool Input

| Field           | Type   | Example                    | Description                                  |
| :-------------- | :----- | :------------------------- | :------------------------------------------- |
| `prompt`        | string | `"Find all API endpoints"` | The task for the agent to perform            |
| `description`   | string | `"Find API endpoints"`     | Short description of the task                |
| `subagent_type` | string | `"Explore"`                | Type of specialized agent to use             |
| `model`         | string | `"sonnet"`                 | Optional model alias to override the default |

#### PreToolUse Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "My reason here",
    "updatedInput": {
      "field_to_modify": "new value"
    },
    "additionalContext": "Current environment: production. Proceed with caution."
  }
}
```

| Field                      | Description                                                                                                              |
| :------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| `permissionDecision`       | `"allow"` skips the permission prompt. `"deny"` prevents the tool call. `"ask"` prompts the user. `"defer"` exits        |
| `permissionDecisionReason` | For `"allow"` and `"ask"`, shown to the user but not Claude. For `"deny"`, shown to Claude. For `"defer"`, ignored      |
| `updatedInput`             | Modifies the tool's input parameters before execution. Replaces the entire input object                                  |
| `additionalContext`        | String added to Claude's context before the tool executes                                                                |

### PermissionRequest

Runs when the user is shown a permission dialog. Use to allow or deny on behalf of the user.

#### PermissionRequest Input

```json
{
  "session_id": "abc123",
  "hook_event_name": "PermissionRequest",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf node_modules",
    "description": "Remove node_modules directory"
  },
  "permission_suggestions": [
    {
      "type": "addRules",
      "rules": [{ "toolName": "Bash", "ruleContent": "rm -rf node_modules" }],
      "behavior": "allow",
      "destination": "localSettings"
    }
  ]
}
```

#### PermissionRequest Decision Control

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": {
        "command": "npm run lint"
      }
    }
  }
}
```

### PostToolUse

Runs immediately after a tool completes successfully.

#### PostToolUse Input

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.txt",
    "content": "file content"
  },
  "tool_response": {
    "filePath": "/path/to/file.txt",
    "success": true
  },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}
```

#### PostToolUse Decision Control

```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Additional information for Claude"
  }
}
```

### PostToolUseFailure

Runs when a tool execution fails.

#### PostToolUseFailure Input

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "tool_use_id": "toolu_01ABC123...",
  "error": "Command exited with non-zero status code 1",
  "is_interrupt": false,
  "duration_ms": 4187
}
```

### PermissionDenied

Runs when a tool call is denied by the auto mode classifier. Return `{retry: true}` to tell the model it may retry.

```json
{
  "session_id": "abc123",
  "hook_event_name": "PermissionDenied",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm file.txt"
  },
  "tool_use_id": "toolu_01ABC123...",
  "denial_reason": "Destructive command in auto mode"
}
```

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionDenied",
    "retry": true
  }
}
```

### PostToolBatch

Runs after a full batch of parallel tool calls resolves, before the next model call.

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostToolBatch",
  "tool_results": [
    {
      "tool_name": "Read",
      "tool_input": { "file_path": "/path/to/file.txt" },
      "tool_response": { "content": "file content", "success": true },
      "tool_use_id": "toolu_01ABC123...",
      "status": "success",
      "duration_ms": 5
    }
  ],
  "batch_id": "batch_123abc"
}
```

### Stop

Runs when Claude finishes responding.

```json
{
  "session_id": "abc123",
  "hook_event_name": "Stop",
  "stop_reason": "end_turn"
}
```

```json
{
  "decision": "block",
  "reason": "Insufficient context. Please provide more details.",
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "Try being more specific about requirements"
  }
}
```

### StopFailure

Runs when the turn ends due to an API error. Output and exit code are ignored.

```json
{
  "session_id": "abc123",
  "hook_event_name": "StopFailure",
  "error_type": "rate_limit",
  "error_message": "Rate limit exceeded"
}
```

### SubagentStart / SubagentStop

```json
{
  "session_id": "abc123",
  "hook_event_name": "SubagentStart",
  "agent_type": "Explore",
  "agent_id": "subagent_01ABC123...",
  "prompt": "Find all TypeScript files"
}
```

```json
{
  "session_id": "abc123",
  "hook_event_name": "SubagentStop",
  "agent_type": "Explore",
  "agent_id": "subagent_01ABC123...",
  "stop_reason": "end_turn"
}
```

### TaskCreated / TaskCompleted

Fire when tasks are created or completed via `TaskCreate`. Exit code 2 blocks the action.

```json
{
  "session_id": "abc123",
  "hook_event_name": "TaskCreated",
  "task_title": "Fix bug in payment processing",
  "task_description": "Resolve issue with subscription renewals"
}
```

### Notification

Runs when Claude Code sends a notification.

```json
{
  "session_id": "abc123",
  "hook_event_name": "Notification",
  "notification_type": "permission_prompt",
  "notification_title": "Permission Required",
  "notification_body": "Claude wants to run a Bash command"
}
```

### TeammateIdle

Runs when an agent team teammate is about to go idle.

```json
{
  "session_id": "abc123",
  "hook_event_name": "TeammateIdle",
  "teammate_name": "search-specialist",
  "teammate_role": "Explore"
}
```

### ConfigChange

Runs when a configuration file changes during a session.

```json
{
  "session_id": "abc123",
  "hook_event_name": "ConfigChange",
  "config_source": "project_settings",
  "config_file_path": "/Users/my-project/.claude/settings.json",
  "change_summary": "Updated hook configuration"
}
```

### CwdChanged

Runs when the working directory changes.

```json
{
  "session_id": "abc123",
  "hook_event_name": "CwdChanged",
  "previous_cwd": "/Users/my-project",
  "new_cwd": "/Users/my-project/src"
}
```

### FileChanged

Runs when a watched file changes on disk. The matcher uses literal filenames separated by `|`:

```json
{ "matcher": ".envrc|.env|.node-version" }
```

```json
{
  "session_id": "abc123",
  "hook_event_name": "FileChanged",
  "file_path": "/Users/my-project/.env",
  "change_type": "modified"
}
```

### PreCompact / PostCompact

```json
{
  "session_id": "abc123",
  "hook_event_name": "PreCompact",
  "compaction_reason": "manual"
}
```

```json
{
  "session_id": "abc123",
  "hook_event_name": "PostCompact",
  "compaction_reason": "manual",
  "messages_before": 50,
  "messages_after": 25
}
```

### WorktreeCreate / WorktreeRemove

```json
{
  "session_id": "abc123",
  "hook_event_name": "WorktreeCreate",
  "branch": "feature/new-feature",
  "base_directory": "/Users/my-project"
}
```

The hook prints the worktree path to stdout on exit 0:

```bash
#!/bin/bash
echo "/custom/path/to/worktree"
exit 0
```

### Elicitation / ElicitationResult

Runs when an MCP server requests user input during a tool call.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": { "channel": "general" }
  }
}
```

### SessionEnd

Runs when a session terminates. No decision control.

```json
{
  "session_id": "abc123",
  "hook_event_name": "SessionEnd",
  "end_reason": "end_turn"
}
```

## Example Hook Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/lint-check.sh"
          }
        ]
      }
    ]
  }
}
```

## Example: Block Destructive Commands

```bash
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0
fi
```

## Security Considerations

- Hook commands run with your user permissions. Treat hook scripts as trusted code.
- Validate and sanitize `tool_input` fields parsed from JSON before passing to shells.
- Prefer absolute paths or `$CLAUDE_PROJECT_DIR`-relative paths to avoid PATH ambiguity.
- For HTTP hooks, never embed secrets in `url`; use `headers` with `allowedEnvVars`.
- Use `.claude/settings.local.json` for hooks that depend on machine-local paths.
