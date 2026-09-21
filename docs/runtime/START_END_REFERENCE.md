# Start / End Reference

This is the compact command card for opening and closing a working session.

## Start

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm:
   - repo or worktree context
   - active branch
3. State before implementation:
   - current state
   - risks
   - next kernel
   - repo or worktree context
   - active branch
4. Run:
   - `make doctor-env`
   - `make start-runtime-check`
   - `make session-status`

## End

1. Run branch-local validation:
   - `make end-docs-check`
   - `make doctor-env`
   - `make path-leak-check`
   - `make path-leak-audit-local`
   - `make lint-docs`
   - `make scripts-check`
   - `make check`
   - `make package-check`
   - `make package-install-check`
   - `make end-runtime-check`
   - `make security-checks`
   - `make refresh-deps` when dependency metadata changed
2. Print the repository and runtime snapshot:
   - `make session-status`
3. Finish on clean synced `main`:
   - `make end-git-check`

The external Coffee Codex plugin owns Mac-wide keep-awake state. Scorey's
start and end wrappers leave that shared session unchanged.

## Wrapper Shortcuts

| Command | Job |
| --- | --- |
| `make start` | runs the startup sequence and prints the rehydrate prompt |
| `make end` | runs the full closeout sequence and final git check |

## Golden Smoke

New preparation and generation are paused under D-045 pending protocol
alignment. Saved evidence and its review tooling remain available.

| Command | Job |
| --- | --- |
| `make smoke-prepare` | freeze the six independent cases, source condition, prompts, settings, schema, and retrieval context without making model requests |
| `make smoke-run SMOKE_RUN=.local/smoke/<id>` | execute the prepared run with one fresh request per case and write isolated receipts and mechanical results |
| `make smoke-review-import SMOKE_RUN=.local/smoke/<id>` | import one saved smoke run and frozen criteria into additive `review_*` tables without changing the run folder or making model requests |
| `PYTHONPATH=src .venv/bin/python -m scorey.review_store import .local/smoke/<id> --criteria .local/reviews/<id>/review-criteria.md` | reimport using the exact frozen criteria copy when the research document has changed |
| `PYTHONPATH=src .venv/bin/python -m scorey.review_store show <dataset-id>` | read-only status for one imported staged-review dataset |
| `make smoke-review-sync REVIEW_NOTES=output/jupyter-notebook/scorey-coherent-absurdity-review.notes.json` | explicitly validate and append new attributed review events from the separate notes sidecar |

The smoke run does not write canonical eval rows or establish a quality
verdict. The staged review importer does not change `eval_*` rows or establish
a promotion. Use the review notebook for attributed observations and judgments;
sync its separate sidecar outside the immutable smoke folder explicitly.

## Close Condition

The repo is closed only when:

- `make end` has passed
- local `main` is clean
- local `main` is synced with `origin/main`
