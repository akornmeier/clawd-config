> Source: https://code.claude.com/docs/en/skills (custom commands have been merged into Skills)
> Snapshot: 2026-04-25
> Local cache for Claude Code agent reference. Re-fetch when behavior changes.

# Custom slash commands (now Skills)

> **Important — terminology shift:** Custom slash commands have been merged into Skills. A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Existing `.claude/commands/` files keep working. Skills add: a directory for supporting files, frontmatter to control invocation, and the ability for Claude to load them automatically when relevant.

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Create a skill when you keep pasting the same playbook, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact.

## Bundled skills

Built-in: `/simplify`, `/batch`, `/debug`, `/loop`, `/claude-api`, etc. Bundled skills are prompt-based — Claude orchestrates the work using its tools.

## Getting started

### Create your first skill

```bash
mkdir -p ~/.claude/skills/explain-code
```

Create `~/.claude/skills/explain-code/SKILL.md`:

```yaml
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks "how does this work?"
---

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
3. **Walk through the code**: Explain step-by-step what happens
4. **Highlight a gotcha**: What's a common mistake or misconception?

Keep explanations conversational. For complex concepts, use multiple analogies.
```

Test by asking "How does this code work?" or by typing `/explain-code src/auth/login.ts`.

### Where skills live

| Location   | Path                                                | Applies to                     |
| :--------- | :-------------------------------------------------- | :----------------------------- |
| Enterprise | Managed settings                                    | All users in your organization |
| Personal   | `~/.claude/skills/<skill-name>/SKILL.md`            | All your projects              |
| Project    | `.claude/skills/<skill-name>/SKILL.md`              | This project only              |
| Plugin     | `<plugin>/skills/<skill-name>/SKILL.md`             | Where plugin is enabled        |

Priority: enterprise > personal > project. Plugin skills use a `plugin-name:skill-name` namespace.

#### Live change detection

Claude Code watches skill directories. Adding/editing/removing a skill takes effect within the current session without restarting. Creating a top-level skills directory that didn't exist when the session started requires a restart.

#### Automatic discovery from nested directories

When you work with files in subdirectories (e.g. `packages/frontend/`), Claude Code also looks for skills in `packages/frontend/.claude/skills/`. This supports monorepos.

Each skill is a directory with `SKILL.md` as the entrypoint:

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples/
│   └── sample.md      # Example output showing expected format
└── scripts/
    └── validate.sh    # Script Claude can execute
```

Files in `.claude/commands/` still work and support the same frontmatter.

## Configure skills

### Types of skill content

**Reference content** adds knowledge Claude applies to current work (conventions, patterns, style guides):

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**Task content** gives Claude step-by-step instructions for a specific action. Often invoked directly with `/skill-name`. Use `disable-model-invocation: true` to prevent automatic triggering.

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

### Frontmatter reference

| Field                      | Required    | Description                                                                                                                                |
| :------------------------- | :---------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                     | No          | Display name. Lowercase letters, numbers, and hyphens (max 64 chars). Defaults to directory name                                           |
| `description`              | Recommended | What the skill does and when to use it. First 1,536 chars are kept                                                                         |
| `when_to_use`              | No          | Additional context for when Claude should invoke. Counts toward 1,536-char cap                                                            |
| `argument-hint`            | No          | Hint shown during autocomplete (e.g., `[issue-number]` or `[filename] [format]`)                                                          |
| `arguments`                | No          | Named positional arguments for `$name` substitution                                                                                        |
| `disable-model-invocation` | No          | If `true`, only user can invoke. Use for `/commit`, `/deploy`, etc.                                                                       |
| `user-invocable`           | No          | If `false`, hide from `/` menu. For background knowledge users shouldn't invoke directly                                                  |
| `allowed-tools`            | No          | Tools Claude can use without permission while skill is active                                                                              |
| `model`                    | No          | Model override. Same values as `/model` or `inherit`                                                                                       |
| `effort`                   | No          | `low`, `medium`, `high`, `xhigh`, `max`                                                                                                    |
| `context`                  | No          | Set to `fork` to run in a forked subagent context                                                                                          |
| `agent`                    | No          | Which subagent type to use when `context: fork`                                                                                            |
| `hooks`                    | No          | Hooks scoped to this skill's lifecycle                                                                                                     |
| `paths`                    | No          | Glob patterns that limit when this skill is auto-activated                                                                                 |
| `shell`                    | No          | `bash` (default) or `powershell` for `` !`command` `` execution                                                                            |

#### Available string substitutions

| Variable               | Description                                                                                                            |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `$ARGUMENTS`           | All arguments passed when invoking the skill                                                                            |
| `$ARGUMENTS[N]`        | Access a specific argument by 0-based index                                                                             |
| `$N`                   | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`)                                                                       |
| `$name`                | Named argument declared in `arguments` frontmatter                                                                      |
| `${CLAUDE_SESSION_ID}` | Current session ID                                                                                                      |
| `${CLAUDE_SKILL_DIR}`  | Directory containing the skill's `SKILL.md` file                                                                        |

