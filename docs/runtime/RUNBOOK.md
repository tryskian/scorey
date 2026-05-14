# Runbook

This is the operator guide for local setup, procedure, validation, and eval
work.

Use `docs/runtime/ARCHITECTURE.md` for system shape. Use this file when you
need to inspect, check, or advance the repo.

For the compact session-open/session-close sheet, use
`docs/runtime/START_END_REFERENCE.md`.

## Start A Session

1. Read the tracked instruction surface:
  - from the final `STOP` block in `make start`
  - `README.md`
  - `docs/governance/CHARTER.md`
  - `docs/governance/DECISIONS.md`
  - `docs/runtime/ARCHITECTURE.md`
  - `docs/runtime/RUNBOOK.md`
  - `docs/runtime/START_END_REFERENCE.md`
  - `docs/governance/SESSION_HANDOFF.md`
2. Confirm you are at the repo root:
  - `git rev-parse --show-toplevel`
  - or `pwd`
3. Run session preflight:
  - `make doctor-env`
  - `make start-runtime-check`
  - `make session-status`
4. Treat the tracked docs as current project state.
5. Install or refresh the local environment:
  - `make install`
6. Keep the display awake during active work on macOS:
  - `make caffeinate`
7. Add live runtime credentials when needed:
  - put `OPENAI_API_KEY` in the repo `.env`
  - or export it in the shell
8. For any live API work, keep token monitoring available when needed:
  - use `make open-limits` or `make open-usage` directly when a tighter check is enough
  - use `make open-cost-console` only when you actually want the full dashboard set
9. State the active kernel before editing tracked files.

## Everyday Commands

