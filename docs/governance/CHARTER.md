# Scorey Charter

## Mission

Build a small, local, CLI-first mini chatbot for inspecting constrained round
behaviour through rigged rock, paper, scissors outcomes and fail-first
evaluation.

## Durable Rules

- Local CLI runtime is canonical.
- Runtime stays agent-backed through the OpenAI Agents SDK.
- Prompt surface stays fixed to:
  - `rock`
  - `paper`
  - `scissors`
- Scorey round contract stays unfair and legible:
  - Scorey wins
  - the user loses
  - same-pick rounds remain valid losses
- Runtime owns route selection, round composition, and output labels.
- Live generation owns only the small unstable round fields:
  - Scorey's winning state
  - the user's worse state
  - a scoreboard claim
- Responses stay lowercase, bratty, unfair, and round-aware.
- Eval semantics stay binary:
  - `pass`
  - `fail`
  - after `fail`, choose:
    - `retain`
    - `evict`
- The active eval loop starts with route correctness and expands only after
  the core round stays stable.
- Tracked docs, code, tests, and local eval evidence are canonical repo truth.
- `docs/peanut/` stays the local and private lane.
- Small, testable changes are the default delivery shape.
- Evidence inspection comes before interpretation.
- Evidence chains stay preserved through archive-first handling.

## Working Model

- Human lead owns:
  - hypotheses
  - scope boundaries
  - acceptance criteria
  - meaning-level trade-offs
  - go or no-go decisions
- Engineer owns:
  - implementation
  - validation
  - Git and PR flow
  - proactive hygiene
  - execution recommendations
- Default execution model:
  - one feature branch per change set
  - protected-main PR flow
  - clean synced `main` as the tracked stop state
- Parallel implementation uses dedicated worktrees.

## Documentation Governance

- `docs/governance/DECISIONS.md`
  - durable repo decisions
- `docs/governance/SESSION_HANDOFF.md`
  - active slice and carryover
- `docs/runtime/RUNBOOK.md`
  - operator procedure
- `docs/runtime/ARCHITECTURE.md`
  - stable system shape
- `docs/runtime/START_END_REFERENCE.md`
  - compact command card
- `docs/research/`
  - tracked beta findings
- `docs/diagrams/`
  - tracked runtime and eval diagrams
- `docs/peanut/`
  - local and private working lane

## Current Scope

- local CLI runtime and operator surface
- fixed pick selection
- runtime-owned route composition for one unfair round
- binary eval stack with explicit `retain` and `evict` outcomes
- tone-first review after route stability
- tracked beta research notes and diagrams
- smaller, single-purpose docs aligned with live repo behaviour

## Security / Ops Baseline

- `OPENAI_API_KEY` is present for live runtime work.
- Local `.venv` is the canonical development environment.
- Local terminal execution is the trusted development boundary.
- `.local/evals.sqlite` is the live eval evidence store.
- `make doctor-env` is the environment confirmation entrypoint.
- Local validation exposes Make targets for docs linting, package checks, and
  dependency security checks.
