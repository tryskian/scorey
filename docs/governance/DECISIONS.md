# Decisions Log

This file is the durable archive of Scorey's engineering, runtime, and eval decisions.

## How To Use This File

- Need the current durable rules:
  - start with `docs/governance/CHARTER.md`
- Need the current system shape:
  - use `docs/runtime/ARCHITECTURE.md`
- Need the active kernel and carryover:
  - use `docs/governance/SESSION_HANDOFF.md`
- Need the reasoning behind a repo choice:
  - use this file

Keep entries short, but informative enough to show what changed and why.

## Taxonomy

- `runtime_engineering`
- `eval_quality`
- `evidence_governance`
- `workflow_environment`

## Provenance Rule

Each decision should read as one of these:

- `human-led method decision`
  - the theory, bridge logic, or eval meaning came from the human lead
- `repo formalization`
  - the repo later encoded an already-active method or contract
- `implementation decision`
  - the engineering layer chose mechanics after the method was already set

If a decision crosses layers, say so plainly instead of flattening the method into implementation authorship.

## Entry Rule

Add an entry only when the decision still governs the repo.

Good fits:

- runtime contract changes
- eval method boundaries
- evidence handling rules
- workflow or closeout rules
- durable document-role changes

Keep branch-local cleanup, temporary wrapper churn, wording tweaks, and current-session facts out of this file.

## D-001: Local CLI runtime remains canonical

- Date: `2026-05-15`
- Category: `runtime_engineering`
- Tags: `local_first`, `cli`, `mini_chatbot`
- Decision: Bare `scorey` remains the canonical user-facing runtime path, with
  operator work kept on explicit CLI and `make` surfaces.
- Why: This keeps the interaction surface small and keeps operator work
  separate from the round loop.

## D-002: Fixed picks remain the active interaction boundary

- Date: `2026-05-15`
- Category: `runtime_engineering`
- Tags: `fixed_picks`, `interaction_contract`, `rps`
- Decision: The active interaction surface stays fixed to `rock`, `paper`, and
  `scissors`.
- Why: This keeps the runtime inside the constrained round theory and makes
  behaviour comparable across runs.

## D-003: The unfair round contract stays route-bounded

- Date: `2026-05-15`
- Category: `runtime_engineering`
- Tags: `round_contract`, `same_pick`, `unfairness`
- Decision: Valid routes stay inside the rigged round families, and same-pick
  rounds remain valid losses for the user.
- Why: This keeps the round logic legible and preserves the narrow contract
  that Scorey is meant to stress.

## D-004: Runtime owns round composition and the live model stays narrow

- Date: `2026-05-15`
- Category: `runtime_engineering`
- Tags: `runtime_ownership`, `structured_fields`, `model_boundary`
- Decision: Runtime owns route selection, output labels, and final round
  composition, while the live model supplies only `winning_state`,
  `worse_state`, and `scoreboard_claim`.
- Why: This keeps the unstable model seam small and preserves an evalable
  round contract.

## D-005: Eval outcomes stay binary with explicit post-fail handling

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `binary_gate`, `retain_evict`, `lane_contract`
- Decision: Route review and tone review both stay on `pass` / `fail`, and
  every failed tone row is handled through `retain` or `evict`.
- Why: This keeps the gate legible and preserves a clean loop for upstream
  failure handling.

## D-006: Route validity remains the floor and tone-first stays the first widened lens

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `route_floor`, `tone_first`, `beta_method`
- Decision: Route correctness remains the first gate, and tone-first remains
  the first widened review lens once the route floor is stable.
- Why: This keeps the method sequence clear and prevents wider judgement from
  obscuring the core round contract.

## D-007: Local deterministic runs are baseline evidence and live batches are the growth surface

- Date: `2026-05-15`
- Category: `evidence_governance`
- Tags: `local_baseline`, `live_batches`, `evidence_surface`
- Decision: The deterministic local queue stays baseline evidence, while live
  route-passed batches provide the active seam-finding surface.
- Why: This keeps baseline proof and active signal distinct.

## D-008: `docs/peanut` is the local-only lane

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `local_only`, `private_lane`, `working_notes`
- Decision: `docs/peanut/` holds local notes, resets, sketches, and other
  private working surfaces.
