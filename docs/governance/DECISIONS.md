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
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - use a compact docs spine:
    - charter
    - decisions
    - session handoff
    - architecture
    - runbook
    - research readme
    - pipeline diagram
- Why: The repo needed to follow the tiny toy-docs shape the human lead wanted,
  and the engineering layer formalized that into the tracked file stack.

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
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - keep routing, output labels, and final round composition in the runtime
  - let the live model generate only:
    - Scorey's winning state
    - the user's worse state
    - a small scoreboard claim
- Why: The human-led method wanted a narrow, evalable boundary, and the
  engineering layer formalized that by keeping composition in the runtime and
  generation in a small structured model seam.

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
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - include `ruff`, `mypy`, and `pytest` in the tracked dev toolchain
  - expose them as first-class operator commands
  - make `make check` run formatting checks, linting, typing, tests, and diff hygiene
- Why: Tooling discipline was an explicit human concern after the previous
  runtime drifted, and the engineering layer answered that by making the core
  checks part of the default operator loop.

## D-013: Pre-commit hooks and branch coverage are part of baseline hygiene

- Date: `2026-05-04`
- Category: `workflow_environment`
- Tags: `pre_commit`, `coverage`, `branch_coverage`, `tooling`
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - add tracked `pre-commit` hooks for repo hygiene and Python checks
  - install both `pre-commit` and `pre-push` hook types by default
  - add branch-coverage test runs as a first-class operator surface
- Why: The human lead made tooling drift a first-class problem to solve, and
  the engineering layer responded by hardening the automatic hook and coverage
  surface into the repo baseline.

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

## D-015: Research Beta 1.0 judges only pick routing

- Date: `2026-05-04`
- Category: `eval_quality`
- Tags: `beta_1_0`, `pick_routing`, `truth_table`, `binary_gate`
- Provenance: `human-led method decision`
- Decision:
  - name the first active gate `Research Beta 1.0`
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

## D-018: Local eval sampling keeps separate soak and coverage patterns

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `local_eval_sampling`, `beta_1_0`, `coverage`, `operator_surface`
- Provenance: `implementation decision`
- Decision:
  - keep `baseline` as the default local sampling pattern
  - let `baseline` cycle the narrow local fixture subset for soak/population runs
  - add `research-beta-1-coverage` as a second deterministic local pattern
  - let `research-beta-1-coverage` cycle all six `Research Beta 1.0` pass pairs evenly
- Why: The first hour-long local soak proved the storage path and gate but only
  exercised three valid pass pairs. Keeping soak and full pass-table coverage as
  separate explicit patterns makes the signal clearer without broadening local
  mode into a fake diversity surface.

## D-019: Focused local eval lanes can name explicit pair cycles

- Date: `2026-05-04`
- Category: `runtime_engineering`
- Tags: `local_eval_sampling`, `focused_lanes`, `pair_cycle`, `operator_surface`
- Provenance: `human-led method decision`
- Decision:
  - let `eval-sample-local` accept explicit pair cycles in `scorey_pick,user_pick` order
  - use that lane for narrow research lanes when one object needs to be isolated
  - support the current rock lane as:
    - `rock,paper`
    - `scissors,rock`
- Why: After the broad `Research Beta 1.0` pass-table coverage run, the next research
  step is to inspect one object in a tighter role. Explicit pair cycles make
  that lane first-class without turning the local sampler into a pile of
  one-off named patterns.

## D-020: Research Beta 2.0 uses focused object lanes

- Date: `2026-05-05`
- Category: `eval_quality`
- Tags: `beta_eval_2_0`, `focused_lanes`, `object_roles`, `one_focus`
- Provenance: `human-led method decision`
- Decision:
  - treat the next active eval architecture as `Research Beta 2.0`
  - keep `Research Beta 1.0` as the routing gate underneath it
  - use explicit local pair cycles to isolate one object across a win role and a loss role
  - start with the rock lane:
    - `rock,paper`
    - `scissors,rock`
- Why: Once the full `Research Beta 1.0` pass table was stable, the next useful question
  was not whether Scorey could route at all, but whether one object could stay
  stable when forced through both sides of the rigged round. That is a real
  shift in eval shape, so it earns its own beta note instead of hiding inside
  operator commands.

