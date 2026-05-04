# Scorey

## rock, paper, scissors, scorey

scorey keeps the score.  
sorry. you already lost.

Scorey is a small, local, agent-backed CLI mini chatbot in the  
**[Polinko research line](https://github.com/tryskian/polinko)**.

It is a rigged rock, paper, scissors spinoff of  
**[Probaboracle](https://github.com/tryskian/probaboracle)**. It inherits the  
Probaboracle-style idea of a narrow, agent-backed generation pipeline, but its  
surface is more bratty and game-shaped.

Scorey does not generate generic jokes about winning. It preserves the round:

- what you picked
- what scorey picked
- why your pick failed
- why scorey's pick worked
- why scorey still wins
- what the scoreboard now claims

Example:

```text
you: rock
me: scissors

my scissors beats your rock because my scissors were for snacks and your rock was a marshmallow that looked like a rock.

me: 1, you: none

scorey.
```

## Run It

```sh
make install
scorey
```

The app opens a compact terminal loop. Choose `rock`, `paper`, or `scissors`  
with the arrow keys, press `enter`, or hit `esc` to exit.

Scorey uses the live agent-backed generation path by default. Create `.env` from  
`.env.example` and set `OPENAI_API_KEY`, or export it in your shell.

For a deterministic contract smoke test without live generation:

```sh
scorey --local
```

Operator one-round commands are still available underneath the app path:

```sh
scorey play rock
scorey --local play rock
```

## Eval It

Scorey uses the same repo-native eval discipline as the other Polinko research  
instruments: local SQLite storage, append-only judgments, and binary  
`pass` / `fail` lenses.

```sh
scorey eval-init
scorey sample --count 5
scorey eval-list
scorey judge-round 1 pass --note "keeps both picks in the ruling"
scorey judge-picks 1 pass --note "uses the selected rock matchup"
scorey judge-brat 1 pass --note "plain unfair kid logic"
scorey judge 1 pass --note "feels like scorey"
```

Eval samples use live generation by default. Use `scorey --local sample` only  
for fixture checks, not as the primary research surface.

The active lenses are:

- product fit
- round coherence
- pick relevance
- brat fit

Current eval beta:

- `Beta Eval 1.0`: pick routing only
- Scorey must pick the object the user's pick would normally beat, or the same  
object

## Read Next

- [docs/governance/CHARTER.md](./docs/governance/CHARTER.md)
  - durable scope and working model
- [docs/governance/SESSION_HANDOFF.md](./docs/governance/SESSION_HANDOFF.md)
  - current state and next kernel
- [docs/governance/DECISIONS.md](./docs/governance/DECISIONS.md)
  - durable decisions log
- [docs/diagrams/PIPELINE.md](./docs/diagrams/PIPELINE.md)
  - public generation and eval shape
- [docs/runtime/ARCHITECTURE.md](./docs/runtime/ARCHITECTURE.md)
  - stable runtime, eval, and docs map
- [docs/runtime/RUNBOOK.md](./docs/runtime/RUNBOOK.md)
  - setup and CLI commands
- [docs/research/README.md](./docs/research/README.md)
  - current research lane and beta framing