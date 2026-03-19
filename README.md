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
| `.env.sample`           | Template for required environment variables             |
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

## Features

### Build-and-Ship Pipeline (`/build-and-ship`)

An end-to-end autonomous development pipeline that takes a plan file and executes all stages from implementation to PR creation. The pipeline enforces a 5-phase workflow:

1. **Implementation** — Executes plan tasks via subagents (parallel where possible)
2. **Local Pre-flight Review** — Runs `code-review` on all changes before committing
3. **Git Operations** — Stages, commits, pushes, and creates a PR via the `git-ops` agent
4. **PR Review Loop** — Monitors for reviewer comments, fixes actionable ones, and replies (up to 3 rounds)
5. **Notification** — Sends macOS desktop notification and SMS (via Twilio) when the PR is ready for human review

A stop hook (`build_ship_stop_gate.py`) prevents the pipeline from exiting before all 5 phases complete.

**Hard constraints**: The pipeline never approves, merges, or force-pushes. Only the human approves and merges.

### Design-to-Plan Flow (`/design` and `/plan_w_team`)

`/design` now prompts the user to automatically invoke `/plan_w_team` after completing the design process, creating a seamless design-to-plan-to-build workflow.

`/plan_w_team` now generates a **Build-and-Ship Configuration** section in every plan, including git branch/base settings, review configuration, reviewer assignments, and notification preferences — ready for `/build-and-ship` to consume.

### Specialized Agents

| Agent               | Model  | Purpose                                                           |
| ------------------- | ------ | ----------------------------------------------------------------- |
| `git-ops`           | Sonnet | Git operations only (stage, commit, push, PR). Cannot write code. |
| `pr-review-monitor` | Haiku  | Performs a single check for new PR review comments. Intended to be called repeatedly via /loop. Read-only. |

### SMS Notifications

Twilio-based SMS notifications with iMessage fallback for macOS. Used by the build-and-ship pipeline to notify when PRs are ready for review.

## Setup

### 1. Clone

```bash
git clone git@github.com:akornmeier/clawd-config.git ~/.claude
```

### 2. Environment Variables

Copy the sample environment file and fill in your values:

```bash
cp ~/.claude/.env.sample ~/.claude/.env.local
```

See `.env.sample` for all available variables and descriptions. At minimum, you need `ANTHROPIC_API_KEY`. For the build-and-ship SMS notifications, configure the Twilio variables.

### 3. Dependencies

The SMS notification script uses [uv](https://docs.astral.sh/uv/) for dependency management (auto-installs `twilio` and `python-dotenv` on first run).

## Notes

- `.env.local` is gitignored — secrets never leave your machine
- Conversation history and project data are intentionally excluded to protect privacy
- Cache files are excluded to keep the repo lightweight
- After cloning, Claude Code will recreate any missing transient directories automatically
