from __future__ import annotations

from scorey.config import Settings
from scorey.pipeline import RoundFields, normalise_round_fields

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
Keep each pick inside its exact object class.
Return only the structured fields.
""".strip()


def build_prompt(user_pick: str, scorey_pick: str, route_family: str) -> str:
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
    return (
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


def generate_live_round_fields(
    settings: Settings,
    user_pick: str,
    scorey_pick: str,
    route_family: str,
) -> RoundFields:
    try:
        from agents import Agent, Runner
    except ImportError as exc:  # pragma: no cover - requires optional runtime deps
        raise RuntimeError(
            "Live generation requires the openai-agents package."
        ) from exc

    agent = Agent(
        name=settings.app_name,
        instructions=SCOREY_INSTRUCTIONS,
        model=settings.model,
        output_type=RoundFields,
    )
    result = Runner.run_sync(agent, build_prompt(user_pick, scorey_pick, route_family))
    output = result.final_output
    if isinstance(output, RoundFields):
        return normalise_round_fields(output)
    if isinstance(output, dict):
        return normalise_round_fields(RoundFields(**output))
    raise RuntimeError("Live generation returned an unexpected output shape.")
