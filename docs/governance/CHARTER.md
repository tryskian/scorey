# Scorey Charter

This page owns durable rules, collaboration model, and document boundaries.

- Use `docs/governance/DECISIONS.md` for durable decision history.
- Use `docs/governance/SESSION_HANDOFF.md` for the active kernel and carryover.
- Use `docs/runtime/ARCHITECTURE.md` for the stable system shape.
- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/runtime/START_END_REFERENCE.md` for the compact command card.

## Mission

Scorey is a small local CLI research instrument for one unfair rock, paper,
scissors round.

The point is not breadth. The point is to keep the round narrow, legible, and
comparable while bounded eval lenses test whether the visible result still
holds together.

## Core Round Contract

- The local CLI runtime is canonical.
- The fixed interaction boundary stays:
  - `rock`
  - `paper`
  - `scissors`
- Scorey wins and the user loses.
- Same-pick rounds are valid losses, not ties.
- The runtime owns:
  - route selection
  - output labels
  - final round composition
- The live model owns only:
  - `winning_state`
  - `worse_state`
  - `scoreboard_claim`
- The visible round should stay compact, unfair, and round-aware.
- Tracked repo truth lives in code, tests, docs, and local eval evidence.

## Evaluation Charter

- Route validity stays the floor.
- Tone stays the first widened row-level lens above route.
- Failed tone rows stay explicit:
  - `retain`
  - `evict`
- Widened lenses advance one layer at a time and must close back to
  `0` pending.
- Pulse stays the bounded run-level lens:
  - rows are labelled as `anchor`, `counted_seam`, or `excluded_noise`
  - only anchors and counted seams affect the pulse verdict
- Scoreboard stays a row-level lens on `scoreboard_claim`.
- Broader prose stays a row-level lens on the round body around the score
  line.
- Menace is the active lens above broader prose on the full visible round.

Current tracked method ladder:

- `Research Beta 4.0`
  - closed abstract tone measurement baseline
- `Research Beta 5.0`
  - closed fail-pressure pulse baseline
- `Research Beta 6.0`
  - closed scoreboard judgement baseline
- `Research Beta 7.0`
  - closed broader prose judgement baseline
- `Research Beta 8.0`
  - active menace judgement lane

## Collaboration Model

Human lead owns:

- hypotheses
- scope boundaries
- acceptance criteria
- meaning-level trade-offs
- go or no-go decisions

Engineer owns:

- implementation
- validation
- Git and PR flow
- proactive hygiene
- execution recommendations

Working shape:

- one active kernel at a time
- one tracked change set per feature branch
- protected-main flow for tracked merges
- clean synced `main` as the tracked stop state

## Repo Truth Boundaries

- Tracked repo docs and live repo state outrank memory when they disagree.
- Stale tracked docs are defects.
- `docs/peanut/` stays the local and private working lane.
- Local eval evidence is part of repo truth, not disposable narration.

## Document Roles

| Surface | Owns |
| --- | --- |
| `CHARTER` | durable rules and collaboration model |
| `DECISIONS` | durable decision history |
| `SESSION_HANDOFF` | active kernel and carryover |
| `ARCHITECTURE` | stable runtime shape |
| `RUNBOOK` | operator procedure |
| `START_END_REFERENCE` | compact command card |
| `docs/research/` | tracked beta boundaries and evidence notes |
| `docs/diagrams/` | tracked diagrams |
| `docs/peanut/` | local and private working surfaces |

## Ops Baseline

- Local `.venv` is the canonical development environment.
- The repo `.local` surface is the canonical live eval store.
- Secondary worktrees reuse the canonical repo `.local` surface for live eval
  work.
- A session is not closed until `make end` passes on clean synced `main`.
