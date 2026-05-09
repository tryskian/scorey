# Session Handoff

Last updated: 2026-05-09

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - this file
2. Confirm you are at the repo root.
3. Treat the tracked docs as current project state.
4. State the active kernel before changing files.

## Current State

Scorey is a small rigged rock, paper, scissors toy with a working runtime, a
settled local eval lane, and an active live review queue.

The core tracked surfaces are:

- `README.md`
- `docs/governance/`
- `docs/runtime/`
- `docs/research/`
- `docs/diagrams/`

A small operator surface now exists:

- `make caffeinate`
- `make decaffeinate`
- `make decaffeinate-all`
- `make doctor-env`
- `make precommit-install`
- `make precommit-run`
- `make session-status`
- `make lint`
- `make typecheck`
- `make test-cov`
- `make check`
- `make eval-init`
- `make eval-list`
- `make eval-review-sample`
- `make eval-judge`
- `make eval-tone-sample`
- `make eval-tone-judge`
- `make eval-tone-archive`
- `make eval-tone-disposition-sample`
- `make eval-tone-dispose`
- `make research-beta1`
- `make eval-sample-live`
- `make open-limits`
- `make open-usage`
- `make open-billing`
- `make open-cost-console`
- `make eod`
- `make eod-preflight`

Repo automation is now in place:

- GitHub Actions CI
- Dependabot for `pip` and `github-actions`
- markdownlint config aligned with sibling repos
- stale dependency PR queue cleared

The round contract is now defined in tracked docs:

- allowed Scorey routing is narrow
- same-pick rounds are valid losing rounds, not ties
- the runtime owns composition
- the live model owns only small unstable state fields

A first runtime package is now tracked:

- `pyproject.toml`
- `.env.example`
- `src/scorey/config.py`
- `src/scorey/pipeline.py`
- `src/scorey/agent.py`
- `src/scorey/main.py`
- `src/scorey/eval_db.py`
- `tests/`

Current runtime surfaces:

- bare `scorey` opens the app loop
- the app opens with a responsive banner and narrower fallbacks
- the TTY app loop now stages the round:
  - `you:` selector first
  - `me:` inactive until reveal
  - Scorey's pick revealed before the ruling finishes
  - inline Braille spinner during live generation
  - `enter` replay / `esc` exit footer
- `scorey play rock` plays one live round
- `scorey --local play rock` plays one deterministic local round
- `scorey eval-init` initializes the local eval database
- `scorey eval-list --limit 10` lists recent eval rows
- `scorey eval-list --limit 10 --verdict pending` lists only pending eval rows
- `scorey eval-review-sample --limit 12` lists the newest pending row per model/pair sample
- `scorey eval-judge 17922 pass --note "route-valid and legible"` records one human verdict
- `scorey eval-tone-sample --limit 12` lists the newest pending live tone row per model/pair sample
- `scorey eval-tone-sample --limit 12 --pick paper` narrows the tone review queue to paper-only user picks
- `scorey eval-tone-judge 17922 pass --note "pick-aware playful confident coherent imaginative"` records one tone verdict
- `scorey eval-tone-archive 17922 --note "paper seam archived out of active queue"` archives one pending tone row out of the active review surface
- `scorey eval-tone-disposition-sample --limit 12` lists failed tone rows that still need `RETAIN` or `EVICT`
- `scorey eval-tone-dispose 17922 retain --note "keep in active lane"` records one failure disposition after a tone `fail`
- `scorey research-beta-1 --limit 10` runs the current picks gate against recent rows
- `scorey eval-sample-local --count 30` records deterministic baseline local eval rows
- `scorey eval-sample-local --count 30 --pattern research-beta-1-coverage`
  records all six `Research Beta 1.0` pass pairs in a deterministic cycle
- `scorey eval-sample-local --count 30 --pair rock,paper --pair scissors,rock`
  records a focused local pair cycle for a rock win/loss lane
- `scorey eval-sample-live --count 12` records live API eval rows into the same DB
- `make caffeinate` keeps the display awake on macOS during active sessions
- `make decaffeinate` releases the managed wake lock
- `make decaffeinate-all` clears matching background `caffeinate` processes
- `make open-limits`, `make open-usage`, and `make open-billing` expose the OpenAI cost console
- `make open-cost-console` opens the full token and spend dashboard set

A first eval storage lane now exists:

- local SQLite at `.local/evals.sqlite`
- append-only top-level judgments
- explicit CLI judgment recording for pending rows
- explicit CLI review sampling for pending rows
- a notebook walkthrough in `output/jupyter-notebook/`
- a deterministic local population path for batch row creation
- a live batch path for real API row creation
- the local deterministic queue is fully judged:
  - `17,922` pass
  - `0` fail
  - `0` pending
- the live review queue now exists:
  - `1579` total live rows
  - `1579` pass
  - `0` fail
  - `0` pending beab route reviews
- the active tone queue now exists on top of the route-pass live rows:
  - `297` tone pass
  - `555` tone fail
  - `727` archived tone rows
  - `0` pending tone reviews on route-passed live rows
  - explicit tone fail dispositions now exist on the fresh post-surface lane:
    - `196` evict
    - `0` retain
    - older pre-surface tone fails still exist without dispositions and should
      not be confused with the fresh active queue
  - isolated paper-only tone lane:
    - `722` total
    - `185` pass
    - `381` fail
    - `156` archived
    - `0` pending
- tone failures now use a second explicit disposition layer:
  - `retain`
  - `evict`
