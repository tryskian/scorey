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

## D-005: Start from the contract outward

- Date: `2026-05-04`
- Category: `collaboration_method`
- Tags: `contract_first`, `runtime_boundary`, `project_shape`
- Provenance: `human-led method decision`
- Decision:
  - define the round contract before expanding the runtime shell
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

## D-007: Scorey gets a small operator command surface from day zero

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `makefile`, `operators`, `eod`, `session_status`
- Provenance: `human-led method decision`
- Decision:
  - add a small `Makefile` operator surface before the runtime lands
  - include `eod` as a first-class operator command
  - keep the operator surface toy-sized rather than inheriting `polinko` scale
- Why: The toy family uses operators as part of the working method, and end-of-day
  closeout is important enough to exist from the start instead of arriving later.

## D-008: Valid Scorey routing stays narrow and same-pick rounds still lose

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `routing`, `same_pick`, `round_contract`
- Provenance: `human-led method decision`
- Decision:
  - keep the allowed Scorey pick routes to:
    - `rock` -> `scissors` or `rock`
    - `paper` -> `rock` or `paper`
    - `scissors` -> `paper` or `scissors`
  - treat same-pick rounds as valid losing rounds for the user, not ties
- Why: Scorey should stay anchored to the user's actual pick instead of drifting
  into ordinary counter-pick logic, and same-pick loophole wins are part of the
  toy's contract rather than an edge case.

## D-009: Runtime owns round composition and the model owns only small unstable fields

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `composition`, `model_boundary`, `round_contract`
- Provenance: `implementation decision`
- Decision:
  - keep routing, output labels, and final round composition in the runtime
  - let the live model generate only:
    - Scorey's winning state
    - the user's worse state
    - a small scoreboard claim
- Why: The unstable creative parts should stay generated, but the runtime should
  own the contract shape so the toy remains legible and easier to evaluate.

## D-010: Live generation uses structured round fields

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `agents_sdk`, `structured_output`, `round_fields`
- Provenance: `implementation decision`
- Decision:
  - use the OpenAI Agents SDK live path with structured output
  - have the live model return only:
    - `winning_state`
    - `worse_state`
    - `scoreboard_claim`
- Why: Structured fields fit the contract better than free-text whole-round
  generation and make runtime composition more stable.

## D-011: Local runtime uses deterministic fixture routes

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `local_mode`, `fixtures`, `deterministic_baseline`
- Provenance: `implementation decision`
- Decision:
  - keep `--local` deterministic
  - back the local path with fixed route fixtures rather than ad hoc random text
  - include at least one same-pick local route so the loophole family stays real
- Why: The local path is a contract baseline, not the primary research surface.
  It should be cheap, predictable, and broad enough to hold both route families.

## D-012: Python quality gates are first-class operator checks

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `ruff`, `mypy`, `pytest`, `quality_gates`
- Provenance: `implementation decision`
- Decision:
  - include `ruff`, `mypy`, and `pytest` in the tracked dev toolchain
  - expose them as first-class operator commands
  - make `make check` run formatting checks, linting, typing, tests, and diff hygiene
- Why: Scorey is small enough that the core quality gates can stay fast and
  local. If they are not part of the default operator loop, they will drift
  into optional cleanup instead of baseline discipline.

## D-013: Pre-commit hooks and branch coverage are part of baseline hygiene

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `pre_commit`, `coverage`, `branch_coverage`, `tooling`
- Provenance: `implementation decision`
- Decision:
  - add tracked `pre-commit` hooks for repo hygiene and Python checks
  - install both `pre-commit` and `pre-push` hook types by default
  - add branch-coverage test runs as a first-class operator surface
- Why: Tooling drift was part of what made the previous runtime sloppy. These
  checks should be automatic and visible enough that they stay part of the
  baseline instead of becoming cleanup work.

## D-014: Scorey eval storage starts as a small local SQLite lane

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `eval_db`, `sqlite`, `binary_verdicts`, `notebook`
- Provenance: `implementation decision`
- Decision:
  - store eval rows locally in `.local/evals.sqlite`
  - keep top-level verdict history append-only
  - mirror the current verdict onto the output row for fast listing
  - add one notebook walkthrough that uses the same tracked module functions
- Why: The first eval lane should be small enough to inspect directly while
  still behaving like a real persistence surface. The notebook is for following
  along, not for inventing a separate eval system.

## D-015: Beta 1.0 judges only pick routing

- Date: `2026-05-04`
- Category: `eval_quality`
- Tags: `beta_1_0`, `pick_routing`, `truth_table`, `binary_gate`
- Provenance: `human-led method decision`
- Decision:
  - name the first active gate `Beta 1.0`
  - judge only the pick pair in `scorey_pick, user_pick` order
  - `pass`:
    - `paper, scissors`
    - `rock, paper`
    - `scissors, rock`
    - `paper, paper`
    - `rock, rock`
    - `scissors, scissors`
  - `fail`:
    - every other `scorey_pick, user_pick` pair
  - keep the gate read-only in the operator surface for now
- Why: This is the narrowest clean gate for the first Scorey beta. It tests
  the object's core routing claim without mixing in prose quality, tone, or
  scoreboard judgment too early.

## D-016: Local eval batches use a deterministic population command

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `local_eval_sampling`, `sqlite`, `soak`, `operator_surface`
- Provenance: `human-led method decision`
- Decision:
  - add a first-class local eval sampling command
  - let it record deterministic fixture rounds into `.local/evals.sqlite`
  - support both bounded row counts and duration-based runs
  - treat this lane as batch population and soak coverage, not as a diversity claim
- Why: The first eval rows should be cheap to generate and easy to inspect
  without involving live generation. A tracked operator command is cleaner than
  one-off shell loops, and the repo should say plainly what this lane can and
  cannot demonstrate.

## D-017: Display wake control is a first-class session operator

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `caffeinate`, `display_sleep`, `session_ops`, `eod`
- Provenance: `human-led method decision`
- Decision:
  - add managed `make caffeinate` and `make decaffeinate` commands for macOS sessions
  - add `make decaffeinate-all` for matching background `caffeinate -d -i -m` processes
  - track the managed process with a PID file
  - make `make eod` always attempt `decaffeinate-all` before exit
- Why: Long local sessions and eval runs should not lose the display to sleep,
  but wake control should still be explicit and easy to shut off at session end,
  including the cases where a background `caffeinate` outlives the managed PID file.
