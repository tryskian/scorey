from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from scorey.config import Settings, normalise_pick, route_family_for
from scorey.pipeline import RoundFields, normalise_round_fields
from scorey.retrieval import (
    FrozenMemory,
    RetrievalContext,
    generation_receipt,
    write_json,
)

if TYPE_CHECKING:
    from agents import Agent

SCOREY_PROMPT_VERSION = "restored-321d970"

SCOREY_INSTRUCTIONS = """
You are Scorey, a bratty rigged rock, paper, scissors mini chatbot.

The runtime already chose the picks.
Return structured output with exactly these fields:
- winning_state
- worse_state
- scoreboard_claim

Keep every field lowercase.
Write short phrase fragments that fit directly into the runtime sentence.
Make each round a clear Scorey win and a clear user loss.
Keep the voice unfair, childish, playful, and pick-specific.
Keep the scene concrete, physical, and easy to picture.
Use object-specific slapstick, physical demotion, and concrete prop imagery.
Keep same-pick rounds as two unequal copies of the same object.
Keep cross-object rounds as immediate cause-and-effect between the two picks.
Keep winning_state and worse_state as matching halves of one small rigged scene.
Keep scoreboard_claim short and pointed at the user's losing side of the score line.
Keep scoreboard_claim free of the word "you"; the runtime supplies the you: label.
Keep each pick inside its exact object class.
Return only the structured fields.
""".strip()


def build_prompt(
    user_pick: str,
    scorey_pick: str,
    route_family: str,
    *,
    context: str = "",
) -> str:
    if route_family == "same-pick":
        route_guidance = (
            "Same-pick round: keep the distinction material and physical between two "
            "copies of the same object. Make Scorey's object feel meaner in a "
            "concrete way, and let the user's object land as a degraded version "
            "of that same object while staying inside the same object class.\n"
        )
    else:
        route_guidance = (
            "Cross-object round: make the mismatch feel immediate, physical, and "
            "causal. Let the user's degraded state feel like something Scorey's "
            "object did to it, with both picks still recognisable as themselves.\n"
        )
    prompt = (
        f"User pick: {user_pick}\n"
        f"Scorey pick: {scorey_pick}\n"
        f"Route family: {route_family}\n"
        "Write only the three runtime fields.\n"
        "Keep the mismatch concrete, physical, and specific to both picks.\n"
        "Keep the scene immediate, causal, and easy to picture.\n"
        "Keep scoreboard_claim short, direct, and on the user's losing side "
        "of the score line.\n"
        f"{route_guidance}"
        "The runtime will compose:\n"
        f"my {scorey_pick} beats your {user_pick} because my {scorey_pick} was/were "
        f"[winning_state] and your {user_pick} was/were [worse_state].\n"
        "me: [scorey score], you: [scoreboard_claim]\n"
        "Keep the fragments aligned with that exact matchup."
    )
    if context:
        prompt += (
            "\n\n[Scorey principles]\n"
            + context
            + "\nApply this context within the existing round and field contract."
        )
    return prompt


def build_live_agent(settings: Settings) -> Agent[None]:
    """Use one request contract for the app and its golden smoke runs."""
    try:
        from agents import Agent, ModelSettings
        from openai.types.shared import Reasoning
    except ImportError as exc:  # pragma: no cover - optional live dependencies
        raise RuntimeError(
            "Live generation requires the openai-agents package."
        ) from exc
    return Agent(
        name=settings.app_name,
        instructions=SCOREY_INSTRUCTIONS,
        model=settings.model,
        model_settings=ModelSettings(
            reasoning=(
                Reasoning(
                    effort=settings.reasoning_effort,
                    summary=settings.reasoning_summary,
                )
                if settings.reasoning_effort or settings.reasoning_summary
                else None
            ),
            verbosity=settings.verbosity,
            top_p=settings.top_p,
        ),
        output_type=RoundFields,
    )


def generate_live_round_fields(
    settings: Settings,
    user_pick: str,
    scorey_pick: str,
    route_family: str,
    *,
    retrieval_context: RetrievalContext | None = None,
    receipt_sink: Callable[[Path], None] | None = None,
) -> RoundFields:
    try:
        from agents import Runner
    except ImportError as exc:  # pragma: no cover - requires optional runtime deps
        raise RuntimeError(
            "Live generation requires the openai-agents package."
        ) from exc

    if settings.memory_enabled:
        user_pick, scorey_pick = normalise_pick(user_pick), normalise_pick(scorey_pick)
        if route_family != route_family_for(user_pick, scorey_pick):
            raise ValueError("Route family does not match the selected picks.")
        retrieval_context = retrieval_context or FrozenMemory(settings).retrieve(
            user_pick, scorey_pick
        )
        if (
            retrieval_context.index != settings.memory_index
            or retrieval_context.embedding_model != settings.memory_embedding_model
            or (
                retrieval_context.user_pick,
                retrieval_context.scorey_pick,
                retrieval_context.route_family,
            )
            != (user_pick, scorey_pick, route_family)
            or retrieval_context.top_k != settings.memory_top_k
            or retrieval_context.max_chars != settings.memory_max_chars
        ):
            raise ValueError("Retrieval context does not match this round's condition.")
    elif retrieval_context is not None:
        raise ValueError("Retrieval context supplied while memory is disabled.")
    prompt = build_prompt(
        user_pick,
        scorey_pick,
        route_family,
        context=retrieval_context.context if retrieval_context else "",
    )
    agent = build_live_agent(settings)
    record = (
        generation_receipt(settings, retrieval_context, prompt, SCOREY_INSTRUCTIONS)
        if retrieval_context is not None
        else None
    )
    started = time.monotonic()
    try:
        result = Runner.run_sync(agent, prompt)
        output = result.final_output
        if isinstance(output, RoundFields):
            fields = normalise_round_fields(output)
        elif isinstance(output, dict):
            fields = normalise_round_fields(RoundFields(**output))
        else:
            raise RuntimeError("Live generation returned an unexpected output shape.")
        if record is not None:
            path, receipt = record
            receipt.update(
                status="completed",
                fields=asdict(fields),
                generation_seconds=time.monotonic() - started,
                response_ids=[r.response_id for r in result.raw_responses],
            )
            write_json(path, receipt)
            if receipt_sink is not None:
                receipt_sink(path)
        return fields
    except BaseException as error:
        if record is not None:
            path, receipt = record
            receipt.update(
                status="failed",
                error_type=type(error).__name__,
                generation_seconds=time.monotonic() - started,
            )
            write_json(path, receipt)
        raise
