# Research

Scorey is a small Polinko-line CLI mini chatbot and research toy for testing
whether a model can preserve a concrete rigged round while inventing unfair,
childish logic.

The narrow surface is intentional. Scorey is not a general chatbot and not a
general joke generator. It only handles rock, paper, scissors rounds.

## Current Focus

Current rebuild focus:

- same toy object
- fresh runtime
- tighter contract
- calmer process

Current research question:

Can a generated round stay pick-specific, unfair, and legible without
collapsing into generic joke writing or loose nonsense?

## Current Status

Beta naming is intentionally pending.

The day-zero research posture is already set:

- fixed pick surface
- narrow generation seam
- binary evaluation
- local-first runtime

More detailed beta docs should only be added once a distinct method shift earns
them.

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
