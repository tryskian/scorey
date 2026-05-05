from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scorey.config import Settings
from scorey.eval_db import counts, list_outputs
from scorey.eval_sampling import (
    explicit_local_sample_pairs,
    explicit_user_pick_cycle,
    sample_live_eval_outputs,
    sample_local_eval_outputs,
)
from scorey.pipeline import RoundFields


class EvalSamplingTests(TestCase):
    def test_sample_local_eval_outputs_records_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                summary = sample_local_eval_outputs(count=3)

                self.assertEqual(summary.recorded, 3)
                self.assertEqual(summary.research_beta_1_pass, 3)
                self.assertEqual(summary.research_beta_1_fail, 0)
                self.assertIsNotNone(summary.first_output_id)
                self.assertIsNotNone(summary.last_output_id)

                totals = counts(db_path)
                self.assertEqual(totals["total"], 3)
                self.assertEqual(totals["pending"], 3)

                rows = list_outputs(db_path, limit=3)
                observed_pairs = [
                    (str(row["scorey_pick"]), str(row["user_pick"]))
                    for row in reversed(rows)
                ]
                self.assertEqual(
                    observed_pairs,
                    [
                        ("scissors", "rock"),
                        ("paper", "paper"),
                        ("paper", "scissors"),
                    ],
                )

    def test_sample_local_eval_outputs_research_beta_1_coverage_cycles_all_pass_pairs(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                summary = sample_local_eval_outputs(
                    count=6,
                    pattern="research-beta-1-coverage",
                )

                self.assertEqual(summary.recorded, 6)
                self.assertEqual(summary.research_beta_1_pass, 6)
                self.assertEqual(summary.research_beta_1_fail, 0)

                rows = list_outputs(db_path, limit=6)
                observed_pairs = {
                    (str(row["scorey_pick"]), str(row["user_pick"])) for row in rows
                }
                self.assertEqual(
                    observed_pairs,
                    {
                        ("paper", "scissors"),
                        ("rock", "paper"),
                        ("scissors", "rock"),
                        ("paper", "paper"),
                        ("rock", "rock"),
                        ("scissors", "scissors"),
                    },
                )

    def test_sample_local_eval_outputs_with_explicit_pair_cycle(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                summary = sample_local_eval_outputs(
                    count=4,
                    pair_cycle=explicit_local_sample_pairs(
                        ("rock,paper", "scissors,rock")
                    ),
                )

                self.assertEqual(summary.recorded, 4)
                self.assertEqual(summary.research_beta_1_pass, 4)
                self.assertEqual(summary.research_beta_1_fail, 0)

                rows = list_outputs(db_path, limit=4)
                observed_pairs = [
                    (str(row["scorey_pick"]), str(row["user_pick"]))
                    for row in reversed(rows)
                ]
                self.assertEqual(
                    observed_pairs,
                    [
                        ("rock", "paper"),
                        ("scissors", "rock"),
                        ("rock", "paper"),
                        ("scissors", "rock"),
                    ],
                )

    def test_sample_live_eval_outputs_records_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                with patch(
                    "scorey.eval_sampling.require_openai_api_key", return_value=None
                ):
                    with patch(
                        "scorey.eval_sampling.load_settings",
                        return_value=Settings(app_name="Scorey", model="gpt-test"),
                    ):
                        with patch(
                            "scorey.eval_sampling.choose_scorey_pick",
                            side_effect=("scissors", "paper", "paper"),
                        ):
                            with patch(
                                "scorey.eval_sampling.generate_live_round_fields",
                                return_value=RoundFields(
                                    winning_state="for snacks",
                                    worse_state="a fake one",
                                    scoreboard_claim="none",
                                ),
                            ):
                                summary = sample_live_eval_outputs(count=3)

                self.assertEqual(summary.recorded, 3)
                self.assertEqual(summary.research_beta_1_pass, 3)
                self.assertEqual(summary.research_beta_1_fail, 0)

                totals = counts(db_path)
                self.assertEqual(totals["total"], 3)
                self.assertEqual(totals["pending"], 3)

                rows = list_outputs(db_path, limit=3)
                observed_rows = [
                    (
                        str(row["scorey_pick"]),
                        str(row["user_pick"]),
                        str(row["source_mode"]),
                        str(row["model"]),
                    )
                    for row in reversed(rows)
                ]
                self.assertEqual(
                    observed_rows,
                    [
                        ("scissors", "rock", "live", "gpt-test"),
                        ("paper", "paper", "live", "gpt-test"),
                        ("paper", "scissors", "live", "gpt-test"),
                    ],
                )

    def test_explicit_user_pick_cycle_normalises_values(self) -> None:
        self.assertEqual(
            explicit_user_pick_cycle((" Rock ", "PAPER")),
            ("rock", "paper"),
        )
