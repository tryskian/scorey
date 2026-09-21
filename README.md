# Scorey

[![Research Stage](https://img.shields.io/badge/research_stage-pre--beta%209.0-E9C46A)](./docs/research/420_PB-COHERENT_ABSURDITY.md)
[![Polinko Model](https://img.shields.io/badge/polinko_model-staged_next_beta-4C956C)](https://github.com/tryskian/polinko)
[![Polinko toy factory](https://img.shields.io/badge/polinko_toy_factory-active-4C956C)](https://github.com/tryskian/polinko)
![Model Refactor](https://img.shields.io/badge/model_refactor-paused-F28E2B)

## rock, paper, scissors, scorey

> [!NOTE]
> **Current status:** The coherent-absurdity experiment is paused for alignment
> with Scorey's established research protocol. The previous generation
> instructions are restored. Saved responses and human verdicts are preserved.

scorey keeps the score and you've already lost.\
sorry.

Scorey is a small, local, agent-backed CLI mini chatbot using the **[Polinko research model](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of **[Probaboracle](https://github.com/tryskian/probaboracle)**. The surface stays tiny: three picks in, one unfair round out. Instead of oracle drift, Scorey turns that narrow shape into a rigged game.

It only accepts three picks:

- `rock`
- `paper`
- `scissors`

The restored prompt preserves Scorey's established voice and physical round
contract. The runtime keeps the picks, three generated fields, scoring, and
final round composition. The experimental six-case fixture records matchup
coverage; it does not yet contain the high-signal user/assistant golden pairs
requested by the human lead.

The [research map](./docs/research/README.md) preserves the closed Beta 1–8
baselines and the earlier staged 410 positive-runtime contract. The current
inquiry is recorded in the paused [Pre-Beta 9.0: Coherent Absurdity](./docs/research/420_PB-COHERENT_ABSURDITY.md)
boundary. Its [recorded execution pipeline](./docs/diagrams/GOLDEN_SMOKE.md)
records the six-case mechanics. Current review contains six human `FAIL`
judgements with notes preserved, one human observation, six assistant
observations, and zero assistant judgements; no historical gate has been
promoted or relabelled.

The [coherent-absurdity review notebook](./output/jupyter-notebook/scorey-coherent-absurdity-review.ipynb)
reads the existing smoke responses one complete round at a time. It keeps the
existing measures visible: picks, score, route and mechanical checks, complete
responses, conditions, timings, and token use. It preserves the original app
scoring, including `me: [score], you: [scoreboard_claim]`. Separately attributed
assistant observations may exist without a verdict; explicit quality judgments
remain distinct and attributed. These review responses do not close the
relational or historical gates. Further generation and method implementation
remain stopped while the existing protocol is traced and aligned.

That narrow surface is the point. Scorey is not trying to be a general chat tool or a generic joke machine. It is a small instrument for studying whether a model can preserve a rigged round, stay pick-specific, and keep unfair logic legible inside tight interaction guardrails.

In this repo, a new beta gets pinned when the method change alters what the
evidence means. When the contract is changing but fresh evidence is not cut
yet, Scorey stages the next lane as a pre-beta boundary first.

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

The [smoke procedure](./docs/runtime/RUNBOOK.md#golden-prompt-smoke) documents
the retained experimental tooling. New runs are paused pending alignment.

Core operator commands:

```sh
make start
make end-preflight
make end-git-check
make session-status
make security-checks
make check
```

## Read Next

- [docs/research/README.md](./docs/research/README.md)
  - beta map and research reading path
- [docs/governance/DECISIONS.md](./docs/governance/DECISIONS.md)
  - durable runtime and eval decisions
- [docs/diagrams/COLLABORATION.md](./docs/diagrams/COLLABORATION.md)
  - experiment collaboration, transcript capture, documentation lead, and
    helper team

---

*Scorey is not a resource for fairness, sportsmanship, or second chances.*
