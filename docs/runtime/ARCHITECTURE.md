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
- tone stays the first row-level lens above route
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
| `src/scorey/eval_gates.py` | route-floor and lens gate helpers |
| `src/scorey/eval_db.py` | SQLite schema and review persistence |
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

## Runtime Flow

1. Bare `scorey` enters the local CLI loop in `main.py`.
2. The user selects one fixed pick.
3. The runtime validates the selected pick.
4. The runtime routes to an allowed Scorey pick.
5. The runtime reveals Scorey's pick and route frame.
6. The live model generates only the unstable round fields.
7. The runtime composes the final unfair round.

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

Current research note:

- the menace operator surface is now available in the runtime
- `Research Beta 8.0` is the current active widened lane above prose

## Data Surfaces

Local state:

| Surface | Role |
| --- | --- |
| `.local/evals.sqlite` | live eval evidence store |
| `.local/live_eval_batch.meta` | optional live batch metadata for sampler continuity |

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

## Placement Rules

| Surface | Home |
| --- | --- |
| route rules and settings | `src/scorey/config.py` |
| deterministic local round composition | `src/scorey/pipeline.py` |
| live field generation | `src/scorey/agent.py` |
| app loop and operator commands | `src/scorey/main.py` |
| eval schema and persistence | `src/scorey/eval_db.py` |
| eval population helpers | `src/scorey/eval_sampling.py` |
| operator helpers and closeout checks | `scripts/` |
| tracked repo truth | `docs/` |
| local and private notes | `docs/peanut/` |

## Governance Flow

| Doc | Owns |
| --- | --- |
| `CHARTER` | durable rules and collaboration model |
| `DECISIONS` | durable decision history |
| `SESSION_HANDOFF` | active slice and carryover |
| `RUNBOOK` | operator procedure |
| `START_END_REFERENCE` | compact command card |
| `docs/research/` | tracked beta findings |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |

Policy changes are complete when the affected surfaces agree.
