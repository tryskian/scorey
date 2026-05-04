# Runbook

This is the operator guide for local setup, procedure, validation, and rebuild
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
3. Treat `archive/` as reference only.
4. State the active kernel before editing tracked files.

## Everyday Commands

| Task | Command |
| --- | --- |
| show the repo file tree | `find . -maxdepth 2 -type f | sort` |
| show tracked docs | `find docs -maxdepth 3 -type f | sort` |
| inspect archived reference docs | `find archive -maxdepth 3 -type f | sort` |
| search the current docs surface | `rg -n "<term>" README.md docs` |

The runtime command surface is intentionally pending. Bare `scorey` will be the
default user path once the app loop exists.

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

No live or local runtime commands are tracked yet.

When the runtime lands:

- keep bare `scorey` as the app path
- keep explicit subcommands as the operator path
- keep the operator path separate from the app loop

## Eval Commands

No eval command surface is tracked yet.

When the eval lane lands, record the commands here and keep them local-first,
binary, and small.

## Validation

For the current day-zero docs state:

- read back the changed docs
- keep claims aligned with the actual tree
- keep `archive/` clearly marked as reference-only

When git and runtime tooling exist, expand this section with the smallest check
set that matches each kind of change.

## Long-Run Eval Loop

Pending until the runtime and eval lanes exist.

The intended posture is:

1. Hold the current baseline steady.
2. Generate or sample within the active narrow surface.
3. Judge in sweeps.
4. Keep verdicts binary.
5. Let repeated failure clusters earn interventions.

## Layered Eval Lenses

Current day-zero posture:

- keep the top-level verdict binary
- keep one eval focus active at a time
- start with the round contract before broader product taste

The exact lens names and storage shape are intentionally pending.

## Command Ownership

- Human lead owns objective, scope, acceptance, and theory.
- Engineer owns implementation, validation, and repo hygiene.
- Keep bare `scorey` as the intended app path.
- Keep explicit subcommands as the future operator path.
