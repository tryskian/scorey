from __future__ import annotations

from dataclasses import dataclass

from scorey.config import USER_PICKS, normalise_pick

RESEARCH_BETA_1_NAME = "research-beta-1.0"
RESEARCH_BETA_1_DISPLAY_NAME = "Research Beta 1.0"

# Pairs are ordered as (scorey_pick, user_pick).
RESEARCH_BETA_1_PASS_PAIRS: tuple[tuple[str, str], ...] = (
    ("paper", "scissors"),
    ("rock", "paper"),
    ("scissors", "rock"),
    ("paper", "paper"),
    ("rock", "rock"),
    ("scissors", "scissors"),
)

REVERSE_GAMEPLAY_REASON = "reverse gameplay route"
SAME_PICK_REASON = "same-pick loophole route"
FAIL_REASON = "not a research beta 1.0 route"


@dataclass(frozen=True)
class GateResult:
    gate_name: str
    user_pick: str
    scorey_pick: str
    verdict: str
    reason: str


def research_beta_1_pass_pairs() -> tuple[tuple[str, str], ...]:
    return RESEARCH_BETA_1_PASS_PAIRS


def research_beta_1_fail_pairs() -> tuple[tuple[str, str], ...]:
    return tuple(
        (scorey_pick, user_pick)
        for scorey_pick in USER_PICKS
        for user_pick in USER_PICKS
        if (scorey_pick, user_pick) not in RESEARCH_BETA_1_PASS_PAIRS
    )


def evaluate_research_beta_1(user_pick: str, scorey_pick: str) -> GateResult:
    user_value = normalise_pick(user_pick)
    scorey_value = normalise_pick(scorey_pick)
    pair = (scorey_value, user_value)
    if pair in RESEARCH_BETA_1_PASS_PAIRS:
        reason = (
            SAME_PICK_REASON if scorey_value == user_value else REVERSE_GAMEPLAY_REASON
        )
        return GateResult(
            gate_name=RESEARCH_BETA_1_NAME,
            user_pick=user_value,
            scorey_pick=scorey_value,
            verdict="pass",
            reason=reason,
        )
    return GateResult(
        gate_name=RESEARCH_BETA_1_NAME,
        user_pick=user_value,
        scorey_pick=scorey_value,
        verdict="fail",
        reason=FAIL_REASON,
    )


def summarise_gate_results(results: list[GateResult]) -> dict[str, int]:
    pass_count = sum(1 for result in results if result.verdict == "pass")
    fail_count = sum(1 for result in results if result.verdict == "fail")
    return {
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
    }
