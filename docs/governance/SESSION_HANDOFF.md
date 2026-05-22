# Session Handoff

Last updated: 2026-05-21

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
the route pass surface. `Research Beta 4.0` is closed as the row-level
abstract measurement surface. `Research Beta 5.0` is now active as the
fail-pressure pulse lane.

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
  - `2369` route pass
  - `0` fail
  - `0` pending
- tone totals:
  - `454` pass
  - `627` fail
  - `1288` archived
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

Current `Research Beta 5.0` pulse results:

- pulse `1`:
  - family: `cross-object coherence drift`
  - range: `20217-20231`
  - raw: `15`
  - anchors: `8`
  - `counted_seams`: `5`
  - `excluded_noise`: `2`
  - exclusions:
    - `operator_artifact=2`
    - `off_target_failure=0`
  - counted total: `13`
  - verdict: `pass`
- pulse `2`:
  - family: `same-pick object-shape drift`
  - range: `20232-20246`
  - raw: `15`
  - anchors: `15`
  - `counted_seams`: `0`
  - `excluded_noise`: `0`
  - exclusions:
    - `operator_artifact=0`
    - `off_target_failure=0`
  - counted total: `15`
  - verdict: `pass`
- pulse `3`:
  - family: `cross-object coherence drift`
  - range: `20247-20261`
  - raw: `15`
  - anchors: `9`
  - `counted_seams`: `6`
  - `excluded_noise`: `0`
  - exclusions:
    - `operator_artifact=0`
    - `off_target_failure=0`
  - counted total: `15`
  - verdict: `pass`
- pulse `4`:
  - family: `cross-object coherence drift`
  - range: `20262-20276`
  - raw: `15`
  - anchors: `9`
  - `counted_seams`: `6`
  - `excluded_noise`: `0`
  - exclusions:
    - `operator_artifact=0`
    - `off_target_failure=0`
  - counted total: `15`
  - verdict: `pass`
- pulse `5`:
  - family: `same-pick object-shape drift`
  - range: `20277-20291`
  - raw: `15`
  - anchors: `15`
  - `counted_seams`: `0`
  - `excluded_noise`: `0`
  - exclusions:
    - `operator_artifact=0`
    - `off_target_failure=0`
  - counted total: `15`
  - verdict: `pass`

Worktree note:

- use the canonical repo root unless a new kernel explicitly opens a fresh
  worktree lane
- do not treat old side worktrees as warm pulse lanes by default

## Active Kernel

- keep `Beta 4.0` frozen as closed evidence
- keep `Beta 5.0` frozen as the most recently closed pulse baseline
- preserve the explicit comparison boundary:
  - anchored `3.0`
  - abstract row-level `4.0`
  - pulse-level `5.0`
- activate `Beta 6.0` as scoreboard judgment
- keep the scoreboard lane row-level on `scoreboard_claim`
- keep bounded scoreboard runs explicit with `eval-scoreboard-close`
- hold the starting `Beta 6.0` evidence surface at:
  - range `20292-20306`
  - `15` scoreboard pass
  - `0` scoreboard fail
  - range `20307-20321`
  - `15` scoreboard pass
  - `0` scoreboard fail
  - `15` untouched tone rows settled by scoreboard closeout

## Next Slice

1. Keep `Beta 5.0` as the closed pulse baseline:
   - pulse `1`: cross-object `8 / 5 / 2`
   - pulse `2`: same-pick `15 / 0 / 0`
   - pulse `3`: cross-object `9 / 6 / 0`
   - pulse `4`: cross-object `9 / 6 / 0`
   - pulse `5`: same-pick `15 / 0 / 0`
2. Keep `Beta 6.0` active as scoreboard judgment.
3. Use the two bounded scoreboard source passes as the opening evidence
   surface:
   - `20292-20306`: `15` pass / `0` fail
   - `20307-20321`: `15` pass / `0` fail
4. Decide whether to repeat scoreboard on the same cross-object family or
   widen it to a second family.
5. Keep runtime closed at `0` pending across route, tone, and disposition.

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
   - `make lint-docs`
   - `make check`
   - `make package-check`
   - `make package-install-check`
   - `make end-runtime-check`
   - `make security-checks`
2. Stop the repo-managed wake lock:
   - `make decaffeinate`
   - `make decaffeinate-status`
3. Finish on clean synced `main`:
   - `make end-git-check`

## Copy/Paste Refresh Prompt

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Before starting implementation, confirm environment/workspace context: canonical repo path is /abs/path/to/scorey, confirm host vs devcontainer mode, confirm active git branch, and say whether the thread is on clean main or a feature branch. Apply no-guessing controls: prefer repo-scoped edits and preserve user shell profile files and global VS Code settings unless explicitly approved in-chat. Run in one active kernel at a time. Then execute the Next Kernel from SESSION_HANDOFF with minimal behavior drift and full validation.`
