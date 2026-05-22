# Runbook

## When to Read This

Use this doc for operator procedure.

- `README.md`
  - public framing and quick entrypoint
- `docs/governance/CHARTER.md`
  - durable rules and role split
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape
- `docs/governance/SESSION_HANDOFF.md`
  - active slice and carryover
- `docs/governance/DECISIONS.md`
  - durable rationale for repo choices
- `docs/runtime/START_END_REFERENCE.md`
  - compact command card

## Branch, Worktree, and Scope Policy

1. Canonical repo root is:
   - `/abs/path/to/scorey`
2. Default workflow is one feature branch per change set:
   - `git switch -c codex/bigbrain/<task-name>`
3. Start tracked edits from a feature branch.
4. Use a dedicated worktree for parallel implementation tracks.
5. Keep one logical task per branch.
6. Keep one active kernel at a time.
7. Secondary worktrees for live eval work should use:
   - local `.venv`
   - canonical repo `.local`

## Command Surface Rule

1. Keep one atomic command per operator action.
2. Keep operator thinking in procedure.
3. Keep wrapper targets mechanical.
4. Use `make session-status` as the live repo and runtime snapshot.
5. Use runtime gates as repo behaviour checks, not as narrative.

## Morning Startup Ritual

1. Read in this order:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm execution context:
   - canonical repo root or dedicated worktree
   - active branch from `git branch --show-current`
3. Return the startup breakdown before implementation:
   - current state
   - risks
   - next kernel
   - repo or worktree context
   - active branch
4. Run session preflight:
   - `make doctor-env`
   - `make start-runtime-check`
   - `make caffeinate`
   - `make caffeinate-status`
   - `make session-status`
5. Install or refresh the environment when needed:
   - `make install`
6. Add live runtime credentials when needed:
   - repo `.env`
   - or shell export
7. For live API work, open cost surfaces only when needed:
   - `make open-limits`
   - `make open-usage`
   - `make open-cost-console`

## Environment Doctor

1. Run:
   - `make doctor-env`
2. It checks:
   - Python path
   - venv
   - package imports
   - repo runtime files
   - live credential visibility
3. Resolve actionable issues before runtime or eval work.

## Inspect-First Rule

1. Inspect named files, paths, screenshots, logs, reports, and transcripts
   before interpretation.
2. Use source evidence as the basis for interpretation.
3. State inspection status plainly.

## Command Ownership

1. Human lead owns:
   - objective
   - scope
   - acceptance criteria
   - meaning-level trade-offs
   - go or no-go decisions
2. Engineer owns:
   - implementation
   - validation
   - command execution
   - Git and PR flow
   - proactive hygiene
3. Default mode is execution-first:
   - do the work directly when asked

## Protected Main PR Flow

1. Work on a feature branch.
2. Serialize git write actions.
   - Do not parallelize `git add`, `git commit`, `git push`, branch switches,
     merges, rebases, or PR creation.
   - Use:
     - `git add ...`
     - verify staged state with `git status --short` or `git diff --cached --stat`
     - `git commit ...`
3. Commit locally.
4. Push the branch.
5. Open a PR to `main`.
6. Wait for required checks.
7. Merge through the protected-main flow.
8. Sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
9. Final local repo state is clean and synced with `origin/main`.

## End Of Day

1. Finish branch-local validation before merge:
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
2. Package the branch when the kernel is ready.
3. Merge through the protected-main flow.
4. After merge, switch back to `main` and pull fast-forward only.
5. Run closeout checks:
   - `make decaffeinate`
   - `make decaffeinate-status`
   - `make end-git-check`
6. Update tracked handoff and research truth before stopping.
7. End state is:
   - merged
   - clean local `main`
   - synced with `origin/main`

## Runtime Gate Notes

1. `make start-runtime-check` confirms the day can open safely.
2. `make end-runtime-check` confirms the live slice is closed.
3. `make end-docs-check` confirms tracked current-truth docs were refreshed
   today.
4. `make session-status` is the compact status surface for:
   - branch state
   - worktree cleanliness
   - runtime queue state
   - live batch boundary state

## Local-Only Docs Policy

1. `docs/peanut/` is the local and private lane.
2. Use it for:
   - interface sketches
   - rough notes
   - private scratch material
3. Tracked docs remain canonical project truth.

## Atomic Commands

- `make install`
  - install or refresh the local environment
- `make doctor-env`
  - environment health check
- `make start-runtime-check`
  - start-of-day runtime safety gate
- `make session-status`
  - live repo and runtime snapshot
- `make caffeinate`
  - start repo-managed wake lock
- `make caffeinate-status`
  - report repo-managed wake-lock status
- `make decaffeinate`
  - stop repo-managed wake lock
- `make decaffeinate-status`
  - report closeout wake-lock status
- `make end-docs-check`
  - current-truth docs freshness gate
- `make end-runtime-check`
  - closeout runtime gate
- `make eval-pulse-open`
  - open one bounded pulse over a route-pass output range
- `make eval-pulse-sample`
  - list newest unlabeled rows inside one pulse
- `make eval-pulse-judge`
  - label one row as `anchor`, `counted_seam`, or `excluded_noise`
- `make eval-pulse-summary`
  - report raw rows, counted totals, exclusions, and pulse verdict
- `make eval-pulse-close`
  - close one pulse once every row in range has a pulse label
  - settle any still-unreviewed legacy tone rows in that pulse range out of the
    active tone queue
- `make lint-docs`
  - tracked docs lint gate
- `make check`
  - repo validation suite
- `make package-check`
  - distribution build check
- `make package-install-check`
  - editable package import smoke
- `make security-checks`
  - local dependency security check
- `make end-git-check`
  - clean-main closeout check
