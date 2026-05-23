from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TextIO, cast
from unittest import TestCase
from unittest.mock import patch

from scorey.eval_db import (
    init_db,
    judge_output,
    judge_output_for_lens,
    lens_counts,
    record_output,
)
from scorey.eval_sampling import EvalSampleSummary
from scorey.main import (
    build_round_scene_lines,
    choose_banner_lines,
    main,
    read_selector_key,
)


class _FakeTTYStream:
    def __init__(self, reads: list[str], fileno: int = 99) -> None:
        self._reads = reads
        self._fileno = fileno

    def isatty(self) -> bool:
        return True

    def fileno(self) -> int:
        return self._fileno

    def read(self, _count: int) -> str:
        if not self._reads:
            raise AssertionError("Unexpected extra read")
        return self._reads.pop(0)


class MainCommandTests(TestCase):
    def test_choose_banner_lines_uses_box_when_wide(self) -> None:
        lines = choose_banner_lines(terminal_width=80)

        self.assertEqual(
            lines[0], "┌──────────────────────────────────────────────────────────────┐"
        )
        self.assertIn("SCOREY RESEARCH PRE-BETA 8.0", lines[1])

    def test_choose_banner_lines_uses_stacked_header_when_mid_width(self) -> None:
        lines = choose_banner_lines(terminal_width=56)

        self.assertEqual(
            lines,
            (
                "SCOREY RESEARCH PRE-BETA 8.0",
                "scorey keeps the score and you've already lost.",
                "github.com/tryskian/scorey",
            ),
        )

    def test_choose_banner_lines_uses_minimal_header_when_narrow(self) -> None:
        lines = choose_banner_lines(terminal_width=40)

        self.assertEqual(
            lines,
            (
                "scorey research pre-beta 8.0",
                "scorey keeps the score and",
                "you've already lost.",
                "sorry.",
                "github.com/tryskian/scorey",
            ),
        )

    def test_choose_banner_lines_drops_repo_when_tiny(self) -> None:
        lines = choose_banner_lines(terminal_width=24)

        self.assertEqual(
            lines,
            (
                "scorey research pre-beta 8.0",
                "scorey keeps the score and",
                "you've already lost.",
                "sorry.",
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

    def test_read_selector_key_returns_esc_without_waiting_for_followup_byte(
        self,
    ) -> None:
        stream = _FakeTTYStream(["\x1b"])

        with patch("scorey.main.termios.tcgetattr", return_value=object()):
            with patch("scorey.main.tty.setraw"):
                with patch("scorey.main.termios.tcsetattr"):
                    with patch(
                        "scorey.main.select.select",
                        return_value=([], [], []),
                    ):
                        self.assertEqual(read_selector_key(cast(TextIO, stream)), "ESC")

    def test_read_selector_key_still_parses_arrow_sequences(self) -> None:
        stream = _FakeTTYStream(["\x1b", "[", "B"])

        with patch("scorey.main.termios.tcgetattr", return_value=object()):
            with patch("scorey.main.tty.setraw"):
                with patch("scorey.main.termios.tcsetattr"):
                    with patch(
                        "scorey.main.select.select",
                        side_effect=[
                            ([stream.fileno()], [], []),
                            ([stream.fileno()], [], []),
                        ],
                    ):
                        self.assertEqual(
                            read_selector_key(cast(TextIO, stream)),
                            "DOWN",
                        )

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

    def test_eval_list_filtered_empty_subset_reports_no_matching_rows(self) -> None:
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
                    result = main(["eval-list", "--limit", "5", "--verdict", "pass"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("eval counts: total=1 pass=0 fail=0 pending=1", output)
        self.assertIn("no pass eval outputs.", output)
        self.assertNotIn("no eval outputs yet.", output)

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

    def test_eval_tone_sample_lists_distinct_pending_live_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            first_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="first tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            second_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="second tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            other_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="third tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, first_id, "pass", "route pass")
            judge_output(db_path, second_id, "pass", "route pass")
            judge_output(db_path, other_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(["eval-tone-sample", "--limit", "5"])

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("tone counts: total=3 pass=0 fail=0 pending=3", output)
        self.assertIn("tone sample: newest pending live row per model/pair", output)
        self.assertIn("second tone row", output)
        self.assertIn("third tone row", output)
        self.assertNotIn("first tone row", output)

    def test_eval_tone_sample_can_filter_to_one_user_pick(self) -> None:
        stdout = io.StringIO()
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
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(
                        ["eval-tone-sample", "--limit", "5", "--pick", "paper"]
                    )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("tone counts: total=1 pass=0 fail=0 pending=1", output)
        self.assertIn("user_picks=paper", output)
        self.assertIn("paper tone row", output)
        self.assertNotIn("rock tone row", output)

    def test_eval_tone_judge_records_lens_verdict(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            output_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, output_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    result = main(
                        [
                            "eval-tone-judge",
                            str(output_id),
                            "pass",
                            "--note",
                            "pick-aware playful confident coherent imaginative",
                        ]
                    )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn(f"judged tone output {output_id}: pass", output)
        self.assertIn("tone row", output)

    def test_eval_tone_archive_records_archive_and_updates_sample_counts(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            archived_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="archived tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            active_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="active tone row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, archived_id, "pass", "route pass")
            judge_output(db_path, active_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    archive_result = main(
                        [
                            "eval-tone-archive",
                            str(archived_id),
                            "--note",
                            "paper seam archived out of active queue",
                        ]
                    )
                    sample_result = main(
                        ["eval-tone-sample", "--limit", "5", "--pick", "paper"]
                    )

        self.assertEqual(archive_result, 0)
        self.assertEqual(sample_result, 0)
        output = stdout.getvalue()
        self.assertIn(f"archived tone output {archived_id}", output)
        self.assertIn("tone counts: total=2 pass=0 fail=0 pending=1 archived=1", output)
        self.assertIn("active tone row", output)
        self.assertNotIn("archived tone row", output.split("tone sample:")[-1])

    def test_eval_scoreboard_sample_judge_and_archive_cover_row_level_lane(
        self,
    ) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            archived_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="paper",
                route_family="same-pick",
                round_text="archived scoreboard row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judged_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="judged scoreboard row",
                source_mode="live",
                model="gpt-5-nano",
            )
            active_id = record_output(
                db_path,
                user_pick="scissors",
                scorey_pick="scissors",
                route_family="same-pick",
                round_text="active scoreboard row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, archived_id, "pass", "route pass")
            judge_output(db_path, judged_id, "pass", "route pass")
            judge_output(db_path, active_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    archive_result = main(
                        [
                            "eval-scoreboard-archive",
                            str(archived_id),
                            "--note",
                            "staged out of the first scoreboard lane",
                        ]
                    )
                    judge_result = main(
                        [
                            "eval-scoreboard-judge",
                            str(judged_id),
                            "pass",
                            "--note",
                            "compact unfair losing-side claim",
                        ]
                    )
                    sample_result = main(["eval-scoreboard-sample", "--limit", "5"])

        self.assertEqual(archive_result, 0)
        self.assertEqual(judge_result, 0)
        self.assertEqual(sample_result, 0)
        output = stdout.getvalue()
        self.assertIn(
            f"archived scoreboard output {archived_id}",
            output,
        )
        self.assertIn(
            f"judged scoreboard output {judged_id}: pass",
            output,
        )
        self.assertIn(
            "scoreboard counts: total=3 pass=1 fail=0 pending=1 archived=1",
            output,
        )
        self.assertIn("active scoreboard row", output)
        self.assertNotIn(
            "archived scoreboard row", output.split("scoreboard sample:")[-1]
        )

    def test_eval_scoreboard_close_settles_tone_lane_after_row_level_review(
        self,
    ) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            first_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="first bounded scoreboard row",
                source_mode="live",
                model="gpt-5-nano",
            )
            second_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="second bounded scoreboard row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, first_id, "pass", "route pass")
            judge_output(db_path, second_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    judge_first_result = main(
                        [
                            "eval-scoreboard-judge",
                            str(first_id),
                            "pass",
                            "--note",
                            "compact unfair losing-side claim",
                        ]
                    )
                    judge_second_result = main(
                        [
                            "eval-scoreboard-judge",
                            str(second_id),
                            "fail",
                            "--note",
                            "contradictory losing-side claim",
                        ]
                    )
                    close_result = main(
                        [
                            "eval-scoreboard-close",
                            "--first-output-id",
                            str(first_id),
                            "--last-output-id",
                            str(second_id),
                            "--note",
                            "settled by first bounded scoreboard run",
                        ]
                    )

            tone_summary = lens_counts(db_path, lens="tone")

        self.assertEqual(judge_first_result, 0)
        self.assertEqual(judge_second_result, 0)
        self.assertEqual(close_result, 0)
        self.assertEqual(int(tone_summary["pending"] or 0), 0)
        self.assertEqual(int(tone_summary["archived"] or 0), 2)
        output = stdout.getvalue()
        self.assertIn(
            f"judged scoreboard output {first_id}: pass",
            output,
        )
        self.assertIn(
            f"judged scoreboard output {second_id}: fail",
            output,
        )
        self.assertIn(
            f"closed scoreboard range {first_id}-{second_id}",
            output,
        )
        self.assertIn(
            "scoreboard range counts: total=2 pass=1 fail=1 pending=0",
            output,
        )
        self.assertIn("settled tone rows: 2", output)

    def test_eval_prose_sample_judge_archive_and_close_cover_row_level_lane(
        self,
    ) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            archived_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="archived prose row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judged_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="judged prose row",
                source_mode="live",
                model="gpt-5-nano",
            )
            active_id = record_output(
                db_path,
                user_pick="scissors",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="active prose row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, archived_id, "pass", "route pass")
            judge_output(db_path, judged_id, "pass", "route pass")
            judge_output(db_path, active_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    archive_result = main(
                        [
                            "eval-prose-archive",
                            str(archived_id),
                            "--note",
                            "staged out of the first prose lane",
                        ]
                    )
                    judge_result = main(
                        [
                            "eval-prose-judge",
                            str(judged_id),
                            "pass",
                            "--note",
                            "coherent unfair prose",
                        ]
                    )
                    sample_result = main(["eval-prose-sample", "--limit", "5"])

        self.assertEqual(archive_result, 0)
        self.assertEqual(judge_result, 0)
        self.assertEqual(sample_result, 0)
        output = stdout.getvalue()
        self.assertIn(
            f"archived prose output {archived_id}",
            output,
        )
        self.assertIn(
            f"judged prose output {judged_id}: pass",
            output,
        )
        self.assertIn(
            "prose counts: total=3 pass=1 fail=0 pending=1 archived=1",
            output,
        )
        self.assertIn("active prose row", output)
        self.assertNotIn("archived prose row", output.split("prose sample:")[-1])

    def test_eval_prose_close_settles_tone_and_scoreboard_lanes(
        self,
    ) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)
            first_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="first bounded prose row",
                source_mode="live",
                model="gpt-5-nano",
            )
            second_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="second bounded prose row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, first_id, "pass", "route pass")
            judge_output(db_path, second_id, "pass", "route pass")
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    judge_first_result = main(
                        [
                            "eval-prose-judge",
                            str(first_id),
                            "pass",
                            "--note",
                            "coherent unfair prose",
                        ]
                    )
                    judge_second_result = main(
                        [
                            "eval-prose-judge",
                            str(second_id),
                            "fail",
                            "--note",
                            "generic filler drift",
                        ]
                    )
                    close_result = main(
                        [
                            "eval-prose-close",
                            "--first-output-id",
                            str(first_id),
                            "--last-output-id",
                            str(second_id),
                            "--note",
                            "settled by first bounded prose run",
                        ]
                    )

            tone_summary = lens_counts(db_path, lens="tone")
            scoreboard_summary = lens_counts(db_path, lens="scoreboard")

        self.assertEqual(judge_first_result, 0)
        self.assertEqual(judge_second_result, 0)
        self.assertEqual(close_result, 0)
        self.assertEqual(int(tone_summary["pending"] or 0), 0)
        self.assertEqual(int(tone_summary["archived"] or 0), 2)
        self.assertEqual(int(scoreboard_summary["pending"] or 0), 0)
        self.assertEqual(int(scoreboard_summary["archived"] or 0), 2)
        output = stdout.getvalue()
        self.assertIn(
            f"judged prose output {first_id}: pass",
            output,
        )
        self.assertIn(
            f"judged prose output {second_id}: fail",
            output,
        )
        self.assertIn(
            f"closed prose range {first_id}-{second_id}",
            output,
        )
        self.assertIn(
            "prose range counts: total=2 pass=1 fail=1 pending=0",
            output,
        )
        self.assertIn("settled lower-lens rows: tone=2 scoreboard=2", output)

    def test_eval_tone_disposition_sample_dispose_and_archive_cover_failed_rows(
        self,
    ) -> None:
        stdout = io.StringIO()
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
                user_pick="paper",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="archived tone fail row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, pending_id, "pass", "route pass")
            judge_output(db_path, disposed_id, "pass", "route pass")
            judge_output(db_path, archived_id, "pass", "route pass")
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
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    before_result = main(
                        [
                            "eval-tone-disposition-sample",
                            "--limit",
                            "5",
                            "--pick",
                            "paper",
                        ]
                    )
                    dispose_result = main(
                        [
                            "eval-tone-dispose",
                            str(disposed_id),
                            "retain",
                            "--note",
                            "keep in active lane",
                        ]
                    )
                    archive_result = main(
                        [
                            "eval-tone-disposition-archive",
                            str(archived_id),
                            "--note",
                            "historical stale fail",
                        ]
                    )
                    after_result = main(
                        [
                            "eval-tone-disposition-sample",
                            "--limit",
                            "5",
                            "--pick",
                            "paper",
                        ]
                    )

        self.assertEqual(before_result, 0)
        self.assertEqual(dispose_result, 0)
        self.assertEqual(archive_result, 0)
        self.assertEqual(after_result, 0)
        output = stdout.getvalue()
        self.assertIn(
            "tone fail disposition counts: total=3 retain=0 evict=0 pending=3",
            output,
        )
        self.assertIn(
            f"recorded tone disposition for output {disposed_id}: retain",
            output,
        )
        self.assertIn(
            f"archived tone disposition output {archived_id}",
            output,
        )
        self.assertIn(
            (
                "tone fail disposition counts: total=3 retain=1 evict=0 "
                "pending=1 archived=1"
            ),
            output,
        )
        self.assertIn("pending tone fail row", output)

    def test_eval_pulse_commands_cover_open_sample_judge_summary_and_close(
        self,
    ) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            init_db(db_path)

            anchor_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="anchor row",
                source_mode="live",
                model="gpt-5-nano",
            )
            seam_id = record_output(
                db_path,
                user_pick="scissors",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="counted seam row",
                source_mode="live",
                model="gpt-5-nano",
            )
            artifact_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="paper",
                route_family="cross-object",
                round_text="operator artifact row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, anchor_id, "pass", "route pass")
            judge_output(db_path, seam_id, "pass", "route pass")
            judge_output(db_path, artifact_id, "pass", "route pass")

            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with redirect_stdout(stdout):
                    open_result = main(
                        [
                            "eval-pulse-open",
                            "--first-output-id",
                            str(anchor_id),
                            "--last-output-id",
                            str(artifact_id),
                            "--target-family",
                            "cross-object coherence drift",
                            "--note",
                            "first bounded pulse",
                        ]
                    )
                    sample_result = main(["eval-pulse-sample", "1", "--limit", "5"])
                    judge_anchor_result = main(
                        ["eval-pulse-judge", "1", str(anchor_id), "anchor"]
                    )
                    judge_seam_result = main(
                        ["eval-pulse-judge", "1", str(seam_id), "counted_seam"]
                    )
                    judge_fail_result = main(
                        [
                            "eval-pulse-judge",
                            "1",
                            str(artifact_id),
                            "excluded_noise",
                            "--reason",
                            "operator_artifact",
                        ]
                    )
                    summary_result = main(["eval-pulse-summary", "1"])
                    close_result = main(["eval-pulse-close", "1"])

        self.assertEqual(open_result, 0)
        self.assertEqual(sample_result, 0)
        self.assertEqual(judge_anchor_result, 0)
        self.assertEqual(judge_seam_result, 0)
        self.assertEqual(judge_fail_result, 0)
        self.assertEqual(summary_result, 0)
        self.assertEqual(close_result, 0)
        output = stdout.getvalue()
        self.assertIn("opened pulse 1", output)
        self.assertIn(
            (
                "pulse [1] target_family=cross-object coherence drift "
                "range=1-3 status=open"
            ),
            output,
        )
        self.assertIn("pulse sample: newest unlabeled row in range", output)
        self.assertIn("operator artifact row", output)
        self.assertIn("judged pulse output 1 in pulse 1: anchor", output)
        self.assertIn("judged pulse output 2 in pulse 1: counted_seam", output)
        self.assertIn(
            "judged pulse output 3 in pulse 1: excluded_noise",
            output,
        )
        self.assertIn("reason: operator_artifact", output)
        self.assertIn(
            (
                "pulse counts: raw=3 anchors=1 counted_seams=1 "
                "excluded_noise=1 counted_total=2 pending=0 verdict=fail"
            ),
            output,
        )
        self.assertIn("closed pulse 1", output)

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

    def test_eval_sample_live_reports_rows(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with patch(
                    "scorey.main.sample_live_eval_outputs",
                    return_value=EvalSampleSummary(
                        recorded=3,
                        first_output_id=101,
                        last_output_id=103,
                        research_beta_1_pass=2,
                        research_beta_1_fail=1,
                        elapsed_seconds=0.25,
                    ),
                ):
                    with redirect_stdout(stdout):
                        result = main(
                            [
                                "eval-sample-live",
                                "--count",
                                "3",
                                "--pick",
                                "rock",
                                "--pick",
                                "paper",
                            ]
                        )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("live eval sample complete: count=3", output)
        self.assertIn("user_picks=rock paper", output)
        self.assertIn(
            "recorded=3 research_beta_1_pass=2 research_beta_1_fail=1",
            output,
        )
        self.assertIn(f"db={db_path}", output)

    def test_eval_sample_live_reports_explicit_pairs(self) -> None:
        stdout = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "evals.sqlite"
            with patch("scorey.main.default_eval_db_path", return_value=db_path):
                with patch(
                    "scorey.main.sample_live_eval_outputs",
                    return_value=EvalSampleSummary(
                        recorded=2,
                        first_output_id=201,
                        last_output_id=202,
                        research_beta_1_pass=2,
                        research_beta_1_fail=0,
                        elapsed_seconds=0.5,
                    ),
                ):
                    with redirect_stdout(stdout):
                        result = main(
                            [
                                "eval-sample-live",
                                "--count",
                                "2",
                                "--pair",
                                "rock,paper",
                                "--pair",
                                "paper,scissors",
                            ]
                        )

        self.assertEqual(result, 0)
        output = stdout.getvalue()
        self.assertIn("live eval sample complete: count=2", output)
        self.assertIn("pairs=rock/paper paper/scissors", output)
        self.assertIn(
            "recorded=2 research_beta_1_pass=2 research_beta_1_fail=0",
            output,
        )
        self.assertIn(f"db={db_path}", output)
