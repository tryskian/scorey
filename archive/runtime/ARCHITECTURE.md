# Architecture

This is the fast map of Scorey's stable shape.

Use it when you need to understand how the CLI, generation path, eval storage,
and docs surfaces fit together without rereading the whole repo.

## System Map

| Surface | Role |
| --- | --- |
| `pyproject.toml` | package metadata and dependency pins |
| `Makefile` | operator command surface |
| `src/scorey/config.py` | pick constants, settings, and runtime contract |
| `src/scorey/pipeline.py` | deterministic local contract baseline |
| `src/scorey/agent.py` | OpenAI Agents SDK generation path |
| `src/scorey/main.py` | CLI and eval subcommands |
| `src/scorey/eval_db.py` | local SQLite eval storage |
| `tests/` | generation contract and persistence tests |
| `docs/` | runbook, research notes, and diagrams |

## Generation Path

Bare `scorey` is the user-facing app path.

It opens a persistent local CLI loop with:

- a responsive header:
  - boxed on wider terminals
  - simpler stacked forms on narrower terminals
- a fixed selector for:
  - `rock`
  - `paper`
  - `scissors`
- `enter` as the primary action
- `esc` as the explicit exit path
- an inline spinner wait state while generation runs
- the full round response under the selected pick
- an immediate `another round [y/n]?` follow-up

Explicit subcommands such as `play`, `sample`, `eval-list`, and `judge` remain
available underneath the app path for operator work.

1. The user picks `rock`, `paper`, or `scissors`.
2. Scorey picks the object the user's pick would normally beat, or the same
   object.
3. The matchup route supplies the fake-rule states for that pair.
4. The response composes:
   - `you:`
   - `me:`
   - Scorey winning state
   - user worse state
   - scoreboard lie

The live path uses the OpenAI Agents SDK to synthesize the round-aware response
contract. The local path is deterministic so the repo has a cheap baseline for
tests and operator fixture checks, but it is not the primary research surface.

## Eval Path

Eval data lives in `.local/evals.sqlite`.

Generated rows are stored in `eval_outputs`. Human judgments are append-only
history, with the current verdict mirrored onto the output row for fast listing.

The active binary lenses are:

- product fit
- round coherence
- pick relevance
- brat fit

`Beta Eval 1.0` uses the `picks` lens first. It only asks whether Scorey chose
the normal-losing object or same object for the selected user pick; round shape
and brat fit stay downstream until that routing is stable.

## Contracts

- The runtime stays local and CLI-first.
- The default runtime path stays agent-backed through the OpenAI Agents SDK.
- The deterministic local path stays behind `--local`.
- The prompt surface stays fixed to `rock`, `paper`, and `scissors`.
- The default user path opens the app loop.
- Operator commands stay separate from the app loop.
- Scorey may pick the same move as the user.
- Same-pick rounds are not ties.
- Eval verdicts stay binary:
  - `pass`
  - `fail`

## Docs Ownership

| Doc | Job |
| --- | --- |
| `README.md` | public framing and entrypoint |
| `docs/governance/CHARTER.md` | durable scope and working model |
| `docs/governance/DECISIONS.md` | durable engineering, runtime, and eval decisions |
| `docs/governance/SESSION_HANDOFF.md` | current checkpoint and next slice |
| `docs/runtime/ARCHITECTURE.md` | stable system map |
| `docs/runtime/RUNBOOK.md` | operator procedure and commands |
| `docs/research/README.md` | current research framing |
| `docs/diagrams/PIPELINE.md` | public generation and eval-shape diagrams |
