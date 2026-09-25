<!-- @format -->

# Validation Template

Use this for tracked or staged run, soak, or gate proof docs where the job is
to show whether a bounded operator or evidence surface actually held.

## Metadata

| Field | Value |
| --- | --- |
| Code | `NNN_VALIDATION` |
| Category | `validation` |
| Status | `staged`, `running`, `closed`, `failed`, or `snapshot` |
| Last evidence | `YYYY-MM-DD` |
| Owns | one sentence naming the gate or proof surface this doc covers |

## Headline Shape

- `Validation: Name`
- or `Gate Proof: Name`
- or `Closeout Proof: Name`

## Section Order

1. metadata table
2. `Question`
3. `Run`
4. `Decision`
5. `Residual Risk`
6. `Next Move`

## Required Validation Moves

- state the exact gate, closeout, or soak surface being proved
- state the bounded run or command surface explicitly
- keep the proof in a compact table
- state the decision plainly:
  - `pass`
  - `hold`
  - `rerun`
  - `fail`
- state what the validation still does not prove

## Default Run Table

| Check | Result | Read |
| --- | ---: | --- |
| runtime gate | `pass` | `0` pending and no live sampler |
| bounded closeout | `pass` | range settled back to clean runtime |
| operator checks | `n/n` | short read |
| residual failures | `0` | compact note |

## Default Decision Table

| Decision | Reason |
| --- | --- |
| `pass`, `hold`, `rerun`, or `fail` | one sentence |

## Validation Questions To Answer

- what exact surface is being proved?
- what bounded run or command sequence produced the evidence?
- did the gate or closeout actually hold?
- what still remains outside the proof?
- what is the immediate next move?

## Style Rules

- lead with the metadata table
- keep the run proof in tables
- keep the decision short and operational
- keep residual risk to one or two bullets
- do not let the doc drift into a broader lane recap
