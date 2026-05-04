# Architecture

This is the fast map of Scorey's stable shape.

The runtime and first eval lane now exist. This file records what is already
real and what is still intentionally narrow.

## System Map

| Surface | Role |
| --- | --- |
| `README.md` | public framing and current repo entrypoint |
| `pyproject.toml` | package metadata and dependency pins |
| `Makefile` | small operator command surface |
| `docs/governance/CHARTER.md` | durable rules and scope |
| `docs/governance/DECISIONS.md` | durable runtime and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next kernel |
| `docs/runtime/ARCHITECTURE.md` | stable system map |
| `docs/runtime/RUNBOOK.md` | operator procedure and validation |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |
| `scripts/` | operator helpers for environment checks and end-of-day closeout |
| `src/scorey/config.py` | fixed picks, routing rules, and settings |
| `src/scorey/pipeline.py` | deterministic local fixtures and final round composition |
| `src/scorey/agent.py` | structured live round-field generation through the OpenAI Agents SDK |
| `src/scorey/eval_gates.py` | explicit eval truth tables and gate helpers |
| `src/scorey/eval_db.py` | local SQLite eval storage |
| `src/scorey/eval_sampling.py` | deterministic local eval population and soak helper |
| `src/scorey/main.py` | app loop and `play` operator command |
| `tests/` | contract and CLI tests |
| `output/jupyter-notebook/` | follow-along notebooks and lightweight research walkthroughs |

## Default App Path

The default user path is bare `scorey`.

It opens a persistent local CLI loop with:

- a compact startup header
- a fixed selector for:
  - `rock`
  - `paper`
  - `scissors`
- `enter` as the primary action
- `esc` as the explicit exit path
- a visible wait state while generation runs
- the full round reveal under the selected pick
- an immediate replay prompt

The app loop also supports a non-TTY fallback prompt path.

## Generation Path

The current generation shape is:

1. The user selects `rock`, `paper`, or `scissors`.
2. The runtime validates the fixed pick.
3. Scorey routes to an allowed Scorey pick.
4. The route defines the matchup frame for the round.
5. The live model generates only the unstable unfair round state it needs as
   structured fields.
6. The runtime composes the final round shape.

The exact boundary is now part of the tracked contract.

## Round Contract

Allowed routes:

| User Pick | Allowed Scorey Picks | Route Families |
| --- | --- | --- |
| `rock` | `scissors`, `rock` | cross-object, same-pick |
| `paper` | `rock`, `paper` | cross-object, same-pick |
| `scissors` | `paper`, `scissors` | cross-object, same-pick |

Same-pick rounds are valid Scorey wins. They do not fall back to tie logic.

Ownership boundary:

| Field | Owner | Job |
| --- | --- | --- |
| `user_pick` | runtime | preserve the selected fixed pick |
| `scorey_pick` | runtime | enforce valid routing |
| `route_family` | runtime | distinguish cross-object from same-pick logic |
| `winning_state` | model | explain why Scorey's version wins |
| `worse_state` | model | explain why the user's version loses |
| `scoreboard_claim` | model | provide a small unfair score-side claim |
| final round template | runtime | compose labels, prose shape, and closing tag |

Current final round shape:

```text
you: [rock|paper|scissors]
me: [rock|paper|scissors]

my [scorey pick] beats your [user pick] because my [scorey pick] was/were [winning state] and your [user pick] was/were [worse state].

me: [scorey score], you: [scoreboard claim]

scorey.
```

The runtime owns the labels, ordering, and composition. The score line must
present Scorey as ahead after the round.

## Eval Path

Eval data now lives in `.local/evals.sqlite`.

The current tracked shape is intentionally small:

- generated or recorded rounds live in `eval_outputs`
- human judgments are append-only in `eval_judgments`
- the current top-level verdict is mirrored onto the output row for fast listing
- verdicts stay binary:
  - `pass`
  - `fail`

The current row shape records:

- `user_pick`
- `scorey_pick`
- `route_family`
- `round_text`
- `source_mode`
- `model`
- `current_verdict`
- `current_note`

The first notebook lane lives in
`output/jupyter-notebook/scorey-eval-db-walkthrough.ipynb` and uses the same
module functions as the runtime surface.

The first named eval gate is `Beta 1.0`.

It only judges the pick pair in `scorey_pick, user_pick` order.

`pass` pairs:

- `paper, scissors`
- `rock, paper`
- `scissors, rock`
- `paper, paper`
- `rock, rock`
- `scissors, scissors`

`fail` pairs:

- every other `scorey_pick, user_pick` pair

The local sampling lane now has two deterministic patterns:

- `baseline` cycles the fixed picks through the narrow local fixtures and is
  best read as population/soak coverage
- `beta-1-coverage` cycles all six `Beta 1.0` pass pairs evenly

Neither local pattern is a diversity claim.

## Contracts

- The runtime stays local and CLI-first.
- The default runtime path stays agent-backed.
- The deterministic local path stays beside the live path.
- The prompt surface stays fixed to `rock`, `paper`, and `scissors`.
- Valid Scorey routes stay narrow and same-pick rounds are not ties.
- The runtime owns route enforcement and final round composition.
- The local path stays deterministic.
- The default user path opens the app loop.
- Operator commands stay separate from the app loop.
- Eval storage stays local and SQLite-backed.
- Eval verdicts stay binary:
  - `pass`
  - `fail`

## Docs Ownership

| Doc | Job |
| --- | --- |
| `README.md` | public framing and entrypoint |
| `docs/governance/CHARTER.md` | durable rules and working model |
| `docs/governance/DECISIONS.md` | durable engineering, runtime, and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next slice |
| `docs/runtime/ARCHITECTURE.md` | stable system map |
| `docs/runtime/RUNBOOK.md` | operator procedure and validation |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | canonical round and eval flow |
