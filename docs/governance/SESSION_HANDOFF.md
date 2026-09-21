# Session Handoff

Last updated: 2026-09-20

## Start Here

Read `README.md`, `docs/governance/CHARTER.md`, this file,
`docs/governance/DECISIONS.md`, `docs/runtime/ARCHITECTURE.md`, and
`docs/runtime/RUNBOOK.md`. Confirm the checkout and branch, then run:

```sh
make doctor-env
make start-runtime-check
make session-status
```

The Beta 1 local restart is complete. The next gate has not started. Current
discussion is shaping a coherent-absurdity research arc from the prompt and
model experiments; its Scorey rubric and beta identifier remain open.

## Current Snapshot

Scorey remains a local CLI research instrument for one unfair rock, paper,
scissors round. Runtime owns routing and composition; the model supplies only
`winning_state`, `worse_state`, and `scoreboard_claim`. Route validity remains
the first gate, and the closed Beta 1–8 surfaces remain historical baselines.

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

Verification: `make check` passed 120 tests; package build, docs lint, and path
checks passed. Six local previews all selected `pair-awareness` and
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

The human identified coherent absurdity as a new research arc, using the
magic-paper/scissors-to-frog response as useful signal. The exact Scorey
criteria, gate placement, and beta identifier still need shaping. The primary
recommends reviewing the base prompt, matchup guidance, and retrieved
principles together: the current exact-object-class instruction is in tension
with that transformation. This recommendation has not changed the prompt.

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
user-selected session. The packet retains the proposed scope; the
coherent-absurdity rubric and next discussion above remain open.

## Method: Restart From Beta 1

[D-039](DECISIONS.md#d-039-restart-changed-model-measurement-at-beta-1) records
the human-led decision to follow the original gate sequence after the model
change. Start with [Beta 1](../research/010_B-PICK_ROUTING.md): picks only, in
Scorey/user order, all six allowed pairs, with full six-pair coverage. The
current primary user delegation permits Codex to judge current runs in real
time; the human lead still owns scope, criteria, meaning-level judgement, and
go/no-go.

Follow the documented method exactly: tie procedure and criteria to source, with
no assumptions or inferences. Keep missing or ambiguous method details
unresolved until the human lead clarifies them before dependent work. This
applies to the primary, documentation, and readers.

Before generation, record the source revision, prompt, model and reasoning
settings, captured uncommitted patch, source mode, run scope, generation
command, and intended pair cycle. Historically, Beta 1 established the
deterministic six-pair route baseline; Beta 2 then bridged to a 395-row live
queue. Those counts are historical evidence, not new minimums. For the
long-run condition, synchronous grouped runs exist, but no OpenAI Batch API
submit/import adapter was found in the inspected path. Honor the Polinko
batch-call intent and consult
`docs/peanut/research/2026-09-19-model-experiments/usage-and-batching.md`.
Record the selected transport, run size, and budget before generation.

Use the Beta 1 route computation, then persist individual route verdicts for
the exact output-ID range and per-pair counts. The `research-beta1` reporting
path computes and prints recent results, but does not itself persist those
verdicts, and its initialization path may migrate the schema; treat it as
write-capable. Record PASS/FAIL and pending state before advancing.

Advance only in order: Beta 2 object lanes; Beta 3/4 positive tone with
`retain`/`evict`; then Beta 5 pulse, Beta 6 scoreboard, Beta 7 prose, and Beta
8 menace, each using its own judged object and close condition. Closeout is
not a measured pass, and archived rows remain distinct from PASS. Preserve
Beta 4 de-anchoring: findings do not become generator phrase examples, and
the restart does not restore historical phrase banks. `pre-Beta 9.0` remains a
staged historical comparison, not an immediate menace command.

The source-linked memory path does not change this order. It remains a separate
named generation condition with the current base prompt and route gates intact;
receipts stay evidence metadata beside eval rows rather than new verdict fields.
Its behavioral efficacy still needs measurement under the existing gates, and
activation does not advance a beta.

## Workflow and Closeout

Companion task: **Scorey documentation**,
`01a0bb5c-6c52-7301-99e7-82d3364f6fd5`, using this checkout. The primary owns
generation, live state, integration, verification, and Git; documentation
delegates edit only the assigned files.

Use `make end-preflight` for branch validation. Follow the protected PR flow,
then finish with `make end` on clean synced `main`. The
[runbook](../runtime/RUNBOOK.md) owns the individual checks.

The [session closeout receipt](../peanut/research/2026-09-20-session-closeout/closeout.json)
records final validation and Git state. Closeout also preserved eleven original
path-bearing logs/records in a verified archive before making portable working
copies; future retrieval receipts use repository-relative paths. The
[portability receipt](../peanut/research/2026-09-20-session-closeout/path-portability.json)
records original and working-copy hashes. Responses and verdicts are unchanged.
