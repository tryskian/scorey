# Runbook

Use this doc for operator procedure.

- Use `README.md` for public framing and the quick entrypoint.
- Use `docs/runtime/ARCHITECTURE.md` for stable system shape.
- Use `docs/governance/SESSION_HANDOFF.md` for the active kernel and carryover.
- Use `docs/governance/DECISIONS.md` for durable rationale.
- Use `docs/runtime/START_END_REFERENCE.md` for the compact command card.

## Operating Posture

Scorey stays small on purpose.

The operator posture is:

- one active kernel at a time
- one feature branch per tracked change set
- repo-scoped edits by default
- inspect first, interpret second
- clean synced `main` is the tracked stop state

Local-only lane:

- `docs/peanut/` stays private and ignored

## Branch, Worktree, and Scope Policy

1. Canonical repo root is:
   - `/abs/path/to/scorey`
2. Default tracked workflow is:
   - `git switch -c codex/bigbrain/<task-name>`
3. Start tracked edits from a feature branch.
4. Use a dedicated worktree only for parallel implementation tracks.
5. Secondary worktrees for live eval work should use:
   - local `.venv`
   - canonical repo `.local`
6. Keep one logical task per branch.

## Morning Startup

1. Read in this order:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm:
   - canonical repo root or dedicated worktree
   - active branch from `git branch --show-current`
3. Return before implementation:
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
5. Install or refresh the environment when needed:
   - `make install`

## Inspect-First Rule

1. Inspect named files, runtime state, logs, transcripts, and DB surfaces
   before interpretation.
2. Prefer source evidence over memory when they disagree.
3. State inspection status plainly.

## Command Ownership

Human lead owns:

- objective
- scope
- acceptance criteria
- meaning-level trade-offs
- go or no-go decisions

Engineer owns:

- implementation
- validation
- command execution
- Git and PR flow
- proactive hygiene

Default mode is execution-first:

- do the work directly when asked

## Git Write Discipline

Serialize git write actions.

Do not parallelize:

- `git add`
- `git commit`
- `git push`
- branch switches
- merges
- rebases
- PR creation

Use:

1. `git add ...`
2. verify staged state with:
   - `git status --short`
   - or `git diff --cached --stat`
3. `git commit ...`

## Protected-Main Flow

1. Work on a feature branch.
2. Commit locally.
3. Push the branch.
4. Open a PR to `main`.
5. Wait for required checks.
6. Merge through the protected-main flow.
7. Sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
8. Final tracked repo state is:
   - merged
   - clean local `main`
   - synced with `origin/main`

## Runtime Gates

Use gates as behaviour checks, not narrative.

| Command | Job |
| --- | --- |
| `make doctor-env` | environment health check |
| `make start-runtime-check` | start-of-day runtime safety gate |
| `make end-runtime-check` | confirms the live slice is closed |
| `make end-docs-check` | confirms tracked current-truth docs were refreshed today |
| `make session-status` | compact repo and runtime snapshot |

`make session-status` is the compact live surface for:

- branch state
- worktree cleanliness
- runtime queue state
- live batch boundary state

## Evaluation Command Surface

Top-level and tone review:

| Command | Job |
| --- | --- |
| `make eval-init` | initialise the eval database schema |
| `make eval-list` | list top-level judged rows |
| `make eval-review-sample` | list pending top-level review sample |
| `make eval-judge` | record top-level route verdict |
| `make eval-tone-sample` | list pending tone review sample |
| `make eval-tone-judge` | record tone verdict |
| `make eval-tone-archive` | archive one pending tone row |
| `make eval-tone-disposition-sample` | list failed tone rows that still need `retain` or `evict` |
| `make eval-tone-disposition-archive` | archive one failed tone row from the disposition surface |
| `make eval-tone-dispose` | record `retain` or `evict` for one failed tone row |

Bounded widened lenses:

| Command | Job |
| --- | --- |
| `make eval-scoreboard-sample` | list pending scoreboard review sample from live route-pass rows |
| `make eval-scoreboard-judge` | record row-level scoreboard verdict on `scoreboard_claim` |
| `make eval-scoreboard-archive` | archive one pending scoreboard row |
| `make eval-scoreboard-close` | close one bounded scoreboard range and settle untouched tone rows in-range |
| `make eval-prose-sample` | list pending broader-prose review sample from live route-pass rows |
| `make eval-prose-judge` | record row-level prose verdict on the round body around the score line |
| `make eval-prose-archive` | archive one pending prose row |
| `make eval-prose-close` | close one bounded prose range and settle untouched lower-lens rows in-range |

Pulse surface:

| Command | Job |
| --- | --- |
| `make eval-pulse-open` | open one bounded pulse over a route-pass output range |
| `make eval-pulse-sample` | list newest unlabeled rows inside one pulse |
| `make eval-pulse-judge` | label one row as `anchor`, `counted_seam`, or `excluded_noise` |
| `make eval-pulse-summary` | report raw rows, counted totals, exclusions, and pulse verdict |
| `make eval-pulse-close` | close one pulse and settle untouched legacy tone rows in-range |

Sampling surface:

| Command | Job |
| --- | --- |
| `make eval-sample-local` | record deterministic local rounds |
| `make eval-sample-live` | record live API rounds |

## Validation Surface

| Command | Job |
| --- | --- |
| `make lint-docs` | tracked docs lint gate |
| `make check` | format, lint, typecheck, tests, and `git diff --check` |
| `make package-check` | distribution build check |
| `make package-install-check` | editable package import smoke |
| `make security-checks` | local dependency security audit |

## Wake-Lock Surface

| Command | Job |
| --- | --- |
| `make caffeinate` | start repo-managed wake lock |
| `make caffeinate-status` | report repo-managed wake-lock status |
| `make decaffeinate` | stop repo-managed wake lock |
| `make decaffeinate-status` | report closeout wake-lock status |

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

The repo is closed only when:

- `make end` has passed
- local `main` is clean
- local `main` is synced with `origin/main`
