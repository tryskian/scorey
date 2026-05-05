# Runbook

This is the operator guide for local setup, procedure, validation, and eval
work.

Use `docs/runtime/ARCHITECTURE.md` for system shape. Use this file when you
need to inspect, check, or advance the repo.

## Start A Session

1. Read the local instruction surface:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm the repo path:
   - `/Users/tryskian/Github/scorey`
3. Treat the tracked docs as current project state.
4. Install or refresh the local environment:
   - `make install`
5. Keep the display awake during active work on macOS:
   - `make caffeinate`
6. Add live runtime credentials when needed:
   - put `OPENAI_API_KEY` in the repo `.env`
   - or export it in the shell
7. State the active kernel before editing tracked files.

## Everyday Commands

| Task | Command |
| --- | --- |
| show the repo file tree | `find . -maxdepth 2 -type f | sort` |
| show tracked docs | `find docs -maxdepth 3 -type f | sort` |
| inspect recent history when needed | `git log --stat --oneline --max-count=5` |
| search the current docs surface | `rg -n "<term>" README.md docs` |
| install or refresh the runtime env | `make install` |
| keep the display awake on macOS | `make caffeinate` |
| release the display wake lock | `make decaffeinate` |
| stop all matching caffeinate processes | `make decaffeinate-all` |
| check the environment | `make doctor-env` |
| show session status | `make session-status` |
| run tests | `make test` |
| run tests with branch coverage | `make test-cov` |
| run lint checks | `make lint` |
| run format checks | `make format-check` |
| format the Python surface | `make format` |
| run static typing | `make typecheck` |
| install git hooks | `make precommit-install` |
| run pre-commit hooks on all files | `make precommit-run` |
| run pre-push hooks on all files | `make prepush-run` |
| run the current baseline checks | `make check` |
| build the package | `make package-check` |
| initialize the eval database | `make eval-init` |
| list recent eval rows | `make eval-list EVAL_LIMIT=10` |
| list only pending eval rows | `make eval-list EVAL_LIMIT=10 EVAL_VERDICT=pending` |
| list a stratified pending review sample | `make eval-review-sample EVAL_LIMIT=12` |
| record one human verdict | `make eval-judge OUTPUT_ID=17922 VERDICT=pass NOTE='route-valid and legible'` |
| run the Research Beta 1.0 picks gate | `make research-beta1 EVAL_LIMIT=10` |
| record a baseline local eval batch | `make eval-sample-local EVAL_COUNT=30` |
| record a six-pair `Research Beta 1.0` local coverage batch | `make eval-sample-local EVAL_COUNT=30 EVAL_PATTERN=research-beta-1-coverage` |
| record an explicit local pair cycle | `make eval-sample-local EVAL_COUNT=30 EVAL_PAIRS='rock,paper scissors,rock'` |
| record a live API eval batch | `make eval-sample-live EVAL_COUNT=12` |
| run end-of-day preflight | `make eod-preflight` |
| run end-of-day closeout | `make eod` |

## Upstream Resources

Check the live upstream surface before making SDK or runtime-pattern choices
that depend on OpenAI tooling.

