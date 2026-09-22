from unittest import TestCase

from scorey.agent import SCOREY_INSTRUCTIONS, build_live_agent, build_prompt
from scorey.config import Settings, route_family_for
from scorey.eval_gates import research_beta_1_pass_pairs
from scorey.pipeline import RoundFields

PROHIBITION_DIRECTIVES = (
    "never",
    "do not",
    "don't",
    "not ",
    "without",
    "avoid",
    "instead of",
    "no ",
)


class AgentPromptTests(TestCase):
    def test_instructions_use_positive_target_behaviour(self) -> None:
        self.assertIn(
            "Keep same-pick rounds as two unequal copies of the same object.",
            SCOREY_INSTRUCTIONS,
        )
        self.assertIn(
            "Keep cross-object rounds as immediate cause-and-effect",
            SCOREY_INSTRUCTIONS,
        )
        self.assertIn(
            "Keep scoreboard_claim short and pointed at the user's losing side",
            SCOREY_INSTRUCTIONS,
        )
        self.assertIn(
            "Keep each pick inside its exact object class.",
            SCOREY_INSTRUCTIONS,
        )
        self.assertIn("Return only the structured fields.", SCOREY_INSTRUCTIONS)
        self.assertNotIn("real one", SCOREY_INSTRUCTIONS)
        self.assertNotIn("napkin", SCOREY_INSTRUCTIONS)
        self.assertNotIn("version/build/patch/update/firmware", SCOREY_INSTRUCTIONS)

        lower_instructions = SCOREY_INSTRUCTIONS.lower()
        for directive in PROHIBITION_DIRECTIVES:
            with self.subTest(directive=directive):
                self.assertNotIn(directive, lower_instructions)

    def test_same_pick_prompt_biases_toward_concrete_demotion(self) -> None:
        prompt = build_prompt("paper", "paper", "same-pick")

        self.assertIn(
            "Keep the mismatch concrete, physical, and specific to both picks.",
            prompt,
        )
        self.assertIn(
            (
                "keep the distinction material and physical between two "
                "copies of the same object."
            ),
            prompt,
        )
        self.assertIn(
            (
                "let the user's object land as a degraded version "
                "of that same object while staying inside the same "
                "object class."
            ),
            prompt,
        )
        self.assertIn(
            (
                "Keep scoreboard_claim short, direct, and on the user's "
                "losing side of the score line."
            ),
            prompt,
        )
        self.assertNotIn("real one", prompt)
        self.assertNotIn("napkin", prompt)
        self.assertNotIn("version/build/patch/update/firmware", prompt)

        lower_prompt = prompt.lower()
        for directive in PROHIBITION_DIRECTIVES:
            with self.subTest(directive=directive):
                self.assertNotIn(directive, lower_prompt)

    def test_cross_object_prompt_requires_causal_mismatch(self) -> None:
        prompt = build_prompt("paper", "rock", "cross-object")

        self.assertIn(
            (
                "Let the user's degraded state feel like something "
                "Scorey's object did to it"
            ),
            prompt,
        )
        self.assertIn(
            (
                "Keep scoreboard_claim short, direct, and on the user's "
                "losing side of the score line."
            ),
            prompt,
        )
        self.assertIn(
            "both picks still recognisable as themselves.",
            prompt,
        )

        lower_prompt = prompt.lower()
        for directive in PROHIBITION_DIRECTIVES:
            with self.subTest(directive=directive):
                self.assertNotIn(directive, lower_prompt)


def test_matchup_and_optional_context_are_preserved() -> None:
    for scorey, user in research_beta_1_pass_pairs():
        route = route_family_for(user, scorey)
        prompt = build_prompt(user, scorey, route)
        assert f"User pick: {user}" in prompt
        assert f"Scorey pick: {scorey}" in prompt
        assert f"Route family: {route}" in prompt
        assert "[winning_state]" in prompt
        assert "[worse_state]" in prompt
        assert "you: [scoreboard_claim]" in prompt
        augmented = build_prompt(user, scorey, route, context="frozen test context")
        assert augmented.startswith(prompt)
        assert augmented.count("frozen test context") == 1
        assert "frozen test context" not in prompt


def test_shared_agent_preserves_application_settings_and_schema() -> None:
    settings = Settings("Scorey", "test-model", "medium", "detailed", "low", 0.98)
    agent = build_live_agent(settings)
    assert agent.model == settings.model
    assert agent.output_type is RoundFields
    assert agent.instructions == SCOREY_INSTRUCTIONS
    assert agent.model_settings.reasoning is not None
    assert agent.model_settings.reasoning.effort == "medium"
    assert agent.model_settings.reasoning.summary == "detailed"
    assert agent.model_settings.verbosity == "low"
    assert agent.model_settings.top_p == 0.98
