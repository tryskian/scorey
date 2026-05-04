# Scorey Charter

## Mission

Scorey is a small, local, agent-backed rock, paper, scissors mini chatbot.

It explores constrained human-AI interaction through deliberately unfair round
reasoning, narrow generation, and strict binary evaluation.

Scorey is part of the Polinko research line, but it is shaped like the other
tiny toy siblings: small surface, clear scope, hard evals, and careful docs.

## Durable Rules

These rules define the project shape.

Runtime:

- local and CLI-first
- agent-backed through the OpenAI Agents SDK once the live path lands
- deterministic local fixture path beside the live path
- live generation owns only the unstable round state it needs
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
- start with the round contract before broader product taste

Project posture:

- keep it small
- keep it local-first
- keep it aligned with Polinko's eval discipline
- evolve tooling intentionally
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
- runtime hygiene
- docs upkeep
- execution recommendations

Default execution model:

- one active kernel at a time
- local-first iteration
- visible checkpoints
- keep working through non-blocking side thoughts during an active task
- only redirect mid-run when the new information materially changes the active kernel
- docs stay in sync with real state

## Documentation Ownership

| Doc | Job |
| --- | --- |
| `README.md` | public framing and current entrypoint |
| `docs/governance/DECISIONS.md` | durable engineering, runtime, and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next kernel |
| `docs/runtime/ARCHITECTURE.md` | stable system shape |
| `docs/runtime/RUNBOOK.md` | operator procedure and validation |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |

After runtime, product-shape, or research-method changes, sweep the tracked
docs before calling the state settled.

## Scope

In scope:

- local CLI runtime
- fixed pick selection
- agent-backed generation
- deterministic local baseline
- binary human judgment
- local eval storage when the eval lane lands
- diagram-backed runtime explanation
- governance docs for charter, decisions, and handoff state

Out of scope:

- web UI
- backend API
- auth
- deployment scaffolding
- freeform chat input

## Security And Ops

- `OPENAI_API_KEY` is required for live generation once the runtime exists.
- The local runtime should auto-load the repo `.env`.
- Local CLI execution is the trusted development boundary.
- Local eval data should live under `.local/` when the eval lane lands.
