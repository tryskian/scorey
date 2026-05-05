# Session Handoff

Last updated: 2026-05-05

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

Scorey is a small rigged rock, paper, scissors toy with a working runtime and a
first eval lane.

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
- `make eod`
- `make eod-preflight`

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
- the first live batch now exists:
  - `12` rows
  - `12` routing pass
  - `0` routing fail
  - `12` human pass
  - `0` human fail
  - `0` human pending

## Research Snapshot

Scorey remains a small rigged rock, paper, scissors research toy.

Current project posture:

- preserve the object
- keep the surface small and local
- keep evals binary

Current named gate:

- `Research Beta 1.0`
- picks only
- `scorey_pick, user_pick` orientation
- `pass` on reverse gameplay routes and same-pick loophole routes
- `fail` on every other pair

Current tracked research beta:

- `Research Beta 2.0`
- focused object lanes
- local lane set:
  - rock: complete
  - paper: complete
  - scissors: complete

## Next Kernel

Choose one lane at a time:

- contract:
  - locked in tracked docs
- runtime:
  - first package skeleton is in place
  - keep the wrapper small while the live path settles
  - keep route enforcement and composition in the runtime
  - next useful runtime move: widen the live queue carefully after the clean first judged batch
- eval:
  - keep `Research Beta 1.0` as the routing gate
  - use `Research Beta 2.0` for focused object-lane runs
  - keep the gate read-only until a stored judgment path earns a wider surface
  - use local `baseline` sampling for soak/population, not for diversity claims
  - use local `research-beta-1-coverage` sampling when the full pass-pair truth table matters
  - use explicit local pair cycles when a research lane needs one object in a
    narrow win/loss role
  - rock lane: complete and stable
  - paper lane: complete and stable
  - scissors lane: complete and stable
  - next useful move: run a slightly wider judged live batch
  - keep one narrow binary focus active at a time
- operators:
  - keep the Makefile small and useful
  - preserve `eod` as a first-class closeout command
  - keep display-sleep control explicit and managed
  - let `eod` clear stray background `caffeinate` processes
  - keep live-token visibility explicit before extended runs
- docs:
  - keep tracked docs aligned with what actually exists

## Guardrails

- Keep the app small.
- Keep the runtime local and CLI-first.
- Keep generation agent-backed once the live path exists.
- Keep active input fixed to `rock`, `paper`, and `scissors`.
- Do not add freeform input while the constrained interaction theory is active.
- Keep eval verdicts binary only.
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