Indexed arguments use shell-style quoting: `/my-skill "hello world" second` makes `$0` expand to `hello world` and `$1` to `second`.

**Example:**

```yaml
---
name: session-logger
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

### Add supporting files

```
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

Reference supporting files from `SKILL.md`:

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

> Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

### Control who invokes a skill

* **`disable-model-invocation: true`**: Only you can invoke. Use for `/commit`, `/deploy`, `/send-slack-message`.
* **`user-invocable: false`**: Only Claude can invoke. Use for background knowledge that isn't actionable as a command.

| Frontmatter                      | You can invoke | Claude can invoke | When loaded into context                                     |
| :------------------------------- | :------------- | :---------------- | :----------------------------------------------------------- |
| (default)                        | Yes            | Yes               | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes            | No                | Description not in context, full skill loads when you invoke |
| `user-invocable: false`          | No             | Yes               | Description always in context, full skill loads when invoked |

### Pre-approve tools for a skill

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

### Pass arguments to skills

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

`/fix-issue 123` → "Fix GitHub issue 123 following our coding standards..."

By position:

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

`/migrate-component SearchBar React Vue` → expands `$0=SearchBar`, `$1=React`, `$2=Vue`.

## Advanced patterns

### Inject dynamic context

The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude. The output replaces the placeholder.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

For multi-line commands, use a fenced code block opened with ` ```! `:

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

To disable shell execution: `"disableSkillShellExecution": true` in settings.

> Tip: include the word "ultrathink" anywhere in skill content to enable extended thinking.

### Run skills in a subagent

Add `context: fork` to run a skill in isolation. The skill content becomes the prompt that drives the subagent.

| Approach                     | System prompt                             | Task                        | Also loads                   |
| :--------------------------- | :---------------------------------------- | :-------------------------- | :--------------------------- |
| Skill with `context: fork`   | From agent type (`Explore`, `Plan`, etc.) | SKILL.md content            | CLAUDE.md                    |
| Subagent with `skills` field | Subagent's markdown body                  | Claude's delegation message | Preloaded skills + CLAUDE.md |

Example:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### Restrict Claude's skill access

**Disable all skills** by denying the Skill tool in `/permissions`:

```
# Add to deny rules:
Skill
```

**Allow or deny specific skills**:

```
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

`Skill(name)` for exact match, `Skill(name *)` for prefix match with any arguments.

## File references and bash execution (legacy syntax)

These continue to work in `.claude/commands/*.md` files:

* **`@filename`**: include the contents of a file
* **`` !`command` ``**: execute a shell command and substitute output (same as Skills)
* **`$ARGUMENTS`**: substitute arguments (same as Skills)

## Namespacing via subdirectories

For `.claude/commands/`, subdirectories namespace commands. A file at `.claude/commands/git/commit.md` becomes `/commit` (filename wins; the path is metadata only). For Skills, use the directory name as the skill name.

## MCP slash commands

MCP servers can expose slash commands via the MCP prompts capability. They appear in the typeahead with the prefix `/mcp__<server>__<prompt>`.

## Troubleshooting

### Skill not triggering

1. Check the description includes keywords users would say
2. Verify the skill appears in `What skills are available?`
3. Try rephrasing your request to match the description
4. Invoke directly with `/skill-name`

### Skill triggers too often

1. Make the description more specific
2. Add `disable-model-invocation: true` for manual-only

### Descriptions cut short

Set `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var to raise the limit. Or trim `description` and `when_to_use` — each entry capped at 1,536 chars.
