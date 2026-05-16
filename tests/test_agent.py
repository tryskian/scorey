from unittest import TestCase

from scorey.agent import SCOREY_INSTRUCTIONS, build_prompt


class AgentPromptTests(TestCase):
    def test_instructions_use_abstract_constraints_not_phrase_anchors(self) -> None:
        self.assertIn(
            "same-pick rounds still need a concrete physical mismatch",
            SCOREY_INSTRUCTIONS,
        )
        self.assertIn(
            (
                "do not rely on abstract ranking, edition, software, "
                "or duplicate-object shorthand"
            ),
            SCOREY_INSTRUCTIONS,
        )
        self.assertNotIn("real one", SCOREY_INSTRUCTIONS)
        self.assertNotIn("napkin", SCOREY_INSTRUCTIONS)
        self.assertNotIn("version/build/patch/update/firmware", SCOREY_INSTRUCTIONS)

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
                "demote the user's object into a specific pathetic prop "
                "or degraded stand-in."
            ),
            prompt,
        )
        self.assertNotIn("real one", prompt)
        self.assertNotIn("napkin", prompt)
        self.assertNotIn("version/build/patch/update/firmware", prompt)
