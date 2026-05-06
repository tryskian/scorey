# Scorey

[![Research Beta](https://img.shields.io/badge/research_beta-2.0%20focused%20object%20lanes-E15759)](./docs/research/README.md)
[![Polinko toy factory](https://img.shields.io/badge/polinko_toy_factory-active-4C956C)](https://github.com/tryskian/polinko)

## rock, paper, scissors, scorey

scorey keeps the score.\
you already lost. sorry.

Scorey is a small, local, agent-backed CLI mini chatbot using the **[Polinko research model](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. It keeps the same narrow, agent-backed mini chatbot shape, but turns it into a rigged round instead of an oracle prompt.

It only accepts three picks:

- `rock`
- `paper`
- `scissors`

Current tracked research beta:

- `Research Beta 2.0`
- `focused object lanes`

That narrow surface is the point. Scorey is not trying to be a general chat tool or a generic joke machine. It is a small instrument for studying whether a model can preserve a rigged round, stay pick-specific, and keep unfair logic legible inside tight interaction guardrails.

In this repo, major betas are research architectures, and minor versions tighten the active method without changing the whole eval shape.

## What This Repo Demonstrates

- constrained round preservation through a fixed pick surface
- runtime-owned routing and composition around a narrow agent seam
- binary eval architectures from pick routing to focused object lanes

## Run It

```sh
make install
scorey
```

The app opens a compact terminal loop. Choose `rock`, `paper`, or `scissors` with the arrow keys, press `enter`, or hit `esc` to exit.

For the deterministic local path:

```sh
scorey --local
```

The operator commands, eval workflow, and setup checks live in the [runtime runbook](./docs/runtime/RUNBOOK.md).

## Read Next

- [docs/research/README.md](./docs/research/README.md)
  - beta map and research reading path
- [docs/governance/DECISIONS.md](./docs/governance/DECISIONS.md)
  - durable runtime and eval decisions

---

*Scorey is not a resource for fairness, sportsmanship, or second chances.*
