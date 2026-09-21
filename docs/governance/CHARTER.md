# Scorey Charter

This page owns durable rules, collaboration model, and document boundaries.

- Use `docs/governance/DECISIONS.md` for runtime decision history.
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
- Menace is the most recently closed lens above broader prose on the full
  visible round.
- The next staged boundary above menace is a runtime instruction contract
  reset before fresh evidence is promoted again.
- Under [D-039](DECISIONS.md#d-039-restart-changed-model-measurement-at-beta-1),
  this current changed-model restart begins at the established Beta 1 route
  gate. It is a planned measurement sequence, not a new beta or a restoration
  of historical generator phrase banks.

Current tracked method ladder:

- `Research Beta 1.0`
  - closed pick-routing baseline
- `Research Beta 2.0`
  - closed focused object-lane baseline
- `Research Beta 3.0`
  - closed anchored tone-first baseline
- `Research Beta 4.0`
  - closed abstract tone measurement baseline
- `Research Beta 5.0`
  - closed fail-pressure pulse baseline
- `Research Beta 6.0`
  - closed scoreboard judgement baseline
- `Research Beta 7.0`
  - closed broader prose judgement baseline
- `Research Beta 8.0`
  - closed menace judgement baseline
- `pre-Beta 9.0`
  - staged positive runtime instruction contract

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

### Documentation Delegation

The human lead and primary engineer manage experiments together. The primary
engineer delegates supporting research, transcript capture, note-taking,
diagrams, and document writing to a continuing Scorey project task using the
same local checkout.
These assignments are pieces of the primary engineer's own work, with their
relevant conversation, sources, scope, and intended result made explicit.

This workflow is established and the research is already underway. The human
lead owns scope, acceptance criteria, meaning-level judgement, and go/no-go;
current user delegation permits the primary engineer to judge current runs in
real time. The documentation team records exact verdicts and reasons with
output IDs and source provenance.

The documentation task acts as a lead. It can handle small assignments directly
or delegate bounded parts to its own subagents. It coordinates helper file
ownership, reviews their contributions, and returns one coherent result to the
primary engineer. The [collaboration diagram](../diagrams/COLLABORATION.md)
shows both levels of delegation and review.

The documentation team can capture exchanges while the experiment discussion
continues. Captures preserve source wording, speakers, order, and source
location, with summaries and interpretation clearly distinguished. Gaps remain
explicit; capture dates and discourse dates remain distinct, and later
corrections retain their context. Transcript captures stay private under
`docs/peanut/transcripts/`.

The primary engineer coordinates file ownership, personally reads the returned
reports, checks their supporting evidence, and integrates the findings into the
correct documentation surface. Experiment execution
and shared-checkout Git operations remain with the primary engineer. The
documentation task edits assigned files within the same active kernel.
Observations, hypotheses, human decisions, and engineer interpretations retain
distinct attribution. Human criteria, meaning-level judgement, and go/no-go
ownership remain current; the primary's delegated live judging is recorded with
its source and attribution.

## Repo Truth Boundaries

- Tracked repo docs and live repo state outrank memory when they disagree.
- Stale tracked docs are defects.
- `docs/peanut/` stays the local and private working lane.
- Local eval evidence is part of repo truth, not disposable narration.

## Document Roles

All documentation stays concise, including private notes and helper reports.
Lead with the useful finding, decision, or action. State each point once and link supporting evidence.
Keep the conditions and attribution needed to understand it accurately.

The runtime decision ledger records runtime choices. Capture experiment
conditions, findings, and proposed research directions in research notes;
keep collaboration and writing preferences here. A proposal retains its
attribution until the human lead adopts it.

| Surface | Owns |
| --- | --- |
| `CHARTER` | durable rules and collaboration model |
| `DECISIONS` | runtime decision history |
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