- Why: This preserves a clean boundary between tracked repo truth and
  exploratory material.

## D-009: Clean synced `main` is the tracked stop state

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `protected_main`, `feature_branch`, `stop_state`
- Decision: Tracked truth ends on clean synced `main` through feature
  branches, required checks, and protected-main merges.
- Why: This keeps local and remote tracked truth aligned.

## D-010: `session-status` and runtime gates are the live operator snapshot

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `session_status`, `runtime_gates`, `live_truth`
- Decision: `make session-status`, `make start-runtime-check`,
  `make end-runtime-check`, and `make end-docs-check` remain the compact live
  checks for repo cleanliness, queue state, and open or close safety.
- Why: This keeps runtime truth visible during active work without widening the
  operator surface unnecessarily.

## D-011: Secondary worktrees reuse the canonical eval store

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `worktrees`, `canonical_local`, `eval_store`
- Decision: Secondary worktrees keep local `.venv` and reuse the canonical
  repo `.local` eval store for live runtime and review work.
- Why: This keeps parallel implementation aligned to one live evidence surface.

## D-012: Document roles are explicit and non-overlapping

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `docs_roles`, `non_duplication`, `current_truth`
- Decision: `CHARTER` holds durable rules, `SESSION_HANDOFF` holds active
  carryover, `RUNBOOK` holds procedure, `ARCHITECTURE` holds system shape,
  `START_END_REFERENCE` holds the compact command card, and `DECISIONS` holds
  the durable ledger.
- Why: This keeps the docs stack legible and prevents overlap drift.

## D-013: Startup and closeout remain real operator procedures

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `startup`, `closeout`, `operator_surface`
- Decision: Startup is a real read-and-check pass backed by `make doctor-env`,
  `make start-runtime-check`, wake-lock commands, and `make session-status`.
  Closeout is a real docs, runtime, wake-lock, and clean-main pass culminating
  in `make end`.
- Why: This keeps the discipline in the actual operator flow while the command
  surface stays small and honest.

## D-014: The tracked repo surface stays clean of local path leaks

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `public_surface`, `path_leaks`, `repo_hygiene`
- Decision: Tracked docs, scripts, and operator surfaces stay free of
  hardcoded machine-local paths and editor residue.
- Why: This keeps the public repo surface clean and keeps tracked truth
  portable.

## D-015: Reset the docs stack through focused replaces and a smaller ledger

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `docs_reset`, `focused_replace`, `downsizing`, `structure_alignment`
- Decision: Reset the tracked docs stack by replacing each core doc with a
  smaller single-purpose version aligned to the family structure, while
  keeping Scorey's tracked handoff and live runtime gates where they still
  govern real repo behaviour.
- Why: The stack had drifted into overlapping warehouse surfaces where
  procedure, carryover, structure, and rationale duplicated each other. The
  reset keeps the docs truthful, smaller, and easier to use during active
  work.

## D-016: Live prompt surfaces stay abstract and de-anchored

- Date: `2026-05-16`
- Category: `eval_quality`
- Tags: `prompt_contract`, `deanchoring`, `measurement_integrity`
- Provenance: `human-led method decision with implementation decision`
- Decision: Live generator instructions and per-round prompts must stay on
  abstract constraints rather than hard-coded phrase blacklists, canned good
  fragments, or canned bad fragments.
- Why: Phrase-specific anchoring contaminates the measurement surface. It can
  manufacture the same fallback seams the eval lane is supposed to observe.
  Findings belong in tracked research docs, not in the live generator
  contract.

## D-017: Pin Beta 4.0 as the abstract measurement boundary

- Date: `2026-05-16`
- Category: `eval_quality`
- Tags: `beta_boundary`, `abstract_measurement`, `comparison_surface`
- Provenance: `human-led method decision with implementation decision`
- Decision: The shift from phrase-anchored tone-first measurement to abstract
  tone measurement is tracked as `Research Beta 4.0`, not as a minor update
  inside `Research Beta 3.0`.
- Why: This changes what the evidence means. `Research Beta 3.0` remains the
  historical anchored comparison surface, while `Research Beta 4.0` becomes
  the clean comparison surface.

## D-018: Active fail families get isolated short measurement runs

