# Architecture

This page is the structural map of the tracked system.

- Use `docs/runtime/RUNBOOK.md` for operator procedure.
- Use `docs/governance/SESSION_HANDOFF.md` for the active slice.

## Top-Level Map

- `README.md`
  - public framing and current entrypoint
- `pyproject.toml`
  - package metadata and dependency pins
- `Makefile`
  - operator command surface
- `scripts/`
  - environment, runtime-state, and closeout helpers
- `src/scorey/config.py`
  - fixed picks, routing rules, and settings
- `src/scorey/pipeline.py`
  - deterministic local fixtures and round composition
- `src/scorey/agent.py`
  - structured live round-field generation
- `src/scorey/eval_gates.py`
  - explicit eval truth tables and gate helpers
- `src/scorey/eval_db.py`
  - local SQLite eval storage
- `src/scorey/eval_sampling.py`
  - local and live eval population helpers
- `src/scorey/main.py`
  - app loop and operator commands
- `tests/`
  - contract and CLI regression checks
- `docs/`
  - governance, runtime references, research notes, and diagrams
- `output/jupyter-notebook/`
  - follow-along notebooks over tracked module functions

## Runtime Flow

1. Bare `scorey` enters the local CLI loop in `main.py`.
2. The user selects one fixed pick:
   - `rock`
   - `paper`
   - `scissors`
3. The runtime validates the selected pick.
4. The runtime routes to an allowed Scorey pick.
5. The runtime reveals Scorey's pick and route frame.
6. The live model generates only the unstable round fields:
   - `winning_state`
   - `worse_state`
   - `scoreboard_claim`
7. The runtime composes the final unfair round.

## Round Contract

Allowed routes:

| User Pick | Allowed Scorey Picks | Route Families |
| --- | --- | --- |
| `rock` | `scissors`, `rock` | cross-object, same-pick |
| `paper` | `rock`, `paper` | cross-object, same-pick |
| `scissors` | `paper`, `scissors` | cross-object, same-pick |

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
| final round composition | runtime | output labels, prose shape, and closing tag |

## Data Surfaces

- live eval store:
  - `.local/evals.sqlite`
- active round rows:
  - `eval_outputs`
- top-level judgements:
  - `eval_judgments`
- lens-specific judgements:
  - `eval_lens_judgments`
- failed-lens dispositions:
  - `eval_lens_failure_dispositions`
- archived stale failed dispositions:
  - `eval_lens_failure_disposition_archives`
- current top-level verdict mirrors onto the output row for fast listing
- current route verdict values:
  - `pass`
  - `fail`
  - `pending`
- failure disposition values after tone `fail`:
  - `retain`
  - `evict`

Canonical repo work uses the repo `.local` surface. Secondary worktrees should
bind back to the canonical queue state before live eval work.

## Placement Rules

- runtime config and contract logic:
  - `src/scorey/config.py`
- deterministic local round composition:
  - `src/scorey/pipeline.py`
- live field generation:
  - `src/scorey/agent.py`
- app loop and operator commands:
  - `src/scorey/main.py`
- eval storage and sampling:
  - `src/scorey/eval_db.py`
  - `src/scorey/eval_sampling.py`
- operator helpers and closeout checks:
  - `scripts/`
- tracked repo truth:
  - `docs/`
- local and private notes:
  - `docs/peanut/`

## Governance Flow

- `CHARTER`
  - durable rules and collaboration model
- `DECISIONS`
  - durable decision history
- `SESSION_HANDOFF`
  - active slice and carryover
- `RUNBOOK`
  - operator procedure
- `START_END_REFERENCE`
  - compact command card
- `docs/research/`
  - tracked beta findings
- `docs/diagrams/PIPELINE.md`
  - canonical round and eval flow

Policy changes are complete when the affected surfaces agree.
