from unittest import TestCase

from scorey.config import (
    allowed_scorey_picks,
    local_scorey_pick_for,
    normalise_pick,
    route_family_for,
)


class PickConfigTests(TestCase):
    def test_normalise_pick_lowercases_valid_input(self) -> None:
        self.assertEqual(normalise_pick(" Rock "), "rock")

    def test_allowed_scorey_picks_are_narrow(self) -> None:
        self.assertEqual(allowed_scorey_picks("paper"), ("rock", "paper"))

    def test_route_family_for_same_pick(self) -> None:
        self.assertEqual(route_family_for("scissors", "scissors"), "same-pick")

    def test_local_scorey_pick_can_use_same_pick(self) -> None:
        self.assertEqual(local_scorey_pick_for("paper"), "paper")
