# Session Handoff

Last updated: 2026-05-04

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - this file
2. Confirm repo and branch:
   - `/Users/tryskian/Github/scorey`
   - clean `main` when starting from a completed handoff
3. If the checkout is on `main`, cut a task branch before tracked edits.
4. State the active kernel before changing files.

## Current State

Scorey is a local, CLI-first, agent-backed rock, paper, scissors mini chatbot.

The default app path is bare `scorey`:

- responsive startup header
- fixed selector for `rock`, `paper`, and `scissors`
- `enter` selects
- `esc` exits
- inline spinner wait state
- collapsed selected prompt with no colon
- Scorey's pick shown as `scorey: [pick]` in the app reveal
- immediate `another round [y/n]?`

Operator commands remain separate:

- `play`
- `sample`
- `eval-list`
- `judge`
- sidecar judgment commands

## Research Snapshot

Current tracked research beta:

- `Research Beta 1.0`
- `round-aware brat logic`

Current eval beta:

- `Beta Eval 1.0`
- `pick routing`

Valid Beta Eval 1.0 routes:

| User Pick | Valid Scorey Picks |
| --- | --- |
| `rock` | `scissors`, `rock` |
| `paper` | `rock`, `paper` |
| `scissors` | `paper`, `scissors` |

Latest local eval checkpoint:

- rows `21-26` pass the `picks` lens
- product, round, and brat lenses remain intentionally pending
- total stored rows at handoff: `26`

## Next Kernel

Choose one lane at a time:

- eval:
  - keep Beta Eval 1.0 focused on pick routing until it is stable
  - do not judge product, round, or brat fit in the same pass
- app:
  - keep the wrapper small
  - keep user app flow separate from operator commands
- docs:
  - sweep tracked docs after runtime, product-shape, or research-method changes
  - update this handoff before ending a session when state changes

## Guardrails

- Keep the app small.
- Keep the runtime local and CLI-first.
- Keep generation agent-backed through the OpenAI Agents SDK.
- Keep active input fixed to `rock`, `paper`, and `scissors`.
- Do not add freeform input while the constrained interaction theory is active.
- Keep eval verdicts binary only.
- Keep one eval focus active at a time.
- End sessions on clean, synced `main` when possible.
- Keep local editor/session state out of git:
  - `.history/`
  - `*.code-workspace`

## Close A Session

At minimum:

- validate the active branch
- run checks
- merge only after checks pass
- update this handoff if current state changed
- end on clean `main` when possible

## Copy/Paste Refresh Prompt

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Confirm the repo path is /Users/tryskian/Github/scorey, confirm the active git branch, and say whether the thread is on clean main or a feature branch. Then execute the Next Kernel with minimal drift and full validation.`
