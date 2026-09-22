# Runbook

Use this doc for operator procedure.

- Use `README.md` for public framing and the quick entrypoint.
- Use `docs/runtime/ARCHITECTURE.md` for stable system shape.
- Use `docs/governance/SESSION_HANDOFF.md` for the active kernel and carryover.
- Use `docs/governance/DECISIONS.md` for durable rationale.
- Use `docs/runtime/START_END_REFERENCE.md` for the compact command card.

## Operating Posture

Scorey stays small on purpose.

The operator posture is:

- one active kernel at a time
- one feature branch per tracked change set
- repo-scoped edits by default
- inspect first, interpret second
- clean synced `main` is the tracked stop state

Local-only lane:

- `docs/peanut/` stays private and ignored

## Branch, Worktree, and Scope Policy

1. Canonical repo root is:
   - `/abs/path/to/scorey`
2. Default tracked workflow is:
   - `git switch -c codex/bigbrain/<task-name>`
3. Start tracked edits from a feature branch.
4. Use a dedicated worktree only for parallel implementation tracks.
5. Secondary worktrees for live eval work should use:
   - local `.venv`
   - canonical repo `.local`
6. Keep one logical task per branch.

## Morning Startup

1. Read in this order:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm:
   - canonical repo root or dedicated worktree
   - active branch from `git branch --show-current`
3. Return before implementation:
   - current state
   - risks
   - next kernel
   - repo or worktree context
   - active branch
4. Run:
   - `make doctor-env`
   - `make start-runtime-check`
   - `make session-status`
5. Install or refresh the environment when needed:
   - `make install`

## Inspect-First Rule

1. Inspect named files, runtime state, logs, transcripts, and DB surfaces
   before interpretation.
2. Prefer source evidence over memory when they disagree.
3. State inspection status plainly.

## Command Ownership

Human lead owns:

- objective
- scope
- acceptance criteria
- meaning-level trade-offs
- go or no-go decisions

Engineer owns:

- implementation
- validation
- command execution
- Git and PR flow
- proactive hygiene

Default mode is execution-first:

- do the work directly when asked

## Git Write Discipline

Serialize git write actions.

Do not parallelize:

- `git add`
- `git commit`
- `git push`
- branch switches
- merges
- rebases
- PR creation

Use:

1. `git add ...`
2. verify staged state with:
   - `git status --short`
   - or `git diff --cached --stat`
3. `git commit ...`

## Local Checkpoints and Commit Cadence

The primary saves local recovery checkpoints under
`.local/checkpoints/<UTC-id>/` between coherent groups of committed changes.

The primary engineer records a snapshot manifest containing:

- `HEAD` and the active branch;
- the binary tracked diff from `HEAD`;
- explicit lists of current changed and untracked code/docs files, with copies
  and SHA-256 hashes for the named files only;
- selected private notes or transcripts, with their copies and SHA-256 hashes;
- repository-relative references and SHA-256 hashes for canonical run evidence
  and databases, which are not copied or mutated.

Exclude environment and credential files. The manifest defines the saved scope;
a checkpoint is not a full-repo backup. Group commits around coherent changes
and keep the required checks, protected-main flow, and `make end` closeout.

## Protected-Main Flow

1. Work on a feature branch.
2. Commit locally.
3. Push the branch.
4. Open a PR to `main`.
5. Wait for required checks.
6. Merge through the protected-main flow.
7. Sync local `main`:
   - `git switch main`
   - `git pull --ff-only`
8. Final tracked repo state is:
   - merged
   - clean local `main`
   - synced with `origin/main`

## Runtime Gates

Use gates as behaviour checks, not narrative.

| Command | Job |
| --- | --- |
| `make doctor-env` | environment health check |
| `make start-runtime-check` | start-of-day runtime safety gate |
| `make end-runtime-check` | confirms the live slice is closed |
| `make end-docs-check` | confirms tracked current-truth docs were refreshed today |
| `make session-status` | compact repo and runtime snapshot |

