from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, TypeVar

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

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh"]
ReasoningSummary = Literal["auto", "concise", "detailed"]
Verbosity = Literal["low", "medium", "high"]
Choice = TypeVar("Choice", bound=str)


@dataclass(frozen=True)
class Settings:
    app_name: str
    model: str
    reasoning_effort: ReasoningEffort | None = None
    reasoning_summary: ReasoningSummary | None = None
    verbosity: Verbosity | None = None
    top_p: float | None = None
    memory_enabled: bool = False
    memory_db_path: str = str(ROOT / ".local" / "memory.sqlite")
    memory_index: str = ""
    memory_embedding_model: str = "text-embedding-3-small"
    memory_top_k: int = 2
    memory_max_chars: int = 1200


def _optional_choice(name: str, choices: tuple[Choice, ...]) -> Choice | None:
    value = os.getenv(name)
    if not value:
        return None
    for choice in choices:
        if value == choice:
            return choice
    raise ValueError(f"{name} must be one of: {', '.join(choices)}.")


def load_settings() -> Settings:
    if load_dotenv is not None:
        load_dotenv(ROOT / ".env", override=False)
    model = os.getenv("SCOREY_MODEL")
    if not model:
        model = os.getenv("OPENAI_DEFAULT_MODEL")
    if not model:
        model = "gpt-5-nano"
    top_p_value = os.getenv("SCOREY_TOP_P")
    top_p = float(top_p_value) if top_p_value else None
    if top_p is not None and not 0 <= top_p <= 1:
        raise ValueError("SCOREY_TOP_P must be between 0 and 1.")
    memory_flag = os.getenv("SCOREY_MEMORY_ENABLED", "false").lower()
    if memory_flag not in ("true", "false", "1", "0"):
        raise ValueError("SCOREY_MEMORY_ENABLED must be true or false.")
    memory_top_k = int(os.getenv("SCOREY_MEMORY_TOP_K") or "2")
    memory_max_chars = int(os.getenv("SCOREY_MEMORY_MAX_CHARS") or "1200")
    if memory_top_k < 1 or memory_max_chars < 1:
        raise ValueError("Memory result and context limits must be positive.")
    memory_path = Path(
        os.getenv("SCOREY_MEMORY_DB") or ".local/memory.sqlite"
    ).expanduser()
    if not memory_path.is_absolute():
        memory_path = ROOT / memory_path
    return Settings(
        app_name="Scorey",
        model=model,
        reasoning_effort=_optional_choice(
            "SCOREY_REASONING_EFFORT",
            ("none", "minimal", "low", "medium", "high", "xhigh"),
        ),
        reasoning_summary=_optional_choice(
            "SCOREY_REASONING_SUMMARY", ("auto", "concise", "detailed")
        ),
        verbosity=_optional_choice("SCOREY_VERBOSITY", ("low", "medium", "high")),
        top_p=top_p,
        memory_enabled=memory_flag in ("true", "1"),
        memory_db_path=str(memory_path),
        memory_index=os.getenv("SCOREY_MEMORY_INDEX", ""),
        memory_embedding_model=os.getenv("SCOREY_MEMORY_EMBEDDING_MODEL")
        or "text-embedding-3-small",
        memory_top_k=memory_top_k,
        memory_max_chars=memory_max_chars,
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
