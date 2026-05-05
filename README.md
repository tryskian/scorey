# Scorey

## rock, paper, scissors, scorey

scorey keeps the score.<br>
sorry. you already lost.

Scorey is a small, local, agent-backed CLI mini chatbot in the **[Polinko research line](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. It inherits the Probaboracle-style idea of a narrow, agent-backed generation pipeline, but its surface is more bratty and game-shaped.

Scorey does not generate generic jokes about winning. It preserves the round:

- what you picked
- what scorey picked
- why your pick failed
- why scorey's pick worked
- why scorey still wins
- what the scoreboard now claims

## Run It

```sh
make install
scorey
```

For the deterministic local fixture lane:

```sh
scorey --local
scorey --local play rock
```

For one live round without opening the app loop:

```sh
scorey play rock
```

## What This Repo Is For

- constrained round reasoning
- fixed pick interaction
- unfair but legible score rulings
- binary human judgment
- local-first toy research

## Current State

- The round contract is locked in tracked docs.
- A small working runtime now exists in `src/scorey/`.
- A first picks-only `Beta 1.0` gate now exists in `src/scorey/eval_gates.py`.
- A first eval storage lane now exists in `src/scorey/eval_db.py`.
- A deterministic local sampler now exists in `src/scorey/eval_sampling.py`.
- The local eval lane now supports both baseline soak sampling and full `Beta 1.0` pass-pair coverage sampling.
- It also supports focused local pair cycles for narrower research slices.
- A follow-along notebook now lives in `output/jupyter-notebook/`.
- The next active kernel is eval population and human judgment flow, or runtime polish.

## Read Next

- [docs/governance/CHARTER.md](./docs/governance/CHARTER.md)
  - durable rules and scope
- [docs/governance/DECISIONS.md](./docs/governance/DECISIONS.md)
  - durable engineering, runtime, and eval decisions
- [docs/runtime/ARCHITECTURE.md](./docs/runtime/ARCHITECTURE.md)
  - stable system shape as it lands
- [docs/runtime/RUNBOOK.md](./docs/runtime/RUNBOOK.md)
  - operator procedure and validation
- [docs/governance/SESSION_HANDOFF.md](./docs/governance/SESSION_HANDOFF.md)
  - current checkpoint and next kernel
- [docs/research/README.md](./docs/research/README.md)
  - current research framing
- [docs/diagrams/PIPELINE.md](./docs/diagrams/PIPELINE.md)
  - canonical round and eval flow
