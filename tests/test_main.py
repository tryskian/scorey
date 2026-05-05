from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scorey.eval_db import init_db, record_output
from scorey.main import main


class MainCommandTests(TestCase):
    def test_local_play_prints_a_round(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = main(["--local", "play", "rock"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("you: rock", output)
        self.assertIn("me: scissors", output)
        self.assertIn("scorey.", output)

    def test_live_play_without_api_key_fails_cleanly(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch.dict("os.environ", {}, clear=True):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = main(["play", "rock"])

        self.assertEqual(result, 1)
        self.assertIn("OPENAI_API_KEY", stderr.getvalue())

    def test_eval_init_creates_db(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-init"])

            self.assertTrue(db_path.exists())

        self.assertEqual(result, 0)
        self.assertIn("initialized eval db:", stdout.getvalue())

    def test_eval_list_empty_db_prints_counts(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-list", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("eval counts: total=0 pass=0 fail=0 pending=0", output)
        self.assertIn("no eval outputs yet.", output)

    def test_eval_beta_1_empty_db_prints_gate_definition(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-beta-1", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("Beta 1.0 gate: picks only (`scorey_pick`, `user_pick`)", output)
        self.assertIn("- paper / scissors", output)
        self.assertIn("- scissors / scissors", output)
        self.assertIn("fail: all other scorey/user pick pairs.", output)
        self.assertIn("no eval outputs yet.", output)

    def test_eval_beta_1_reports_pass_and_fail_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="my scissors beats your rock because snacks.",
                source_mode="local",
                model="local-fixture",
            )
            record_output(
                db_path,
                user_pick="rock",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="my paper beats your rock because i said so.",
                source_mode="local",
                model="local-fixture",
            )
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-beta-1", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("Beta 1.0 counts: total=2 pass=1 fail=1", output)
        self.assertIn("scorey=paper user=rock", output)
        self.assertIn("reason: not a beta 1.0 route", output)
        self.assertIn("scorey=scissors user=rock", output)
        self.assertIn("reason: reverse gameplay route", output)

    def test_eval_sample_local_records_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                    with redirect_stdout(stdout):
                        result = main(["eval-sample-local", "--count", "3"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("local eval sample complete: count=3", output)
        self.assertIn("pattern=baseline", output)
        self.assertIn("recorded=3 beta_1_pass=3 beta_1_fail=0", output)

    def test_eval_sample_local_beta_1_coverage_reports_pattern(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                    with redirect_stdout(stdout):
                        result = main(
                            [
                                "eval-sample-local",
                                "--count",
                                "6",
                                "--pattern",
                                "beta-1-coverage",
                            ]
                        )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("local eval sample complete: count=6", output)
        self.assertIn("pattern=beta-1-coverage", output)
        self.assertIn("recorded=6 beta_1_pass=6 beta_1_fail=0", output)

    def test_eval_sample_local_explicit_pairs_report_pair_cycle(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
                    with redirect_stdout(stdout):
                        result = main(
                            [
                                "eval-sample-local",
                                "--count",
                                "4",
                                "--pair",
                                "rock,paper",
                                "--pair",
                                "scissors,rock",
                            ]
                        )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("local eval sample complete: count=4", output)
        self.assertIn("pairs=rock/paper scissors/rock", output)
        self.assertIn("recorded=4 beta_1_pass=4 beta_1_fail=0", output)