| Task                                                                  | Command                                                                                                                            |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| show the repo file tree                                               | `find . -maxdepth 2 -type f \| sort`                                                                                               |
| show tracked docs                                                     | `find docs -maxdepth 3 -type f \| sort`                                                                                            |
| inspect recent history when needed                                    | `git log --stat --oneline --max-count=5`                                                                                           |
| search the current docs surface                                       | `rg -n "<term>" README.md docs`                                                                                                    |
| run the compact day-open routine                                      | `make start`                                                                                                                       |
| print the compact start/end operator sheet                            | `make rituals`                                                                                                                     |
| install or refresh the runtime env                                    | `make install`                                                                                                                     |
| keep the display awake on macOS                                       | `make caffeinate`                                                                                                                  |
| show display wake-lock status on macOS                                | `make caffeinate-status`                                                                                                           |
| release the display wake lock                                         | `make decaffeinate`                                                                                                                |
| alias wake-lock status for closeout language                          | `make decaffeinate-status`                                                                                                         |
| check the environment                                                 | `make doctor-env`                                                                                                                  |
| run the start-of-day runtime gate                                     | `make start-runtime-check`                                                                                                         |
| show session status                                                   | `make session-status`                                                                                                              |
| run tests                                                             | `make test`                                                                                                                        |
| run tests with branch coverage                                        | `make test-cov`                                                                                                                    |
| run lint checks                                                       | `make lint`                                                                                                                        |
| run format checks                                                     | `make format-check`                                                                                                                |
| format the Python surface                                             | `make format`                                                                                                                      |
| run static typing                                                     | `make typecheck`                                                                                                                   |
| install git hooks                                                     | `make precommit-install`                                                                                                           |
| run pre-commit hooks on all files                                     | `make precommit-run`                                                                                                               |
| run pre-push hooks on all files                                       | `make prepush-run`                                                                                                                 |
| run the current baseline checks                                       | `make check`                                                                                                                       |
| build the package                                                     | `make package-check`                                                                                                               |
| initialize the eval database                                          | `make eval-init`                                                                                                                   |
| list recent eval rows                                                 | `make eval-list EVAL_LIMIT=10`                                                                                                     |
| list only pending eval rows                                           | `make eval-list EVAL_LIMIT=10 EVAL_VERDICT=pending`                                                                                |
| list a stratified pending review sample                               | `make eval-review-sample EVAL_LIMIT=12`                                                                                            |
| record one human verdict                                              | `make eval-judge OUTPUT_ID=17922 VERDICT=pass NOTE='route-valid and legible'`                                                      |
| list a stratified pending tone review sample                          | `make eval-tone-sample EVAL_LIMIT=12`                                                                                              |
| list a paper-only pending tone review sample                          | `make eval-tone-sample EVAL_LIMIT=12 EVAL_USER_PICKS='paper'`                                                                      |
| record one tone verdict                                               | `make eval-tone-judge OUTPUT_ID=17922 VERDICT=pass NOTE='pick-aware playful confident coherent imaginative'`                       |
| archive one pending tone row out of the active queue                  | `make eval-tone-archive OUTPUT_ID=17922 NOTE='paper seam archived out of active queue'`                                            |
| list failed tone rows that still need `RETAIN / EVICT`                | `make eval-tone-disposition-sample EVAL_LIMIT=12`                                                                                  |
| archive one stale failed tone row out of the active disposition queue | `make eval-tone-disposition-archive OUTPUT_ID=17922 NOTE='historical stale fail backlog archived out of active disposition queue'` |
| record `RETAIN` or `EVICT` for one failed tone row                    | `make eval-tone-dispose OUTPUT_ID=17922 DISPOSITION=retain NOTE='keep in active lane'`                                             |
| run the Research Beta 1.0 picks gate                                  | `make research-beta1 EVAL_LIMIT=10`                                                                                                |
| record a baseline local eval batch                                    | `make eval-sample-local EVAL_COUNT=30`                                                                                             |
| record a six-pair `Research Beta 1.0` local coverage batch            | `make eval-sample-local EVAL_COUNT=30 EVAL_PATTERN=research-beta-1-coverage`                                                       |
| record an explicit local pair cycle                                   | `make eval-sample-local EVAL_COUNT=30 EVAL_PAIRS='rock,paper scissors,rock'`                                                       |
| record a live API eval batch                                          | `make eval-sample-live EVAL_COUNT=12`                                                                                              |
| open the OpenAI limits page                                           | `make open-limits`                                                                                                                 |
| open the OpenAI usage page                                            | `make open-usage`                                                                                                                  |
| open the OpenAI billing page                                          | `make open-billing`                                                                                                                |
| open all three OpenAI cost pages                                      | `make open-cost-console`                                                                                                           |
| run the compact end-of-day alias                                      | `make end`                                                                                                                         |
| run end-of-day preflight                                              | `make end-preflight`                                                                                                               |
| run the runtime completion gate directly                              | `make end-runtime-check`                                                                                                           |

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
- `make eval-tone-sample EVAL_LIMIT=12`
- `make eval-tone-sample EVAL_LIMIT=12 EVAL_USER_PICKS='paper'`
- `make eval-tone-judge OUTPUT_ID=17922 VERDICT=pass NOTE='pick-aware playful confident coherent imaginative'`
- `make eval-tone-archive OUTPUT_ID=17922 NOTE='paper seam archived out of active queue'`
- `make eval-tone-disposition-sample EVAL_LIMIT=12`
- `make eval-tone-disposition-archive OUTPUT_ID=17922 NOTE='historical stale fail backlog archived out of active disposition queue'`
- `make eval-tone-dispose OUTPUT_ID=17922 DISPOSITION=retain NOTE='keep in active lane'`
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
- explicit top-level verdicts only:
  - `pass`
  - `fail`
  - `pending`
- failed rows use an explicit disposition layer:
  - `retain`
  - `evict`
- stale failed tone rows can also be archived out of the active disposition queue without becoming `retain` or `evict`
- pending tone rows can also be archived out of the active queue without turning archive into a verdict
- one notebook walkthrough beside the operator path
- explicit human judgments now have a first-class operator command
- stratified pending review now has a first-class operator command
- tone judgments now have a separate first-class operator path
- tone archives now have a separate first-class operator path
- tone fail dispositions now have a separate first-class operator path
- stale tone fail disposition archives now have a separate first-class operator path
- `Research Beta 1.0` judges only the pick pair in `scorey_pick, user_pick` order
- `Research Beta 3.0` keeps the route-pass floor and judges tone on live rows through:
  - `pick-aware`
  - `playful`
  - `confident`
  - `coherent`
  - `imaginative`
- local `baseline` sampling is a soak/population lane, not a diversity lane
- local `research-beta-1-coverage` sampling cycles all six `Research Beta 1.0` pass pairs evenly
- explicit local pair cycles let the research lane isolate narrow lanes like
`rock,paper` and `scissors,rock`
- live sampling uses the real API path and records rows as `source_mode=live`
- live sampling cycles `rock paper scissors` by default unless a narrower user-pick cycle is supplied
- throughput pressure and spend pressure are treated as separate operator concerns

