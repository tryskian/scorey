# Session Handoff

Last updated: 2026-05-04

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - this file
2. Confirm repo path:
   - `/Users/tryskian/Github/scorey`
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
- `scorey play rock` plays one live round
- `scorey --local play rock` plays one deterministic local round
- `scorey eval-init` initializes the local eval database
- `scorey eval-list --limit 10` lists recent eval rows
- `scorey eval-beta-1 --limit 10` runs the current picks gate against recent rows
- `scorey eval-sample-local --count 30` records deterministic baseline local eval rows
- `scorey eval-sample-local --count 30 --pattern beta-1-coverage` records all
  six `Beta 1.0` pass pairs in a deterministic cycle
- `scorey eval-sample-local --count 30 --pair rock,paper --pair scissors,rock`
  records a focused local pair cycle for the rock win/loss slice
- `make caffeinate` keeps the display awake on macOS during active sessions
- `make decaffeinate` releases the managed wake lock
- `make decaffeinate-all` clears matching background `caffeinate` processes

A first eval storage lane now exists:

- local SQLite at `.local/evals.sqlite`
- append-only top-level judgments
- a notebook walkthrough in `output/jupyter-notebook/`
- a deterministic local population path for batch row creation

## Research Snapshot

Scorey remains a small rigged rock, paper, scissors research toy.

Current project posture:

- preserve the object
- keep the surface small and local
- keep evals binary

Current named gate:

- `Beta 1.0`
- picks only
- `scorey_pick, user_pick` orientation
- `pass` on reverse gameplay routes and same-pick loophole routes
- `fail` on every other pair

Current tracked eval beta:

- `Beta Eval 2.0`
- focused object slices
- current live slice:
  - `rock,paper`
  - `scissors,rock`

## Next Kernel

Choose one lane at a time:

- contract:
  - locked in tracked docs
- runtime:
  - first package skeleton is in place
  - keep the wrapper small while the live path settles
  - keep route enforcement and composition in the runtime
  - polish the interactive app only if it helps the core object
- eval:
  - keep `Beta 1.0` as the routing gate
  - use `Beta Eval 2.0` for focused object-slice runs
  - keep the gate read-only until a stored judgment path earns a wider surface
  - use local `baseline` sampling for soak/population, not for diversity claims
  - use local `beta-1-coverage` sampling when the full pass-pair truth table matters
  - use explicit local pair cycles when a research slice needs one object in a
    narrow win/loss role
  - keep one narrow binary focus active at a time
- operators:
  - keep the Makefile small and useful
  - preserve `eod` as a first-class closeout command
  - keep display-sleep control explicit and managed
  - let `eod` clear stray background `caffeinate` processes
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

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Confirm the repo path is /Users/tryskian/Github/scorey. Treat the tracked docs as current project state. Then execute the Next Kernel with minimal drift and full validation.`
