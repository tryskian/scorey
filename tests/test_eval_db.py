from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scorey.eval_db import (
    counts,
    init_db,
    judge_output,
    judge_output_for_lens,
    lens_counts,
    list_lens_review_sample,
    list_outputs,
    list_review_sample,
    record_output,
)


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

    def test_review_sample_returns_one_pending_row_per_model_pair(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            older_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="older",
                source_mode="local",
                model="batch-a",
            )
            newer_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="newer",
                source_mode="local",
                model="batch-a",
            )
            record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="other",
                source_mode="local",
                model="batch-a",
            )
            judge_output(db_path, older_id, "pass", "already judged")

            rows = list_review_sample(db_path, limit=5)
            self.assertEqual(len(rows), 2)
            ids = {int(row["id"]) for row in rows}
            self.assertIn(newer_id, ids)
            self.assertNotIn(older_id, ids)

    def test_tone_review_sample_uses_route_pass_rows_and_skips_tone_judged(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            older_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="older tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            newer_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="newer tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            other_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="other tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, older_id, "pass", "route pass")
            judge_output(db_path, newer_id, "pass", "route pass")
            judge_output(db_path, other_id, "pass", "route pass")
            judge_output_for_lens(
                db_path,
                other_id,
                lens="tone",
                verdict="pass",
                note="already tone judged",
            )

            rows = list_lens_review_sample(
                db_path,
                lens="tone",
                source_mode="live",
                limit=5,
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["id"]), newer_id)

            summary = lens_counts(db_path, lens="tone", source_mode="live")
            self.assertEqual(summary["total"], 3)
            self.assertEqual(summary["pass"], 1)
            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pending"], 2)

    def test_tone_review_sample_can_filter_to_one_user_pick(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            paper_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="paper tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            rock_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="rock tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, paper_id, "pass", "route pass")
            judge_output(db_path, rock_id, "pass", "route pass")

            rows = list_lens_review_sample(
                db_path,
                lens="tone",
                source_mode="live",
                limit=5,
                user_picks=("paper",),
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["id"]), paper_id)

            summary = lens_counts(
                db_path,
                lens="tone",
                source_mode="live",
                user_picks=("paper",),
            )
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["pass"], 0)
            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pending"], 1)
