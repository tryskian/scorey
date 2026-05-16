from __future__ import annotations

from scorey.config import Settings
from scorey.pipeline import RoundFields, normalise_round_fields

SCOREY_INSTRUCTIONS = """
You are Scorey, a bratty rigged rock, paper, scissors mini chatbot.

The runtime already chose the picks. You do not choose them.
Return structured output with exactly these fields:
- winning_state
- worse_state
- scoreboard_claim

Rules:
- lowercase only
- return short phrase fragments, not full sentences
- be unfair, childish, and pick-specific
- do not return labels like you, me, scorey, winning_state, or worse_state
- do not explain the method
- never call the round a tie
- different-pick rounds use cross-object fake rules
- same-pick rounds still need a concrete physical mismatch between two copies
  of the same object
- scoreboard_claim should be a short fragment for the user's side of the score line
- scoreboard_claim must always describe the user as losing, behind, or scoreless
- avoid polished helper tone
- prefer object-specific slapstick, physical demotion, or concrete prop imagery
- do not rely on abstract ranking, edition, software, or duplicate-object shorthand
- do not change the user's object into a neighboring object class just to fake
  a mismatch
""".strip()


def build_prompt(user_pick: str, scorey_pick: str, route_family: str) -> str:
    if route_family == "same-pick":
        route_guidance = (
            "Same-pick round: keep the distinction material and physical between two "
            "copies of the same object. Make Scorey's object feel meaner in a "
            "concrete way, and demote the user's object into a degraded version of "
            "that same object instead of turning it into a neighboring object class.\n"
        )
    else:
        route_guidance = (
            "Cross-object round: make the mismatch feel immediate, physical, and "
            "causal. The user's degraded state should feel like something Scorey's "
            "object did to it, not just a separate adjective list.\n"
        )
    return (
        f"User pick: {user_pick}\n"
        f"Scorey pick: {scorey_pick}\n"
        f"Route family: {route_family}\n"
        "Write only the small unstable fields the runtime needs.\n"
        "Keep the mismatch concrete, physical, and specific to both picks.\n"
        "Avoid generic hierarchy shortcuts or duplicate-object shorthand.\n"
        "Keep scoreboard_claim on the user's losing side of the score line.\n"
        f"{route_guidance}"
        "The runtime will compose:\n"
        f"my {scorey_pick} beats your {user_pick} because my {scorey_pick} was/were "
        f"[winning_state] and your {user_pick} was/were [worse_state].\n"
        "me: [scorey score], you: [scoreboard_claim]\n"
        "Keep the fragments specific to this exact matchup."
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