## D-021: Human judgments get a first-class CLI path

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `eval_judgment`, `operator_surface`, `pending_queue`
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - let `eval-list` filter for `pending` rows
  - add `eval-judge` as an explicit operator command for one output at a time
  - keep human notes attached at judgment time instead of leaving verdicts bare
- Why: The human lead pushed the repo from generation into actual review, and
  the engineering layer had to turn that into a normal operator path instead of
  ad hoc database poking.

## D-022: Human lead called the shift to judgment after noticing 17,922 outputs with no judgments

- Date: `2026-05-05`
- Category: `eval_quality`
- Tags: `human_judgment`, `backlog`, `pending_queue`, `review_start`
- Provenance: `human-led method decision`
- Decision:
  - start judging evals after the human lead noticed the database had reached `17,922` outputs with `0` judgments
- Why: That backlog state made the bottleneck obvious. More row generation without review was no longer adding useful signal.

## D-023: Pending review sampling gets a first-class CLI path

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `eval_review`, `stratified_sample`, `operator_surface`, `pending_queue`
- Provenance: `implementation decision`
- Decision:
  - add `eval-review-sample` as an explicit operator command
  - list the newest pending row per model/pair sample
  - keep the review queue usable without ad hoc SQL
- Why: Once human review started, the next engineering bottleneck was queue
  selection. A tracked command is more durable and less error-prone than
  repeating manual database queries.

## D-024: Scorey uses a real startup banner with width-aware fallbacks

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `banner`, `header`, `cli_typography`, `responsive_fallback`
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - port the Probaboracle-style banner geometry and breakpoint logic into Scorey
  - keep a boxed banner when the terminal is wide enough
  - fall back to stacked and then minimal banner forms as width narrows
  - style only the repo line with bold accent treatment
- Why: Scorey needs a real startup identity block, but the right shape is still
  a compact CLI banner with tested fallbacks rather than a larger UI surface or
  hand-tuned one-off centring.

## D-025: The TTY app loop stages the round with a revealed `me:` slot

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `app_loop`, `selector`, `reveal`, `spinner`, `tty`
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - keep `you:` as the only active selector
  - keep `me:` inactive until the user presses `enter`
  - reveal Scorey's pick before the ruling text finishes
  - use the Probaboracle-style Braille spinner for the live wait state
  - use `enter` to play again and `esc` to exit in the TTY replay step
- Why: The round needs to feel revealed, not jointly chosen. Staging the picks,
  reveal, and ruling in-place makes the interaction legible without widening
  the UI surface or turning Scorey into a bigger app.

## D-026: Live API eval batches get a first-class operator path

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `live_eval`, `operator_surface`, `batch_generation`, `sqlite`
- Provenance: `human-led runtime request with implementation decision`
- Decision:
  - add `eval-sample-live` as an explicit operator command
  - record live API rounds into the same SQLite eval DB as local rows
  - cycle `rock`, `paper`, and `scissors` in user order by default
  - preserve immediate `Research Beta 1.0` route counters on the live batch output
- Why: Once the local deterministic queue was fully settled, the next useful
  signal had to come from real generated gameplay rather than more local
  repetition. A tracked live batch command is safer and more legible than
  improvised shell loops or manual one-round recording.

## D-027: Live evals follow the token management protocol

- Date: `2026-05-05`
- Category: `runtime_engineering`
- Tags: `token_management`, `cost_console`, `live_eval`, `operator_posture`
- Provenance: `human-led runtime suggestion with implementation decision`
- Decision:
  - port the Polinko-style cost console idea into Scorey's live eval operator surface
  - treat throughput limits and spend as separate operator control planes
  - keep interactive live checks synchronous
  - use extended live runs only as explicit batch work
  - add quick operator shortcuts for visibility:
    - `make open-limits`
    - `make open-usage`
    - `make open-billing`
    - `make open-cost-console`
- Why: Live eval latency can make "just let it run longer" look harmless when it
  is actually consuming budget slowly in the background. The cost console keeps
  spend visible, while the batch-first posture preserves the research signal
  without turning Scorey's live lane into an unbounded token sink.

## D-028: The tracked repo surface should read cleanly in public

