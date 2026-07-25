# Settle Window

Read this reference when Full-mode step 8's re-fetch came back **empty** *and* this round **pushed a fix**. That is the only case where waiting can still buy anything: a bot may be mid-re-review, and concluding now would hand the user a "0 unresolved" that the next round contradicts.

Every other case has already been decided in step 8 — new threads means loop, nothing pushed means conclude. Do not wait in either.

## Why a window and not a poll-until-quiet

Automated reviewers (Copilot, CodeRabbit, Greptile) re-review **asynchronously**, seconds to minutes after a push. Waiting for that is worth a bounded pause, not an open one: the reviewer that has nothing to say is indistinguishable from the reviewer that has not started, and both look identical to a poll. Step 8 already made the cheap check, so this is a second look after a short delay — not the primary signal.

## Run it

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/wait-for-bot-review" PR_NUMBER "$(git rev-parse HEAD)" OWNER/REPO 60
```

The fourth argument is the window in seconds. Pass `60` here. The script's own default is 150s, sized for when it was the primary check; it no longer is.

Keep this a single pinned command, not an `if [ -f … ]` guard. A guard that evaluates false skips the window *silently* and the round reads as settled when it never waited; an unguarded call that cannot find its script fails loudly and is fixed in one step. Prefer the loud failure.

**Bots only — never humans.** The window targets known automated reviewer logins that are *active* on this PR (have at least one prior review). It **never waits on human reviewers** — human threads are handled in the round they are present, not waited on. The script intersects its known-bot list with the PR's actual reviewers, so a configured bot that never reviews this PR is a no-op, not a wait.

## Then

Re-fetch once more via `get-pr-comments`.

- **New threads** → return to step 8 and loop from step 2, subject to the max fix-round cap of 3.
- **Still empty** → conclude.

Either way, if the window elapsed without the bot reaching HEAD, the script prints `timed-out waiting for: <logins>`. Note it on the step 9 `Reviewer wait` line: the result does not imply full quiescence, and a late round may still arrive. That is an accepted outcome, not a failure — a late bot round costs one re-run, and blocking longer to avoid it costs every run.
