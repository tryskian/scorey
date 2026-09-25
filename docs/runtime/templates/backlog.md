<!-- @format -->

# Backlog Template

Use this for candidate seams, source pools, and parked follow-up lanes that
are not yet promoted into an active boundary, lane, or hypothesis doc.

## Metadata

| Field | Value |
| --- | --- |
| Code | `NNN_BACKLOG` |
| Category | `backlog` |
| Status | `source_pool`, `triaged`, `parked`, or `promoted` |
| Last evidence | `YYYY-MM-DD` |
| Owns | one sentence naming the candidate pool this doc holds |

## Headline Shape

- `Backlog: Name`
- or `Candidate Pool: Name`
- or `Parked Lanes: Name`

## Section Order

1. metadata table
2. `Triage`
3. `Promotion Rule`
4. `Current Read`
5. `Next Move`

## Required Backlog Moves

- keep candidates in a compact table
- separate recurring seams from one-off noise
- state why a candidate is not yet promoted
- define the promotion rule explicitly
- keep the next move to triage, staging, or retirement

## Default Triage Table

| Family | Surface | Evidence | Read | Action |
| --- | --- | ---: | --- | --- |
| candidate seam | route, tone, pulse, scoreboard, prose, or menace | `n` bounded hits | compact pressure read | hold, stage, review, or retire |

## Default Promotion Rule Table

| Requirement | Meaning |
| --- | --- |
| distinct judged object | not a duplicate of an existing lane |
| recurring seam | appears more than once under a bounded read |
| method consequence | changes what the repo should test or preserve |
| bounded source plan | can be tested without reopening the whole queue |

## Backlog Questions To Answer

- what candidate seams are in the pool?
- which ones are recurring rather than noisy?
- why is each candidate still unpromoted?
- what exact rule would promote one into a staged lane?
- what should happen next to the pool?

## Style Rules

- lead with the metadata table
- keep backlog triage in tables
- avoid long narrative inventories
- keep promotion rules explicit and mechanical
- keep `Current Read` and `Next Move` short