- Date: `2026-05-16`
- Category: `eval_quality`
- Tags: `fail_families`, `isolated_runs`, `measurement_shape`
- Provenance: `human-led method decision`
- Decision: Once a mixed run identifies the active fail families, the next
  eval pass should split them into individual short runs, one fail family at a
  time, instead of immediately widening back to another broad mixed run.
- Why: This keeps the evidence surface narrow enough to read clearly and shows
  whether a weak seam is coherent under isolation or only looked strong inside
  the mixed batch.

## D-019: Pin fail-pressure pulse as Research Beta 5.0

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `beta_boundary`, `pulse_measurement`, `active_method`
- Provenance: `human-led method decision with implementation decision`
- Decision: Treat fail-pressure pulse as active `Research Beta 5.0` once the
  first bounded pulse is run and closed on the live surface. `Research Beta
  4.0` stays closed as the row-level abstract measurement baseline.
- Why: The first real pulse changed what the evidence means. `Beta 4.0`
  remains the finished row-level comparison surface, while `Beta 5.0` becomes
  the active pulse-level comparison surface.

## D-020: Beta 5.0 pulse counting stays anchor-versus-seam

- Date: `2026-05-17`
- Category: `eval_quality`
- Tags: `pulse_counting`, `evidence_taxonomy`, `exclusions`
- Provenance: `human-led method decision with implementation decision`
- Decision: `Research Beta 5.0` pulse review counts only `anchor` and
  `counted_seam` rows toward the pulse verdict. `excluded_noise` stays
  auditable, reported by reason, and outside the counted total.
- Why: This keeps bounded run judgement strict without hiding row evidence.

## D-021: Local tooling targets mirror closeout and CI gates

- Date: `2026-05-21`
- Category: `workflow_environment`
- Tags: `tooling_baseline`, `closeout`, `security_gates`, `operator_surface`
- Provenance: `human-led tooling hygiene decision with implementation decision`
- Decision: Keep `Makefile` as the explicit operator surface for local
  validation by exposing first-class targets for docs linting, package build,
  editable package import, runtime closeout, and dependency security checks.
- Why: This keeps local validation repeatable and keeps closeout discipline on
  the same small operator surface as the rest of the repo.

## D-022: Scoreboard judgement is the staged next lens after Beta 5.0 pulse

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `next_lens`, `scoreboard`, `beta_staging`
- Provenance: `human-led method decision with implementation decision`
- Decision: After the active `Beta 5.0` pulse surface stabilizes, the staged
  next widening step is scoreboard judgement rather than broad prose
  judgement.
- Why: Scoreboard is the smaller next lens. It stays tied to the explicit
  `scoreboard_claim` field without immediately reopening the whole round prose
  as one broad quality question.

## D-023: The first scoreboard lane stays row-level

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `scoreboard`, `row_level`, `next_lens`
- Provenance: `human-led method decision with implementation decision`
- Decision: The first scoreboard judgement lane stays row-level on
  `scoreboard_claim`. Bounded runs can source the rows, but the scoreboard
  verdict itself does not inherit pulse math on the first pass.
- Why: This keeps the widening step smaller than full prose and simpler than
  repeating `Beta 5.0` mechanics by habit.

## D-024: Scoreboard close settles untouched tone rows in-range

- Date: `2026-05-21`
- Category: `runtime_engineering`
- Tags: `scoreboard`, `closeout`, `queue_hygiene`
- Provenance: `human-led method decision with implementation decision`
- Decision: Bounded scoreboard runs close through an explicit scoreboard-close
  step that settles any still-untouched tone rows inside that bounded range
  out of the active tone queue.
- Why: Scoreboard is a row-level lens on `scoreboard_claim`, not a request to
  reopen legacy tone review by accident. Bounded scoreboard work needs the same
  clean closeout discipline as pulse work.

## D-025: Beta 6.0 starts on scoreboard judgement

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `beta_boundary`, `scoreboard`, `row_level`
- Provenance: `human-led method decision with implementation decision`
- Decision: `Research Beta 6.0` starts once the scoreboard lane has both a
  locked row-level contract and a clean bounded closeout proof on live
  evidence.
- Why: That changes what the evidence means and therefore justifies a real
  beta boundary.

