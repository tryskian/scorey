# Decisions Log

This file records Scorey's runtime decisions, including executable evaluation
and evidence contracts. Research findings belong in `docs/research/` and
private research notes; collaboration and writing rules belong in
[CHARTER](CHARTER.md). Historical entries retain their original provenance.

## How To Use This File

- Need the current durable rules:
  - start with `docs/governance/CHARTER.md`
- Need the current system shape:
  - use `docs/runtime/ARCHITECTURE.md`
- Need the active kernel and carryover:
  - use `docs/governance/SESSION_HANDOFF.md`
- Need the reasoning behind a runtime choice:
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

Add an entry when an agreed decision changes the runtime or its executable
evaluation and evidence contract.

Good fits:

- runtime contract changes
- eval method boundaries
- evidence handling rules

Keep collaboration, document roles, and writing preferences in the charter.

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

## D-033: Shell helper contracts are a named local gate

- Date: `2026-06-18`
- Category: `workflow_environment`
- Tags: `tooling_baseline`, `shell_scripts`, `closeout`, `maintenance`
- Provenance: `implementation decision`
- Decision:
  - expose `make scripts-check` as the shell helper contract gate
  - validate tracked `scripts/*.sh` shebangs and strict modes
  - run `make scripts-check` inside the active closeout routine
  - keep closeout control environment variables uppercase:
    - `END_SKIP_GIT_CHECK`
    - `END_GIT_BRANCH`
    - `END_GIT_REMOTE`
- Validation:
  - `make scripts-check`
  - `make check`
  - `make lint-docs`
  - `make end-preflight`
- Why: Shell helper drift should fail through a small explicit operator target
  before longer closeout checks run. Uppercase closeout environment variables
  keep the branch-local preflight and clean-main git gate aligned with the
  surrounding repo-family convention.

## D-034: Keep Mac-wide power control outside the repository lifecycle

- Date: `2026-09-18`
- Category: `workflow_environment`
- Tags: `coffee_plugin`, `keep_awake`, `operator_surface`, `repo_lifecycle`
- Provenance: `human-led repo-family decision`, later `implementation decision`
- Decision:
  - let the external Coffee Codex plugin exclusively own the one shared
    Mac-wide keep-awake session for Polinko and the toys
  - remove Scorey's power-control variables and Make targets
  - keep startup, preflight, closeout, and session status focused on
    repository-owned runtime, eval, validation, and Git state
  - leave external Coffee state unchanged throughout the repo lifecycle
  - supersede the wake-lock portion of `D-013` while preserving its runtime
    gates and shared start/end operator contract
- Validation:
  - `make start`
  - `make end-preflight`
  - `make end` on clean synced `main`
  - tooling contracts reject repository-owned power-control targets and calls
- Why: A Mac-wide process is shared across repositories and tasks. Repository
  lifecycle hooks create conflicting ownership and allow one closeout to
  interfere with unrelated work.

## D-035: Both picks come before a brief dots loader and the ruling

- Date: `2026-09-18`
- Category: `runtime_engineering`
- Tags: `interaction_contract`, `after_pick_loader`, `decision_provenance`
- Provenance: `human-led method decision`, recorded from the human lead's
  direct clarification and subsequent refinement.
- Source:
  - initial clarification: "scorey doesn't think. he answers as soon as the
    user picks, as if they were playing in real life"
  - refinement: "scorey can think after the picks" and "so we can use a short
    loader there (the one with the dots haha)"
  - presentation clarification: "with no weird narratives lol"
- Decision:
  - the user confirms a pick, then Scorey's pick appears as the other move in
    the round
  - once both picks are visible, allow a brief dots loader while Scorey
    prepares the ruling
  - show only the loader during that wait, with no caption or narrated
    thinking, deciding, or other inner monologue
  - follow the loader with the ruling and score
  - route selection and field generation remain internal runtime work under
    `D-003` and `D-004`
  - the refinement supersedes this entry's initial requirement for one
    complete response with no loader
- Attribution: The human lead now authorizes an after-pick loader. This does
  not retroactively validate the human-led provenance claimed by the
  historical May 5 `D-025` at commit `4ad6818`. That historical entry is not
  the current ledger's `D-025`.
