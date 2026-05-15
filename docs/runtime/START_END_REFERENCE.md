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
  - print the canonical rehydrate prompt
  - the prompt tells the agent to:
    - read `README.md`, `CHARTER`, `DECISIONS`, `RUNBOOK`, `ARCHITECTURE`, and `SESSION_HANDOFF`
    - return 5 bullets covering current state, risks, and next kernel
    - confirm repo path, host vs devcontainer mode, active branch, and whether the thread is on clean `main` or a feature branch
    - apply the no-guessing controls
    - run one active kernel at a time
    - execute the `Next Kernel` from `SESSION_HANDOFF` with full validation

Source of truth:

- [scripts/start_of_day_routine.sh](../../scripts/start_of_day_routine.sh)

Wake-lock rule:

- `make caffeinate` records only this repo's managed PID
- unmanaged `caffeinate` processes are reported but never adopted or stopped

## End

Command:

```bash
make end
```

Sequence:

1. Run the closeout safety path:
  - docs truth check
  - environment check
  - tracked path leak check
  - local path leak audit
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
