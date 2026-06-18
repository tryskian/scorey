# Start / End Reference

This is the compact command card for opening and closing a working session.

## Start

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm:
   - repo or worktree context
   - active branch
3. State before implementation:
   - current state
   - risks
   - next kernel
   - repo or worktree context
   - active branch
4. Run:
   - `make doctor-env`
   - `make start-runtime-check`
   - `make caffeinate`
   - `make caffeinate-status`
   - `make session-status`

## End

1. Run branch-local validation:
   - `make end-docs-check`
   - `make doctor-env`
   - `make path-leak-check`
   - `make path-leak-audit-local`
   - `make lint-docs`
   - `make check`
   - `make package-check`
   - `make package-install-check`
   - `make end-runtime-check`
   - `make security-checks`
   - `make refresh-deps` when dependency metadata changed
2. Stop the repo-managed wake lock:
   - `make decaffeinate`
   - `make decaffeinate-status`
3. Finish on clean synced `main`:
   - `make end-git-check`

## Wrapper Shortcuts

| Command | Job |
| --- | --- |
| `make start` | runs the startup sequence and prints the rehydrate prompt |
| `make end` | runs the full closeout sequence and final git check |

## Close Condition

The repo is closed only when:

- `make end` has passed
- local `main` is clean
- local `main` is synced with `origin/main`
