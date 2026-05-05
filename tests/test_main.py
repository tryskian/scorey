from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scorey.eval_db import init_db, record_output
from scorey.main import build_round_scene_lines, choose_banner_lines, main


class MainCommandTests(TestCase):
    def test_choose_banner_lines_uses_box_when_wide(self) -> None:
        lines = choose_banner_lines(terminal_width=80)

        self.assertEqual(
            lines[0], "┌──────────────────────────────────────────────────────────────┐"
        )
        self.assertIn("SCOREY RESEARCH BETA 2.0", lines[1])

    def test_choose_banner_lines_uses_stacked_header_when_mid_width(self) -> None:
        lines = choose_banner_lines(terminal_width=56)

        self.assertEqual(
            lines,
            (
                "SCOREY RESEARCH BETA 2.0",
                "scorey keeps the score. you never win. sorry.",
                "github.com/tryskian/scorey",
            ),
        )

    def test_choose_banner_lines_uses_minimal_header_when_narrow(self) -> None:
        lines = choose_banner_lines(terminal_width=40)

        self.assertEqual(
            lines,
            (
                "scorey research beta 2.0",
                "scorey keeps the score.",
                "you never win. sorry.",
                "github.com/tryskian/scorey",
            ),
        )

    def test_choose_banner_lines_drops_repo_when_tiny(self) -> None:
        lines = choose_banner_lines(terminal_width=24)

        self.assertEqual(
            lines,
            (
                "scorey research beta 2.0",
                "scorey keeps the score.",
                "you never win. sorry.",
            ),
        )

    def test_choose_banner_lines_styles_repo_when_active(self) -> None:
        lines = choose_banner_lines(terminal_width=80, style_active=True)

        self.assertIn("\x1b]8;;https://github.com/tryskian/scorey\x1b\\", lines[4])
        self.assertIn("\x1b[1m", lines[4])
        self.assertIn("\x1b[38;5;117m", lines[4])

    def test_round_scene_keeps_consistent_height_across_reveal_states(self) -> None:
        hidden_lines = build_round_scene_lines(selected_index=1)
        loading_lines = build_round_scene_lines(
            selected_index=1,
            revealed_scorey_pick="rock",
            loading_frame="⠋",
        )

        self.assertEqual(len(hidden_lines), len(loading_lines))
        self.assertEqual(hidden_lines[7], "me:")
        self.assertEqual(hidden_lines[8], "  [inactive until you press enter]")

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
            with patch("scorey.config.load_dotenv", None):
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

    def test_eval_list_pending_filter_prints_pending_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            record_output(
                db_path,
                user_pick="paper",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="my scissors beats your paper because snacks.",
                source_mode="local",
                model="local-fixture",
            )
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-list", "--limit", "5", "--verdict", "pending"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("eval counts: total=1 pass=0 fail=0 pending=1", output)
        self.assertIn("(cross-object, local, pending)", output)

    def test_research_beta_1_empty_db_prints_gate_definition(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["research-beta-1", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn(
            "Research Beta 1.0 gate: picks only (`scorey_pick`, `user_pick`)",
            output,
        )
        self.assertIn("- paper / scissors", output)
        self.assertIn("- scissors / scissors", output)
        self.assertIn("fail: all other scorey/user pick pairs.", output)
        self.assertIn("no eval outputs yet.", output)

    def test_research_beta_1_reports_pass_and_fail_rows(self) -> None:
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
                    result = main(["research-beta-1", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("Research Beta 1.0 counts: total=2 pass=1 fail=1", output)
        self.assertIn("scorey=paper user=rock", output)
        self.assertIn("reason: not a research beta 1.0 route", output)
        self.assertIn("scorey=scissors user=rock", output)
        self.assertIn("reason: reverse gameplay route", output)

    def test_eval_beta_1_alias_still_works(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-beta-1", "--limit", "5"])

        self.assertEqual(result, 0)
        self.assertIn(
            "Research Beta 1.0 gate: picks only (`scorey_pick`, `user_pick`)",
            stdout.getvalue(),
        )

    def test_eval_review_sample_lists_distinct_pending_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="first",
                source_mode="local",
                model="batch-a",
            )
            record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="second",
                source_mode="local",
                model="batch-a",
            )
            record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="third",
                source_mode="local",
                model="batch-a",
            )
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-review-sample", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("review sample: newest pending row per model/pair", output)
        self.assertIn("second", output)
        self.assertIn("third", output)
        self.assertNotIn("first", output)

    def test_eval_judge_updates_output(self) -> None:
        stdout = io.StringIO()
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
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(
                        [
                            "eval-judge",
                            str(output_id),
                            "pass",
                            "--note",
                            "route-valid and legible",
                        ]
                    )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn(f"judged output {output_id}: pass", output)
        self.assertIn("note: route-valid and legible", output)
        self.assertIn("(cross-object, local, pass)", output)

    def test_eval_judge_can_render_older_output_ids(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            first_output_id = None
            for index in range(1005):
                output_id = record_output(
                    db_path,
                    user_pick="rock",
                    scorey_pick="scissors",
                    route_family="cross-object",
                    round_text=f"row {index}",
                    source_mode="local",
                    model="local-fixture",
                )
                if first_output_id is None:
                    first_output_id = output_id
            assert first_output_id is not None
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(
                        [
                            "eval-judge",
                            str(first_output_id),
                            "pass",
                            "--note",
                            "route-valid and legible",
                        ]
                    )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn(f"judged output {first_output_id}: pass", output)
        self.assertIn("row 0", output)

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
        self.assertIn(
            "recorded=3 research_beta_1_pass=3 research_beta_1_fail=0",
            output,
        )

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
                                "research-beta-1-coverage",
                            ]
                        )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("local eval sample complete: count=6", output)
        self.assertIn("pattern=research-beta-1-coverage", output)
        self.assertIn(
            "recorded=6 research_beta_1_pass=6 research_beta_1_fail=0",
            output,
        )

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
        self.assertIn(
            "recorded=4 research_beta_1_pass=4 research_beta_1_fail=0",
            output,
        )
