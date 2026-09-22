# Session Handoff

Last updated: 2026-09-21

## Start Here

Read `README.md`, `docs/governance/CHARTER.md`, this file,
`docs/governance/DECISIONS.md`, `docs/runtime/ARCHITECTURE.md`, and
`docs/runtime/RUNBOOK.md`. Confirm the checkout and branch, then run:

```sh
make doctor-env
make start-runtime-check
make session-status
```

Generation and method implementation are paused. The human directed restoration
of the established prompt, followed by a Polinko method report and a stop.
Restoration is complete under D-045. The report remains incomplete as a trace
of the golden-prompt and smoke-test protocol; tracing context plumbing alone
did not answer the research question. Existing changes are grouped into generation
evidence, attributed review, and restoration/alignment records. No later
historical gate has been opened.

## Current Snapshot

Scorey remains a local CLI research instrument for one unfair rock, paper,
scissors round. Runtime owns routing and composition; the model supplies only
`winning_state`, `worse_state`, and `scoreboard_claim`. Route validity remains
the first gate, and the closed Beta 1–8 surfaces remain historical baselines.

The current prompt version is `restored-321d970`. Instructions and all six
matchup prompts, with and without retrieved context, match the previous
`321d970` baseline exactly. The rejected `coherent-absurdity-1` condition remains
frozen in the original smoke evidence. Model settings, fields, composer, and
scoring are unchanged. The high-signal user/assistant golden pairs requested
by the human have not been implemented.

The human reaffirmed original scoring: retain the app's score progression and
`me: [score], you: [scoreboard_claim]`. Platform scoring is outside this
adaptation; smoke cases start at 1 because each is an independent first round.

| Surface | Current state |
| --- | --- |
| Shared agent contract | `build_live_agent` in `src/scorey/agent.py` serves app and smoke |
| Experimental inputs | `src/scorey/data/golden_cases.json`: six reverse/same-pick matchups at score 1; no assistant reference answers |
| Preparation | Tooling retained; new preparation paused pending alignment |
| Execution | Tooling retained; new generation paused pending alignment |
| Evidence | Run folders preserve requests, raw responses, receipts, and mechanical results; human review is recorded separately |
| Review import | Dataset `20260921T165455028594Z`: 6 cases, 6 assistant observation events, 6 human `FAIL` judgment events, 1 human observation event, 0 assistant judgment events |
| Verification | Restoration: `make check` passed 154 tests; all 40 protected evidence files match their hashes |
| Live smoke | `20260921T165455028594Z`: 6 mechanical passes, 0 failures; 6 human `FAIL` reviews recorded |

The [validation record](../research/300_VALIDATION-GOLDEN_SMOKE.md) links the
run condition and evidence. Six attempts used 3,330 tokens in 34.262 seconds
combined. Raw hashes verified; that smoke run left both databases unchanged.
The later review import added only the `review_*` tables and events described below.
The [execution pipeline](../diagrams/GOLDEN_SMOKE.md) records the verified
preparation, execution, and implemented research review flow.

The six existing smoke responses are the only review material in scope. The
implemented one-round reader is
`output/jupyter-notebook/scorey-coherent-absurdity-review.ipynb`. Its
top-to-bottom run against a temporary import of all six original receipts
passed 9 new UI tests and 10 historical tests; live Jupyter checks confirmed
Next/Previous navigation, wrapped content without horizontal overflow, and
separate assistant observations from saved human verdicts. No new model calls
and no generated reasons were added. Human review now contains six saved `FAIL`
judgements and one saved observation; six assistant observations remain
separate, with zero assistant judgements.
The active ignored working copy is open at round 6 with its saved FAIL in Jupyter:
`http://127.0.0.1:8893/lab/tree/output/jupyter-notebook/scorey-coherent-absurdity-review.local.ipynb`.
The tracked notebook has execution outputs cleared.

The canonical import is idempotent and byte-exact for source requests,
responses, and receipts. Criteria are frozen at SHA-256
`6fae6ca3b0f8cf6879d9ff55e0bf4819e7ec73e8f3b94fbdbabbe728fbb3cbea`, with the
local copy at `.local/reviews/20260921T165455028594Z/review-criteria.md`.
The initial setup verification receipt is
`.local/reviews/20260921T165455028594Z/verification.json`. SQLite
`quick_check` and `foreign_key_check` passed; all eight historical `eval_*`
table row counts and hashes, plus 48 protected source-file hashes, remain
unchanged. Existing review tooling and historical gate tables remain intact.
Import is review setup evidence, not a quality verdict or promotion.

The latest save-fix receipt is
`.local/reviews/20260921T165455028594Z/20260921T191226Z-save-fix/verification.json`.
It verifies preservation of the human reasons and phrases, with none generated.
The sync added exactly 7 human events, and the repeat sync added 0; existing
events and all historical eval tables remain unchanged.

