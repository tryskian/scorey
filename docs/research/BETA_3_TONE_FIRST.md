# Research Beta 3.0: Tone First

## What This Beta Asked

Can Scorey keep its own voice once route validity and pick legibility are no longer the open question?

## Short Answer

Started, separating real signal, but not settled.

The tone lane now has real separation, and the widened live tone surface is
fully dispositioned. The stale queue is closed; the next useful evidence should
come from a fresh post-archive run.

## Eval Shape

`Research Beta 3.0` keeps the live route-valid floor from the earlier betas, but changes the verdict question.

It judges each live round through five positive-only traits:

- `pick-aware`
- `playful`
- `confident`
- `coherent`
- `imaginative`

Its failure handling is now two-stage:

- `PASS / FAIL` at the tone gate
- if `FAIL`, then `RETAIN / EVICT`

What stays out of scope:

- scoreboard judgement as its own lane
- broader prose judgement as its own lane

## Diagram

```mermaid
flowchart LR
  L["judged live round"]
  R["route-valid floor already held"]
  T["five-point tone bar"]
  P["pick-aware"]
  Q["playful"]
  C["confident"]
  H["coherent"]
  I["imaginative"]

  L --> R --> T
  T --> P
  T --> Q
  T --> C
  T --> H
  T --> I
```

## What It Showed

This beta has now started, and the first widened tone queue is not an all-pass surface.

Its starting surface was the already-judged live queue:

- `395` live rows
- `395` beab pass under the current narrow route-and-legibility lens
- `0` fail
- `0` pending

Since then, six more extended live runs have widened the active surface:

- `12` new live rows after output `18317`
- `257` new live rows after output `18329`
- `294` new live rows after output `18586`
- `294` new paper-only live rows after output `18880`
- `170` new live rows after output `19174`
- `157` new live rows after output `19344`
- `342` new live rows after output `19501`
- all six runs stayed entirely inside the valid `Research Beta 1.0` route set

The current live snapshot is now:

- `1921` live rows recorded
- `1921` beab pass at the route-and-legibility floor
- `0` beab fail
- `0` pending route review
- the newest paper-only batch stayed inside the expected paper route families:
  - `paper/paper`: `144`
  - `paper/rock`: `150`
- the first mixed post-surface run also stayed inside the valid route families:
  - `paper/paper`: `34`
  - `paper/scissors`: `24`
  - `rock/paper`: `23`
  - `rock/rock`: `29`
  - `scissors/rock`: `28`
  - `scissors/scissors`: `32`
- the newest post-evict run also stayed inside the valid route families:
  - `paper/paper`: `25`
  - `paper/scissors`: `21`
  - `rock/paper`: `27`
  - `rock/rock`: `27`
  - `scissors/rock`: `26`
  - `scissors/scissors`: `31`

The current tone lane now records:

- `860` rows judged
- `302` tone pass
- `558` tone fail
- `1061` tone rows archived out of the active queue
- `0` route-passed live rows still pending tone review
- the first fresh post-surface live run is now fully closed:
  - `170` route pass
  - `66` tone pass
  - `104` tone fail
  - `104` evict
  - `0` fresh pending route reviews
  - `0` fresh pending tone reviews
  - `0` fresh pending fail dispositions
- the next post-evict run is also fully closed:
  - `157` route pass
  - `65` tone pass
  - `92` tone fail
  - `92` evict
  - `0` fresh pending route reviews
  - `0` fresh pending tone reviews
  - `0` fresh pending fail dispositions
- the corrected two-hour live batch after output `19501` is wind-down-closed:
  - `342` route pass
  - `5` tone pass
  - `3` tone fail
  - `334` archived at wind-down before full tone review
  - `3` retain
  - `0` evict
  - `0` fresh pending route reviews
  - `0` fresh pending tone reviews
  - `0` fresh pending fail dispositions
- historical pre-surface tone fails no longer sit in the active disposition queue:
  - `359` stale failed rows are archived out of that surface
- the strongest pass pattern is object-specific slapstick or physical demotion that still tracks both picks
- the weak pattern has tightened from generic `real one` / `napkin` toward cross-object coherence drift, with a smaller same-pick object-shape drift

Inside the paper-only lane, the first isolated judged surface is now:

- `722` route-passed paper rows total
- `566` judged paper-only tone rows
- `185` pass
- `381` fail
- `156` archived out of the active paper queue
- `0` pending
- `my paper was the real one and your paper was a napkin` is still a weak fail
- `my rock was stone-cold advantage and your paper was a napkin` is still a stronger pass
- the seam is not "napkin" by itself
- the seam is the thinner paper/paper framing around `real one`

So the open question is no longer whether Scorey stayed on-pick. It is whether Scorey sounds like Scorey once that floor is already satisfied.

## Why It Matters

Tone is the cleanest next widening step.

It is more specific than a broad prose pass, and it stays closer to the object's identity than a scoreboard-first lane would.

## What It Could Not Show

- scoreboard quality as its own judged lane
- broader prose quality as its own judged lane
- whether the five-point tone bar will stay stable across a larger judged queue
- whether later lenses will need a different sampling shape
- whether tone review can keep up once live generation widens again

## What Changed Next

The next useful move is still to keep the fresh-slice closure rule in place and
start the next live run from the now-clean boundary instead of widening another
stale queue.

That now includes a sharper failure rule:

- retain failures that still belong in the active lane as live evidence
- evict failures that prove the paper seam or another lane boundary needs an
  upstream correction before rerun
- archive stale failed rows out of the active disposition queue when they are no
  longer the live work surface