- Date: `2026-05-05`
- Category: `workflow_environment`
- Tags: `public_surface`, `docs_hygiene`, `repo_posture`
- Provenance: `human-led method decision with repo formalization`
- Decision:
  - treat the tracked docs and operator surface as public-facing by default
  - keep hardcoded personal machine paths out of tracked docs
  - keep editor-specific workspace files out of the tracked repo surface
  - keep scratch lanes local or ignored instead of advertising them in public-facing operator output
- Why: Once Scorey stopped being a private repo, the tracked surface needed to
  read like an intentional public project rather than a personal checkout with
  machine-specific residue and visible scratch scaffolding.

## D-029: Scorey should mirror Polinko's Apache license shape

- Date: `2026-05-05`
- Category: `repo_governance`
- Tags: `license`, `public_surface`, `polinko_alignment`
- Provenance: `human-led method decision with repo formalization`
- Decision:
  - keep Scorey under Apache-2.0
  - align the tracked `LICENSE` file to the exact `polinko` shape rather than
    using a looser standard-only Apache text
- Why: The human lead wanted Scorey to inherit the same explicit public
  licensing posture as Polinko and to keep the toy-family repo surface aligned
  on the legal artifact too, not just on runtime and docs structure.

## D-030: The OpenAI Python SDK is pinned directly, not only through Agents

- Date: `2026-05-06`
- Category: `runtime_engineering`
- Tags: `openai_sdk`, `dependency_pin`, `runtime_contract`
- Provenance: `implementation decision`
- Decision:
  - pin the official `openai` Python SDK directly in `pyproject.toml`
  - do not leave Scorey's runtime depending on `openai` only as a transitive
    dependency of `openai-agents`
  - keep the direct SDK pin current alongside the Agents SDK pin
- Why: Scorey is agent-backed, but the OpenAI runtime dependency should still
  be explicit. A direct pin makes upgrades and compatibility checks legible
  instead of leaving the effective SDK version to drift underneath the repo.

## D-031: Research Beta 3.0 is a positive-only tone-first lane

- Date: `2026-05-07`
- Category: `research_method`
- Tags: `research_beta_3`, `tone`, `live_eval`, `positive_only`
- Provenance: `human-led method decision`
- Decision:
  - make tone the next research beta after the route-valid live queue settled
  - keep the tone bar positive-only rather than defining it by anti-patterns
  - judge the tone lane through five desired traits:
    - `pick-aware`
    - `playful`
    - `confident`
    - `coherent`
    - `imaginative`
  - treat scoreboard and broader prose as later lenses
- Why: Once live route validity and legibility stopped being the open question,
  tone became the cleanest next method shift. It is narrower and more
  Scorey-specific than a general prose pass, and the positive-only bar keeps
  the lens focused on what the toy is actually trying to sound like.

## D-032: Tone review gets a separate operator surface instead of overwriting route verdicts

- Date: `2026-05-07`
- Category: `runtime_engineering`
- Tags: `tone_review`, `operator_surface`, `eval_storage`, `research_beta_3`
- Provenance: `implementation decision`
- Decision:
  - keep the existing `current_verdict` lane as the route-valid floor
  - add a separate append-only tone review store for later lenses
  - expose tone review explicitly through:
    - `eval-tone-sample`
    - `eval-tone-judge`
    - `make eval-tone-sample`
    - `make eval-tone-judge`
- Why: Once `Research Beta 3.0` became the active lane, reusing the top-level
  route verdict would have blurred two different questions into one field.
  Tone review needed its own surface so later lenses can stack on the same live
  rows without erasing the route-pass baseline.

## D-033: Live evals should be judged while the batch is still running

- Date: `2026-05-07`
- Category: `research_method`
- Tags: `live_eval`, `tandem_review`, `signal_observation`, `research_beta_3`
- Provenance: `human-led method decision`
- Decision:
  - judge live rows while the eval batch is still running
  - observe the signal in motion rather than waiting for the full batch to end
  - keep route validation and tone review moving in tandem with generation
- Why: The point of the live lane is not just to accumulate rows. It is to
  watch where the signal strengthens, weakens, or drifts while the batch is
  active. Judging in tandem makes those shifts visible sooner and keeps the
  research lane responsive instead of purely archival.

## D-034: Paper-only live evals isolate the weakest tone seam

