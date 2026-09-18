# Session Handoff

Last updated: 2026-09-18

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
   - `make session-status`

## Current Snapshot

Scorey is a small local CLI research instrument for one unfair rock, paper,
scissors round. `Research Beta 4.0` is closed as the abstract row-level
measurement baseline. `Research Beta 5.0` is closed as the fail-pressure pulse
baseline. `Research Beta 6.0` is closed as the scoreboard baseline.
`Research Beta 7.0` is closed as the broader prose baseline. `Research Beta 8.0`
is closed as the menace baseline. `pre-Beta 9.0` is the current staged positive
runtime instruction contract and its first fresh `15`-minute pulse.

The session resumed on `2026-09-18` from clean `main` at `cb80bb0`.

Mac-wide power control is external to this repository. The Coffee Codex plugin
owns the one shared keep-awake session for Polinko and the toys. Scorey's
startup, preflight, closeout, and session status leave it unchanged.
`make start` passed, and the live runtime counts below were confirmed.
The handoff reconciliation passed `make end-preflight` on `2026-09-18`,
including `91` tests, packaging, runtime closeout, and the dependency security
audit.

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
- those dispositions belong to the failed-tone workflow and do not apply to the
  active pre-Beta 9.0 pulse

Open dependency PRs, checked on `2026-09-18`:

- [#94](https://github.com/tryskian/scorey/pull/94): grouped GitHub Actions updates
- [#100](https://github.com/tryskian/scorey/pull/100): grouped Python dependency updates

The older Python dependency PR `#97` is closed without merging.

Current runtime truth:

- `live_batch: closed`
- `batch_meta: missing`
- `route_pending=0`
- `tone_pending=0`
- `disposition_pending=0`
- live totals:
  - `2495` route pass
  - `0` fail
  - `0` pending
- tone totals:
  - `454` pass
  - `627` fail
  - `1414` archived
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

## Landed Runtime Work

The positive runtime instruction rewrite merged through PR `#78` at `af789c3`:

- `src/scorey/config.py` remains structural: picks, routing, and settings
- `src/scorey/agent.py` already owns the live instructions and per-round prompt
- the rewrite states the wanted output as positive target behaviour
- the runtime still owns routing and composition around the three model fields

The CLI arrow-navigation repair merged through PR `#98` at `51eb2a8`:

- live CLI arrow navigation is restored without changing its intentional timing
- `up` and `down` are the only selection-moving keys
- `enter` confirms and `esc` exits
- selector input now reads terminal bytes directly instead of mixing buffered
  text reads with file-descriptor polling
- one terminal mode remains active across the selector interaction so rapid
  keypresses cannot fall into a canonical-mode gap
- the duplicate scene render after each arrow movement is removed
- `ESC_SEQUENCE_TIMEOUT_SECONDS` remains `0.03`
- validation recorded on `2026-08-10`:
  - focused `tests/test_main.py`: `38` pass with `4` arrow-sequence subtests
  - real pseudo-terminal smoke: rapid `down`, `up`, wrap-`up`, `enter`, and
    `esc` passed without echoed escape garbage
  - `make check`: `90` pass
  - feature-branch `make end` validation passed through security and
    runner shutdown before merge
  - PR `#98` required checks passed

## Active Kernel

The next research slice is one `15`-minute live cross-object pulse under the
positive runtime instructions already in `agent.py`. `Research Beta 8.0`
remains the frozen comparison baseline; `pre-Beta 9.0` remains staged while
that fresh pulse evidence is gathered.

What is live now:

- the current staged boundary is `pre-Beta 9.0` positive runtime instruction
  contract plus a `15`-minute binary pulse
- `src/scorey/config.py` stays structural only
- `src/scorey/agent.py` owns the live runtime instruction shape
- new live evidence belongs above the rewritten prompt contract rather than
  inside Beta 8.0
- operator surface:
  - `eval-sample-live` with `EVAL_DURATION_SECONDS=900`
  - `eval-pulse-open`
  - `eval-pulse-sample`
  - `eval-pulse-judge`
  - `eval-pulse-summary`
  - `eval-pulse-close`
- rows are `anchor`, `counted_seam`, or `excluded_noise`; only the first two
  affect the strict `PASS` / `FAIL` result
- `retain` and `evict` are not pulse dispositions
- `D-032` freezes Beta 8.0 below a staged positive runtime instruction
  contract
- `D-035` fixes the first fresh evidence unit as a `15`-minute binary pulse
- frozen bounded menace evidence:
  - `20410-20417`: `6 / 2`
  - `20397-20403`: `4 / 3`
  - `20404-20409`: `4 / 2`
  - `20307-20321`: `11 / 4`
  - `20382-20396`: `9 / 6`
  - `20352-20366`: `11 / 4`
  - `20367-20381`: `15 / 0`

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

Current staged research lane:

- `pre-Beta 9.0`
- positive runtime instruction contract and one `15`-minute binary pulse
- frozen baseline:
  - `Research Beta 8.0` menace judgement
- active family for the first fresh comparison slice:
  - `cross-object coherence drift`
- active note:
  - `docs/research/410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md`

## Next Slice

1. Keep `Beta 5.0`, `Beta 6.0`, `Beta 7.0`, and `Beta 8.0` frozen as the
   closed evidence ladder below the staged runtime contract.
2. Use the agent-local positive runtime instruction contract already merged
   through PR `#78` for fresh live evidence.
3. Sample the fixed cross-object pair cycle for `900` seconds. Record the
   actual UTC window and output-id range; same-pick is out of scope unless a
   later kernel explicitly reopens it.
4. Open that route-pass range as one pulse. Label every row as `anchor`,
   `counted_seam`, or reasoned `excluded_noise`, then close it at `0` pending.
5. Report the pulse-level `PASS` / `FAIL` result beside the frozen Beta 8.0
   baseline. Promotion remains a human method decision only if the completed
   pulse changes what the post-rewrite evidence means.

## Risks

- low runtime risk: the queue is fully closed and there is no active sampler
- one complete `15`-minute pulse is still needed to assess the rewritten runtime
  contract beside the frozen Beta 8.0 baseline
- dependency maintenance remains queued separately: open Dependabot PRs `#94`
  and `#100` were verified on `2026-09-18`

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
   - `make scripts-check`
   - `make check`
   - `make package-check`
   - `make package-install-check`
   - `make end-runtime-check`
   - `make security-checks`
2. Print the repository and runtime snapshot:
   - `make session-status`
3. Finish on clean synced `main`:
   - `make end-git-check`
