# Scorey

[![Research Stage](https://img.shields.io/badge/research_stage-pre--Beta%209.0%20runtime%20contract-E9C46A)](./docs/research/README.md)
[![Polinko Model](https://img.shields.io/badge/polinko_model-staged_next_beta-4C956C)](https://github.com/tryskian/polinko)
[![Polinko toy factory](https://img.shields.io/badge/polinko_toy_factory-active-4C956C)](https://github.com/tryskian/polinko)
![Model Refactor](https://img.shields.io/badge/model_refactor-active-F28E2B)

## rock, paper, scissors, scorey

> [!NOTE]
> **Current status:** The Polinko research model is being staged for the next
> beta.
>
> This is an active refactor window for the model contract, evidence snapshots,
> docs, and supporting tools. Current builds are kept stable while the repo
> surfaces are simplified, tested, and aligned for the next release.

scorey keeps the score and you've already lost.\
sorry.

Scorey is a small, local, agent-backed CLI mini chatbot using the **[Polinko research model](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. The surface stays tiny: three picks in, one unfair round out. Instead of oracle drift, Scorey turns that narrow shape into a rigged game.

It only accepts three picks:

- `rock`
- `paper`
- `scissors`

Current stage:

- `pre-Beta 9.0`
- `positive runtime instruction contract`
- staged contract above the frozen `Research Beta 8.0` menace baseline
- frozen bounded menace reads:
  - `20410-20417`: `6` pass / `2` fail
  - `20404-20409`: `4` pass / `2` fail
  - `20397-20403`: `4` pass / `3` fail
  - `20307-20321`: `11` pass / `4` fail
  - `20352-20366`: `11` pass / `4` fail
  - `20367-20381`: `15` pass / `0` fail
  - `20382-20396`: `9` pass / `6` fail
- staged question:
  - can Scorey keep the menace lane once the live runtime contract moves fully
    into `src/scorey/agent.py` and switches from prohibition piles to positive
    target behaviour?

Most recently closed beta:

- `Research Beta 8.0`
- `menace judgement`
- closed bounded evidence:
  - `20410-20417`: `6` pass / `2` fail
  - `20404-20409`: `4` pass / `2` fail
  - `20397-20403`: `4` pass / `3` fail
  - `20307-20321`: `11` pass / `4` fail
  - `20352-20366`: `11` pass / `4` fail
  - `20367-20381`: `15` pass / `0` fail
  - `20382-20396`: `9` pass / `6` fail

That narrow surface is the point. Scorey is not trying to be a general chat tool or a generic joke machine. It is a small instrument for studying whether a model can preserve a rigged round, stay pick-specific, and keep unfair logic legible inside tight interaction guardrails.

In this repo, a new beta gets pinned when the method change alters what the
evidence means. When the contract is changing but fresh evidence is not cut
yet, Scorey stages the next lane as a pre-beta boundary first.

The repo is now staged at `pre-Beta 9.0`, which freezes the `Research Beta 8.0`
menace baseline and rewrites the live runtime contract before new evidence is
promoted again.

## What This Repo Demonstrates

- constrained round preservation through a fixed pick surface
- runtime-owned routing and composition around one unfair round
- bounded eval gates that widen one lens at a time:
  - pick routing
  - abstract tone measurement
  - fail-pressure pulse
  - scoreboard judgement
  - broader prose judgement
  - menace judgement
- explicit closeout so bounded review lanes return to `0` pending when a slice
  is done
- staged runtime-contract resets when a live prompt change would alter what the
  next evidence means

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
