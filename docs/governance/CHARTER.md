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
- Tone stays the first widened row-level lens above route in the established
  database evaluation sequence.
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
- `410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md` remains the earlier
  historical staged positive-runtime contract above menace.
- The current [Pre-Beta 9.0: Coherent Absurdity](../research/420_PB-COHERENT_ABSURDITY.md)
  inquiry is paused for protocol alignment under D-045.
- Under [D-039](DECISIONS.md#d-039-restart-changed-model-measurement-at-beta-1),
  the September 20 changed-model restart began at Beta 1. Its completed route
  baseline remains distinct from the new coherent-absurdity arc.
- The [experimental execution pipeline](../diagrams/GOLDEN_SMOKE.md) records
  six independent matchup calls. Its fixture has no high-signal assistant
  reference answers. The requested user/assistant golden pairs and their use
  must be aligned with the established protocol before further implementation.
- `coherent-absurdity-review-1` remains the frozen review condition for the
  saved experiment. Its engineering formalization is paused; original
  mechanics, scoreboard, menace, and attributed human verdicts stay separate.
- Smoke receipts preserve requests, raw responses, failures, and mechanical
  results. The six current mechanical passes are separate from six human
  `FAIL` judgements with preserved notes, one human observation, six assistant
  observations, and zero assistant judgements. These review responses do not
  close historical gates. The established protocol governs any resumed
  evaluation and promotion. Smoke and review sync do not change historical
  eval rows or advance historical gates.
- The staged review reader works one complete composed round at a time and
  preserves the complete response, picks, conditions, timings, token use,
  verdict, reason, source, and field-or-phrase location when present.
- Assistant observations are separately attributed from human verdicts. An
  observation may exist without a verdict, and exact human wording remains
  preserved rather than being rewritten as an assistant conclusion.
- The implemented review setup is additive: an imported dataset with case and
  event tables in the existing eval database, plus a separate notebook
  `.notes.json` sidecar. Existing review tooling and historical gate tables
  remain intact. Import preserves attributed review events but does not itself
  imply promotion.

Historical tracked method ladder:

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
  - earlier 410 positive-runtime staging and paused 420 coherent-absurdity inquiry

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
- local checkpoints during work, with commits grouped around coherent changes
- protected-main flow for tracked merges
- clean synced `main` as the tracked stop state

Scorey is an existing research project with an established protocol. Read and
follow that protocol before adapting the work; align proposed changes with the
human lead. When understanding is incomplete, check authoritative sources or
ask the human lead. Keep uncertainty explicit and never present an unverified
interpretation as an established finding, decision, or implementation basis.
These requirements apply to the primary engineer and delegated readers.

### Documentation Delegation

The human lead and primary engineer manage experiments together. The primary
engineer dispatches four focused continuing tasks for alignment, runtime
records, research records, and transcript capture in the same local checkout.
Each assignment carries its relevant conversation, sources, scope, intended
result, and exact file boundary.

Research records include relevant research diagrams; runtime records include
execution pipelines. Owners create or update these alongside their records,
using verified method and implementation and labelling proposed flows.
Alignment checks consistency and coordinates changes across file owners.
Source diagrams retain their original form and provenance; new explanatory
drawings remain distinct from source evidence.

This workflow is established and the research is already underway. The human
lead owns scope, acceptance criteria, meaning-level judgement, and go/no-go;
explicit delegation permits the primary engineer to judge the named runs in
real time. D-045 currently pauses generation. The documentation team records verdicts and reasons with
output IDs and source provenance.

Each focused task can handle a small assignment directly or use bounded internal
subagents within its inherited file boundary. The task reviews its contributions
and returns to the primary engineer. The [collaboration diagram](../diagrams/COLLABORATION.md)
shows the four-task pattern and review path.

The documentation team can capture exchanges while the experiment discussion
continues. Captures preserve source wording, speakers, order, and source
location, with summaries and interpretation clearly distinguished. Gaps remain
explicit; capture dates and discourse dates remain distinct, and later
corrections retain their context. Transcript captures stay private under
`docs/peanut/transcripts/` and follow the format routed by the [local transcript
README](../peanut/transcripts/README.md), which points to the canonical
transcript standard.

The primary engineer coordinates file ownership, personally reads the returned
reports, checks their supporting evidence, and integrates the findings into the
correct documentation surface. Experiment execution
and shared-checkout Git operations remain with the primary engineer. The
documentation task edits assigned files within the same active kernel.
Observations, hypotheses, human decisions, and engineer interpretations retain
distinct attribution. Human criteria, meaning-level judgement, and go/no-go
ownership remain current; the primary's delegated live judging is recorded with
its source and attribution.

### Focused continuing tasks

The primary engineer dispatches bounded source packets to continuing tasks and
personally reads every return. The tasks do not automatically receive later
parent messages or monitor continuously; each return is tied to its assignment.

| Task | Ownership | Return path |
| --- | --- | --- |
| Alignment / documentation | `README.md`, `CHARTER.md`, `SESSION_HANDOFF.md`, `COLLABORATION.md` | Primary review, integration, and cross-owner gap report |
| Runtime records | `DECISIONS.md`, `ARCHITECTURE.md`, `RUNBOOK.md`, `START_END_REFERENCE.md` | Primary review and integration |
| Research records | Assigned tracked research and current private research summaries | Primary review and integration |
| Transcript keeper | Curated excerpts under `docs/peanut/transcripts/` | Primary review of sourced capture and gaps |

Supporting bounded subagents remain available inside a task's inherited file
boundary. Transcript capture begins only when a supplied or directly inspected
exchange contains a meaningful discovery, correction, or rationale; exact
speech, source limits, and interpretation remain separate. The task does not
invent a new transcript format.

## Repo Truth Boundaries

- Tracked repo docs and live repo state outrank memory when they disagree.
- Stale tracked docs are defects.
- `docs/peanut/` stays the local and private working lane.
- Local eval evidence is part of repo truth, not disposable narration.

## Document Roles

All documentation must use concise, natural language, including public docs,
research notes, private notes, and helper reports. Follow the applicable
template while preserving required structure, evidence, conditions, and
attribution. Lead with the useful point, state it once, and link supporting detail.

Reader briefs carry this rule and name the applicable template and filename
pattern. The primary engineer checks these before integration.

The runtime decision ledger records runtime choices. Capture experiment
conditions, findings, and proposed research directions in research notes;
keep collaboration and writing preferences here. A proposal retains its
attribution until the human lead adopts it.

The primary engineer keeps all affected documentation current during work:
decisions, research notes, diagrams, runtime guidance, handoff, and private notes.
Record agreed runtime and executable evaluation choices before dependent
implementation; update implementation and evidence descriptions as verified.
Incorporate clarifications with source and attribution. The primary owns this
responsibility through delegated work and personally checks that affected
surfaces agree. Updates happen as work progresses, without waiting for closeout
or reminders.

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

### Document Naming

Use these patterns for new documents and deliberate renames.

| Document type | Naming pattern |
| --- | --- |
| Governance, runtime, and diagram docs | `UPPER_SNAKE_CASE.md`; keep established canonical names |
| Folder indexes | `README.md`; the research legend remains `000_LEGEND.md` |
| Tracked research records | Follow the [research codes and type-specific templates](../runtime/templates/README.md); the metadata `Code` matches the filename without `.md` |
| Template source files | Lowercase type name, such as `hypothesis.md` |
| Private dated notes and transcripts | `YYYY-MM-DD-topic.md` |
| Private research or reentry packets | `YYYY-MM-DD-topic/` containing `README.md` |
| Private reference notes and packet files | Lowercase words separated by hyphens, such as `method-report.md` or `rounds.md`; use `01-topic.md` when reading order matters |

Private filename dates identify capture; packet dates identify the packet's
start. Record source and event dates separately inside. Tracked research keeps
dates inside documents, as its template requires.

Preserve existing paths and explicitly chosen names such as
`Getting to know Scorey.md`. When deliberately renaming a file, update its links
and provenance references together.

## Ops Baseline

- Local `.venv` is the canonical development environment.
- The repo `.local` surface is the canonical live eval store.
- Secondary worktrees reuse the canonical repo `.local` surface for live eval
  work.
- A session is not closed until `make end` passes on clean synced `main`.
