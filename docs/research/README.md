# Research

Scorey keeps the tracked research lane small on purpose.

Each beta is a distinct eval approach. This folder preserves the method shifts that changed what the evidence means.

Raw run notes and scratch material stay out of the tracked research surface until they become evidence.

## Current Beta

Current tracked research beta:

- `Research Beta 3.0`
- `tone first`

Current question:

Can Scorey hold its voice once route validity and pick legibility are no longer the open question?

Current finding:

- `Research Beta 1.0` proved the narrow routing contract
- `Research Beta 2.0` showed that each object lane can hold cleanly on the local deterministic path
- all three focused lanes completed with stable balance under the same routing gate:
  - rock:
    - `1790` rows of `rock/paper`
    - `1790` rows of `scissors/rock`
  - paper:
    - `1790` rows of `paper/scissors`
    - `1789` rows of `rock/paper`
  - scissors:
    - `1790` rows of `scissors/rock`
    - `1789` rows of `paper/scissors`
- the local deterministic queue is now fully judged:
  - `17,922` pass
  - `0` fail
  - `0` pending
- the live surface has now widened again:
  - `1252` live rows recorded
  - `1252` beab pass at the route-and-legibility floor
  - `0` beab fail
  - `0` pending route review
  - four recent extended live runs all stayed entirely inside the valid `Research Beta 1.0` route set:
    - after output `18317`: `12` new live rows
    - after output `18329`: `257` new live rows
    - after output `18586`: `294` new live rows
    - after output `18880`: `294` new paper-only live rows
  - the paper-only run stayed inside the expected paper route families:
    - `paper/paper`: `144`
    - `paper/rock`: `150`
  - `Research Beta 3.0` is now defined as a positive-only tone lens:
  - `pick-aware`
  - `playful`
  - `confident`
  - `coherent`
  - `imaginative`
  - the widened tone queue is now separating real signal:
    - `525` rows judged
    - `166` pass
    - `359` fail
    - `727` archived out of the active tone queue
    - `0` route-passed live rows still pending tone review
    - the current pass signal is object-specific slapstick or physical demotion that still tracks both picks
    - the current weak pattern is usually either generic `real one` / `napkin` or version/copy language, with a smaller playful line that is not coherent enough to keep
  - inside the isolated paper-only tone lane:
    - `613` route-passed paper rows total
    - `457` judged
    - `138` pass
    - `319` fail
    - `156` archived after the failure seam was established
    - `0` pending

Current clean lane:

- the route floor is caught up again on the completed paper-only batch
- use the completed paper-only run as the clean isolation lane for the current
  `real one` / `napkin` seam
- the widened live tone queue is now fully dispositioned: judged or archived
- the stale active queue is closed; the next tone evidence should come from a
  fresh post-archive live run instead of more backlog traversal
- treat tone failures through explicit disposition:
  - `retain` when the seam still belongs in the active lane
  - `evict` when the seam proves the lane definition itself is wrong
- keep route and legibility as the floor even if the next lens widens
- keep the local deterministic queue as baseline evidence, not as the active growth surface
- widen into scoreboard or prose judgement only after the tone lane earns it

## Beta Map

| Beta | Question | What Changed |
| --- | --- | --- |
| `Research Beta 1.0` | Does Scorey choose a valid rigged route? | The first gate narrowed to pick routing only. |
| `Research Beta 2.0` | Can one object hold a stable win/loss lane? | Explicit local pair cycles isolate one object across both roles in one focused lane. |
| `Research Beta 3.0` | Can Scorey keep its own voice once routing is settled? | The live judged lane keeps the route floor but switches the verdict lens to tone first. |

Read in order:

1. [Research Beta 1.0: Pick Routing First](./BETA_1_PICK_ROUTING.md)
2. [Research Beta 2.0: Focused Object Lanes](./BETA_2_OBJECT_LANES.md)
3. [Research Beta 3.0: Tone First](./BETA_3_TONE_FIRST.md)

## How To Read The Betas

These betas are research architectures. They are not app release versions, package versions, branch names, or one more sweep.

Each beta marks a real change in what the evaluation is asking:

- `Research Beta 1.0` proved route validity at the pick level
- `Research Beta 2.0` keeps the same gate but changes the sampling shape to inspect one object lane at a time
- `Research Beta 3.0` keeps the live route floor but changes the verdict lens to Scorey's voice
- failed rows now stay binary first and then move through `RETAIN / EVICT` as
  the disposition layer

Later betas do not erase earlier ones. They narrow what each verdict is allowed to mean.

## Cross-Beta Flow

```mermaid
flowchart LR
  B1["Research Beta 1.0<br/>pick routing only"]
  B2["Research Beta 2.0<br/>focused object lanes"]
  B3["Research Beta 3.0<br/>tone first"]

  S1["six valid pass pairs<br/>and nothing else"]
  S2["one object isolated<br/>across win and loss roles"]
  S3["five positive tone traits<br/>on judged live rounds"]

  B1 --> S1 --> B2 --> S2 --> B3 --> S3
```

## Plans

Plans are useful, but they are not evidence. They do not become active method until the repo earns them.

Parked lanes:

- object lanes:
  - complete for the current local pass
- live gameplay:
  - the widened live queue is now fully route-passed again
  - keep using those route-passed live rows as the tone-first evidence surface
  - after the stale queue archive, use fresh runs rather than old backlog traversal for the next tone evidence
- later eval lenses:
  - only widen into scoreboard or prose judgement after the tone lane stabilises
- research visuals:
  - keep the beta map and per-beta notes in tracked docs
  - only add heavier cross-beta visuals if the method story actually needs them

## Polinko Contrast

Scorey uses the same **[Polinko research model](https://github.com/tryskian/polinko)**, but it is a smaller rigged-round instrument.

```mermaid
flowchart LR
  P["Polinko"]
  P1["broader research system"]
  P2["many runtime and eval surfaces"]
  P3["binary fail pressure across products"]

  Q["Scorey"]
  Q1["rigged round instrument"]
  Q2["pick-routed round generation"]
  Q3["routing-first and lane-shaped evals"]

  S["shared line\\nhuman-led research\\nbinary eval discipline\\nrepo-native docs and diagrams"]

  P --> P1
  P --> P2
  P --> P3

  Q --> Q1
  Q --> Q2
  Q --> Q3

  P --- S
  Q --- S
```
