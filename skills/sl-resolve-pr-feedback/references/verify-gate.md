# Reviewer-Quiescence Gate

Read this reference when Full-mode step 8 says a fix was pushed this round. A reply-only round never reaches here — there is no new commit for a bot to re-review, so it goes straight to the re-fetch in step 8.

## Why the wait exists

Automated reviewers (Copilot, CodeRabbit, Greptile) re-review **asynchronously**: a fix push triggers a re-review that lands seconds-to-minutes later. Re-fetching immediately after the push sees "0 unresolved," concludes, and the bot's next round arrives afterward -- forcing the user to re-run.

## Run it

```bash
SKILL_DIR="<absolute path of the directory containing the SKILL.md you just read>"
bash "$SKILL_DIR/scripts/wait-for-bot-review" PR_NUMBER "$(git rev-parse HEAD)"
```

Keep this a single pinned command, not an `if [ -f … ]` guard. A guard that evaluates false skips the wait *silently* and the run reads as quiescent when it never waited; an unguarded call that cannot find its script fails loudly and is fixed in one step. Prefer the loud failure.

**Bots only -- never humans.** The wait targets known automated reviewer logins that are *active* on this PR (have at least one prior review). It **never waits on human reviewers** -- human threads are handled in the round they are present, not waited on. The script intersects its known-bot list with the PR's actual reviewers, so a configured bot that never reviews this PR is a no-op, not a wait.

## Bounds

- **Per-wait timeout.** The script stops waiting and exits after ~5 minutes even if an active bot never reaches HEAD (hanging is the worst failure). On timeout it prints `timed-out waiting for: <logins>` -- **proceed anyway** (re-fetch), and note in the step 9 summary that a late bot round may still arrive, so the result does not imply full quiescence.
- **Max fix-round cap of 3.** Enforced in step 8, where the loop lives. After the third fix-verify cycle the recurring-pattern escalation fires instead of looping again.

**Settle-window fallback (C).** Some reviewers post feedback that is *not* detectable as a re-review on HEAD -- a top-level comment with no SHA-tied review. For those the `commit.oid == HEAD` signal never trips, so do not wait on it forever: fall back to a **settle-window** -- after the gate returns, wait ~60s and re-fetch once via `get-pr-comments`; if no new threads appeared, conclude. This bounds the wait for non-SHA reviewers rather than blocking on a signal that will not come. Option A (poll-for-review-on-HEAD, above) is the primary, deterministic path; C is the documented secondary path for the non-SHA case.

Every path returns to step 8's re-fetch. The gate never terminates the run.
