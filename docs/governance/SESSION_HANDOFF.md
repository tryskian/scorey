# Session Handoff

Last updated: 2026-05-16

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm execution context:
   - repo root or dedicated worktree
   - active branch from `git branch --show-current`
3. Return the startup breakdown:
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

## Current Snapshot

Scorey is a small, local, agent-backed rock, paper, scissors mini chatbot with
a real runtime, a settled route-valid floor, and a tracked tone lane on top of
the route pass surface. `Research Beta 4.0` is now closed as the row-level
abstract measurement surface. The next staged lane is `pre-Beta 5.0`
fail-pressure pulse.

The core tracked shape is:

- bare `scorey` opens the app loop
- the runtime keeps picks fixed to:
  - `rock`
  - `paper`
  - `scissors`
- the runtime owns routing and round composition
- the live model owns only the small unstable round fields
- route verdicts stay binary
- tone failures use explicit `retain` or `evict`

Canonical live work stays on the repo `.local` surface. Secondary worktrees use
the canonical queue state rather than forking a second eval store, while
keeping local `.venv` environments.

Current runtime truth:

- `live_batch: closed`
- `route_pending=0`
- `tone_pending=0`
- `disposition_pending=0`
- live totals:
  - `2294` route pass
  - `0` fail
  - `0` pending
- tone totals:
  - `454` pass
  - `627` fail
  - `1213` archived
  - `0` pending
- disposition totals:
  - `72` retain
  - `196` evict
  - `359` archived
  - `0` pending

Current `Research Beta 4.0` tranche after output `19998`:

- `69` route pass
- `47` tone pass
- `22` tone fail
- `22` retain
- `0` evict
- `0` pending at any active layer
- no `real one` / `napkin` relapse across the closed slice
- weak seam still reads as cross-object coherence drift
- restored interrupted segment after output `20005` closed at:
  - `62` route pass
  - `42` tone pass
  - `20` tone fail
  - `20` retain
  - `0` evict
- first isolated fail-family run after output `20139` closed at:
  - family: `cross-object coherence drift`
  - `77` route pass
  - `50` tone pass
  - `27` tone fail
  - `27` retain
  - `0` evict
  - fail mix:
    - `26` `cross-object coherence drift`
    - `1` `anchor relapse`

Current staged next lane:

- `pre-Beta 5.0`
- `fail-pressure pulse`
- status:
  - hypothesis translated into Scorey terms
  - not promoted to `Beta 5.0`
  - no pulse run started yet

Reusable worktrees currently kept warm:

- `scorey-canonical-env`
- `scorey-fresh-mixed-run`

Both are normalized to:

- local `.venv`
- canonical repo `.env`
- canonical repo `.local`
- clean `make doctor-env`
- clean `make session-status`

## Active Kernel

- keep `Beta 4.0` frozen as closed evidence
- stage the pulse method cleanly without promoting `Beta 5.0` yet
- preserve the explicit comparison boundary:
  - anchored `3.0`
  - abstract row-level `4.0`
  - staged pulse-level pre-`5.0`

## Next Slice

1. Finish the pre-`Beta 5.0` docs transition.
2. Decide whether pulse staging needs a durable decision entry before any run.
3. Promote to `Beta 5.0` only when the first real pulse run starts.

## Guardrails

- keep the repo small and local
- keep the runtime CLI-first
- keep picks fixed to `rock`, `paper`, and `scissors`
- keep one active kernel at a time
- keep route validity as the first gate
- keep tone review and failure disposition explicit
- keep the canonical `.local` queue as the live eval surface
- keep tracked docs truthful to the current repo surface

## Close A Session

1. Run:
   - `make end-docs-check`
   - `make doctor-env`
   - `make path-leak-check`
   - `make path-leak-audit-local`
   - `make check`
   - `make end-runtime-check`
2. Stop the repo-managed wake lock:
   - `make decaffeinate`
   - `make decaffeinate-status`
3. Finish on clean synced `main`:
   - `make end-git-check`

## Copy/Paste Refresh Prompt

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Before starting implementation, confirm environment/workspace context: canonical repo path is /abs/path/to/scorey, confirm host vs devcontainer mode, confirm active git branch, and say whether the thread is on clean main or a feature branch. Apply no-guessing controls: prefer repo-scoped edits and preserve user shell profile files and global VS Code settings unless explicitly approved in-chat. Run in one active kernel at a time. Then execute the Next Kernel from SESSION_HANDOFF with minimal behavior drift and full validation.`
