# Scorey

## rock, paper, scissors, scorey

Scorey is a small, local, agent-backed CLI toy in the
**[Polinko research line](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors mini chatbot. The surface is silly. The
method is not.

This rebuild keeps the toy and resets the runtime. The goal is a calmer,
cleaner Scorey: tight contract, small surface, binary evals, and docs that stay
honest about what exists.

## What This Repo Is For

- constrained round reasoning
- fixed pick interaction
- unfair but legible score rulings
- binary human judgment
- local-first toy research

## Current State

- The archived reference docs live under `archive/`.
- The tracked docs in this repo are the new source of truth.
- The runtime is being rebuilt intentionally from the contract outward.
- The next active kernel is the day-zero round contract.

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