- OpenAI API Python quickstart:
  - [developers.openai.com/api/docs/quickstart](https://developers.openai.com/api/docs/quickstart)
- OpenAI Python SDK repo:
  - [github.com/openai/openai-python](https://github.com/openai/openai-python)
- OpenAI Agents guide:
  - [developers.openai.com/api/docs/guides/agents](https://developers.openai.com/api/docs/guides/agents)
- OpenAI Agents SDK Python repo:
  - [github.com/openai/openai-agents-python](https://github.com/openai/openai-agents-python)

## Scorey Commands

App path:

- `scorey`
- `scorey --local`
- `make app`
- `LOCAL=1 make app`

Operator path:

- `scorey play rock`
- `scorey --local play paper`
- `make play PICK=rock`
- `LOCAL=1 make rock`
- `LOCAL=1 make paper`
- `LOCAL=1 make scissors`

The local path is deterministic. The live path uses the OpenAI Agents SDK and
requires `OPENAI_API_KEY`.

TTY interaction shape:

- banner first
- `you:` selector is the only active control
- `me:` stays inactive until `enter`
- Scorey's pick reveals before the explanation finishes
- the inline spinner uses the Probaboracle-style Braille loader
- `enter` starts the next round
- `esc` exits the app loop

## Eval Commands

Storage:

- `make eval-init`
- `make eval-list EVAL_LIMIT=10`
- `make eval-list EVAL_LIMIT=10 EVAL_VERDICT=pending`
- `make eval-review-sample EVAL_LIMIT=12`
- `make eval-judge OUTPUT_ID=17922 VERDICT=pass NOTE='route-valid and legible'`
- `make research-beta1 EVAL_LIMIT=10`
- `make eval-sample-local EVAL_COUNT=30`
- `make eval-sample-local EVAL_COUNT=30 EVAL_PATTERN=research-beta-1-coverage`
- `make eval-sample-local EVAL_COUNT=30 EVAL_PAIRS='rock,paper scissors,rock'`
- `make eval-sample-live EVAL_COUNT=12`
- `make eval-sample-live EVAL_COUNT=12 EVAL_USER_PICKS='rock paper'`

Compatibility aliases:

- `scorey eval-beta-1 --limit 10`
- `make eval-beta1 EVAL_LIMIT=10`

Notebook:

- `output/jupyter-notebook/scorey-eval-db-walkthrough.ipynb`

Current posture:

- local SQLite only
- binary top-level verdicts only
- one notebook walkthrough beside the operator path
- explicit human judgments now have a first-class operator command
- stratified pending review now has a first-class operator command
- `Research Beta 1.0` judges only the pick pair in `scorey_pick, user_pick` order
- local `baseline` sampling is a soak/population lane, not a diversity lane
- local `research-beta-1-coverage` sampling cycles all six `Research Beta 1.0` pass pairs evenly
- explicit local pair cycles let the research lane isolate narrow lanes like
  `rock,paper` and `scissors,rock`
- live sampling uses the real API path and records rows as `source_mode=live`
- live sampling cycles `rock paper scissors` by default unless a narrower user-pick cycle is supplied

## Validation

For docs-only changes:

- read back the changed docs
- keep claims aligned with the actual tree
- run `make doctor-env`
- run `make check`

For round-contract changes specifically:

- sweep `docs/diagrams/PIPELINE.md`
- sweep `docs/runtime/ARCHITECTURE.md`
- sweep `docs/research/README.md`
- sweep `docs/governance/SESSION_HANDOFF.md`
- record durable runtime choices in `docs/governance/DECISIONS.md`

When git and runtime tooling exist, expand this section with the smallest check
set that matches each kind of change.

For runtime changes:

- `make doctor-env`
- `make lint`
- `make typecheck`
- `make check`
- `LOCAL=1 make rock`

For eval storage changes:

- `make eval-init`
- `make eval-list EVAL_LIMIT=5`
- `make eval-list EVAL_LIMIT=5 EVAL_VERDICT=pending`
- `make eval-review-sample EVAL_LIMIT=6`
- `make eval-judge OUTPUT_ID=17922 VERDICT=pass NOTE='route-valid and legible'`
- `make research-beta1 EVAL_LIMIT=5`
- `make eval-sample-local EVAL_COUNT=9`
- `make eval-sample-local EVAL_COUNT=12 EVAL_PATTERN=research-beta-1-coverage`
- `make eval-sample-local EVAL_COUNT=8 EVAL_PAIRS='rock,paper scissors,rock'`
- `make eval-sample-live EVAL_COUNT=3`
- `make check`
- `make package-check`

For tooling-baseline changes:

- `make doctor-env`
- `make precommit-run`
- `make prepush-run`
- `make check`
- `make package-check`

If packaging metadata changed:

- `make package-check`

If live generation changed and `OPENAI_API_KEY` is available:

- `scorey play rock`

## End Of Day

Use this closeout flow before ending a working session:

- `make eod-preflight`
- `make eod`

Current `eod` checks:

- `eod-docs-check`
- `doctor-env`
- `check`
- `session-status`
- git closeout on clean, synced `main`
- `decaffeinate-all`

## Long-Run Eval Loop

The eval lane is now real, but it is still intentionally small.

The intended posture is:

1. Hold the current baseline steady.
2. Record or generate within the active narrow surface.
3. Judge in sweeps.
4. Keep verdicts binary.
5. Let repeated failure clusters earn the next lens or intervention.

## Layered Eval Lenses

Current day-zero posture:

- keep the top-level verdict binary
- keep one eval focus active at a time
- start with the round contract before broader fit judgments

The storage shape now exists for the top-level verdict. Additional lens names
and sidecar judgment tables are still intentionally pending beyond `Research Beta 1.0`.

## Command Ownership

- Human lead owns objective, scope, acceptance, and theory.
- Engineer owns implementation, validation, and repo hygiene.
- Keep bare `scorey` as the app path.
- Keep explicit subcommands as the operator path.
