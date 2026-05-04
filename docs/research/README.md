# Research

Scorey is a small Polinko-line CLI mini chatbot and research toy for testing
whether a model can preserve a concrete rigged round while inventing unfair,
childish logic.

The narrow surface is intentional. Scorey is not a general chatbot and not a
general joke generator. It only handles rock, paper, scissors rounds.

## Current Focus

Current focus:

- preserve the toy
- fresh runtime
- tighter contract
- calmer process

Current research question:

Can a generated round stay pick-specific, unfair, and legible without
collapsing into generic joke writing or random drift?

## Current Status

The first eval lane now exists, and the first named gate is now live.

The day-zero research posture is already set:

- fixed pick surface
- narrow generation seam
- binary evaluation
- local-first runtime

The current round contract now says:

- Scorey only routes to the pick the user would normally beat, or to the same pick
- same-pick rounds still produce losing loophole logic
- the runtime preserves the round shape
- the model only supplies small unstable unfair fields

The current runtime now exists:

- deterministic `--local` fixtures
- live structured round fields through the OpenAI Agents SDK
- one-round operator play path
- small interactive app loop
- local SQLite eval storage
- deterministic local batch population
- one follow-along notebook for the first eval lane

## Current Beta

Current beta:

- `Beta 1.0`

Scope:

- judge the pick pair only
- read it in `scorey_pick, user_pick` order
- ignore round prose, tone, and scoreboard claim
- treat local `baseline` sampling as a soak lane, not as a diversity claim
- treat local `beta-1-coverage` sampling as the deterministic six-pair pass table

`PASS`

- `paper, scissors`
- `rock, paper`
- `scissors, rock`
- `paper, paper`
- `rock, rock`
- `scissors, scissors`

`FAIL`

- every other `scorey_pick, user_pick` pair

## Working Hypotheses

- A smaller runtime-owned contract should reduce drift.
- Same-pick rounds need deliberate logic, not tie fallback.
- Binary evals stay clearer when one focus is active at a time.

## Project Relation

Scorey sits in the same
**[Polinko research line](https://github.com/tryskian/polinko)** as
**[Probaboracle](https://github.com/tryskian/probaboracle)**.

It shares the same discipline:

- local CLI-first runtime
- narrow interaction surface
- agent-backed generation
- binary human judgment
- repo-native docs and diagrams

The toy object is different:

- Probaboracle studies answer-shaped non-answers.
- Scorey studies rigged round rulings.
