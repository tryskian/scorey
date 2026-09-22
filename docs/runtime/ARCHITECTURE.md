# Architecture

This page owns the stable system shape.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/governance/SESSION_HANDOFF.md` for the active kernel and carryover.
- Use `docs/research/` for beta boundaries and closed evidence reads.

## System Shape

Scorey is a small local CLI that keeps one unfair rock, paper, scissors round
legible on purpose.

The stable runtime contract is:

- the user chooses one fixed pick:
  - `rock`
  - `paper`
  - `scissors`
- the runtime owns route selection and final round composition
- the live model owns only the small unstable fields:
  - `winning_state`
  - `worse_state`
  - `scoreboard_claim`
- the route floor stays binary:
  - `pass`
  - `fail`
- tone stays the first row-level lens above route in the established database
  evaluation sequence
- failure disposition remains explicit:
  - `retain`
  - `evict`

## Top-Level Map

| Surface | Owns |
| --- | --- |
| `README.md` | public framing and current entrypoint |
| `pyproject.toml` | package metadata and dependency pins |
| `Makefile` | operator command surface |
| `scripts/` | environment, runtime-state, and closeout helpers |
| `src/scorey/config.py` | fixed picks, route rules, and settings |
| `src/scorey/pipeline.py` | deterministic local fixtures and round composition |
| `src/scorey/agent.py` | structured live field generation |
| `src/scorey/smoke.py` | frozen independent smoke preparation, calls, and receipts |
| `src/scorey/data/golden_cases.json` | six versioned input cases at starting score 1 |
| `src/scorey/retrieval.py` | source-linked corpus loading, frozen retrieval, and receipts |
| `src/scorey/vector_store.py` | immutable content-addressed local memory snapshots |
| `src/scorey/memory.py` | memory build, status, and preview commands |
| `src/scorey/data/principles.json` | four exact source-linked pipeline principles |
| `src/scorey/eval_gates.py` | route-floor and lens gate helpers |
| `src/scorey/eval_db.py` | SQLite schema and review persistence |
| `src/scorey/review_store.py` | source-bound smoke dataset import, read-only status, and attributed review-event sync |
| `src/scorey/eval_sampling.py` | local and live eval population helpers |
| `src/scorey/main.py` | app loop and operator commands |
| `tests/` | contract and CLI regression checks |
| `docs/` | governance, runtime references, research notes, and diagrams |

## Round Contract

Allowed routes:

| User Pick | Allowed Scorey Picks | Route Families |
| --- | --- | --- |
| `rock` | `scissors`, `rock` | `cross-object`, `same-pick` |
| `paper` | `rock`, `paper` | `cross-object`, `same-pick` |
| `scissors` | `paper`, `scissors` | `cross-object`, `same-pick` |

Same-pick rounds are valid Scorey wins. They are part of the contract rather
than a fallback tie path.

Ownership boundary:

| Field | Owner | Job |
| --- | --- | --- |
| `user_pick` | runtime | preserve the selected fixed pick |
| `scorey_pick` | runtime | enforce valid routing |
| `route_family` | runtime | distinguish cross-object and same-pick logic |
| `winning_state` | model | explain why Scorey's version wins |
| `worse_state` | model | explain why the user's version loses |
| `scoreboard_claim` | model | provide the small unfair score-side claim |
| final round composition | runtime | output labels, prose shape, and close |

The runtime supplies the scoreboard's `you:` label. `D-036` adds a live
instruction to keep the word `you` out of `scoreboard_claim`, preserving the
existing response styles. The composer and fragment cleanup are unchanged.
The app advances its runtime-owned score each round and keeps
`me: [score], you: [scoreboard_claim]`. D-041 preserves this original scoring;
Platform reference responses supply no scoring changes.

The previous instructions and matchup prompts are restored exactly from
`321d970`, identified as `restored-321d970`. The experimental
`coherent-absurdity-1` condition remains in saved smoke evidence. The shared
`build_live_agent` factory supplies the app and smoke runner with the same
instructions, schema, and model settings. Golden-pair adaptation remains paused.

## Runtime Flow

1. Bare `scorey` enters the local CLI loop in `main.py`.
2. The user selects one fixed pick.
3. The runtime validates the selected pick.
4. The runtime routes to an allowed Scorey pick.
5. The runtime displays Scorey's pick alongside the user's pick.
6. In the live TTY, a dots loader appears after both picks while the model
   generates only the unstable round fields.
7. The runtime composes and displays the ruling and score.

`D-035` specifies a brief after-pick dots loader with no caption or narrated
deliberation. The live TTY uses the existing Braille-dot spinner alone until
generation completes, then displays the ruling and score without an added
minimum wait. Live response duration has not been measured for this change.

The [opt-in source-linked retrieval flow](../diagrams/PIPELINE.md#opt-in-source-linked-retrieval)
is implemented after pick and route selection, but it is not part of the default
runtime or the completed Beta 1 local restart. `memory-build` freezes the four exact
source-linked principles plus six pair queries into a content-addressed local
SQLite snapshot. An enabled run loads one pinned snapshot, retrieves locally with
the route filter, `top_k=2`, and `max_chars=1200`, and records provenance beside
the live eval output. Activation is per named local condition; behavioral
efficacy is measured under the existing gates. No retrieval receipt changes an
eval verdict or advances a beta.

## Selector Input Contract

- `up` and `down` are the only keys that move the active pick.
- `enter` confirms the active pick.
- `esc` exits the app or declines another round.
- Arrow sequences are read directly from the terminal file descriptor while
  one terminal mode remains active for the whole selector interaction.
- `ESC_SEQUENCE_TIMEOUT_SECONDS = 0.03` is the intentional boundary between a
  bare `esc` press and the remaining bytes of an arrow sequence. A key-mapping
  repair does not implicitly authorise changing that interaction timing.

## Evaluation Stack

| Surface | Binary Unit | Stable Shape | Notes |
| --- | --- | --- | --- |
| route floor | row | top-level `pass` / `fail` | mirrored onto `eval_outputs.current_verdict` for listing |
| tone | row | row-level `pass` / `fail` | active lower lens above route |
| failure disposition | failed tone row | `retain` / `evict` | explicit handling for tone failures |
| scoreboard | row | bounded row-level lens on `scoreboard_claim` | closeout can settle untouched tone rows in-range |
| prose | row | bounded row-level lens on broader round prose | closeout can settle untouched tone and scoreboard rows in-range |
| menace | row | bounded row-level lens on the full visible round | closeout can settle untouched tone, scoreboard, and prose rows in-range |
| pulse | bounded range | bounded pass/fail over route-pass rows | rows stay visible as `anchor`, `counted_seam`, or `excluded_noise` |

Historical research comparison:

- the menace operator surface is now available in the runtime
- `Research Beta 8.0` is the closed widened menace baseline above prose
- `pre-Beta 9.0` preserves the staged positive runtime contract above that baseline

### Golden Prompt Smoke

The paused experimental runner uses six fixed Scorey/user pairs: the three reverse
routes and three same-pick routes, each starting at score 1. Preparation freezes
source snapshots and patch, instruction and case versions, requested settings,
schema, provider endpoint, matchup prompts, and retrieval context. Omitted
parameters remain explicit in the recorded condition.

The runner uses the shared agent factory for at most six independent Responses
calls, one per case, with zero retries and a 60-second limit per case. It records
exact request and response bodies, IDs, usage, failures, generated fields,
composed rounds, and mechanical checks. Retrieval is frozen at preparation;
execution tests those saved inputs.
The app retains its SDK transport/retry defaults. Original artifacts stay read-only;
the smoke runner itself does not make semantic quality judgments.

This surface writes only its run folder. It does not write canonical eval rows,
advance historical gates, or establish a beta promotion. The
[execution diagram](../diagrams/GOLDEN_SMOKE.md) records this path; the
[Pre-Beta 9 relational boundary](../research/420_PB-COHERENT_ABSURDITY.md)
preserves the proposed review, pending protocol alignment. Current evidence status
belong in the handoff.

### Staged Smoke Review

The staged review is an explicit, source-bound layer around a saved smoke run.
`src/scorey/review_store.py` imports one frozen run and the current criteria
document into additive `review_*` tables in `.local/evals.sqlite`:

- `review_datasets` preserves the dataset identity, manifest bytes and hash, and
  criteria bytes and hash.
- `review_cases` preserves each case, receipt, request, and raw response bytes
  with their source hashes. The dataset ID is the original smoke-run folder
  name.
- `review_events` stores attributed observations and judgments. Observations do
  not carry a verdict. Judgments require an explicit `PASS` or `FAIL`, but an
  explanation is optional; shared pulse issues need not be duplicated per row.
  Only complete source receipts can receive a semantic verdict.
- `review_rounds` is a human-readable reporting view over the imported cases,
  receipts, and dataset metadata. It does not include `review_events`.

The importer is idempotent for identical frozen inputs and rejects a reimport
whose manifest, criteria, or case evidence differs. The original smoke folder
and the canonical `eval_*` tables remain unchanged. The review notebook reads
`review_datasets`, `review_cases`, and `review_events` from the imported SQLite
dataset and saves a separate source-bound `.notes.json`
sidecar; `import-notes` is the explicit append-only sync into `review_events`.
No new model calls, automatic judgments, historical gate changes, or promotion
claims belong to this layer. The current implementation and evidence state are
reported separately from the eventual review verdicts. Automated route and
mechanical checks are evidence checks, not judgments of voice or quality.

## Data Surfaces

Local state:

| Surface | Role |
| --- | --- |
| `.local/evals.sqlite` | live eval evidence store plus additive staged-review tables |
| `.local/live_eval_batch.meta` | optional live batch metadata for sampler continuity |
| `.local/memory.sqlite` | immutable content-addressed source-linked memory snapshots |
| `.local/memory-receipts/` | per-generation prompt, settings, retrieval, fields, and response receipts |
| `.local/evals.sqlite.retrieval/` | output-ID sidecars linking completed receipts to eval rows |
| `.local/smoke/<id>/` | frozen smoke condition, original artifacts, and source evidence for staged review |

SQLite tables:

| Table | Owns |
| --- | --- |
| `eval_outputs` | source rows and mirrored top-level verdict state |
| `eval_judgments` | top-level route-floor judgements |
| `eval_lens_judgments` | row-level lens verdicts for `tone`, `scoreboard`, `prose`, and `menace` |
| `eval_lens_archives` | archived rows per lens |
| `eval_lens_failure_dispositions` | `retain` / `evict` records for failed lens rows |
| `eval_lens_failure_disposition_archives` | archived failed-lens disposition rows |
| `eval_pulses` | bounded pulse ranges and their status |
| `eval_pulse_judgments` | row labels inside a pulse |
| `review_datasets` | imported smoke manifests and frozen review criteria |
| `review_cases` | source-bound case, receipt, request, and response evidence |
| `review_events` | append-only attributed observations and semantic judgments |
| `review_rounds` | read-only reporting view for staged review work |

Stable enums:

| Surface | Values |
| --- | --- |
| route families | `cross-object`, `same-pick` |
| lenses | `tone`, `scoreboard`, `prose`, `menace` |
| top-level verdicts | `pass`, `fail`, `pending` |
| dispositions | `retain`, `evict` |
| pulse labels | `anchor`, `counted_seam`, `excluded_noise` |
| pulse exclusion reasons | `operator_artifact`, `off_target_failure` |
| pulse status | `open`, `closed` |

Canonical repo work uses the repo `.local` surface. Secondary worktrees should
bind back to the canonical queue state before live eval work.

## Closeout Model

Bounded closeouts are part of the architecture, not just operator habit.

| Close Surface | Stable Behaviour |
| --- | --- |
| `eval-scoreboard-close` | closes one bounded scoreboard range and settles untouched tone rows in-range |
| `eval-prose-close` | closes one bounded prose range and settles untouched tone and scoreboard rows in-range |
| `eval-menace-close` | closes one bounded menace range and settles untouched tone, scoreboard, and prose rows in-range |
| `eval-pulse-close` | closes one pulse once every row is labeled and settles untouched legacy tone rows in-range |
| `make end-runtime-check` | confirms there is no active sampler and no open live review slice |

The closeout target for the repo is still:

- clean synced `main`
- runtime back at `0` pending

Mac-wide keep-awake state sits outside this architecture. The external Coffee
Codex plugin owns the shared session; Scorey's lifecycle commands neither
inspect nor mutate it.

## Placement Rules

| Surface | Home |
| --- | --- |
| route rules and settings | `src/scorey/config.py` |
| deterministic local round composition | `src/scorey/pipeline.py` |
| live field generation | `src/scorey/agent.py` |
| golden cases and independent smoke runs | `src/scorey/data/golden_cases.json` and `src/scorey/smoke.py` |
| source-linked retrieval and receipts | `src/scorey/retrieval.py` |
| immutable local memory snapshots | `src/scorey/vector_store.py` |
| memory operator commands | `src/scorey/memory.py` and `src/scorey/main.py` |
| source-linked corpus | `src/scorey/data/principles.json` |
| app loop and operator commands | `src/scorey/main.py` |
| eval schema and persistence | `src/scorey/eval_db.py` |
| staged smoke review import and sync | `src/scorey/review_store.py` |
| eval population helpers | `src/scorey/eval_sampling.py` |
| operator helpers and closeout checks | `scripts/` |
| tracked repo truth | `docs/` |
| local and private notes | `docs/peanut/` |

## Governance Flow

| Doc | Owns |
| --- | --- |
| `CHARTER` | durable rules and collaboration model |
| `DECISIONS` | runtime decision history |
| `SESSION_HANDOFF` | active slice and carryover |
| `RUNBOOK` | operator procedure |
| `START_END_REFERENCE` | compact command card |
| `docs/research/` | tracked beta findings |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |

Policy changes are complete when the affected surfaces agree.