- Why: The picks establish the round first. A brief loader then gives Scorey
  a moment to prepare the explanation before the ruling and score appear.
- Implementation: The live TTY shows both picks, then the existing Braille-dot
  spinner without a caption, then the ruling and score. The loader stops when
  generation finishes; no minimum wait is added. This implements the requested
  presentation without claiming a measured live response duration.

## D-036: Reserve the word you for the scoreboard label

- Date: `2026-09-18`
- Category: `runtime_engineering`
- Tags: `scoreboard_claim`, `field_contract`, `positive_instructions`
- Provenance: `human-led method decision`. The human lead flagged
  `you: you lose` and clarified that the needed change is restricting the
  word `you`, while keeping the existing response styles.
- Decision: Keep the word `you` out of `scoreboard_claim`. The runtime already
  supplies the `you:` label under `D-004`. This restriction applies only to
  the scoreboard field and adds no new grammatical or response-style rule.
- Live instruction: 'Keep scoreboard_claim free of the word "you"; the runtime
  supplies the you: label.'
- Why: Prevent the generated field from repeating the user reference already
  present in the score line.
- Implementation: The instruction lives in `src/scorey/agent.py`. Composition
  and fragment cleanup are unchanged; this is a generation instruction, not
  a deterministic word-removal rule.

## Relocated Documentation Guidance

<!-- markdownlint-disable MD033 -->
<a id="d-037-delegate-documentation-to-a-continuing-project-task"></a>
<a id="d-038-keep-all-documentation-concise"></a>
<!-- markdownlint-enable MD033 -->

