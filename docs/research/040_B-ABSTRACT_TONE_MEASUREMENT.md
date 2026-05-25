# Research Beta 4.0: Abstract Tone Measurement

| Field | Value |
| --- | --- |
| Code | `040_B-ABSTRACT_TONE_MEASUREMENT` |
| Category | `boundary` |
| Status | `closed` |
| Last evidence | `2026-05-16` |
| Owns | the de-anchored tone-first measurement boundary. |

## What This Beta Asks

Can Scorey keep its own voice once route validity and pick legibility are
settled, without contaminating the live measurement surface with hard-coded
phrase anchors?

## Status

Closed.

The same-pick lane is materially stronger, there is no early `real one` /
`napkin` relapse across the closed slice, and the retained weak seam is still
cross-object coherence drift.

## Eval Shape

`Research Beta 4.0` keeps the widened lane from `Research Beta 3.0`:

- live route-valid floor first
- positive-only tone bar:
  - `pick-aware`
  - `playful`
  - `confident`
  - `coherent`
  - `imaginative`
- `PASS / FAIL` at the tone gate
- if `FAIL`, then `RETAIN / EVICT`

What changed is the generator contract:

- no phrase blacklists in the live prompt surface
- no canned `good fragments`
- no canned `bad fragments`
- findings stay in tracked research docs, not in the generator prompt

This is the Polinko-family method boundary carried back into Scorey.

## Diagram

```mermaid
flowchart LR
  L["judged live round"]
  R["route-valid floor already held"]
  T["five-point tone bar"]
  A["abstract prompt constraints"]
  S["specific pick-shaped mismatch"]

  L --> R --> T --> A --> S
```

Slice chart:

```mermaid
xychart-beta
  title "Beta 4.0 closed slice reads"
  x-axis "Slice type" ["mixed tranche", "restored segment", "isolated family"]
  y-axis "Rows" 0 --> 80
  bar "Tone pass" [47, 42, 50]
  bar "Tone fail" [22, 20, 27]
```

## What It Showed

The first fresh `4.0` mixed tranche begins after output `19998`.

That tranche is now fully closed:

| Slice | Route pass | Tone pass | Tone fail | Retain | Evict | Pending |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| first closed tranche after `19998` | `69` | `47` | `22` | `22` | `0` | `0` |

Inside that first closed tranche, the restored interrupted segment after
output `20005` closed at:

| Segment | Route pass | Tone pass | Tone fail | Retain | Evict |
| --- | ---: | ---: | ---: | ---: | ---: |
| restored interrupted segment after `20005` | `62` | `42` | `20` | `20` | `0` |

What that first closed slice shows:

| Signal | Read |
| --- | --- |
| same-pick rows | stronger and more physical |
| anchor relapse | no `real one` / `napkin` relapse across the closed slice |
| active weak seam | `cross-object coherence drift` |
| fail handling | `20` fail / `20` retain / `0` evict |

The first isolated fail-family run then narrowed directly onto the active weak
surface after output `20139`:

| Family | Route pass | Tone pass | Tone fail | Retain | Evict |
| --- | ---: | ---: | ---: | ---: | ---: |
| `cross-object coherence drift` | `77` | `50` | `27` | `27` | `0` |

Inside that isolated run, the fail mix stayed narrow:

| Fail type | Count |
| --- | ---: |
| `cross-object coherence drift` | `26` |
| `anchor relapse` | `1` |

Fail-mix chart:

```mermaid
xychart-beta
  title "Beta 4.0 isolated fail mix"
  x-axis "Fail type" ["cross-object", "anchor relapse"]
  y-axis "Rows" 0 --> 30
  bar "Rows" [26, 1]
```

That isolation run matters because it did not collapse into random noise when
the mixed lane was stripped away. The family kept producing the same kind of
retain-worthy failure under direct pressure.

`Research Beta 3.0` and `Research Beta 4.0` ask the same tone-first question,
but they do not produce the same kind of evidence.

The `3.0` surface still carried phrase residue inside the live generator:

- hard-coded forbidden phrases
- canned positive examples
- canned negative examples

That meant the prompt could manufacture or suppress the very seams the eval
lane was trying to observe.

`Research Beta 4.0` removes that residue and keeps only abstract constraints:

- concrete, pick-specific mismatch
- object-specific slapstick or demotion
- no abstract helper voice
- no duplicate-object shorthand

So the comparison is now explicit:

- `3.0`: anchored tone-first measurement
- `4.0`: abstract tone measurement

## Why It Matters

This is a research integrity correction, not just a prompt wording cleanup.

If the live prompt contains phrase anchors from previously observed failures,
the eval lane stops measuring cleanly. It starts comparing:

- model behaviour
- plus prompt residue

That breaks the intended family method.

`Research Beta 4.0` restores the comparison we actually want:

- live behaviour under the same route floor
- with the same tone bar
- without hard-coded phrase steering

## What It Still Cannot Show

- whether the stronger same-pick signal will hold across the full batch
- whether cross-object coherence drift remains the dominant durable seam after
  one isolated pass
- whether the next move should be another fresh measurement run or an upstream
  correction
- whether the remaining same-pick drift still deserves its own isolated lane

## What Changed Next

The live task under `Research Beta 4.0` is now straightforward:

1. keep the mixed run only long enough to identify the active fail families
2. split retained seams into isolated short runs one family at a time
3. keep route, tone, and disposition pending counts explicit
4. do not package until the fresh slice returns to `0` pending
5. compare each isolated fail-family result directly against the anchored
   `3.0` surface
