# Session Handoff

Last updated: 2026-09-19

## Start Here

1. Read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Confirm execution context:
   - canonical repo root or dedicated worktree
   - active branch from `git branch --show-current`
3. Return the startup breakdown:
   - current state
   - risks
   - next kernel
   - repo or worktree context
   - active branch
4. Run session preflight:
   - `make doctor-env`
   - `make start-runtime-check`
   - `make session-status`

## Current Snapshot

Scorey is a small local CLI research instrument for one unfair rock, paper,
scissors round. `Research Beta 4.0` is closed as the abstract row-level
measurement baseline. `Research Beta 5.0` is closed as the fail-pressure pulse
baseline. `Research Beta 6.0` is closed as the scoreboard baseline.
`Research Beta 7.0` is closed as the broader prose baseline. `Research Beta 8.0`
is closed as the menace baseline. `pre-Beta 9.0` is the current staged runtime
instruction contract.

Mac-wide power control is external to this repository. The Coffee Codex plugin
owns the one shared keep-awake session for Polinko and the toys. Scorey's
startup, preflight, closeout, and session status leave it unchanged.

Stable repo shape:

- bare `scorey` opens the app loop
- the runtime keeps picks fixed to:
  - `rock`
  - `paper`
  - `scissors`
- the runtime owns routing and final round composition
- the live model owns only:
  - `winning_state`
  - `worse_state`
  - `scoreboard_claim`
- route stays the floor
- tone remains the first widened row-level lens
- failure handling stays explicit:
  - `retain`
  - `evict`
- current GitHub dependency queue:
  - `#94`: grouped GitHub Actions updates
  - `#100`: grouped Python dependency updates

Current runtime truth:

- `live_batch: closed`
- `batch_meta: missing`
- `route_pending=0`
- `tone_pending=0`
- `disposition_pending=0`
- live totals:
  - `2520` route pass
  - `0` fail
  - `0` pending
- tone totals:
  - `454` pass
  - `627` fail
  - `1439` archived
  - `0` pending
- disposition totals:
  - `72` retain
  - `196` evict
  - `359` archived
  - `0` pending

## Closed Evidence Surface

`Research Beta 5.0` pulse baseline:

- cross-object:
  - pulse `1`: `8 / 5 / 2`
  - pulse `3`: `9 / 6 / 0`
  - pulse `4`: `9 / 6 / 0`
- same-pick:
  - pulse `2`: `15 / 0 / 0`
  - pulse `5`: `15 / 0 / 0`

`Research Beta 6.0` scoreboard baseline:

- `20292-20306`: `15` pass / `0` fail
- `20307-20321`: `15` pass / `0` fail
- `20322-20336`: `15` pass / `0` fail
- `20337-20351`: `15` pass / `0` fail

`Research Beta 7.0` broader prose baseline:

- `20352-20366`: `9` pass / `6` fail
- `20367-20381`: `15` pass / `0` fail
- `20382-20396`: `9` pass / `6` fail

Stable contrast:

- cross-object prose reopens pressure at `9 / 6` and repeats there
- same-pick prose collapses at `15 / 0`
- newer bounded eval gates are performing cleanly across pulse, scoreboard,
  and prose closeout

## Active Kernel

Latest tracked maintenance slice: document the continuing documentation
task workflow in `D-037` and the charter.

- the human lead and primary engineer manage experiments together
- the primary engineer delegates supporting research, notes, diagrams, and
  document writing to a continuing task in the Scorey project, using the same
  local checkout
- assignments carry the relevant conversation, sources, scope, and result;
  the primary engineer reviews and integrates the returned work
- the primary engineer coordinates file ownership and shared-checkout Git
  operations; supporting work remains within the agreed active kernel
- the workflow is recorded; the companion task has not been created and has
  no task identifier yet
- all twelve `make end-preflight` steps passed, including documentation and
  path checks, all `91` tests, packaging, security, and strict runtime closure

September 19 exploratory evidence is retained in
`docs/peanut/research/2026-09-19-model-experiments/README.md`, with three source
references on settings, measurement, and usage/batching. Five runs produced
`20418-20442`: mini at `none` and `medium`, Luna at `medium` and `low`, then one
Luna round at `none`. The 25 rows have 25 route passes and 24 scoreboard passes
with one numeric-contradiction failure. All 25 composed scoreboard claims
exclude the word `you`; broader response observations remain separate from
the stored lens verdicts. The ranges are closed, with untouched tone archived.
These runs used process-local overrides; ordinary configuration still resolves
to `gpt-5-nano`. No lasting model choice or beta promotion has been made.

