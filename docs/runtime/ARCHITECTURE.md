# Architecture

This is the fast map of Scorey's stable shape.

On day zero, only the docs spine is tracked. This file records the intended
system shape as the rebuild lands, while staying honest about what exists now.

## System Map

| Surface | Role |
| --- | --- |
| `README.md` | public framing and current repo entrypoint |
| `docs/governance/CHARTER.md` | durable rules and scope |
| `docs/governance/DECISIONS.md` | durable runtime and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next kernel |
| `docs/runtime/ARCHITECTURE.md` | stable system map |
| `docs/runtime/RUNBOOK.md` | operator procedure and validation |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |
| planned runtime package under `src/scorey/` | future home for config, agent, CLI, and eval storage |

## Default App Path

The target default user path is bare `scorey`.

When the runtime lands, it should open a persistent local CLI loop with:

- a compact startup header
- a fixed selector for:
  - `rock`
  - `paper`
  - `scissors`
- `enter` as the primary action
- `esc` as the explicit exit path
- a visible wait state while generation runs
- the full round reveal under the selected pick
- an immediate replay prompt

The app loop does not exist yet. This section describes the intended stable
shape, not a shipped command surface.

## Generation Path

The current target shape is:

1. The user selects `rock`, `paper`, or `scissors`.
2. The runtime validates the fixed pick.
3. Scorey routes to an allowed Scorey pick.
4. The route defines the matchup frame for the round.
5. The live model generates only the unstable unfair round state it needs.
6. The runtime composes the final round shape.

The exact boundary between runtime-owned and model-generated fields is the next
active contract kernel.

## Eval Path

No eval storage is tracked yet.

The intended eval shape is:

- local storage under `.local/`
- binary human judgment
- one active eval focus at a time
- explicit separation between top-level product judgment and downstream lenses

This section should tighten only after the round contract and first eval lane
are real.

## Contracts

- The runtime stays local and CLI-first.
- The default runtime path stays agent-backed once it exists.
- The deterministic local path stays beside the live path.
- The prompt surface stays fixed to `rock`, `paper`, and `scissors`.
- The default user path opens the app loop.
- Operator commands stay separate from the app loop.
- Eval verdicts stay binary:
  - `pass`
  - `fail`

## Docs Ownership

| Doc | Job |
| --- | --- |
| `README.md` | public framing and entrypoint |
| `docs/governance/CHARTER.md` | durable rules and working model |
| `docs/governance/DECISIONS.md` | durable engineering, runtime, and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next slice |
| `docs/runtime/ARCHITECTURE.md` | stable system map |
| `docs/runtime/RUNBOOK.md` | operator procedure and validation |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |
