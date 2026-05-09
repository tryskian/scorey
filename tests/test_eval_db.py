import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scorey.eval_db import (
    archive_failure_disposition_for_lens,
    archive_output_for_lens,
    counts,
    init_db,
    judge_output,
    judge_output_for_lens,
    lens_counts,
    lens_failure_disposition_counts,
    list_lens_failure_disposition_sample,
    list_lens_review_sample,
    list_outputs,
    list_review_sample,
    record_failure_disposition_for_lens,
    record_output,
)


class EvalDbTests(TestCase):
    def test_init_db_migrates_null_pending_verdicts_to_literal_pending(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"

            with sqlite3.connect(db_path) as conn:
                conn.executescript(
                    """
                    CREATE TABLE eval_outputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_pick TEXT NOT NULL,
                        scorey_pick TEXT NOT NULL,
                        route_family TEXT NOT NULL,
                        round_text TEXT NOT NULL,
                        source_mode TEXT NOT NULL,
                        model TEXT NOT NULL,
                        current_verdict TEXT DEFAULT NULL
                            CHECK (
                                current_verdict IN ('pass', 'fail')
                                OR current_verdict IS NULL
                            ),
                        current_note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE eval_judgments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        output_id INTEGER NOT NULL
                            REFERENCES eval_outputs(id) ON DELETE CASCADE,
                        verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
                        note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE eval_lens_judgments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        output_id INTEGER NOT NULL
                            REFERENCES eval_outputs(id) ON DELETE CASCADE,
                        lens TEXT NOT NULL CHECK (lens IN ('tone')),
                        verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
                        note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL,
                        UNIQUE (output_id, lens)
                    );

                    CREATE TABLE eval_lens_archives (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        output_id INTEGER NOT NULL
                            REFERENCES eval_outputs(id) ON DELETE CASCADE,
                        lens TEXT NOT NULL CHECK (lens IN ('tone')),
                        note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL,
                        UNIQUE (output_id, lens)
                    );

                    CREATE TABLE eval_lens_failure_dispositions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        output_id INTEGER NOT NULL
                            REFERENCES eval_outputs(id) ON DELETE CASCADE,
                        lens TEXT NOT NULL CHECK (lens IN ('tone')),
                        disposition TEXT NOT NULL
                            CHECK (disposition IN ('retain', 'evict')),
                        note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL,
                        UNIQUE (output_id, lens)
                    );

                    INSERT INTO eval_outputs (
                        user_pick,
                        scorey_pick,
                        route_family,
                        round_text,
                        source_mode,
                        model,
                        current_verdict,
                        created_at
                    ) VALUES (
                        'paper',
                        'paper',
                        'same-pick',
                        'legacy pending row',
                        'live',
                        'gpt-5-nano',
                        NULL,
                        '2026-05-09T00:00:00+00:00'
                    );
                    """
                )

            init_db(db_path)

            rows = list_outputs(db_path, limit=5, verdict="pending")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["current_verdict"], "pending")

            summary = counts(db_path)
            self.assertEqual(summary["total"], 1)
            self.assertEqual(summary["pending"], 1)

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

    def test_tone_archive_removes_pending_row_from_active_sample(self) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            archived_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="archived paper tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            active_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="active paper tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, archived_id, "pass", "route pass")
            judge_output(db_path, active_id, "pass", "route pass")
            archive_output_for_lens(
                db_path,
                archived_id,
                lens="tone",
                note="paper seam archived out of active queue",
            )

            rows = list_lens_review_sample(
                db_path,
                lens="tone",
                source_mode="live",
                limit=5,
                user_picks=("paper",),
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["id"]), active_id)

            summary = lens_counts(
                db_path,
                lens="tone",
                source_mode="live",
                user_picks=("paper",),
            )
            self.assertEqual(summary["total"], 2)
            self.assertEqual(summary["pass"], 0)
            self.assertEqual(summary["fail"], 0)
            self.assertEqual(summary["pending"], 1)
            self.assertEqual(summary["archived"], 1)

    def test_tone_failure_disposition_sample_skips_disposed_and_archived_failed_rows(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            pending_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="pending tone fail row",
                source_mode="live",
                model="gpt-5-nano",
            )
            disposed_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="disposed tone fail row",
                source_mode="live",
                model="gpt-5-nano",
            )
            archived_id = record_output(
                db_path,
                user_pick="scissors",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="archived tone fail row",
                source_mode="live",
                model="gpt-5-nano",
            )
            pass_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="tone pass row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, pending_id, "pass", "route pass")
            judge_output(db_path, disposed_id, "pass", "route pass")
            judge_output(db_path, archived_id, "pass", "route pass")
            judge_output(db_path, pass_id, "pass", "route pass")
            judge_output_for_lens(
                db_path,
                pending_id,
                lens="tone",
                verdict="fail",
                note="generic and thin",
            )
            judge_output_for_lens(
                db_path,
                disposed_id,
                lens="tone",
                verdict="fail",
                note="generic and thin",
            )
            judge_output_for_lens(
                db_path,
                archived_id,
                lens="tone",
                verdict="fail",
                note="generic and thin",
            )
            judge_output_for_lens(
                db_path,
                pass_id,
                lens="tone",
                verdict="pass",
                note="pick-aware playful confident coherent imaginative",
            )
            record_failure_disposition_for_lens(
                db_path,
                disposed_id,
                lens="tone",
                disposition="retain",
                note="keep in active lane",
            )
            archive_failure_disposition_for_lens(
                db_path,
                archived_id,
                lens="tone",
                note="historical stale fail",
            )

            rows = list_lens_failure_disposition_sample(
                db_path,
                lens="tone",
                source_mode="live",
                limit=5,
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["id"]), pending_id)

            summary = lens_failure_disposition_counts(
                db_path,
                lens="tone",
                source_mode="live",
            )
            self.assertEqual(summary["total"], 3)
            self.assertEqual(summary["retain"], 1)
            self.assertEqual(summary["evict"], 0)
            self.assertEqual(summary["pending"], 1)
            self.assertEqual(summary["archived"], 1)