Previous closed maintenance slice: the scoreboard word restriction from
`D-036`, merged through PR `#109`.

- the only added rule is to keep the word `you` out of `scoreboard_claim`,
  since the runtime already supplies `you:`
- existing response styles remain available; the human lead clarified that
  no new grammar rule was needed
- `src/scorey/agent.py` states the restriction in one instruction
- Architecture and the staged pre-Beta 9.0 contract reflect this change
- composition, fragment cleanup, model settings, and workbench code are
  unchanged
- `make check` passed with `91` tests; documentation lint and both path
  audits passed
- `make start` passed in the canonical checkout: environment healthy, sampler
  off, and route, tone, and disposition queues clear
- all twelve `make end-preflight` steps passed, including packaging,
  installation, dependency security, and strict runtime checks
- runtime and evaluation readers confirmed that live play and the live
  sampler already use the updated agent instruction
- the subsequent September 19 exploratory rows exercise this instruction;
  their bounded findings are recorded above, without claiming general
  compliance or a controlled comparison with the earlier prompt

Previous closed maintenance slice: the after-pick dots loader from `D-035`
and the private reading packet's portable links, merged through PRs `#107`
and `#108`.

- the user confirms a pick, then both picks are visible
- the existing Braille-dot spinner runs while the ruling is generated
- the loader has no caption or narrated deliberation
- the ruling and score appear when generation finishes, without an added
  minimum wait
- the decision records the human lead's refinement and preserves the
  correction to the historical attribution
- a controlled rendering smoke verified both picks, the dots-only wait,
  the completed ruling and score, and stable scene height
- `make check` passed with `91` tests
- documentation lint, shell contracts, tracked-path checks, and dependency
  security checks passed
- packaging, editable installation/import, and the strict runtime-state
  check passed; no sampler or open live review slice was present
- the private re-entry packet now uses document-relative source links and
  repository-relative path references; both tracked and local path audits pass
- `make end-preflight` passed after the path cleanup
- the full `make end` then passed on clean synced `main` at `faee7b6`
- no live model request or new research evidence was generated for this change

The research carryover below remains outside this maintenance slice and
requires fresh alignment before a new research run.

Previous closed maintenance slice, retained as historical context:

- live CLI arrow navigation is restored without changing its intentional timing
- the repair lands through PR `#98`
- `up` and `down` are the only selection-moving keys
- `enter` confirms and `esc` exits
- selector input now reads terminal bytes directly instead of mixing buffered
  text reads with file-descriptor polling
- one terminal mode remains active across the selector interaction so rapid
  keypresses cannot fall into a canonical-mode gap
- the duplicate scene render after each arrow movement is removed
- `ESC_SEQUENCE_TIMEOUT_SECONDS` remains `0.03`
- validation completed:
  - focused `tests/test_main.py`: `38` pass with `4` arrow-sequence subtests
  - real pseudo-terminal smoke: rapid `down`, `up`, wrap-`up`, `enter`, and
    `esc` passed without echoed escape garbage
  - `make check`: `90` pass
  - full feature-branch `make end` validation passed through security and
    runner shutdown; only the expected clean-`main` gate remained
  - PR `#98` required checks passed

Research state underneath the maintenance slice:

`Research Beta 8.0` is now frozen on clean synced `main`.

What is live now:

- menace is a real bounded row-level lens on the full visible round
- the next tracked stage is `pre-Beta 9.0` positive runtime instruction
  contract
- `src/scorey/config.py` stays structural only
- `src/scorey/agent.py` owns the live runtime instruction shape
- new live evidence belongs above the rewritten prompt contract rather than
  inside Beta 8.0
- operator surface:
  - `eval-menace-sample`
  - `eval-menace-judge`
  - `eval-menace-archive`
  - `eval-menace-close`
- menace closeout settles untouched `tone`, `scoreboard`, and `prose` rows
  in-range
- `D-030` locks the row-level menace contract in the durable decisions ledger
- `D-031` starts `Research Beta 8.0` on menace judgement
- `D-032` freezes Beta 8.0 below a staged positive runtime instruction
  contract
- frozen bounded menace evidence:
  - `20410-20417`: `6 / 2`
  - `20397-20403`: `4 / 3`
  - `20404-20409`: `4 / 2`
  - `20307-20321`: `11 / 4`
  - `20382-20396`: `9 / 6`
  - `20352-20366`: `11 / 4`
  - `20367-20381`: `15 / 0`

