from unittest import TestCase

from scorey.config import USER_PICKS, allowed_scorey_picks
from scorey.eval_gates import (
    BETA_1_PASS_PAIRS,
    beta_1_fail_pairs,
    evaluate_beta_1,
)


class EvalGateTests(TestCase):
    def test_beta_1_passes_reverse_gameplay_pair(self) -> None:
        result = evaluate_beta_1("scissors", "paper")
        self.assertEqual(result.verdict, "pass")
        self.assertEqual(result.reason, "reverse gameplay route")

    def test_beta_1_passes_same_pick_pair(self) -> None:
        result = evaluate_beta_1("rock", "rock")
        self.assertEqual(result.verdict, "pass")
        self.assertEqual(result.reason, "same-pick loophole route")

    def test_beta_1_fails_other_pair(self) -> None:
        result = evaluate_beta_1("rock", "paper")
        self.assertEqual(result.verdict, "fail")
        self.assertEqual(result.reason, "not a beta 1.0 route")

    def test_beta_1_pairs_cover_the_full_grid(self) -> None:
        self.assertEqual(len(BETA_1_PASS_PAIRS), 6)
        self.assertEqual(len(beta_1_fail_pairs()), 3)

    def test_beta_1_pass_pairs_match_the_current_runtime_contract(self) -> None:
        expected_pairs = {
            (scorey_pick, user_pick)
            for user_pick in USER_PICKS
            for scorey_pick in allowed_scorey_picks(user_pick)
        }
        self.assertEqual(set(BETA_1_PASS_PAIRS), expected_pairs)
