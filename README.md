# Scorey

[![Research Stage](https://img.shields.io/badge/research_stage-Research%20Beta%205.0%20fail--pressure%20pulse-E15759)](./docs/research/README.md)
[![Polinko toy factory](https://img.shields.io/badge/polinko_toy_factory-active-4C956C)](https://github.com/tryskian/polinko)
![Maintenance](https://img.shields.io/badge/maintenance-in%20progress-F28E2B)

> **Maintenance in progress.** Documentation and research surfaces are being
> standardised before this repo is shared as a stable reference.

## rock, paper, scissors, scorey

scorey keeps the score and you've already lost.\
sorry.

Scorey is a small, local, agent-backed CLI mini chatbot using the **[Polinko research model](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. The surface stays tiny: three picks in, one unfair round out. Instead of oracle drift, Scorey turns that narrow shape into a rigged game.

It only accepts three picks:

- `rock`
- `paper`
- `scissors`

Current research lane:

- `Research Beta 5.0`
- `fail-pressure pulse`

Most recently closed beta:

- `Research Beta 4.0`
- `abstract tone measurement`

That narrow surface is the point. Scorey is not trying to be a general chat tool or a generic joke machine. It is a small instrument for studying whether a model can preserve a rigged round, stay pick-specific, and keep unfair logic legible inside tight interaction guardrails.

In this repo, a new beta gets pinned when the method change alters what the
evidence means, not just when wording or procedure gets tidier.

`Research Beta 5.0` began with the first real fail-pressure pulse on the
isolated cross-object family.

## What This Repo Demonstrates

- constrained round preservation through a fixed pick surface
- runtime-owned routing and composition around one unfair round
- binary eval lanes from pick routing to tone-first live review
- explicit post-fail gate stack:
  - `PASS / FAIL`
  - if `FAIL`, then `RETAIN / EVICT`
  - rerun
  - `PASS / FAIL`
- explicit archive cleanup when a pending review lane or stale failed
  disposition lane should leave the active queue without becoming a verdict

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

The operator commands, eval workflow, and setup checks live in the
[runtime runbook](./docs/runtime/RUNBOOK.md). The compact day-open/day-close
sheet lives in [Start / End Reference](./docs/runtime/START_END_REFERENCE.md).

Core operator commands:

```sh
make start
make end-preflight
make end-git-check
make caffeinate-status
make decaffeinate
make check
```

## Read Next

- [docs/research/README.md](./docs/research/README.md)
  - beta map and research reading path
- [docs/governance/DECISIONS.md](./docs/governance/DECISIONS.md)
  - durable runtime and eval decisions

---

*Scorey is not a resource for fairness, sportsmanship, or second chances.*