Former D-037 and D-038 are collaboration and writing guidance, now owned by the
[charter's delegation](CHARTER.md#documentation-delegation) and
[document roles](CHARTER.md#document-roles) sections. Their identifiers remain
reserved; the [original records](https://github.com/tryskian/scorey/blob/e2db735fa01a2b878f879fb4fac1125fe4e74501/docs/governance/DECISIONS.md#L531)
remain in Git history. These links preserve older research references.

## D-039: Restart changed-model measurement at Beta 1

- Date: `2026-09-20`
- Category: `eval_quality`
- Tags: `model_restart`, `beta_1`
- Provenance: `human-led method decision`.
- Source:
  - "can you take a look at scorey's history? we'll need to follow the eval
    gates exactly as they are done"
  - "so we have to start where the first beta starts and measure in that
    established rubric"
  - earlier steering: "we return to polinko's original method: long runs since
    we've completely changed the model" and "for long runs we use batch calls
    polinko has the deets"
  - current clarification: "no assumptions or inferences"
- Decision:
  - use the established [Beta 1 rubric](../research/010_B-PICK_ROUTING.md) and
    [route gate code](../../src/scorey/eval_gates.py): pick-only, Scorey/user
    order, full six-pair coverage
  - compute the route gate, then persist each verdict and record the condition
    and exact output range needed for comparison
  - advance through Beta 2 object lanes, Beta 3/4 tone and retain/evict, then
    later boundaries in order, using each boundary's own object and close rule
  - keep closed betas and staged `pre-Beta 9.0` as comparison surfaces; do not
    open menace immediately, restore phrase anchors, or turn findings into
    generator examples
  - the human lead retains scope, criteria, judgement, and go/no-go, while
    current delegation permits primary judging in real time
  - follow the documented method exactly, tie procedure and criteria to source,
    and keep missing or ambiguous method details unresolved until the human lead
    clarifies them before dependent work; this applies to the primary,
    documentation, and readers
- Boundary: This method-order restart responds to a changed condition; it does
  not invent a universal threshold, create a beta automatically, or rewrite
  later-lens identities and attribution. It restores method order, not old
  instructions.

## D-040: Opt-in source-linked principle memory stays outside the core contract

- Date: `2026-09-20`
- Category: `runtime_engineering`
- Tags: `source_linked_memory`, `frozen_snapshot`, `retrieval_provenance`
- Provenance: `human-led method decision with implementation decision`.
- Source:
  - user approval: "yes we go!" following the recommendation to keep the
    existing core, retrieve a small source-linked set of abstract principles,
    preserve raw outputs and verdicts as evidence, use local SQLite, and freeze
    the run condition with per-output provenance
- Decision:
  - human boundary: keep the existing Scorey identity, pick/route ownership,
    three generated fields, composition, fixtures, and eval gates unchanged;
    preserve raw responses, verdicts, and generated examples as evidence rather
    than prompt context
  - engineering implementation: build an immutable content-addressed local
    SQLite snapshot with `text-embedding-3-small`, the four principle
    embeddings, and six pick-query embeddings in one embedding request
  - engineering implementation: adapt the four exact `PIPELINE.md` Reading
    Note excerpts into `src/scorey/data/principles.json` as source-linked
    context; this selection does not add a taste standard or prompt examples
  - engineering implementation: enable only when the operator pins
    `SCOREY_MEMORY_INDEX` and sets `SCOREY_MEMORY_ENABLED`; retrieve locally
    after pair and route selection with the route filter, `top_k=2`, and
    `max_chars=1200`
  - engineering implementation: freeze one memory snapshot for each
    memory-enabled eval run; record the prompt, settings, selected sources,
    source/index provenance, fields, and response IDs in a receipt, with an
    output-ID sidecar that does not change the eval schema or verdicts
  - keep the current Beta 1 local run separate and do not advance a beta from
    memory activation or retrieval receipts
- Why: This gives Scorey a small, reproducible source-linked context layer
  without turning observed evidence into prompt examples or changing the
  meaning of the established eval sequence.
- Boundary: Defaults stay off. A source change requires a new build and pin.
  Activation is per named local condition, and behavioral efficacy is measured
  under the existing gates rather than inferred from retrieval receipts.

## D-041: Explore coherent absurdity through frozen golden cases

- Date: `2026-09-21`
- Category: `runtime_engineering`
- Tags: `coherent_absurdity`, `golden_cases`, `smoke_tests`
- Provenance: human-led inquiry; the detailed prompt rewrite and six-case
  implementation were engineering choices, later rejected and restored in D-045.
- Source: "that's on you to adapt to scorey"; the four supplied concepts are
  "just a reference", not wording to use verbatim.
- Historical implementation: replace exact-object-class and physical-only instructions with
  imaginative properties, powers, and roles whose relationship makes the
  unfair win follow. Preserve runtime picks, three generated fields, score,
  and composition. References remain research evidence, not generator examples.
- Scoring clarification: the human reaffirmed "i still love our original
  scoring behaviour" and "nothing to adopt from the platform there". Keep
  runtime-owned score progression and `me: [score], you: [scoreboard_claim]`.
  Independent smoke cases start at 1; this does not change app scoring.
- Historical condition: `coherent-absurdity-1` used a shared agent factory for app
  and smoke. Six fixed reverse/same-pick inputs start at score 1. Preparation
  freezes source, settings, prompts, schema, endpoint, and retrieved context;
  execution keeps each request, raw response, failure, and composed round.
- Boundary: one fresh request per case, zero retries, 60 seconds per case.
  Mechanical checks and attributed quality judgments remain separate. Smoke
  writes isolated evidence, advances no historical gate, and supplies no
  numerical beta or automatic quality threshold.

## D-042: Formalize coherent absurdity as the next staged boundary

- Date: `2026-09-21`
- Status: paused under D-045. The engineering formalization below remains
  a record for protocol alignment, not permission to resume evaluation.
- Category: `eval_quality`
- Tags: `pre_beta_9`, `coherent_absurdity`, `bounded_review`
- Provenance: human-led direction with repo formalization of the previous
  boundary method.
- Source: "ok so that's your responsibility haha just follow the previous
  ones", following the request to finish the new beta setup.
- Decision: record [Pre-Beta 9.0: Coherent Absurdity](../research/420_PB-COHERENT_ABSURDITY.md)
  as the current staged refinement above the frozen Beta 8 comparison.
  Preserve the earlier `410` staged contract and closed evidence unchanged.
- Review: apply `coherent-absurdity-review-1` to one complete composed round
  at a time, asking whether its invented relationship makes the unfair win
  follow. Use the six original smoke cases; record attributed judgments in a
  separate sidecar. Mechanical admission, relational quality, scoreboard,
  and menace retain separate meanings. Reference concepts stay out of the
  generator and expected-answer fixtures.
- Close condition: six attributed relational verdicts with reasons, zero
  quality pending, and verified source links. Preserve failed evidence and
  apply disposition only where the inherited lens requires it. No all-pass
  threshold or pulse arithmetic is introduced.
- Promotion: follow the [earlier boundary pattern](../research/070_B-BROADER_PROSE_JUDGEMENT.md):
  a closed bounded review and an explicit comparison must show what changed
  in evidence meaning, with D-039's required lower gates satisfied, before
  the human lead's go/no-go. The current six
  mechanical passes leave quality and promotion pending.
- Boundary: this stages a comparison, not a new active database gate or an
  advance through D-039's ordered restart. The runtime, model settings,
  original scoring, canonical databases, and original smoke artifacts stay
  unchanged.

## D-043: Preserve Scorey's review meaning while adding attributed notes

- Date: `2026-09-21`
- Category: `evidence_governance`
- Tags: `staged_review`, `smoke_evidence`, `attribution`, `notebook`
- Provenance: human-led method decision with implementation contract.
- Source: SCO-2 user messages: "yes...these are things i want scorey to
  keep...i just wanted you to be able to have your notes as well" and "ok yes
  let's finish...beta arc includes updating the readme".
- Decision: finish the staged beta-arc review setup by reusing the six saved
  smoke responses. Preserve Scorey's existing meaningful measures, structure,
  and human wording; add independently attributed assistant observations
  alongside them. An observation does not require a verdict.
- Implementation contract: add `review_datasets`, `review_cases`, and
  `review_events` to the existing `.local/evals.sqlite` without changing
  historical `eval_*` routing, lens, pulse, or judgment rows. Import the frozen
  manifest and criteria plus full receipts, raw request/response bytes and
  hashes, picks, composed text, settings, timing, and token data as a separate
  staged dataset. Store append-only attributed observation and judgment events;
  require a verdict only for judgments.
- Notebook boundary: read SQLite and save a separate source-bound
  `.notes.json` sidecar. An explicit importer syncs notes to the new tables.
  Existing CSV, notebook, and notes remain intact. No new model calls,
  automatic quality judgments, canonical gate changes, or promotion claims.

## D-044: Make staged review verdicts explicit and explanations optional

- Date: `2026-09-21`
- Category: `evidence_governance`
- Tags: `staged_review`, `notebook`, `optional_reason`, `pulse_review`
- Provenance: human-led operational correction with implementation adaptation.
- Source: SCO-2 user clarification: "i can't save notes and you aren't expected
  to save notes every. time. especially in one eval pulse. all of these have
  the same issue".
- Decision: an attributed staged-review judgment is valid when the evaluator
  records an explicit `PASS` or `FAIL`; its explanation is optional. Shared
  issues may be recorded once for a bounded pulse rather than duplicated on
  every row. No new batch-note schema is introduced, and no explanation is
  fabricated or duplicated.
- Implementation contract: `Save all reviews` saves every edited round. The
  notebook labels mechanical evidence as `Automated route check (Valid/Invalid)`
  and `Automated mechanical checks (Checks passed/Checks failed)`, with explicit
  text that these checks do not judge voice or quality. This operational
  correction supersedes D-042's per-row reason requirement while preserving its
  frozen criteria, source boundaries, and pending quality state.

## D-045: Restore the established generation contract and pause adaptation

- Date: `2026-09-21`
- Category: `runtime_engineering`
- Tags: `restoration`, `protocol_alignment`, `golden_cases`
- Provenance: explicit human correction.
- Source: "restore what we already had before anything else" and "Stop there".
  The human specified high-signal user/assistant golden pairs and directed a
  Polinko source report before further work.
- Decision: restore the instructions and matchup prompt builder from
  `321d9702148ece91c39bcd66d64a2e02612a5ce7`. Pause new generation and method
  implementation until the established protocol is understood and aligned.
- Verification: exact instruction equality and all six matchup prompts, with
  and without context, match the baseline; all 154 offline tests pass.
  Model settings, composition, scoring, original smoke evidence, databases,
  and human verdicts are unchanged. No model calls were made.
- Retained state: the shared Agent factory and evidence/review tooling remain.
  Prompt metadata is `restored-321d970`; the rejected experiment remains frozen
  as `coherent-absurdity-1`. The existing six-case fixture provides matchup
  coverage and does not yet implement the requested golden pairs.
