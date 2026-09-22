# Validation: Golden Smoke

| Field | Value |
| --- | --- |
| Code | `300_VALIDATION-GOLDEN_SMOKE` |
| Category | `validation` |
| Status | `snapshot` |
| Last evidence | `2026-09-21` |
| Owns | Integrity of the first six-case coherent-absurdity smoke run. |

## Question

Can six fixed inputs produce independently recorded app rounds while preserving
the generation condition and separating mechanics from quality?

## Run

Run `20260921T165455028594Z` used `make smoke-prepare`, then
`make smoke-run SMOKE_RUN=.local/smoke/20260921T165455028594Z`.
Source: `321d970` plus the captured patch and source snapshots.

| Check | Result | Read |
| --- | --- | --- |
| Condition | `coherent-absurdity-1`, `gpt-5.6-luna` | Medium reasoning, detailed summary, low verbosity, `top_p=0.98`, pinned principle memory |
| Coverage | `6/6` | Three cross-object reverse pairs and three same-pick pairs; each independent first round at score 1 |
| Mechanical checks | `6 pass / 0 fail` | Completed responses, structured fields, valid routes and scoreboard restriction |
| Recording | `6/6` | Request/response hashes verified; original fields and composed rounds preserved |
| Usage | `34.262 s`, `3,330 tokens` | Sum of attempt durations; recorded token usage |
| Protected stores | unchanged | Eval and memory database hashes match before/after |
| Offline validation | `131 tests pass` | Format, lint, type checks and package build passed |
| Quality judgments | pending | Mechanical passes supply no semantic verdict |

The [private run note](../peanut/research/2026-09-21-golden-smoke-audit/first-smoke.md)
links exact requests, raw responses, conditions and verification.

The [staged Pre-Beta 9.0 boundary](./420_PB-COHERENT_ABSURDITY.md) owns the
pending relational review. This snapshot remains mechanical smoke integrity
only; it does not add quality judgments or an active database gate.

D-043 defines the additive review surface for that later review: imported
`review_datasets`, `review_cases`, and `review_events` in the existing eval
database, with the reader's source-bound `.notes.json` kept separate until an
explicit importer syncs events. The staged reader preserves the full round and
the existing measures. The initial canonical import contained six cases, six
Codex-primary observation events, zero quality judgments, and six quality-
pending cases. The one-round notebook executed successfully in live Jupyter;
Next/Previous, wrapped panel content, and separate observations versus pending
human verdicts were verified. Idempotent run re-import and notes import passed.
The eight historical `eval_*` table counts/hashes and 48 protected original
files remain unchanged; SQLite quick-check and foreign-key checks pass. The
criteria copy is [frozen here](../../.local/reviews/20260921T165455028594Z/review-criteria.md)
with SHA-256 `6fae6ca3b0f8cf6879d9ff55e0bf4819e7ec73e8f3b94fbdbabbe728fbb3cbea`.
The [review verification receipt](../../.local/reviews/20260921T165455028594Z/verification.json)
is the canonical detailed record. Review tooling checks reported `149` tests
passing; that receipt remains the initial import snapshot.

## Follow-up review status

The first save attempt exposed a review-control problem: per-round reasons were
mandatory even when the same issue applied across the run. D-044 records the
correction to make reasons optional; live drafts were preserved and backed up.
The follow-up save recorded six exact human `FAIL` judgments and one human
observation. Six Codex-primary observations remain present; there are no
assistant judgments. The [save-fix receipt](../../.local/reviews/20260921T165455028594Z/20260921T191226Z-save-fix/verification.json)
verifies the saved events, `152` tests passing with no warnings, no model
calls, no generation or prompt changes, and `beta_promotion` false. The
canonical SQLite sync added exactly seven human events; repeat sync added zero.

The shared human rejection is behavioral and attributed: “this is not scorey's
voice” and “scorey's 8 years old. the behaviour has drifted from his
established model”. The round-five note asks, “what are your golden prompts?
we need to align before you adjust agents.py”. These saved events are not an
inferred coherent-absurdity relational adjudication and do not close any
historical gate. The original smoke and initial verification receipt remain
frozen.

## Decision

| Decision | Reason |
| --- | --- |
| `pass` for smoke integrity | All six independent attempts were preserved and passed mechanical checks. |
| `hold` for further work | Six human failures led to restoration; protocol alignment is required under D-045. |

## Restoration

D-045 restores the instructions and all six matchup prompts, with and without
context, exactly from `321d970`. All 154 offline tests pass. The original smoke
condition, databases, and review notes match their protected hashes; no model
calls were made. The [restoration receipt](../../.local/checkpoints/20260921T211826Z-before-prompt-restore/receipt.json)
records the verification. New generation and method implementation are paused.

## Residual Risk

- One output per input establishes no quality rate or retrieval efficacy.
- Smoke uses frozen retrieval, zero retries and a 60-second deadline; the app
  retains its SDK transport and retry defaults.

## Next Move

Complete the source-backed method report and align with the human lead before
any further adaptation. Preserve the restored baseline and six human failures.
The current fixture records matchup coverage; it does not yet implement the
requested high-signal user/assistant pairs.
