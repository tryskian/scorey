# Scorey Charter

## Mission

Scorey is a small, local, agent-backed rock, paper, scissors mini chatbot.

It explores constrained human-AI interaction through deliberately unfair
round reasoning, narrow generation, and binary evals.

Scorey is part of the Polinko research line. It is smaller than Polinko, and
it sits near Probaboracle as a toy-factory research instrument: narrow surface,
clear scope, hard evals, and careful docs.

## Durable Rules

These rules define the project shape.

Runtime:

- local and CLI-first
- agent-backed through the OpenAI Agents SDK
- deterministic local fixture path behind `--local`
- live path owns only the small generated state it needs
- Scorey composes the final round shape

Prompt surface:

- `rock`
- `paper`
- `scissors`

The active runtime path does not accept freeform prompt input. The fixed picks
are the interaction boundary and the eval boundary.

Responses:

- lowercase
- bratty
- unfair
- round-aware
- not helpful, polished, legalistic, mystical, or fair

Eval:

- binary verdicts only
- `pass`
- `fail`
- one eval focus at a time
- `Beta Eval 1.0` starts with pick routing only

Project posture:

- keep it small
- keep it local-first
- keep it aligned with Polinko's safety and eval discipline
- archive before delete

## Working Model

Human lead owns:

- objective
- scope boundaries
- acceptance criteria
- theory-level interpretation
- go/no-go decisions

Engineer owns:

- implementation
- validation
- branch and PR flow
- runtime hygiene
- execution recommendations

Default execution model:

- feature branch per change set
- clean `main`
- local-first iteration
- end sessions on synced `main` when possible

## Documentation Ownership

| Doc | Job |
| --- | --- |
| `README.md` | public framing and command entrypoint |
| `docs/governance/DECISIONS.md` | durable engineering, runtime, and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next slice |
| `docs/research/README.md` | current research framing and beta map |
| `docs/runtime/ARCHITECTURE.md` | stable system shape |
| `docs/runtime/RUNBOOK.md` | operator procedure and commands |
| `docs/diagrams/PIPELINE.md` | public generation and eval-shape diagrams |

After runtime, product-shape, or research-method changes, sweep the tracked
docs before merging.

## Scope

In scope:

- local CLI runtime
- fixed pick selection
- agent-backed generation
- local SQLite eval storage
- binary human judgment
- diagram-backed runtime explanation
- governance docs for charter, decisions, and handoff state

Out of scope:

- web UI
- backend API
- auth
- deployment scaffolding
- freeform chat input

## Security And Ops

- `OPENAI_API_KEY` is required for live generation.
- The local runtime auto-loads the repo `.env`.
- Local CLI execution is the trusted development boundary.
- Local eval data stays under `.local/`.
- Local editor/session state stays out of git:
  - `.history/`
  - `*.code-workspace`
