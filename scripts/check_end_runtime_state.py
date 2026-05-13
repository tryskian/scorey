from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scorey.runtime_state import collect_runtime_state, format_runtime_state_lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report Scorey's live runtime state and optionally fail when the "
            "active batch or review slice is still open."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--start-strict",
        action="store_true",
        help=(
            "Fail if a start-of-day check finds a still-running live sampler "
            "or a split worktree-local queue."
        ),
    )
    group.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Fail if a live sampler is still running or the active live "
            "slice is not closed."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = collect_runtime_state(repo_root=Path.cwd())

    for line in format_runtime_state_lines(state):
        print(line)

    failures: list[str] = []
    if state.split_db_risk:
        failures.append(
            "secondary worktree is using a worktree-local .local instead of "
            "the canonical repo .local"
        )
    if state.live_sampler_commands:
        failures.append("live sampler process is still running")
    if state.active_route_pending > 0:
        failures.append(
            "active slice still has "
            f"{state.active_route_pending} route-pending live rows"
        )
    if state.active_tone_pending > 0:
        failures.append(
            f"active slice still has {state.active_tone_pending} tone-pending live rows"
        )
    if state.active_disposition_pending > 0:
        failures.append(
            "active slice still has "
            f"{state.active_disposition_pending} pending tone failure dispositions"
        )

    if args.start_strict:
        start_failures: list[str] = []
        if state.split_db_risk:
            start_failures.append(
                "secondary worktree is using a worktree-local .local queue"
            )
        if state.live_sampler_commands:
            start_failures.append("live sampler process is still running")
        if start_failures:
            print("start-runtime-check: FAIL", file=sys.stderr)
            for failure in start_failures:
                print(f"- {failure}", file=sys.stderr)
            print(
                "Stop the sampler or rebind the worktree queue before "
                "starting a new session.",
                file=sys.stderr,
            )
            return 1
        print("start-runtime-check: PASS (no live sampler and no split queue risk)")
        return 0

    if args.strict and failures:
        print("end-runtime-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        print(
            "Finish or archive the active live slice, stop any live sampler, "
            "and rerun make end.",
            file=sys.stderr,
        )
        return 1

    if args.strict:
        print(
            "end-runtime-check: PASS (no active sampler and no open live review slice)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