Fresh live review rule:

- let the sampler fill and judge the fresh slice in tandem
- route first:
  - `PASS / FAIL`
- then on fresh tone failures:
  - `RETAIN / EVICT`
- do not package or land the branch until the fresh slice is back to `0`
  pending at route, tone, and failure-disposition layers
- if an interrupted slice has gone stale, audit the route floor first and then
  close it in one hand:
  - if the slice is still useful and fresh enough, resume normal tandem review
  - if the slice is Beta 1-valid but no longer a fresh tone lane, bulk-close
    the route floor and archive the stale tone queue instead of pretending it
    is fresh review work
- if a live sampler runs from a secondary worktree, bind that worktree `.local`
  back to the canonical repo `.local` before launch so the active queue stays
  in one SQLite surface
- secondary worktree live lanes should also source the canonical repo `.env`
  and canonical repo `.venv`
- `make start-runtime-check` should catch the two invalid day-open states:
  - a still-running sampler
  - a split worktree-local queue

## Rate And Credit Operator Guardrails

1. Treat throughput and spend as separate control planes:
  - rate limits (`RPM`, `TPM`, queue limits)
  - usage/billing (token burn, budget, credits)
2. Cost posture:
  - keep interactive checks synchronous
  - use short judged live batches by default
  - only use extended live runs as explicit batch work
3. Watch dashboards as part of normal operation:
  - `make open-limits`
  - `make open-usage`
  - `make open-billing`
  - or one-shot: `make open-cost-console`
4. Live API rule:
  - keep the token monitoring dashboard open or immediately reachable during live eval work
  - recheck it before widening a batch or starting an extended run
5. Efficiency defaults:
  - keep `n=1` and structured output surfaces
  - keep the live eval lens narrow before widening
  - keep retry/backoff behaviour enabled in the live SDK path

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
- `make eval-tone-sample EVAL_LIMIT=6`
- `make eval-tone-judge OUTPUT_ID=17922 VERDICT=pass NOTE='pick-aware playful confident coherent imaginative'`
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

Use `make end` as the canonical closeout command.

It runs:

- `scripts/end_of_day_routine.sh`
- `make decaffeinate`
- `make session-status`

The closeout routine now also includes a hard runtime completion gate:

- `make end-runtime-check`

That gate fails if any of these are still open:

- a live sampler process
- route-pending live rows
- tone-pending live rows
- pending `RETAIN / EVICT` work on failed tone rows
- a secondary worktree using its own unsymlinked `.local` queue

Use `make end-preflight` only when you want the validation path without the
final git closeout.

`make start` now also includes a hard start-of-day runtime gate:

- `make start-runtime-check`

That gate fails if any of these are still true before a new day opens:

- a live sampler process is still running
- a secondary worktree is pointed at its own unsymlinked `.local` queue

An interrupted but resumable live slice does not fail `make start`; it is
surfaced in `make session-status` so the next kernel can resume it on purpose.

## Long-Run Eval Loop

The eval lane is now real, but it is still intentionally small.

The intended posture is:

1. Hold the current baseline steady.
2. Record or generate within the active narrow surface.
3. Judge in sweeps.
4. Keep verdicts binary.
5. If a row fails, decide whether that failure should be retained in the active
  lane or evicted through an upstream correction.
6. Let retained failure clusters earn the next lens or intervention.
7. Rerun after evictions instead of leaving known-bad seams in the same queue.

## Layered Eval Lenses

Current day-zero posture:

- keep the top-level verdict binary
- keep failure disposition explicit after `fail`:
  - `retain`
  - `evict`
- keep one eval focus active at a time
- start with the round contract before broader fit judgments

The storage shape now exists for the top-level verdict. Additional lens names
and sidecar judgment tables are still intentionally pending beyond `Research Beta 1.0`.

`RETAIN / EVICT` is a method rule, not a third stored verdict state.

## Command Ownership

- Human lead owns objective, scope, acceptance, and theory.
- Engineer owns implementation, validation, and repo hygiene.
- Keep bare `scorey` as the app path.
- Keep explicit subcommands as the operator path.