`make session-status` is the compact live surface for:

- branch state
- worktree cleanliness
- runtime queue state
- live batch boundary state

## Evaluation Command Surface

Top-level and tone review:

| Command | Job |
| --- | --- |
| `make eval-init` | initialise the eval database schema |
| `make eval-list` | list top-level judged rows |
| `make eval-review-sample` | list pending top-level review sample |
| `make eval-judge` | record top-level route verdict |
| `make eval-tone-sample` | list pending tone review sample |
| `make eval-tone-judge` | record tone verdict |
| `make eval-tone-archive` | archive one pending tone row |
| `make eval-tone-disposition-sample` | list failed tone rows that still need `retain` or `evict` |
| `make eval-tone-disposition-archive` | archive one failed tone row from the disposition surface |
| `make eval-tone-dispose` | record `retain` or `evict` for one failed tone row |

Bounded widened lenses:

| Command | Job |
| --- | --- |
| `make eval-scoreboard-sample` | list pending scoreboard review sample from live route-pass rows |
| `make eval-scoreboard-judge` | record row-level scoreboard verdict on `scoreboard_claim` |
| `make eval-scoreboard-archive` | archive one pending scoreboard row |
| `make eval-scoreboard-close` | close one bounded scoreboard range and settle untouched tone rows in-range |
| `make eval-prose-sample` | list pending broader-prose review sample from live route-pass rows |
| `make eval-prose-judge` | record row-level prose verdict on the round body around the score line |
| `make eval-prose-archive` | archive one pending prose row |
| `make eval-prose-close` | close one bounded prose range and settle untouched lower-lens rows in-range |
| `make eval-menace-sample` | list pending menace review sample from live route-pass rows |
| `make eval-menace-judge` | record row-level menace verdict on the full visible round |
| `make eval-menace-archive` | archive one pending menace row |
| `make eval-menace-close` | close one bounded menace range and settle untouched lower-lens rows in-range |

Pulse surface:

| Command | Job |
| --- | --- |
| `make eval-pulse-open` | open one bounded pulse over a route-pass output range |
| `make eval-pulse-sample` | list newest unlabeled rows inside one pulse |
| `make eval-pulse-judge` | label one row as `anchor`, `counted_seam`, or `excluded_noise` |
| `make eval-pulse-summary` | report raw rows, counted totals, exclusions, and pulse verdict |
| `make eval-pulse-close` | close one pulse and settle untouched legacy tone rows in-range |

Sampling surface:

| Command | Job |
| --- | --- |
| `make eval-sample-local` | record deterministic local rounds |
| `make eval-sample-live` | record live API rounds |

## Golden Prompt Smoke

New preparation and generation are paused under D-045. The existing fixture
contains matchup cases, not high-signal user/assistant pairs. Align the
established protocol before resuming. The commands below document retained
tooling and access to saved evidence.

The experimental smoke uses the app's shared agent contract and six fixed
reverse/same-pick cases, each at score 1. Original artifacts remain read-only;
canonical eval rows and historical gate state stay unchanged.

1. Confirm the intended prompt version, model settings, and retrieval condition.
   Run `make smoke-prepare` to freeze source snapshots and patch, requested
   settings including omitted parameters, endpoint, schema, six prompts, and retrieved
   context under `.local/smoke/<id>/`. Preparation makes no model requests.
2. Inspect `manifest.json` and its source snapshots. When ready to generate,
   run `make smoke-run SMOKE_RUN=.local/smoke/<id>` using the returned folder.
   The runner rejects changed sources/packages or a previously started run.
3. Inspect `review.md`, `summary.json`, and each request, raw response, and
   receipt. Each case has one independent Responses call, zero retries, and a
   60-second limit. Configuration or capacity errors stop the remaining cases;
   the summary records cases not attempted.