## D-026: Broader prose judgement is the staged next lens after Beta 6.0

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `next_lens`, `prose`, `beta_staging`
- Provenance: `human-led method decision with implementation decision`
- Decision: After the active `Beta 6.0` scoreboard surface stabilizes, the
  staged next widening step is broader prose judgement rather than more
  scoreboard repetition on the same tested families.
- Why: The next honest question is whether the broader round prose can still
  hold rigged-round logic once the judged surface widens above
  `scoreboard_claim`.

## D-027: Beta 7.0 starts on broader prose judgement

- Date: `2026-05-21`
- Category: `eval_quality`
- Tags: `beta_boundary`, `prose`, `row_level`
- Provenance: `human-led method decision with implementation decision`
- Decision: `Research Beta 7.0` starts once the broader prose lane has both a
  locked row-level contract and a clean bounded closeout proof on live
  evidence.
- Why: The broader prose lane is no longer just a staged widening idea. It
  changes what the evidence means by proving that cross-object pressure
  reappears above `scoreboard_claim`.

## D-028: Menace judgement is the staged next lens after Beta 7.0

- Date: `2026-05-22`
- Category: `eval_quality`
- Tags: `next_lens`, `menace`, `beta_staging`
- Provenance: `human-led method decision with implementation decision`
- Decision: After the active `Beta 7.0` broader prose surface stabilizes, the
  staged next widening step is menace judgement rather than more prose replay
  on the same tested family shape.
- Why: The next honest question is whether the full visible round lands as the
  right kind of compact rigged-round menace without drifting into smugness,
  cruelty, or generic filler.

## D-029: Research charts stay minimal and note-shaped

- Date: `2026-05-25`
- Category: `evidence_governance`
- Tags: `research_docs`, `chart_language`, `observable_plot`, `visual_clarity`
- Provenance: `human-led docs decision with implementation decision`
- Decision: Public research-note charts use Observable Plot on top of D3 and
  stay limited to `slope chart`, `horizontal bar chart`, and `table heatmap`.
  When a chart adds no value over the evidence table, use a plain table
  instead.
- Why: Scorey's research data is small, discrete, and comparison-heavy. A
  tight chart language keeps the notes visual without drifting into
  decorative or overfit analytics surfaces.

## D-030: Menace judgement stays row-level on the full visible round

- Date: `2026-06-06`
- Category: `eval_quality`
- Tags: `menace`, `row_level`, `bounded_closeout`, `beta_staging`
- Provenance: `human-led method decision with implementation decision`
- Decision: Menace judgement is formalised as a bounded
  row-level lens on the full visible round, with explicit sample, judge,
  archive, and close commands. Menace closeout settles untouched `tone`,
  `scoreboard`, and `prose` rows inside the bounded range.
- Why: This keeps the widening step tighter than a vague whole-app vibe read
  while preserving the queue-hygiene discipline already proven by the lower
  widened lenses.

## D-031: Beta 8.0 starts on menace judgement

- Date: `2026-06-06`
- Category: `eval_quality`
- Tags: `beta_boundary`, `menace`, `row_level`
- Provenance: `human-led method decision with implementation decision`
- Decision: `Research Beta 8.0` starts once the menace lane has a locked
  row-level contract, clean bounded closeout proof, and live evidence that is
  meaningfully different from the closed `Beta 7.0` broader prose surface.
- Why: The second bounded cross-object menace read changed what the evidence
  means by improving one previously weak prose slice from `9 / 6` to `11 / 4`
  under the menace lens.

## D-032: Beta 8.0 freezes below a staged positive runtime instruction contract

- Date: `2026-06-09`
- Category: `eval_quality`
- Tags: `beta_boundary`, `runtime_contract`, `positive_instructions`, `prompt_ownership`
- Provenance: `human-led method decision with implementation decision`
- Decision: Close `Research Beta 8.0` as the frozen menace baseline. Stage
  `pre-Beta 9.0` above it as a runtime instruction contract where
  `src/scorey/config.py` stays structural only and `src/scorey/agent.py` owns
  the live field-generation contract in positive target language.
- Why: The live generator contract is changing again in a way that affects
  evidence meaning. The next evidence must be cut above the new agent-local
  positive-target contract rather than appended to the Beta 8 baseline.
