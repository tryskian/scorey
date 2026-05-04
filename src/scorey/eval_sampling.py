from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from scorey.config import USER_PICKS
from scorey.eval_db import record_round_state
from scorey.eval_gates import evaluate_beta_1
from scorey.pipeline import build_local_round_state, compose_round


@dataclass(frozen=True)
class LocalSampleSummary:
    recorded: int
    first_output_id: int | None
    last_output_id: int | None
    beta_1_pass: int
    beta_1_fail: int
    elapsed_seconds: float


def sample_local_eval_outputs(
    *,
    count: int | None = None,
    duration_seconds: float | None = None,
    interval_seconds: float = 0.0,
    model: str = "local-fixture-batch",
    time_fn: Callable[[], float] = time.monotonic,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> LocalSampleSummary:
    if count is None and duration_seconds is None:
        raise ValueError("Provide count or duration_seconds.")
    if count is not None and count < 1:
        raise ValueError("Count must be at least 1.")
    if duration_seconds is not None and duration_seconds <= 0:
        raise ValueError("Duration must be greater than 0.")
    if interval_seconds < 0:
        raise ValueError("Interval must be at least 0.")

    start = time_fn()
    deadline = None if duration_seconds is None else start + duration_seconds
    output_ids: list[int] = []
    beta_1_pass = 0
    beta_1_fail = 0
    index = 0

    while True:
        if count is not None and index >= count:
            break
        if deadline is not None and time_fn() >= deadline:
            break

        user_pick = USER_PICKS[index % len(USER_PICKS)]
        round_state = build_local_round_state(user_pick, scorey_score=index + 1)
        round_text = compose_round(round_state)
        output_id = record_round_state(
            None,
            round_state,
            round_text,
            source_mode="local",
            model=model,
        )
        output_ids.append(output_id)

        gate_result = evaluate_beta_1(
            user_pick=round_state.user_pick,
            scorey_pick=round_state.scorey_pick,
        )
        if gate_result.verdict == "pass":
            beta_1_pass += 1
        else:
            beta_1_fail += 1

        index += 1

        if interval_seconds <= 0:
            continue

        if deadline is None:
            if count is None or index < count:
                sleep_fn(interval_seconds)
            continue

        remaining = deadline - time_fn()
        if remaining <= 0:
            break
        sleep_fn(min(interval_seconds, remaining))

    elapsed_seconds = time_fn() - start
    return LocalSampleSummary(
        recorded=index,
        first_output_id=output_ids[0] if output_ids else None,
        last_output_id=output_ids[-1] if output_ids else None,
        beta_1_pass=beta_1_pass,
        beta_1_fail=beta_1_fail,
        elapsed_seconds=elapsed_seconds,
    )
