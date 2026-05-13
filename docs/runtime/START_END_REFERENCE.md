# Start / End Reference

This is the compact operator sheet for the canonical day-open/day-close
commands.

## Start

Command:

```bash
make start
```

Sequence:

1. Print workspace context:
  - repo root
  - active branch
  - `git status --short --branch`
2. Run the startup safety path:
  - `make doctor-env`
  - `make start-runtime-check`
  - `make caffeinate`
  - `make caffeinate-status`
  - `make session-status`
3. Stop before repo action:
  - print the canonical docs to read:
    - `README.md`
    - `docs/governance/CHARTER.md`
    - `docs/governance/DECISIONS.md`
    - `docs/runtime/RUNBOOK.md`
    - `docs/runtime/ARCHITECTURE.md`
    - `docs/governance/SESSION_HANDOFF.md`
  - give the startup read
  - name exactly one active kernel
  - do not branch, search, or edit until that is stated

Source of truth:

- [scripts/start_of_day_routine.sh](../../scripts/start_of_day_routine.sh)

## End

Command:

```bash
make end
```

Sequence:

1. Run the closeout safety path:
  - docs truth check
  - environment check
  - full repo validation
  - runtime completion gate
  - session snapshot
  - git closeout check
2. Release the managed wake lock:
  - `make decaffeinate`
3. Print the final repo state:
  - `make session-status`

Source of truth:

- [scripts/end_of_day_routine.sh](../../scripts/end_of_day_routine.sh)
- [Makefile](../../Makefile)
