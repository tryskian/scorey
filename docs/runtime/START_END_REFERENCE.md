<!-- @format -->

# Start / End Reference

This is the compact operator sheet for the canonical day-open/day-close
commands.

## Start

Command:

```bash
make start
```

Sequence:

1. Print the canonical docs to read:
   - `README.md`
   - `docs/governance/CHARTER.md`
   - `docs/governance/DECISIONS.md`
   - `docs/runtime/RUNBOOK.md`
   - `docs/runtime/ARCHITECTURE.md`
   - `docs/governance/SESSION_HANDOFF.md`
2. Print workspace context:
   - repo root
   - active branch
   - `git status --short --branch`
3. Run the startup safety path:
   - `make doctor-env`
   - `make caffeinate`
   - `make caffeinate-status`
   - `make session-status`

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
   - session snapshot
   - git closeout check
2. Final shutdown command:
   - `make end-stop`

`make end-stop` then runs:

- `make decaffeinate-all`
- `make session-status`

Source of truth:

- [scripts/end_of_day_routine.sh](../../scripts/end_of_day_routine.sh)
- [Makefile](../../Makefile)
