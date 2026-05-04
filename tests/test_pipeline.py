from collections.abc import Sequence
from unittest import TestCase

from scorey.pipeline import (
    RoundFields,
    build_local_round_state,
    build_round_state,
    choose_scorey_pick,
    compose_round,
    normalise_generated_fragment,
)


class _FakeRng:
    def choice(self, values: Sequence[str]) -> str:
        return values[-1]


class RoundPipelineTests(TestCase):
    def test_local_round_state_preserves_same_pick_contract(self) -> None:
        round_state = build_local_round_state("paper", scorey_score=2)
        self.assertEqual(round_state.user_pick, "paper")
        self.assertEqual(round_state.scorey_pick, "paper")
        self.assertEqual(round_state.route_family, "same-pick")
        self.assertEqual(round_state.scorey_score, 2)

    def test_build_round_state_normalises_generated_fields(self) -> None:
        round_state = build_round_state(
            "rock",
            "scissors",
            RoundFields(
                winning_state="  For Snacks. ",
                worse_state="A Marshmallow That Looked Like A Rock.",
                scoreboard_claim="None.",
            ),
        )
        self.assertEqual(round_state.winning_state, "for snacks")
        self.assertEqual(
            round_state.worse_state,
            "a marshmallow that looked like a rock",
        )
        self.assertEqual(round_state.scoreboard_claim, "none")

    def test_compose_round_keeps_contract_shape(self) -> None:
        round_text = compose_round(build_local_round_state("rock", scorey_score=3))
        self.assertIn("you: rock", round_text)
        self.assertIn("me: scissors", round_text)
        self.assertIn("me: 3, you: none", round_text)
        self.assertTrue(round_text.endswith("scorey."))

    def test_choose_scorey_pick_uses_only_allowed_routes(self) -> None:
        self.assertEqual(choose_scorey_pick("rock", rng=_FakeRng()), "rock")

    def test_normalise_generated_fragment_strips_terminal_punctuation(self) -> None:
        self.assertEqual(normalise_generated_fragment(' "Still None." '), "still none")
