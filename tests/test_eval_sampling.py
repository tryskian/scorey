from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scorey.eval_db import counts, list_outputs
from scorey.eval_sampling import sample_local_eval_outputs


class EvalSamplingTests(TestCase):
    def test_sample_local_eval_outputs_records_rows(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                summary = sample_local_eval_outputs(count=3)

                self.assertEqual(summary.recorded, 3)
                self.assertEqual(summary.beta_1_pass, 3)
                self.assertEqual(summary.beta_1_fail, 0)
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