The current local experimental configuration uses `gpt-5.6-luna`, medium reasoning,
detailed reasoning summary, low verbosity, and `top_p=0.98`. The September 20
experiment source condition was HEAD `e2db735` on
`codex/bigbrain/luna-model-settings`, with then-uncommitted
model-settings wiring in `.env.example`, `src/scorey/config.py`, and
`src/scorey/agent.py`. The model choice remains experimental; the ordinary
fallback is still `gpt-5-nano`.

Source-linked memory is enabled locally with the pinned index recorded in
`docs/peanut/research/2026-09-20-vector-store-audit/activation.json`.
Four exact pipeline principles and six pair queries use a separate SQLite
snapshot; each enabled live batch freezes its retrieval condition and records
source-linked receipts. The default for a fresh checkout remains off.

September 20 verification: `make check` passed 120 tests; package build, docs
lint, and path checks passed. Six local previews all selected `pair-awareness` and
`unfair-score-posture` (284 characters). One isolated live integration round
succeeded, stayed pending with zero judgements, and wrote no canonical eval
rows. These checks establish integration, not behavioral efficacy. Exact
settings, source snapshots, timings, and receipts are in the private audit
packet; [D-040](DECISIONS.md#d-040-opt-in-source-linked-principle-memory-stays-outside-the-core-contract)
and the [runbook](../runtime/RUNBOOK.md#source-linked-memory) own the contract
and commands.

The one-hour local Beta 1 restart finished at `2026-09-21T01:41:26Z`:
**3,568 pass, 0 fail, 0 pending**, output IDs `20500–24067`, all six pairs
covered. `docs/peanut/research/2026-09-20-beta1-local-restart/verification.json`
confirms one persisted judgement per row, gate agreement, SQLite health, and
unchanged prior evidence. Generation was deterministic local, with no API calls
or memory retrieval. No higher lens was measured and Beta 2 has not started.
The exact human `20449–20454` verdicts retain their source/hash attribution;
disputed `20443–20448` retains historical Codex labels, not accepted-baseline
status.

## Session Findings and Next Conversation

Prompt and model experiments were the main session work. Their settings,
prompts, observed responses, and human readings are linked in the concise
[session findings](../peanut/research/2026-09-20-session-findings.md).
Playground explorations and app eval conditions retain separate provenance.

The engineering prompt rewrite exceeded the intended adjustment to stable
Scorey. All six smoke cases passed mechanics and received human `FAIL`
judgments about voice and behaviour. One human observation, six assistant
observations, and zero assistant judgments remain recorded separately.
The [paused boundary](../research/420_PB-COHERENT_ABSURDITY.md) and its frozen
`coherent-absurdity-review-1` criteria preserve the experimental record.
The human's failures are not relabelled as another lens's verdicts.

Preserved human feedback includes the first reason, `this is not scorey's
voice`; the observation phrase, `scorey's 8 years old. the behaviour has drifted
from his established model`; and the Round 5 note, `\nwhat are your golden
prompts?\nwe need to align before you adjust agents.py`. The next step is to
trace Polinko's established golden-prompt and smoke-test method through a
concrete case, then align its application to Scorey before any adjustment.
The [primary report](../peanut/research/2026-09-21-golden-smoke-audit/polinko-foundation-report.md)
contains verified partial findings, not a completed method audit.

Scorey is an existing research project with a protocol. Read authoritative
sources or ask the human when understanding is incomplete. Do not fill gaps
with invented method or treat an unverified interpretation as a finding.

Supporting context: three readers covered 57 curated records plus two archive
guides. The primary read all reports and checked passages in 20 source files;
the [reading packet](../peanut/research/2026-09-20-context-reading/README.md)
records coverage and findings. Git history also verified the supplied napkin
word bank and later cleanup already recorded in D-016/D-017. The user named
SCO-1 as the rollout source and asked to leave that rollout unopened.

The [Huey–Scorey documentation audit](../peanut/research/2026-09-20-huey-doc-alignment/README.md)
is complete: three readers fully read all 69 tracked Markdown documents
(41 Huey, 28 Scorey), and the primary personally read every report and checked
supporting passages. The audit's findings remain proposed alignment; it changed
no source documents. The user pinned the alignment edits for a later
user-selected session. That broader alignment remains deferred; golden-smoke
adaptation is now paused under D-045.

## Historical Restart and Evidence Boundaries

[D-039](DECISIONS.md#d-039-restart-changed-model-measurement-at-beta-1) records
the September 20 model restart. Its [Beta 1](../research/010_B-PICK_ROUTING.md)
route measurement is complete; the original Beta 2–8 sequence and earlier
staged 410 positive-runtime contract remain documented comparison surfaces. The
paused 420 inquiry preserves the proposed next boundary; its
sidecar comparison does not advance the D-039 gate order, relabel historical
rows, or establish retrieval efficacy.

Continue to record source revision and patch, full instructions, requested
settings, retrieval condition, transport, run bounds, exact artifacts, and
attributed judgments. Human ownership of scope, criteria, meaning-level
judgment, and go/no-go remains; the primary's delegated judgments retain their
attribution. Missing criteria stay unresolved before dependent work.

Any resumed evaluation follows the established protocol and required D-039
gates. The engineering proposal in D-042 is paused. Historical procedure remains in
[the research map](../research/README.md).
`research-beta1` reports route results but does not persist judgments, and its
initialization may migrate the schema. Smoke uses an isolated evidence folder
instead. PASS/FAIL, failure disposition, archive, and mechanical completion
retain separate meanings. Findings and reference responses do not become
generator phrase banks.

Long-run Batch API adaptation remains separate from the six-call smoke; the
[batching note](../peanut/research/2026-09-19-model-experiments/usage-and-batching.md)
preserves that intent and the inspected transport gap.

## Continuing Task Registry

SCO-2 (`01a0b6ed-3be0-7942-9d29-8103fe7d1b2f`) remains the primary director:
it dispatches source packets, owns generation, live state, integration,
verification, and Git, and personally reads returns.

| Continuing task | Sole write ownership | Return to primary |
| --- | --- | --- |
| Scorey documentation / alignment `01a0bb5c-6c52-7301-99e7-82d3364f6fd5` | `README.md`, `docs/governance/CHARTER.md`, `docs/governance/SESSION_HANDOFF.md`, `docs/diagrams/COLLABORATION.md` | Alignment edits, concise synthesis, and cross-owner gaps |
| Scorey runtime records `01a0c4f0-fc8c-7c62-a742-19ebbe9a93d0` | `DECISIONS.md`, `ARCHITECTURE.md`, `RUNBOOK.md`, `START_END_REFERENCE.md` | Runtime record edits and source-backed gaps |
| Scorey research records `01a0c4f1-3173-7f52-b50f-7f0b004f667e` | Assigned tracked research and current private research summaries | Research records and unresolved evidence boundaries |
| Scorey transcript keeper `01a0c4f1-803f-7622-b3c4-0c1f1320e5a1` | Curated excerpts under `docs/peanut/transcripts/` | Exact sourced captures, separated interpretation, and gaps |

Research records include research diagrams; runtime records include execution
pipelines. Owners keep these current with their records and flag cross-owner
changes for alignment. Captures retain source diagrams and provenance;
new explanatory drawings and proposed flows remain clearly labelled.

These tasks receive only dispatched context; later parent messages do not arrive
automatically, and no task continuously monitors the conversation. Supporting
bounded subagents inherit their delegating task's file boundary. Transcript
capture starts when a supplied or directly inspected exchange contains a
meaningful discovery, correction, or rationale. All returns remain subject to
primary review and integration. Transcript format follows the [local transcript
README](../peanut/transcripts/README.md), which routes to the canonical standard;
this task does not invent a new format.

## Workflow and Closeout

The primary owns generation, live state, integration, verification, and Git;
each documentation task edits only its assigned files in this checkout.

Use local checkpoints during work and group commits around coherent changes.
Initial setup checkpoint: `.local/checkpoints/20260921T185820Z/`.
Latest review correction checkpoint: `.local/checkpoints/20260921T191756Z-review-save-fix/`.
Restoration receipt: `.local/checkpoints/20260921T211826Z-before-prompt-restore/receipt.json`.
Pre-commit grouping checkpoint: `.local/checkpoints/20260921T225440Z-before-grouped-commits/`.
Checkpoints preserve the current code/docs
and selected private notes; their manifests list copies, hashes, scope, and
references to existing smoke evidence and databases. Checkpoints follow the
[runbook](../runtime/RUNBOOK.md#local-checkpoints-and-commit-cadence).

Use `make end-preflight` for branch validation. Follow the protected PR flow,
then finish with `make end` on clean synced `main`. The
[runbook](../runtime/RUNBOOK.md) owns the individual checks.

The [September 21 closeout receipt](../peanut/research/2026-09-21-session-closeout/closeout.json)
records validation and Git status. Its
[portability receipt](../peanut/research/2026-09-21-session-closeout/path-portability.json)
preserves exact originals and hashes for seven logs before making portable
reading copies. Recovery checkpoints retain their original manifests and link
to their archived log originals. Responses, verdicts, and databases are unchanged.
The [September 20 receipt](../peanut/research/2026-09-20-session-closeout/closeout.json)
remains the previous closeout record.
