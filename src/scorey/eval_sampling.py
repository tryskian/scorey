from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from scorey.config import USER_PICKS, local_scorey_pick_for, normalise_pick
from scorey.eval_db import record_round_state
from scorey.eval_gates import (
    evaluate_research_beta_1,
    research_beta_1_pass_pairs,
)
from scorey.pipeline import build_local_round_state_for_pair, compose_round

LOCAL_SAMPLE_PATTERNS: tuple[str, ...] = ("baseline", "research-beta-1-coverage")


@dataclass(frozen=True)
class LocalSampleSummary:
    recorded: int
    first_output_id: int | None
    last_output_id: int | None
    research_beta_1_pass: int
    research_beta_1_fail: int
    elapsed_seconds: float


def format_local_sample_pair(pair: tuple[str, str]) -> str:
    return f"{pair[0]}/{pair[1]}"


def parse_local_sample_pair_spec(pair_spec: str) -> tuple[str, str]:
    raw_parts = [part.strip() for part in pair_spec.split(",", maxsplit=1)]
    if len(raw_parts) != 2 or not raw_parts[0] or not raw_parts[1]:
        raise ValueError(
            "Pair specs must be written as 'scorey_pick,user_pick'. "
            "Example: 'rock,paper'."
        )

    pair = (
        normalise_pick(raw_parts[0]),
        normalise_pick(raw_parts[1]),
    )
    if pair not in research_beta_1_pass_pairs():
        valid_pairs = ", ".join(
            format_local_sample_pair(valid_pair)
            for valid_pair in research_beta_1_pass_pairs()
        )
        raise ValueError(
            "Unsupported local pair cycle entry "
            f"'{format_local_sample_pair(pair)}'. Choose from: {valid_pairs}."
        )
    return pair


def explicit_local_sample_pairs(
    pair_specs: tuple[str, ...] | list[str],
) -> tuple[tuple[str, str], ...]:
    if not pair_specs:
        raise ValueError("Provide at least one pair spec.")
    return tuple(parse_local_sample_pair_spec(pair_spec) for pair_spec in pair_specs)


def _sample_pairs_for_pattern(pattern: str) -> tuple[tuple[str, str], ...]:
    if pattern == "baseline":
        return tuple(
            (local_scorey_pick_for(user_pick), user_pick) for user_pick in USER_PICKS
        )
    if pattern == "research-beta-1-coverage":
        return research_beta_1_pass_pairs()
    raise ValueError(
        "Unsupported local sample pattern "
        f"'{pattern}'. Choose one of: {', '.join(LOCAL_SAMPLE_PATTERNS)}."
    )


def _default_model_for_pattern(pattern: str) -> str:
    if pattern == "baseline":
        return "local-fixture-batch"
    if pattern == "research-beta-1-coverage":
        return "local-research-beta-1-coverage-batch"
    raise ValueError(
        "Unsupported local sample pattern "
        f"'{pattern}'. Choose one of: {', '.join(LOCAL_SAMPLE_PATTERNS)}."
    )


def sample_local_eval_outputs(
    *,
    count: int | None = None,
    duration_seconds: float | None = None,
    interval_seconds: float = 0.0,
    pattern: str = "baseline",
    pair_cycle: tuple[tuple[str, str], ...] | None = None,
    model: str | None = None,
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
    sample_pairs = pair_cycle or _sample_pairs_for_pattern(pattern)
    model_name = model or (
        "local-explicit-pair-cycle-batch"
        if pair_cycle is not None
        else _default_model_for_pattern(pattern)
    )

    start = time_fn()
    deadline = None if duration_seconds is None else start + duration_seconds
    output_ids: list[int] = []
    research_beta_1_pass = 0
    research_beta_1_fail = 0
    index = 0

    while True:
        if count is not None and index >= count:
            break
        if deadline is not None and time_fn() >= deadline:
            break

        scorey_pick, user_pick = sample_pairs[index % len(sample_pairs)]
        round_state = build_local_round_state_for_pair(
            user_pick,
            scorey_pick,
            scorey_score=index + 1,
        )
        round_text = compose_round(round_state)
        output_id = record_round_state(
            None,
            round_state,
            round_text,
            source_mode="local",
            model=model_name,
        )
        output_ids.append(output_id)

        gate_result = evaluate_research_beta_1(
            user_pick=round_state.user_pick,
            scorey_pick=round_state.scorey_pick,
        )
        if gate_result.verdict == "pass":
            research_beta_1_pass += 1
        else:
            research_beta_1_fail += 1

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
        research_beta_1_pass=research_beta_1_pass,
        research_beta_1_fail=research_beta_1_fail,
        elapsed_seconds=elapsed_seconds,
    )