4. Before the first import, update the research owner's current criteria
   document at `docs/research/420_PB-COHERENT_ABSURDITY.md`. Import the saved
   run and criteria with:
   `make smoke-review-import SMOKE_RUN=.local/smoke/<id>`.
   This makes no model request, leaves the smoke folder untouched, and writes
   only the additive `review_*` tables in `.local/evals.sqlite`. Identical
   frozen inputs can be re-imported; changed manifest, criteria, or case bytes
   are rejected. The first import freezes the current `420` criteria by
   default. Preserve that exact criteria text outside the immutable smoke
   folder, for example at `.local/reviews/<id>/review-criteria.md`. If the
   research document changes, reimport with the frozen copy:
   `PYTHONPATH=src .venv/bin/python -m scorey.review_store import .local/smoke/<id> --criteria .local/reviews/<id>/review-criteria.md`.
5. Inspect the imported dataset with:
   `PYTHONPATH=src .venv/bin/python -m scorey.review_store show <dataset-id>`.
   This is read-only. The dataset ID is the smoke-run folder name. The importer
   preserves manifest and criteria snapshots plus each receipt, request, and
   raw response with its hash.
6. Launch the staged review notebook:
   `.venv/bin/jupyter lab output/jupyter-notebook/scorey-coherent-absurdity-review.ipynb`.
   For personal execution, use Jupyter's Save As to create the ignored
   `scorey-coherent-absurdity-review.local.ipynb` copy, keeping the tracked
   template clean. It reads the imported SQLite dataset and writes the separate
   `output/jupyter-notebook/scorey-coherent-absurdity-review.notes.json`
   sidecar. Add attributed observations without a verdict, or attributed
   judgments with `PASS` or `FAIL`; explanations are optional, and shared pulse
   issues need not be repeated on every row. Use `Save all reviews` to save all
   edited rounds; do not overwrite earlier event IDs.
7. Sync the sidecar explicitly with:
   `make smoke-review-sync REVIEW_NOTES=output/jupyter-notebook/scorey-coherent-absurdity-review.notes.json`.
   The importer validates the dataset binding, receipt hash, response ID, and
   event shape, then appends only new events to `review_events`. Changed event
   IDs are rejected. This does not change `eval_*` rows, historical gates, or
   promotion state.
8. Keep mechanical checks, attributed observations, and semantic judgments
   distinct. Display `Automated route check (Valid/Invalid)` and `Automated
   mechanical checks (Checks passed/Checks failed)` as evidence only; they do
   not judge voice or quality. Six completed calls or imported evidence do not
   establish quality. Do not make new model calls or promotion claims as part
   of this review surface. Record the current implementation and evidence
   status separately.

Receipts retain request/response IDs, usage, output fields, composed rounds,
and failures. Six completed calls alone do not establish quality or promote a
beta. See the handoff for current verification and live-run status.
The [execution pipeline](../diagrams/GOLDEN_SMOKE.md) shows the implemented
recording path and the separate review surface.

## Coherent-Absurdity Review Workbench

The staged review notebook is the source-bound workbench for the saved
coherent-absurdity smoke dataset. It reads `review_datasets`, `review_cases`,
and `review_events` from the existing `.local/evals.sqlite`; it does not write
the database while the workbench is being used. Save work to its separate
`.notes.json` sidecar outside the immutable `.local/smoke/<id>/` folder, then
use `make smoke-review-sync REVIEW_NOTES=...` to append validated events
explicitly. The older local review workbench below, including its CSV, notebook,
and notes, remains intact and separate.

## Source-Linked Memory

Source-linked memory is an opt-in live-generation condition. It is separate from
the default runtime and from the completed Beta 1 local restart. The corpus is the
four exact principles in `src/scorey/data/principles.json`; raw outputs,
verdicts, and generated examples are not ingested.

Build and inspect the local snapshot:

1. Ensure the source files and corpus entries are the intended revisions.
2. Run `make memory-build` with `OPENAI_API_KEY` available. The command embeds
   the four principles and six pair queries in one request and appends an
   immutable content-addressed snapshot to `.local/memory.sqlite`.
3. Pin the returned snapshot ID in `SCOREY_MEMORY_INDEX` and set
   `SCOREY_MEMORY_ENABLED=true` for the named live condition. The default is
   disabled.
4. Run `make memory-status` locally to inspect the pinned snapshot.
5. Run `make memory-preview PICK=rock MEMORY_SCOREY_PICK=scissors` (or another
   allowed pair) to inspect local route-filtered retrieval.

Enabled rounds load one frozen snapshot for the batch, retrieve locally with
`top_k=2` and `max_chars=1200`, and make no per-round embedding request.
Generation receipts live under `.local/memory-receipts/`; completed live eval
rows receive an output-ID sidecar under `.local/evals.sqlite.retrieval/`. These
receipts are provenance metadata, not verdicts or new gates. A source or corpus
change requires a new build and pin. Activation is per named local condition;
behavioral efficacy must be measured under the existing gates.

Receipt paths resolve from the repository root, as their `path_base` records.

## Local Review Workbench

For the private six-round human-review workbench, from the repository root:

1. Create the local environment and install its requirements:
   - `python3 -m venv .venv`
   - `.venv/bin/python -m pip install -r output/jupyter-notebook/requirements.txt`
2. Launch it:
   - `.venv/bin/jupyter lab output/jupyter-notebook/scorey-review-workbench.ipynb`
3. Run the two code cells. Use `Previous` and `Next` to move between
   rounds; edits remain in memory until explicitly saved.
4. Use `Save review` to write the local
   `output/jupyter-notebook/scorey-review-workbench.notes.json` sidecar. This
   workbench save never writes the evaluation database.

The module, template notebook, requirements, and tests are reusable local
tooling. Original CSV, Numbers, sidecar, and dated six-review notebooks remain
in their original output paths as ignored personal evidence. The default
source path continues to work. This procedure generates no new eval rows and
changes no model or runtime configuration.

## Validation Surface

| Command | Job |
| --- | --- |
| `make lint-docs` | tracked docs lint gate |
| `make scripts-check` | tracked shell helper contract gate |
| `make check` | format, lint, typecheck, tests, and `git diff --check` |
| `make package-check` | distribution build check |
| `make package-install-check` | editable package import smoke |
| `make security-checks` | local dependency security audit |
| `make refresh-deps` | refresh local Python dependencies after Dependabot work |

Dependency maintenance:

1. Merge grouped Dependabot PRs before single-package duplicates.
2. Run `make refresh-deps` after syncing `main`.
3. Run `make security-checks`.
4. Finish with `make end` on clean synced `main`.

## Shared Power Control

The external Coffee Codex plugin owns the one shared Mac-wide keep-awake
session for Polinko and the toys. Scorey does not inspect, start, adopt, or
stop that session during startup, preflight, closeout, or status reporting.

The repository owns no power-control PID file, log, process state, or Make
target. Its lifecycle remains focused on runtime safety, eval evidence,
validation, and Git state.

## End Of Day

1. Finish branch-local validation before merge:
   - `make end-docs-check`
   - `make doctor-env`
   - `make path-leak-check`
   - `make path-leak-audit-local`
   - `make lint-docs`
   - `make scripts-check`
   - `make check`
   - `make package-check`
   - `make package-install-check`
   - `make end-runtime-check`
   - `make security-checks`
2. Package the branch when the kernel is ready.
3. Merge through the protected-main flow.
4. After merge, switch back to `main` and pull fast-forward only.
5. Run closeout checks:
   - `make session-status`
   - `make end-git-check`
6. Update tracked handoff and research truth before stopping.

The repo is closed only when:

- `make end` has passed
- local `main` is clean
- local `main` is synced with `origin/main`
