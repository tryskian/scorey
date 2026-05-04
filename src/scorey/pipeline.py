from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from scorey.config import (
    allowed_scorey_picks,
    local_scorey_pick_for,
    normalise_pick,
    route_family_for,
)


@dataclass(frozen=True)
class RoundFields:
    winning_state: str
    worse_state: str
    scoreboard_claim: str


@dataclass(frozen=True)
class RoundState:
    user_pick: str
    scorey_pick: str
    route_family: str
    winning_state: str
    worse_state: str
    scoreboard_claim: str
    scorey_score: int = 1


class ChoiceSource(Protocol):
    def choice(self, values: Sequence[str]) -> str: ...


LOCAL_ROUND_FIELDS: dict[tuple[str, str], RoundFields] = {
    ("rock", "scissors"): RoundFields(
        winning_state="for snacks",
        worse_state="a marshmallow that looked like a rock",
        scoreboard_claim="none",
    ),
    ("rock", "rock"): RoundFields(
        winning_state="the real rock",
        worse_state="a painted potato",
        scoreboard_claim="still none",
    ),
    ("paper", "rock"): RoundFields(
        winning_state="the official paper",
        worse_state="a receipt pretending to be a rock",
        scoreboard_claim="not even on it",
    ),
    ("paper", "paper"): RoundFields(
        winning_state="the real one",
        worse_state="a napkin",
        scoreboard_claim="none",
    ),
    ("scissors", "paper"): RoundFields(
        winning_state="kitchen scissors",
        worse_state="a permission slip",
        scoreboard_claim="not on the board",
    ),
    ("scissors", "scissors"): RoundFields(
        winning_state="the sharp pair",
        worse_state="safety scissors",
        scoreboard_claim="still zero",
    ),
}


def choose_scorey_pick(user_pick: str, rng: ChoiceSource | None = None) -> str:
    choices = allowed_scorey_picks(user_pick)
    chooser = rng or random.SystemRandom()
    return chooser.choice(choices)


def normalise_generated_fragment(value: str) -> str:
    compact = " ".join(value.strip().strip("\"'").split()).lower()
    return compact.rstrip(".,;:!?")


def normalise_round_fields(fields: RoundFields) -> RoundFields:
    return RoundFields(
        winning_state=normalise_generated_fragment(fields.winning_state),
        worse_state=normalise_generated_fragment(fields.worse_state),
        scoreboard_claim=normalise_generated_fragment(fields.scoreboard_claim),
    )


def build_round_state(
    user_pick: str,
    scorey_pick: str,
    fields: RoundFields,
    *,
    scorey_score: int = 1,
) -> RoundState:
    user_value = normalise_pick(user_pick)
    scorey_value = normalise_pick(scorey_pick)
    route_family = route_family_for(user_value, scorey_value)
    cleaned = normalise_round_fields(fields)
    if scorey_score < 1:
        raise ValueError("Scorey score must be at least 1.")
    if (
        not cleaned.winning_state
        or not cleaned.worse_state
        or not cleaned.scoreboard_claim
    ):
        raise ValueError("Round fields must all be non-empty.")
    return RoundState(
        user_pick=user_value,
        scorey_pick=scorey_value,
        route_family=route_family,
        winning_state=cleaned.winning_state,
        worse_state=cleaned.worse_state,
        scoreboard_claim=cleaned.scoreboard_claim,
        scorey_score=scorey_score,
    )


def build_local_round_state(user_pick: str, *, scorey_score: int = 1) -> RoundState:
    user_value = normalise_pick(user_pick)
    scorey_pick = local_scorey_pick_for(user_value)
    fields = LOCAL_ROUND_FIELDS[(user_value, scorey_pick)]
    return build_round_state(
        user_value,
        scorey_pick,
        fields,
        scorey_score=scorey_score,
    )


def pick_verb(pick: str) -> str:
    if normalise_pick(pick) == "scissors":
        return "were"
    return "was"


def compose_round(round_state: RoundState) -> str:
    return (
        f"you: {round_state.user_pick}\n"
        f"me: {round_state.scorey_pick}\n\n"
        f"my {round_state.scorey_pick} beats your {round_state.user_pick} because my "
        f"{round_state.scorey_pick} {pick_verb(round_state.scorey_pick)} "
        f"{round_state.winning_state} and your {round_state.user_pick} "
        f"{pick_verb(round_state.user_pick)} {round_state.worse_state}.\n\n"
        f"me: {round_state.scorey_score}, you: {round_state.scoreboard_claim}\n\n"
        "scorey."
    )
