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
2. Confirm repo path:
   - `/Users/tryskian/Github/scorey`
3. Treat `archive/` as reference material only.
4. State the active kernel before changing files.

## Current State

Scorey is the same toy object, but the runtime has been reset.

The tracked docs are now the live source of truth:

- `README.md`
- `docs/governance/`
- `docs/runtime/`
- `docs/research/`
- `docs/diagrams/`

The archived reference docs remain under `archive/`, but they are not current
state.

No runtime package, command surface, or eval storage is tracked yet.

## Research Snapshot

Scorey remains a small rigged rock, paper, scissors research toy.

Current rebuild posture:

- preserve the object
- rebuild the runtime intentionally
- keep the surface small and local
- keep evals binary

Current beta naming is intentionally unset until the round contract lands.

## Next Kernel

Choose one lane at a time:

- contract:
  - define what one Scorey round must preserve
  - separate runtime-owned fields from model-generated fields
  - lock valid routing and same-pick behaviour
- runtime:
  - only begin after the round contract is written down
  - keep the wrapper small
  - keep the app path separate from operator commands
- docs:
  - keep tracked docs aligned with what actually exists
  - do not let `archive/` drift back into source-of-truth status

## Guardrails

- Keep the app small.
- Keep the runtime local and CLI-first.
- Keep generation agent-backed once the live path exists.
- Keep active input fixed to `rock`, `paper`, and `scissors`.
- Do not add freeform input while the constrained interaction theory is active.
- Keep eval verdicts binary only.
- Keep one active kernel at a time.

## Close A Session

At minimum:

- confirm the active kernel was actually completed
- update this handoff if current state changed
- keep the docs honest about what exists
- prefer clean `main` once git is initialized

## Copy/Paste Refresh Prompt

`Read README.md, docs/governance/CHARTER.md, docs/governance/DECISIONS.md, docs/runtime/ARCHITECTURE.md, docs/runtime/RUNBOOK.md, and docs/governance/SESSION_HANDOFF.md. In 5 bullets: current state, risks, and next kernel. Confirm the repo path is /Users/tryskian/Github/scorey. Treat archive/ as reference only. Then execute the Next Kernel with minimal drift and full validation.`
