<!-- @format -->

# Lane Template

Use this for current evidence lanes where the method boundary is already known
and the doc's job is to show the active surface cleanly.

## Metadata

| Field | Value |
| --- | --- |
| Code | `NNN_LANE` |
| Category | `lane` |
| Status | `active`, `paused`, `closed`, or `snapshot` |
| Last evidence | `YYYY-MM-DD` |
| Owns | one sentence naming the active lane this doc tracks |

## Headline Shape

- `Lane: Name`
- or `Family Lane: Name`
- or `Source Lane: Name`

## Section Order

1. metadata table
2. `Question`
3. `Current Shape`
4. `Evidence Table`
5. `Diagram`
6. `Read`
7. `Why It Matters`
8. `Next Move`

## Required Lane Moves

- name the exact family or lane being tracked
- state the judged object explicitly
- state whether the lane is active, paused, closed, or a snapshot
- keep the current evidence in a table
- state the next move without turning the doc into a backlog dump

## Default Evidence Table

| Range | Surface | Result | Notes |
| --- | --- | --- | --- |
| `00000-00014` | bounded source | `pass/fail` or pulse shape | one compact note |

## Default Diagram Shape

```mermaid
flowchart LR
  A["Bounded source"]
  B["Lane lens"]
  C["Evidence table"]
  D["Current read"]
  E["Next move"]

  A --> B --> C --> D --> E
```

## Lane Questions To Answer

- what exact lane is open?
- what rows or ranges currently define it?
- what does the lane read show right now?
- what remains unresolved?
- what is the immediate next move?

## Style Rules

- lead with the metadata table
- keep the evidence in tables, not long inventories
- use prose only for interpretation
- prefer one compact diagram over multiple mini-diagrams
- keep `Next Move` concrete and near-term