Research templates and private staging surface:

- `docs/runtime/templates/README.md`
- `docs/runtime/templates/legend.md`
- `docs/runtime/templates/boundary.md`
- `docs/runtime/templates/lane.md`
- `docs/runtime/templates/case.md`
- `docs/runtime/templates/validation.md`
- `docs/runtime/templates/hypothesis.md`
- `docs/runtime/templates/backlog.md`
- `docs/peanut/research/chart-language.md`

Current staged research lane:

- `pre-Beta 9.0`
- `positive runtime instruction contract`
- frozen baseline:
  - `Research Beta 8.0` menace judgement
- active family for the first fresh comparison slice:
  - `cross-object coherence drift`
- active note:
  - `docs/research/410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md`

## Next Session

Start with the September 19 experiment index above and confirm live state with
`make start`. The documentation workflow is agreed; create the companion
project task when asked and record its identifier here. Give it the existing
notes and documentation standards as context, then send bounded assignments
while the human lead and primary engineer continue the experiments.

The next experiment and any lasting model or effort choice still need to be
selected with the human lead. Preserve the five exploratory run receipts and
keep the frozen beta baselines separate.

### Procedure for a Future Scoreboard Restriction Evaluation

The procedure below was prepared before the September 19 trials. It remains
available for a separately selected instruction comparison; it does not
describe those model/effort experiments as a controlled prompt comparison.

1. Run `make start` and record the source commit, prompt hash, configured
   model, chosen eval lens, bounded count, pair family, and generation command
   before generating new rows.
   The human lead still owns the sample scope and acceptance criteria.
2. Use the existing `make eval-sample-live` command with the agreed count and
   pairs, in Scorey-pick/user-pick order. Record its returned first and last
   output IDs. The sampler and live play already use the instruction in
   `src/scorey/agent.py`.
3. Record route verdicts for the new rows before widened-lens review. The
   sampler's printed route-gate totals do not persist those verdicts, and
   `make eval-beta1` is also a read-only report.
4. Review the whole recorded range under the selected lens. In particular,
   `make eval-scoreboard-sample` returns the newest pending row per model/pair;
   it is neither a complete batch listing nor a range filter. Keep each
   reviewed output ID inside the new run's bounds. Check the generated
   scoreboard value for `you`, not the fixed labels elsewhere in the round.
5. Preserve any generated `you` in the evidence so instruction failures stay
   visible. The prompt change adds no output filtering, new grammar rule, or
   fixed response list. Keep model and reasoning settings unchanged when
   assessing this instruction change; the latency hypothesis is separate.
6. Close the selected bounded lens using its existing closeout command after
   every row has been addressed. This preparation creates no new live rows
   and does not promote a research beta.

## Research Carryover

1. Keep `Beta 5.0`, `Beta 6.0`, `Beta 7.0`, and `Beta 8.0` frozen as the
   closed evidence ladder below the staged runtime contract.
2. The agent-local positive runtime instruction contract is already
   implemented. Identify the exact revision, including `D-036`, when cutting
   fresh live evidence.
3. Same-pick menace is confirmed collapsed at `15 / 0`, while cross-object has
   now shown:
   - one opening `9 / 6`
   - two hardened `11 / 4` reads
   - one larger fresh probe at `6 / 2` over `8` rows
   - one compact probe at `4 / 3` over `7` rows
   - one compact repeat at `4 / 2` over `6` rows
4. Open at least one fresh cross-object menace repeat from new live rows after
   the rewritten contract lands.
5. Promote a new beta only if the post-rewrite evidence changes meaning
   cleanly against the frozen Beta 8.0 baseline.

## Risks

- low runtime risk: the queue is fully closed and there is no active sampler
- dependency queue is separate from this kernel: open Dependabot PRs `#94` and
  `#100` remain untouched

## Guardrails

- keep the repo small and local
- keep the runtime CLI-first
- keep picks fixed to `rock`, `paper`, and `scissors`
- keep one active kernel at a time
- keep route validity as the first gate
- keep bounded closeout returning to `0` pending
- keep `docs/peanut/` private unless the boundary is widened explicitly
- keep tracked docs truthful to the current repo surface

## Close A Session

1. Run:
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
2. Print the repository and runtime snapshot:
   - `make session-status`
3. Finish on clean synced `main`:
   - `make end-git-check`