- Date: `2026-05-08`
- Category: `research_method`
- Tags: `paper_only`, `live_eval`, `tone_review`, `failure_isolation`, `research_beta_3`, `operator_surface`
- Provenance: `human-led method decision with implementation decision`
- Decision:
  - narrow the next live eval lane to `paper` only
  - use paper-only generation and paper-only tone sampling to isolate the
    recurring `real one` / `napkin` failure seam
  - implement the diagnostic lane through the paper-filtered live and tone
    operator surface rather than only as an informal review habit
  - treat this as a focused diagnostic pass for low-signal tone failures rather
    than a general coverage expansion
- Why: Once the failure cluster around `real one` and `napkin` became clear,
  broad mixed-pick live batches were no longer the sharpest instrument.
  Restricting the lane to `paper` makes the weak pattern easier to observe,
  compare, and fix without extra noise from stronger picks.

## D-035: Binary verdicts stay strict and failed lanes get explicit disposition

- Date: `2026-05-08`
- Category: `eval_quality`
- Tags: `pass_fail`, `retain_evict`, `failure_disposition`, `rerun_discipline`
- Provenance: `human-led method decision with repo formalization`
- Decision:
  - keep the eval gate itself strictly binary:
    - `pass`
    - `fail`
  - if a row or seam fails, make a second explicit disposition decision:
    - `retain`
    - `evict`
  - treat `retain` as valid in-scope failure evidence that should stay in the
    active lane
  - treat `evict` as the upstream correction that removes a bad lane before a
    rerun
  - rerun after evictions instead of leaving known-bad lanes in the same queue
- Why: Binary judgment should stay hard and legible, but not every failure
  belongs in the active queue forever. This keeps verdicts strict while making
  correction discipline explicit.

## D-036: Pending tone rows can be archived out of the active queue without becoming a verdict

- Date: `2026-05-09`
- Category: `runtime_engineering`
- Tags: `tone_review`, `archive`, `operator_surface`, `pending_queue`
- Provenance: `implementation decision`
- Decision:
  - add an explicit tone-archive operator path:
    - `eval-tone-archive`
    - `make eval-tone-archive`
  - keep archive separate from both binary verdicts and `RETAIN / EVICT`
  - let archived tone rows leave the active review surface without pretending they were judged
  - count archived tone rows explicitly in the operator surface instead of folding them back into `pending`
- Why: Once the paper-only seam was sharp enough, the remaining paper pendings
  no longer belonged in the active queue. They still should not become fake
  verdicts, and archive should not be confused with the post-`FAIL`
  `RETAIN / EVICT` disposition layer.

## D-037: Failed tone rows get an explicit post-fail operator surface

- Date: `2026-05-09`
- Category: `runtime_engineering`
- Tags: `tone_review`, `retain_evict`, `operator_surface`, `failure_disposition`
- Provenance: `implementation decision`
- Decision:
  - add a separate tone failure-disposition sample:
    - `eval-tone-disposition-sample`
    - `make eval-tone-disposition-sample`
  - add a separate tone failure-disposition write path:
    - `eval-tone-dispose`
    - `make eval-tone-dispose`
  - keep `PASS / FAIL` as the first gate
  - only allow `RETAIN / EVICT` after a stored tone `fail`
  - keep archive separate from the post-fail disposition layer
- Why: The method contract is two-step on purpose. `PASS / FAIL` decides the
  row. `RETAIN / EVICT` decides what to do with a failed row next. The runtime
  surface should make that order explicit instead of relying on ad hoc notes or
  memory.

## D-038: Pending route rows should be explicit in `current_verdict`

- Date: `2026-05-09`
- Category: `runtime_engineering`
- Tags: `eval_storage`, `operator_surface`, `pending_queue`
- Provenance: `implementation decision`
- Decision:
  - store pending route rows as the literal `pending` value in
    `eval_outputs.current_verdict`
  - stop using `NULL` as the live pending representation
  - migrate legacy rows forward on DB initialization so direct SQL and the CLI
    surface agree on active queue state
- Why: The operator surface already speaks in `pass`, `fail`, and `pending`.
  Leaving pending rows implicit as `NULL` made direct inspection brittle and let
  route-pending counts disagree depending on how the DB was queried. The runtime
  should use one explicit pending state.
