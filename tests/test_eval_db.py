from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scorey.eval_db import counts, init_db, judge_output, list_outputs, record_output


class EvalDbTests(TestCase):
    def test_round_trip_output_and_judgment(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            output_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="my scissors beats your rock because snacks.",
                source_mode="local",
                model="local-fixture",
            )
            judge_output(db_path, output_id, "pass", "pick-specific and legible")

            rows = list_outputs(db_path, limit=5)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["current_verdict"], "pass")
            self.assertEqual(rows[0]["current_note"], "pick-specific and legible")

            summary = counts(db_path)
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["pass"], 1)
            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pending"], 0)

    def test_counts_pending_before_judgment(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="my paper beats your paper because mine was real.",
                source_mode="local",
                model="local-fixture",
            )

            summary = counts(db_path)
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["pass"], 0)
            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pending"], 1)