- the three most recent extended live runs all held the route contract:
  - after output `18317`: `12` new live rows, all valid `Research Beta 1.0` routes
  - after output `18329`: `257` new live rows, all valid `Research Beta 1.0` routes
  - after output `18586`: `294` new live rows, all valid `Research Beta 1.0` routes
  - after output `18880`: `294` new paper-only live rows, all valid `Research Beta 1.0` routes
  - after output `19174`: `170` new live rows, all valid `Research Beta 1.0` routes
  - first mixed post-surface balance:
    - `paper/paper`: `34`
    - `paper/scissors`: `24`
    - `rock/paper`: `23`
    - `rock/rock`: `29`
    - `scissors/rock`: `28`
    - `scissors/scissors`: `32`
  - the first fresh post-surface slice is fully closed:
    - `170` route pass
    - `66` tone pass
    - `104` tone fail
    - `104` evict
    - `0` fresh pending route reviews
    - `0` fresh pending tone reviews
    - `0` fresh pending fail dispositions
  - after output `19344`: `157` new live rows, all valid `Research Beta 1.0` routes
  - post-evict mixed-run balance:
    - `paper/paper`: `25`
    - `paper/scissors`: `21`
    - `rock/paper`: `27`
    - `rock/rock`: `27`
    - `scissors/rock`: `26`
    - `scissors/scissors`: `31`
  - the post-evict slice is fully closed:
    - `157` route pass
    - `65` tone pass
    - `92` tone fail
    - `92` evict
    - `0` fresh pending route reviews
    - `0` fresh pending tone reviews
    - `0` fresh pending fail dispositions
  - paper-only balance:
    - `paper/paper`: `144`
    - `paper/rock`: `150`

## Research Snapshot

Scorey remains a small rigged rock, paper, scissors research toy.

Current project posture:

- preserve the object
- keep the surface small and local
- keep evals binary
- keep failure disposition explicit after `fail`

Current named gate:

- `Research Beta 1.0`
- picks only
- `scorey_pick, user_pick` orientation
- `pass` on reverse gameplay routes and same-pick loophole routes
- `fail` on every other pair

Current tracked research beta:

- `Research Beta 3.0`
- tone first
- local lane set:
  - rock: complete
  - paper: complete
  - scissors: complete
- live lane:
  - real API rounds recorded
  - route contract still holding so far
  - the latest paper-only run is complete and now promoted through the route floor
  - the active paper-only queue is now closed; its remaining pending rows were archived after the seam was established
  - the widened live tone queue is now also fully closed; the remaining stale non-paper pendings were archived before the next fresh run
  - the active failure contract is now:
    - `PASS / FAIL`
    - if `FAIL`, then `RETAIN / EVICT`
  - the operator surface now matches that two-step contract directly
  - current tone queue:
    - `852` rows judged
    - `297` pass
    - `555` fail
    - `727` archived
    - the strongest pass pattern is object-specific slapstick or physical demotion that still tracks both picks
    - the strongest fail pattern is still generic `real one` / `napkin` or version/copy language, with a smaller thin-power cluster like `paper supremacy` or `paper power`
  - both fresh post-surface live runs are now fully dispositioned at the
    active boundary
  - historical pre-surface tone fails still do not have dispositions and should
    be treated as legacy backlog rather than an active blocker

## Next Kernel

Choose one lane at a time:

- contract:
  - locked in tracked docs
- runtime:
  - first package skeleton is in place
  - keep the wrapper small while the live path settles
  - keep route enforcement and composition in the runtime
  - keep the token monitoring dashboard open or immediately reachable during live API work
- eval:
  - keep `Research Beta 1.0` as the routing gate
  - treat `Research Beta 3.0` as the active tone-first lane
  - use the judged live queue as the evidence surface
  - keep route review and tone review moving in tandem with live generation
  - after `fail`, use explicit failure disposition:
    - `retain` for in-scope live evidence
    - `evict` for seams that have earned an upstream correction before rerun
  - keep fresh-slice closure as the merge bar:
    - `0` route pending
    - `0` tone pending
    - `0` pending fail dispositions
  - do not treat older pre-surface fail rows as an active fresh-slice blocker
  - use the positive-only tone bar:
    - `pick-aware`
    - `playful`
    - `confident`
    - `coherent`
    - `imaginative`
  - on the current branch, package the first fully closed post-evict live slice
    and its docs refresh together
  - after that branch lands, start the next live run from this clean boundary
  - use local `baseline` sampling for soak/population, not for diversity claims
  - use local `research-beta-1-coverage` sampling when the full pass-pair truth table matters
  - use explicit local pair cycles when a research lane needs one object in a
    narrow win/loss role
  - rock lane: complete and stable
  - paper lane: complete and stable
  - scissors lane: complete and stable
  - next useful move:
    - start the next tone measurement from a fresh live run rather than the archived backlog
  - keep one narrow binary focus active at a time
- operators:
  - keep the Makefile small and useful
  - preserve `eod` as a first-class closeout command
  - keep display-sleep control explicit and managed
  - let `eod` clear stray background `caffeinate` processes
  - keep live-token visibility explicit before and during live eval work
- docs:
  - keep tracked docs aligned with what actually exists

## Guardrails

- Keep the app small.
- Keep the runtime local and CLI-first.
- Keep generation agent-backed once the live path exists.
- Keep active input fixed to `rock`, `paper`, and `scissors`.
- Do not add freeform input while the constrained interaction theory is active.
- Keep eval verdicts binary only.
- Keep `RETAIN / EVICT` as a failure-disposition rule, not as a third verdict state.
- Keep one active kernel at a time.
- Keep same-pick rounds as losing loophole rounds, not ties.
- Keep the local path deterministic and cheap.

## Close A Session

At minimum:

- confirm the active kernel was actually completed
- update this handoff if current state changed
- keep the docs honest about what exists
- prefer clean `main` once git is initialized

## Copy/Paste Refresh Prompt

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Confirm you are at the repo root. Treat the tracked docs as current project state. Then execute the Next Kernel with minimal drift and full validation.`
