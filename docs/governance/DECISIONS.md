# Decisions Log

## Taxonomy

- `Category` values:
  - `runtime_engineering`
  - `eval_quality`
  - `collaboration_method`
  - `evidence_governance`
  - `workflow_environment`
- `Tags`:
  - lowercase snake_case labels for quick filtering

## Entry Criteria

Add an entry only when the change is durable and still governs the repo.

Good fits:

- collaboration model or control rights
- repo workflow rules
- runtime or eval contract changes
- evidence handling rules
- documentation governance rules

Keep temporary wrapper churn, wording tweaks, branch-local cleanup,
one-off debugging moves, and current-session handoff facts in the tracked
handoff or branch history instead.

## Entry Style

- keep entries short and operational
- one durable decision per entry
- use one category
- use 3 to 5 tags
- keep `Decision` and `Why` tight

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
  composition, while the live model supplies only Scorey's winning state, the
  user's worse state, and a scoreboard claim.
- Why: This keeps the unstable model seam small and preserves an evalable
  round contract.

## D-005: Eval outcomes stay binary with explicit post-fail handling

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `binary_gate`, `retain_evict`, `lane_contract`
- Decision: Route review and tone review both stay on `pass` / `fail`, and
  every failure is handled through `retain` or `evict`.
- Why: This keeps the gate legible and preserves a clean loop for upstream
  failure handling.

## D-006: Route validity remains the floor and tone-first is the active widened lens

- Date: `2026-05-15`
- Category: `eval_quality`
- Tags: `route_floor`, `tone_first`, `beta_method`
- Decision: Route correctness remains the first gate, and tone-first remains
  the active widened review lens once the route floor is stable.
- Why: This keeps the method sequence clear and prevents wider judgment from
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
  branches, PR checks, and protected-main merges.
- Why: This keeps local and remote tracked truth aligned.

## D-010: `session-status` and runtime gates are the live operator snapshot

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `session_status`, `runtime_gates`, `live_truth`
- Decision: `make session-status`, `make start-runtime-check`,
  `make end-runtime-check`, and `make end-docs-check` remain the compact live
  checks for repo cleanliness, queue state, and open or close safety.
- Why: This repo uses a small operator surface to keep runtime truth visible
  during active work.

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

## D-013: Startup and closeout are operator procedures backed by atomic commands

- Date: `2026-05-15`
- Category: `workflow_environment`
- Tags: `startup`, `closeout`, `atomic_commands`
- Decision: Startup is executed as reading and orientation backed by
  `make doctor-env`, `make start-runtime-check`, wake-lock commands, and
  `make session-status`, while closeout runs docs, runtime, path-leak, wake-lock,
  and clean-main checks in sequence.
- Why: This keeps the discipline in the real operator pass while the command
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
  smaller single-purpose version aligned to the Polinko structure, while
  keeping Scorey's tracked handoff and live runtime gates where they still
  govern real repo behaviour.
- Why: The stack had drifted into overlapping warehouse surfaces where
  procedure, carryover, structure, and rationale were duplicating each other.
  The reset keeps the docs truthful, smaller, and easier to use during active
  work.
- How:
  1. Align the morning process and `make end` implementation to the updated
     house contract before rewriting the docs.
  2. Replace tracked `RUNBOOK.md` with the smaller procedure-only version.
  3. Replace tracked `SESSION_HANDOFF.md` with the smaller active-carryover
     version.
  4. Replace tracked `ARCHITECTURE.md` with the smaller structural version.
  5. Replace tracked `CHARTER.md` with the smaller durable-rules version.
  6. Replace tracked `START_END_REFERENCE.md` with the compact command card.
  7. Replace tracked `DECISIONS.md` last with the compact durable ledger.
- Diff Counts:
  - tracked `RUNBOOK.md`: `183 insertions`, `386 deletions`
  - tracked `SESSION_HANDOFF.md`: `78 insertions`, `375 deletions`
  - tracked `ARCHITECTURE.md`: `116 insertions`, `249 deletions`
  - tracked `CHARTER.md`: `85 insertions`, `134 deletions`
  - tracked `START_END_REFERENCE.md`: `40 insertions`, `64 deletions`
  - tracked `DECISIONS.md`: `147 insertions`, `912 deletions`

## D-016: Live prompt surfaces stay abstract and de-anchored

- Date: `2026-05-16`
- Category: `eval_quality`
- Tags: `prompt_contract`, `deanchoring`, `measurement_integrity`
- Provenance: `human-led method decision with implementation decision`
- Decision: Live generator instructions and per-round prompts must stay on
  abstract constraints rather than hard-coded phrase blacklists, canned good
  fragments, or canned bad fragments.
- Why: Phrase-specific anchoring contaminates the measurement surface. It can
  manufacture the very fallback seams the eval lane is supposed to observe,
  especially in same-pick rounds. That breaks the intended family method by
  turning discovered failure language into part of the generator itself.
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
  the clean Polinko-aligned comparison surface. Splitting them keeps the
  method boundary explicit and makes anchored versus abstract results
  directly comparable.

## D-018: Active fail families get isolated short measurement runs

- Date: `2026-05-16`
- Category: `eval_quality`
- Tags: `fail_families`, `isolated_runs`, `measurement_shape`
- Provenance: `human-led method decision`
- Decision: Once a mixed run identifies the active fail families, the next
  eval pass should split them into individual short runs, one fail family at a
  time, instead of immediately widening back to another broad mixed run.
- Why: This keeps the evidence surface narrow enough to read clearly. It makes
  retained failures easier to compare across runs, reduces queue bloat, and
  shows whether a weak seam is still coherent under isolation or only looked
  strong inside the mixed batch.

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
  the active pulse-level comparison surface once pulse evidence exists instead
  of only a staged hypothesis note.

## D-020: Beta 5.0 pulse counting stays anchor-versus-seam

- Date: `2026-05-17`
- Category: `eval_quality`
- Tags: `pulse_counting`, `evidence_taxonomy`, `exclusions`
- Provenance: `human-led method decision with implementation decision`
- Decision: `Research Beta 5.0` pulse review counts only `anchor` and
  `counted_seam` rows toward the pulse verdict. `excluded_noise` stays
  auditable, reported by reason, and outside the counted total.
- Why: This keeps bounded run judgment strict without hiding row evidence.
  The pulse stays binary at the run level, but the row surface remains visible
  enough to audit how a pass or fail was produced.

## D-021: Local tooling targets mirror closeout and CI gates

- Date: `2026-05-21`
- Category: `workflow_environment`
- Tags: `tooling_baseline`, `closeout`, `security_gates`, `operator_surface`
- Provenance: `human-led tooling hygiene decision with implementation decision`
- Decision: Keep `Makefile` as the explicit operator surface for local
  validation by adding first-class targets for:
  - `make lint-docs`
  - `make package-install-check`
  - `make security-checks`
  The end routine must call Make targets for docs linting, package build,
  editable package import, runtime closeout, and dependency security checks.
  `pip-audit` belongs in the dev dependency surface so local security checks
  do not depend on ad hoc global tooling.
- Validation:
  - `make check`
  - `make lint-docs`
  - `make package-check`
  - `make package-install-check`
  - `make security-checks`
  - `make end-preflight`
- Why: Scorey already had real runtime closeout gates, but its local tooling
  surface still left docs linting, package import smoke, and security audit
  outside the canonical Make workflow. The toy repos need a small shared
  baseline that is easy to repeat without changing runtime or eval behavior.
