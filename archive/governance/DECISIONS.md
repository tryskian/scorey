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
- Why: Scorey is a small Polinko-line research instrument, not a broad app
  shell.

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

## D-003: Agent-backed generation with deterministic shell

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `agents_sdk`, `deterministic_shell`, `round_contract`
- Provenance: `implementation decision`
- Decision:
  - use the OpenAI Agents SDK for live generation
  - constrain the live model to generating small unfair state fields
  - let Scorey compose the final output shape, picks, and score
- Why: The model should provide the unstable creative part while the runtime
  protects the eval surface from avoidable formatting and routing drift.

## D-004: Binary eval gates

- Date: `2026-05-04`
- Category: `eval_quality`
- Tags: `pass_fail`, `polinko_lineage`, `strict_judgment`
- Provenance: `human-led method decision`
- Decision:
  - keep human eval verdicts strictly binary:
    - `pass`
    - `fail`
  - do not add mixed or partial verdict states
- Why: This carries the same pass/fail discipline as the wider Polinko work.

## D-005: Beta Eval 1.0 is pick routing only

- Date: `2026-05-04`
- Category: `eval_quality`
- Tags: `beta_eval_1_0`, `pick_routing`, `one_focus`
- Provenance: `human-led method decision`
- Decision:
  - start batch evals with one focus only: user pick vs. Scorey pick
  - valid Scorey picks are the normal-losing object or the same object:
    - `rock` -> `scissors` or `rock`
    - `paper` -> `rock` or `paper`
    - `scissors` -> `paper` or `scissors`
  - leave product fit, round coherence, and brat fit pending during this pass
- Why: The first eval must establish routing before judging fake-rule quality
  or Scorey's voice.

## D-006: Governance docs mirror the small Polinko pattern

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `docs_governance`, `charter`, `handoff`, `decisions`
- Provenance: `repo formalization`
- Decision:
  - add a small governance stack:
    - charter
    - decisions
    - session handoff
  - keep current state in `docs/governance/SESSION_HANDOFF.md`
  - keep durable decisions in `docs/governance/DECISIONS.md`
- Why: Scorey needs the same session handoff and clean-main discipline as the
  adjacent toy-factory research repos without adding heavy process overhead.

## D-007: Local editor state stays ignored

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `gitignore`, `local_state`, `handoff_hygiene`
- Provenance: `implementation decision`
- Decision:
  - ignore local editor/session files:
    - `.history/`
    - `*.code-workspace`
- Why: These files are local working state, not project artifacts.
