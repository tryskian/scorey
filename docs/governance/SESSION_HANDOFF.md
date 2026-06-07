# Session Handoff

Last updated: 2026-06-06

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm execution context:
   - canonical repo root or dedicated worktree
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

Scorey is a small local CLI research instrument for one unfair rock, paper,
scissors round. `Research Beta 4.0` is closed as the abstract row-level
measurement baseline. `Research Beta 5.0` is closed as the fail-pressure pulse
baseline. `Research Beta 6.0` is closed as the scoreboard baseline.
`Research Beta 7.0` is closed as the broader prose baseline. `Research Beta 8.0`
is the current active menace lane.

Stable repo shape:

- bare `scorey` opens the app loop
- the runtime keeps picks fixed to:
  - `rock`
  - `paper`
  - `scissors`
- the runtime owns routing and final round composition
- the live model owns only:
  - `winning_state`
  - `worse_state`
  - `scoreboard_claim`
- route stays the floor
- tone remains the first widened row-level lens
- failure handling stays explicit:
  - `retain`
  - `evict`

Current runtime truth:

- `live_batch: closed`
- `batch_meta: missing`
- `route_pending=0`
- `tone_pending=0`
- `disposition_pending=0`
- live totals:
  - `2474` route pass
  - `0` fail
  - `0` pending
- tone totals:
  - `454` pass
  - `627` fail
  - `1393` archived
  - `0` pending
- disposition totals:
  - `72` retain
  - `196` evict
  - `359` archived
  - `0` pending

## Closed Evidence Surface

`Research Beta 5.0` pulse baseline:

- cross-object:
  - pulse `1`: `8 / 5 / 2`
  - pulse `3`: `9 / 6 / 0`
  - pulse `4`: `9 / 6 / 0`
- same-pick:
  - pulse `2`: `15 / 0 / 0`
  - pulse `5`: `15 / 0 / 0`

`Research Beta 6.0` scoreboard baseline:

- `20292-20306`: `15` pass / `0` fail
- `20307-20321`: `15` pass / `0` fail
- `20322-20336`: `15` pass / `0` fail
- `20337-20351`: `15` pass / `0` fail

`Research Beta 7.0` broader prose baseline:

- `20352-20366`: `9` pass / `6` fail
- `20367-20381`: `15` pass / `0` fail
- `20382-20396`: `9` pass / `6` fail

Stable contrast:

- cross-object prose reopens pressure at `9 / 6` and repeats there
- same-pick prose collapses at `15 / 0`
- newer bounded eval gates are performing cleanly across pulse, scoreboard,
  and prose closeout

## Active Kernel

Menace operator surface branch:

- branch: `codex/bigbrain/scorey-handoff-menace-sync`
- tracked surfaces in play:
  - `README.md`
  - `docs/governance/CHARTER.md`
  - `Makefile`
  - `src/scorey/eval_db.py`
  - `src/scorey/main.py`
  - `tests/test_eval_db.py`
  - `tests/test_main.py`
  - `docs/runtime/ARCHITECTURE.md`
  - `docs/runtime/RUNBOOK.md`
  - `docs/governance/DECISIONS.md`
  - `docs/governance/SESSION_HANDOFF.md`
  - `docs/research/000_LEGEND.md`
  - `docs/research/README.md`
  - `docs/research/080_B-MENACE_JUDGEMENT.md`
- tracked change:
  - menace is being formalised as a real bounded row-level lens on the full
    visible round
  - `eval-menace-sample`
  - `eval-menace-judge`
  - `eval-menace-archive`
  - `eval-menace-close`
  - menace closeout settles untouched `tone`, `scoreboard`, and `prose` rows
    in-range
  - `D-030` locks the row-level menace contract in the durable decisions ledger
  - `D-031` starts `Research Beta 8.0` on menace judgement
  - hardened cross-object menace repeat `20307-20321` closed at `11 / 4`
  - first bounded menace read `20382-20396` closed at `9 / 6`
  - second bounded menace read `20352-20366` closed at `11 / 4`
  - first bounded same-pick menace read `20367-20381` closed at `15 / 0`
  - the second read moved above the closed `Beta 7.0` prose surface and starts
    `Research Beta 8.0`

Private staging surface:

- `docs/peanut/research/templates/README.md`
- `docs/peanut/research/templates/legend.md`
- `docs/peanut/research/templates/boundary.md`
- `docs/peanut/research/templates/lane.md`
- `docs/peanut/research/templates/case.md`
- `docs/peanut/research/templates/validation.md`
- `docs/peanut/research/templates/hypothesis.md`
- `docs/peanut/research/templates/backlog.md`
- `docs/peanut/research/chart-language.md`

Current active research lane:

- `Research Beta 8.0`
- `menace judgement`
- judged surface:
  - the full visible round
- operator surface:
  - locked
- active family:
  - `cross-object coherence drift`
- active note:
  - `docs/research/080_B-MENACE_JUDGEMENT.md`

## Next Slice

1. Finish the current menace operator branch and merge it on clean synced
   `main`.
2. Keep `Beta 5.0`, `Beta 6.0`, and `Beta 7.0` frozen as the closed evidence
   ladder below active menace.
3. Same-pick menace is now confirmed collapsed at `15 / 0`, while
   cross-object has hardened at `11 / 4` twice after one opening `9 / 6`.
4. Package this `Beta 8.0` branch on clean synced `main`.
5. After merge, decide whether the next kernel is:
   - one more cross-object menace repeat from fresh live rows
   - or the next staged lane above menace

## Risks

- low runtime risk: the queue is fully closed and there is no active sampler
- small ops wrinkle: the repo-managed `caffeinate` PID file is still drifting
  stale

## Guardrails

- keep the repo small and local
- keep the runtime CLI-first
- keep picks fixed to `rock`, `paper`, and `scissors`
- keep one active kernel at a time
- keep route validity as the first gate
- keep bounded closeout returning to `0` pending
- keep `docs/peanut/` private unless the boundary is widened explicitly
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
