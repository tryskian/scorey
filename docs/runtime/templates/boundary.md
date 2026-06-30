<!-- @format -->

# Boundary Template

Use this for tracked or staged method-boundary docs:

- closed beta notes
- active beta notes
- pre-beta staged notes

## Metadata

| Field | Value |
| --- | --- |
| Code | `NNN_B-NAME` or `NNN_PB-NAME` |
| Category | `boundary` |
| Status | `staged`, `active`, or `closed` |
| Last evidence | `YYYY-MM-DD` |
| Owns | one sentence naming the method boundary this doc establishes |

## Headline Shape

- `Research Beta X.Y: Name`
- or `Pre-Beta X.Y: Name`

## Filename Rule

- use `NNN_B-NAME.md` for active or closed beta boundaries
- use `NNN_PB-NAME.md` for staged pre-beta boundaries
- in `scorey`, staged pre-beta boundaries live in the `400-499` range

## Section Order

1. metadata table
2. `What This Beta Asks`
   - or `What This Pre-Beta Asks`
3. `Status`
4. `Eval Shape`
5. `Diagram`
6. `What It Showed`
   - or `What This Would Change`
7. `Why It Matters`
8. `What It Still Cannot Show`
   - or `What It Still Needs`
9. `What Changed Next`
   - or `What Would Promote It`

## Required Boundary Moves

- state the prior closed layer explicitly
- state the current judged object explicitly
- state what changed in the evidence meaning
- state whether the boundary is staged, active, or closed
- state the exact promotion or close condition

## Default Diagram Shape

```mermaid
flowchart TD
  A["Bounded source shape"]
  B["Current lens"]
  C{"Per-row or per-pulse verdict"}
  D["Pass shape"]
  E["Fail shape"]
  F["Bounded read"]
  G["Boundary interpretation"]

  A --> B --> C
  C --> D --> F
  C --> E --> F
  F --> G
```

## Boundary Questions To Answer

- what was the previous layer?
- what is the new judged object?
- what does this boundary allow the repo to claim now?
- what still remains out of scope?
- what exact evidence would promote or close the lane?

## Style Rules

- lead with the metadata table
- keep the opening answer short
- use one compact diagram
- keep evidence examples bounded and explicit
- avoid sprawling recap if the prior beta is already documented elsewhere
