from unittest import TestCase

from scorey.agent import SCOREY_INSTRUCTIONS, build_prompt


class AgentPromptTests(TestCase):
    def test_instructions_block_generic_same_pick_fillers(self) -> None:
        self.assertIn(
            "avoid generic fillers like real one, napkin", SCOREY_INSTRUCTIONS
        )
        self.assertIn(
            "avoid version/build/patch/update/firmware language", SCOREY_INSTRUCTIONS
        )

    def test_same_pick_prompt_biases_toward_concrete_demotion(self) -> None:
        prompt = build_prompt("paper", "paper", "same-pick")

        self.assertIn(
            "Avoid real one, napkin, power, supremacy, domination, copy, and clone.",
            prompt,
        )
        self.assertIn(
            "Do not use version/build/patch/update/firmware language.",
            prompt,
        )
        self.assertIn("Prefer concrete object demotion tied to both picks.", prompt)
