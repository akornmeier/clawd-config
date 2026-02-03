<p align="center">
  <img src="claw.svg" alt="Claude Code" width="120">
</p>

# Clawd Code Configuration

This directory contains configuration and customization files for [Claude Code](https://claude.ai/claude-code).

## Directory Structure

### Tracked (version controlled)

| Path                    | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `settings.json`         | User preferences and configuration                      |
| `agents/`               | Custom agent definitions for specialized tasks          |
| `commands/`             | Custom slash commands                                   |
| `hooks/`                | Event hooks that run on tool calls and lifecycle events |
| `plugins/`              | Installed plugins extending functionality               |
| `skills/`               | Custom skills providing domain-specific workflows       |
| `plans/`                | Implementation plans for projects                       |
| `statusline-command.sh` | Custom statusline script                                |

### Ignored (private/transient)

| Path                        | Description                               |
| --------------------------- | ----------------------------------------- |
| `history.jsonl`             | Conversation history (sensitive)          |
| `projects/`                 | Project-specific session data (sensitive) |
| `session-env/`              | Session environment variables             |
| `cache/`, `paste-cache/`    | Temporary caches                          |
| `debug/`, `file-history/`   | Debug logs and file edit history          |
| `todos/`, `tasks/`, `data/` | Transient session state                   |

## Usage

Clone this repo to `~/.claude` on a new machine to restore your Claude Code configuration:

```bash
git clone git@github.com:akornmeier/clawd-config.git ~/.claude
```

## Notes

- Conversation history and project data are intentionally excluded to protect privacy
- Cache files are excluded to keep the repo lightweight
- After cloning, Claude Code will recreate any missing transient directories automatically
