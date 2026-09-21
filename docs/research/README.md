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

The local [Beta 1 restart](./010_B-PICK_ROUTING.md) under
[D-039](../governance/DECISIONS.md#d-039-restart-changed-model-measurement-at-beta-1)
is complete: 3,568 route passes, 0 fails, 0 pending, IDs `20500-24067`, with
all six pairs covered. The [private receipt](../peanut/research/2026-09-20-beta1-local-restart/verification.json)
verifies persisted judgments and unchanged prior evidence. This deterministic
local run measured routing; live model quality and retrieval efficacy remain
separate questions. Beta 2 has not started.

Research Beta 1.0 through Research Beta 8.0 are closed baselines; only
`pre-Beta 9.0` remains staged.

`pre-Beta 9.0` remains a staged historical comparison above the closed
`Research Beta 8.0` menace baseline. It is not the immediate command to open a
fresh menace run, and it does not authorize restoring historical phrase banks.

| Historical comparison | Evidence |
| --- | --- |
| Cross-object menace | `20410-20417: 6 / 2`; `20404-20409: 4 / 2`; `20397-20403: 4 / 3`; `20307-20321: 11 / 4`; `20382-20396: 9 / 6`; `20352-20366: 11 / 4` |
| Same-pick menace | `20367-20381: 15 / 0` |
| Runtime closure | `0` pending across route, tone and disposition |

Latest exploratory live snapshot (`20455-20499`) is 45 cross-object rows, 15
per reverse pair: route `45` pass and menace `10` pass / `35` fail. Tone,
scoreboard, and prose each have 45 archive rows, not individual measured
passes. The two private packets are [Luna pulse](../peanut/research/2026-09-20-luna-medium-pulse/)
and [Luna two-pulse](../peanut/research/2026-09-20-luna-medium-two-pulses/);
neither is the Beta 1 restart.

Earlier closed contrast:

- Beta 5 pulse: cross-object `8 / 5 / 2`, then `9 / 6 / 0`, then `9 / 6 / 0`; same-pick `15 / 0 / 0`, then `15 / 0 / 0`.
- Beta 6 scoreboard: cross-object and same-pick slices each held at `15 / 0`.
- Beta 7 prose: cross-object reopened at `9 / 6` and repeated; same-pick held at `15 / 0`.

## New Research Direction

The prompt and model experiments led the September 20 session. The human
identified coherent absurdity as a new beta arc: inventive excuses can extend
the relationship between picks, as in the magic-paper/scissors-to-frog example.
Exact Scorey criteria, gate placement, and a beta identifier remain open;
the established measurement order and historical verdicts stay explicit.

The [session findings](../peanut/research/2026-09-20-session-findings.md) link
experiment conditions, human readings, Probsie's evaluation precedent, and the
verified prompt-anchoring history. The [context reports](../peanut/research/2026-09-20-context-reading/README.md)
provide supporting source readings. The primary's proposed next discussion is
a joint review of the full instruction surface before shaping this arc.

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

The established measurement sequence begins with the [Beta 1 route rubric](./010_B-PICK_ROUTING.md):
compute the gate in Scorey/user order, then persist individual route verdicts
for the exact output range and per-pair counts. Advance through each later
boundary only after its own judged object and close condition are met. Record
exact settings, prompt, source revision, any captured patch, source mode, run
scope, and output IDs. `research-beta1` reporting does not itself persist route
verdicts, and its initialization path may migrate the schema.

The private continuation `20449-20454` holds one human `PASS` and five human
`FAIL` verdicts with exact notes and source/hash attribution. Disputed
`20443-20448` retains historical Codex labels and is not an accepted baseline.
No new beta, prompt change, or lasting model choice is claimed by either
continuation.

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
