<!-- @format -->

# Pre-Beta 5.0: Fail-Pressure Pulse

## What This Pre-Beta Asks

Should Scorey treat a bounded non-OCR run as the real binary unit once
run-level seam density matters more than single-row replay?

## Status

Maybe, and the current cross-object isolation result is strong enough to make
the question worth staging explicitly.

`Research Beta 4.0` proved that row-level abstract measurement can narrow a
real seam without falling back into phrase anchors. This pre-beta note asks
whether the next method step should move the binary judgment up one level:

- the pulse becomes the binary unit
- the rows become evidence inside the pulse

## Eval Shape

This is not `Research Beta 5.0` yet.

It is the staging contract for a possible `5.0` promotion.

The proposed pulse shape for Scorey is:

- bounded non-OCR run
- start small:
  - around `15` rows
- first staged target family:
  - `cross-object coherence drift`
- first staged pair cycle:
  - `paper/scissors`
  - `rock/paper`
  - `scissors/rock`
- row evidence is judged first as:
  - `anchor`
  - `counted seam`
  - `excluded noise`
- the pulse verdict is binary:
  - `PASS`
  - `FAIL`

Counted pulse rules:

- more anchors than counted seams: `PASS`
- more counted seams than anchors: `FAIL`
- tie: `FAIL`

Evidence taxonomy:

- `anchor`
  - route-valid row
  - preserves both picks clearly
  - shows a coherent causal mismatch between Scorey's winning state and the
    user's worse state
  - keeps the scoreboard claim on the user's losing side
- `counted seam`
  - route-valid row
  - failure belongs to the active target family
  - row is still coherent enough to retain as live evidence
  - counts against the pulse verdict
- `excluded noise`
  - row does not answer the target-family question cleanly enough to count
    for or against the pulse verdict

Exclusion reasons:

- `operator_artifact`
  - the row is malformed, truncated, or otherwise not honestly reviewable
- `off_target_failure`
  - the row fails for a different seam family than the active pulse target

Exclusion rules:

- raw pulse size stays visible
- counted pulse size stays visible
- every excluded row needs a narrow reason
- excluded rows stay reviewable after the pulse
- excluded rows never disappear into the verdict total

Reporting shape:

- raw rows
- anchors
- counted seams
- excluded rows by reason
- counted total
- pulse verdict

## Diagram

```mermaid
flowchart TD
  A["Isolated pair-cycle run<br/>paper/scissors<br/>rock/paper<br/>scissors/rock"]
  B["Bounded pulse<br/>about 15 rows"]
  C{"Review each row"}
  D["Anchor"]
  E["Counted seam"]
  F["Excluded noise"]
  G["Exclusion reason<br/>operator_artifact<br/>off_target_failure"]
  H["Anchor tally"]
  I["Counted seam tally"]
  J["Excluded tally by reason"]
  K["Counted total<br/>anchors + counted seams"]
  L{"Pulse verdict"}
  M["PASS<br/>anchors > seams"]
  N["FAIL<br/>seams >= anchors"]
  O["Research report<br/>raw rows<br/>counted total<br/>excluded by reason<br/>pulse verdict"]

  A --> B --> C
  C --> D --> H
  C --> E --> I
  C --> F --> G --> J
  H --> K
  I --> K
  H --> L
  I --> L
  L --> M
  L --> N
  J --> O
  K --> O
  M --> O
  N --> O
```

Reading note:

- the pair cycle defines the family under pressure
- raw rows are everything inside the bounded pulse
- only `anchor` and `counted seam` rows enter the verdict math
- excluded rows stay visible by reason, but do not alter the counted total
- the report has to show both the pulse verdict and how that verdict was made

## What This Would Change

If this graduates into `Research Beta 5.0`, Scorey would change the unit of
judgment for bounded non-OCR runs:

- `Beta 4.0`:
  - row-level `PASS / FAIL`
  - row-level `RETAIN / EVICT`
- `Beta 5.0` candidate:
  - row-level evidence labeling inside the pulse
  - pulse-level `PASS / FAIL`

That would make run-level shape harder to fake:

- one lucky row could not make the whole run look healthy
- seam density would matter more than isolated wins
- exclusion review would become part of pulse hygiene

## Why It Matters

The current `Beta 4.0` isolated cross-object run already showed a coherent
fail family:

- `77` route pass
- `50` tone pass
- `27` tone fail
- `27` retain
- `0` evict

That is exactly the kind of result that invites pulse judgment.

The row-level method already proved the seam is real. Pulse judgment would ask
a stricter question:

- does this family actually pass under bounded fail pressure
- or does counted seam density still outweigh the anchors

## What It Still Needs

Before this becomes `Research Beta 5.0`, Scorey still needs:

- one first bounded pulse launched on the staged target family
- explicit research reporting that compares pulse verdicts back to the closed
  `Beta 4.0` row-level baseline

## What Would Promote It

This becomes `Research Beta 5.0` only when Scorey starts the first real pulse
run.

Promotion boundary:

1. pulse contract is accepted as the next eval unit
2. the first bounded pulse is launched
3. the research index flips from closed `4.0` to active `5.0`
4. pulse evidence, not just hypothesis text, becomes the current method
