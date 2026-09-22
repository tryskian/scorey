from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:  # pragma: no cover - optional until live runtime install
    load_dotenv: Callable[..., bool] | None = None
else:
    load_dotenv = _load_dotenv

ROOT = Path(__file__).resolve().parents[2]
EVAL_DB_PATH = ROOT / ".local" / "evals.sqlite"

USER_PICKS: tuple[str, ...] = ("rock", "paper", "scissors")
VERDICTS: tuple[str, ...] = ("pass", "fail")

ALLOWED_SCOREY_PICKS: dict[str, tuple[str, ...]] = {
    "rock": ("scissors", "rock"),
    "paper": ("rock", "paper"),
    "scissors": ("paper", "scissors"),
}

LOCAL_SCOREY_PICKS: dict[str, str] = {
    "rock": "scissors",
    "paper": "paper",
    "scissors": "paper",
}


@dataclass(frozen=True)
class Settings:
    app_name: str
    model: str


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(ROOT / ".env", override=False)
    model = os.getenv("SCOREY_MODEL")
    if not model:
        model = os.getenv("OPENAI_DEFAULT_MODEL")
    if not model:
        model = "gpt-5-nano"
    return Settings(
        app_name="Scorey",
        model=model,
    )


def normalise_pick(pick: str) -> str:
    value = pick.strip().lower()
    if value not in USER_PICKS:
        raise ValueError(
            f"Unsupported pick '{pick}'. Choose one of: {', '.join(USER_PICKS)}."
        )
    return value


def allowed_scorey_picks(user_pick: str) -> tuple[str, ...]:
    return ALLOWED_SCOREY_PICKS[normalise_pick(user_pick)]


def local_scorey_pick_for(user_pick: str) -> str:
    return LOCAL_SCOREY_PICKS[normalise_pick(user_pick)]


def route_family_for(user_pick: str, scorey_pick: str) -> str:
    user_value = normalise_pick(user_pick)
    scorey_value = normalise_pick(scorey_pick)
    if scorey_value not in allowed_scorey_picks(user_value):
        raise ValueError(
            f"Invalid Scorey pick '{scorey_pick}' for user pick '{user_pick}'."
        )
    if user_value == scorey_value:
        return "same-pick"
    return "cross-object"


def require_openai_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for live generation.")
