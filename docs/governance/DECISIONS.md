# Decisions Log

This file is the durable archive of Scorey's engineering, runtime, and eval
decisions.

## How To Use This File

- Need the current durable rules:
  - start with `docs/governance/CHARTER.md`
- Need the current system shape:
  - use `docs/runtime/ARCHITECTURE.md`
- Need the current checkpoint:
  - use `docs/governance/SESSION_HANDOFF.md`
- Need the reasoning behind a repo choice:
  - use this file

Keep entries short, but informative enough to show what changed and why.

## Taxonomy

- `runtime_engineering`
- `eval_quality`
- `collaboration_method`
- `workflow_environment`

## Provenance Rule

Each decision should read as one of these:

- `human-led method decision`
  - the theory, bridge logic, or eval meaning came from the human lead
- `repo formalization`
  - the repo later encoded an already-active method or contract
- `implementation decision`
  - the engineering layer chose mechanics after the method was already set

If a decision crosses layers, say so plainly instead of flattening the method
into implementation authorship.

## D-001: Local CLI first

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `local_first`, `cli`, `small_surface`
- Provenance: `repo formalization`
- Decision:
  - start with a local CLI runtime
  - keep the first execution path terminal-native and local
- Why: Scorey is a tiny research toy, not a broad app shell.

## D-002: Fixed pick surface

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `prompt_surface`, `constrained_input`, `rps`
- Provenance: `human-led method decision`
- Decision:
  - limit the active prompt surface to:
    - `rock`
    - `paper`
    - `scissors`
  - do not accept freeform prompt input in the active runtime path
- Why: Scorey studies constrained round reasoning, not open chat.

## D-003: Binary eval gates

- Date: `2026-05-04`
- Category: `eval_quality`
- Tags: `pass_fail`, `strict_judgment`, `one_focus`
- Provenance: `human-led method decision`
- Decision:
  - keep human eval verdicts strictly binary:
    - `pass`
    - `fail`
  - keep one eval focus active at a time
- Why: This preserves the hard yes/no discipline of the toy family and keeps
  each eval pass interpretable.

## D-004: Small governance and runtime doc stack

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `docs_stack`, `charter`, `runbook`, `handoff`
- Provenance: `implementation decision`
- Decision:
  - use a compact docs spine:
    - charter
    - decisions
    - session handoff
    - architecture
    - runbook
    - research readme
    - pipeline diagram
- Why: The project needs a clear instruction surface without dragging in a
  heavier process shell.

## D-005: Rebuild from the contract outward

- Date: `2026-05-04`
- Category: `collaboration_method`
- Tags: `contract_first`, `rebuild`, `runtime_boundary`
- Provenance: `human-led method decision`
- Decision:
  - define the round contract before rebuilding the runtime shell
  - separate runtime-owned fields from model-generated fields early
- Why: The previous runtime drifted because too much shape was implicit. The new
  build should earn its complexity from a clear contract.

## D-006: OpenAI upstream references stay live

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `openai`, `upstream`, `sdk`, `tooling`
- Provenance: `human-led method decision`
- Decision:
  - check current official OpenAI docs and SDK repositories before hardening
    runtime patterns that depend on them
  - keep a small upstream reference list in the runbook for the tooling this
    project actually uses
- Why: OpenAI tooling changes fast enough that stale habits can quietly harden
  into the repo if the upstream surface is not checked deliberately.
