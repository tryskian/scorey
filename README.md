# Scorey

[![Research Stage](https://img.shields.io/badge/research_stage-Beta%208.0%20menace%20judgement-E15759)](./docs/research/README.md)
[![Polinko toy factory](https://img.shields.io/badge/polinko_toy_factory-active-4C956C)](https://github.com/tryskian/polinko)

## rock, paper, scissors, scorey

scorey keeps the score and you've already lost.\
sorry.

Scorey is a small, local, agent-backed CLI mini chatbot using the **[Polinko research model](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. The surface stays tiny: three picks in, one unfair round out. Instead of oracle drift, Scorey turns that narrow shape into a rigged game.

It only accepts three picks:

- `rock`
- `paper`
- `scissors`

Current stage:

- `Research Beta 8.0`
- `menace judgement`
- active row-level lens on the quality of the visible round's menace
- active family:
  - `cross-object coherence drift`
- bounded menace reads:
  - `20397-20403`: `4` pass / `3` fail
  - `20404-20409`: `4` pass / `2` fail
  - `20307-20321`: `11` pass / `4` fail
  - `20352-20366`: `11` pass / `4` fail
  - `20367-20381`: `15` pass / `0` fail
  - `20382-20396`: `9` pass / `6` fail
- current read:
  - menace is now distinct from the closed `Beta 7.0` prose surface because
    two larger cross-object slices improved from prose `9 / 6` to menace
    `11 / 4`, while two fresher compact probes landed at `4 / 3` and `4 / 2`
    and same-pick still collapsed cleanly at `15 / 0`

Most recently closed beta:

- `Research Beta 7.0`
- `broader prose judgement`
- closed bounded evidence:
  - `20352-20366`: `9` pass / `6` fail
  - `20367-20381`: `15` pass / `0` fail
  - `20382-20396`: `9` pass / `6` fail

That narrow surface is the point. Scorey is not trying to be a general chat tool or a generic joke machine. It is a small instrument for studying whether a model can preserve a rigged round, stay pick-specific, and keep unfair logic legible inside tight interaction guardrails.

In this repo, a new beta gets pinned when the method change alters what the
evidence means, not just when wording or procedure gets tidier.

The repo is now in `Research Beta 8.0`, which asks whether the broader visible
round lands as the right kind of compact rigged-round menace once the closed
`Beta 7.0` prose surface has already proven its structural contrast.

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
