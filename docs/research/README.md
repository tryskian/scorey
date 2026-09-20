# Research

The tracked research lane stays small. Each beta changes what the evidence is
allowed to mean; raw runs and scratch notes remain private until promoted.

| Surface | Current |
| --- | --- |
| Legend | [000_LEGEND.md](./000_LEGEND.md) |
| Staged boundary | [410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md](./410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md) |
| Last closed boundary | [080_B-MENACE_JUDGEMENT.md](./080_B-MENACE_JUDGEMENT.md) |
| Filename contract | `NNN_B-NAME.md` for beta boundaries; `NNN_PB-NAME.md` for staged pre-beta boundaries |

## Current stage

`pre-Beta 9.0` stages a positive runtime instruction contract. It keeps the
closed `Research Beta 8.0` menace baseline while moving live instruction shape
fully into `src/scorey/agent.py`; `config.py` remains structural. No new
menace evidence or lasting model choice has been promoted.

| Baseline | Evidence |
| --- | --- |
| Cross-object menace | `20410-20417: 6 / 2`; `20404-20409: 4 / 2`; `20397-20403: 4 / 3`; `20307-20321: 11 / 4`; `20382-20396: 9 / 6`; `20352-20366: 11 / 4` |
| Same-pick menace | `20367-20381: 15 / 0` |
| Runtime closure | `0` pending across route, tone and disposition |

Earlier closed contrast:

- Beta 5 pulse: cross-object `8 / 5 / 2`, then `9 / 6 / 0`, then `9 / 6 / 0`; same-pick `15 / 0 / 0`, then `15 / 0 / 0`.
- Beta 6 scoreboard: cross-object and same-pick slices each held at `15 / 0`.
- Beta 7 prose: cross-object reopened at `9 / 6` and repeated; same-pick held at `15 / 0`.

## Beta map

| Beta | Question / changed lens |
| --- | --- |
| [1.0](./010_B-PICK_ROUTING.md) | Does Scorey choose a valid rigged route? Pick routing only. |
| [2.0](./020_B-OBJECT_LANES.md) | Can one object hold a stable win/loss lane? Explicit local pair cycles. |
| [3.0](./030_B-TONE_FIRST.md) | Can Scorey keep its voice once routing is settled? Tone first. |
| [4.0](./040_B-ABSTRACT_TONE_MEASUREMENT.md) | What changes when phrase anchors leave tone measurement? Abstract constraints. |
| [5.0](./050_B-FAIL_PRESSURE_PULSE.md) | What changes when bounded fail pressure becomes the binary unit? Pulse evidence. |
| [6.0](./060_B-SCOREBOARD_JUDGEMENT.md) | Does `scoreboard_claim` deserve its own judged lane? Row-level scoreboard. |
| [7.0](./070_B-BROADER_PROSE_JUDGEMENT.md) | What reopens above the scoreboard fragment? Broader round prose. |
| [8.0](./080_B-MENACE_JUDGEMENT.md) | What holds when the full visible round is judged as menace? Menace quality. |
| [pre-9.0](./410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md) | Can positive runtime instructions preserve the menace lane? Staged, not yet new evidence. |

Each later beta narrows its own claim; it does not erase earlier evidence.
Route, tone, pulse, scoreboard, prose and menace verdicts remain distinct.
`PASS`/`FAIL` comes before failure disposition, and archive is not a pass.
Beta labels are research architectures, not app releases, package versions,
branch names or another sweep.

The established evaluation process remains the [Beta 8 Eval
Shape](./080_B-MENACE_JUDGEMENT.md#eval-shape) and the staged [First Kernel
Shape](./410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md#first-kernel-shape):
bounded raw runs, route validity as the floor, full visible rounds judged
row-by-row across cross-object and same-pick families, and human-supplied
verdicts tied to exact settings, prompt, source, and output IDs. The current
private continuation is `20449-20454`: its CSV and notes sidecar hold one
human `PASS` and five `FAIL` verdicts with exact notes. Those human verdicts
are now persisted in the existing menace lens with source and hash attribution;
the separate mechanical route-floor passes are engineer evidence. The range
closed at `6` total, `1` pass, `5` fail, `0` pending, and `0` archived, with
tone, scoreboard, and prose settled for all six rows. No new beta, prompt
change, model choice, or runtime configuration change is claimed.

The older private `20443-20448` continuation retains historical Codex engineer
labels; its human review remains unresolved and disputed, and it is not an
accepted baseline.

## Reading order and boundaries

Read the legend, then Betas 1–8, then the staged pre-Beta 9 contract. Use the
individual boundary document for its judged object, unit, sample range,
baseline, and close condition. Plans are not active method until the repository
earns them.

The local private model packet at
`docs/peanut/research/2026-09-19-model-experiments/README.md` is exploratory
evidence, not a new beta. Its run folders preserve raw outputs, prompts,
reviews and receipts. Scorey uses the shared Polinko research model in a
smaller rigged-round instrument: route-first, lane-shaped evaluation and
binary evidence discipline. Durable decisions belong in
[DECISIONS](../governance/DECISIONS.md); runtime and operator truth belong in
[ARCHITECTURE](../runtime/ARCHITECTURE.md) and [RUNBOOK](../runtime/RUNBOOK.md).
