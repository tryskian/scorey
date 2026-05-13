from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scorey.eval_db import (
    init_db,
    judge_output,
    judge_output_for_lens,
    record_failure_disposition_for_lens,
    record_output,
)
from scorey.runtime_state import collect_runtime_state


class RuntimeStateTests(TestCase):
    def test_collect_runtime_state_reports_closed_slice(self) -> None:
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            db_path = repo_root / ".local" / "evals.sqlite"
            init_db(db_path)

            passing_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="pass row",
                source_mode="live",
                model="gpt-5-nano",
            )
            failing_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="rock",
                route_family="same-pick",
                round_text="fail row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, passing_id, "pass", "route pass")
            judge_output(db_path, failing_id, "pass", "route pass")
            judge_output_for_lens(
                db_path,
                passing_id,
                lens="tone",
                verdict="pass",
                note="tone pass",
            )
            judge_output_for_lens(
                db_path,
                failing_id,
                lens="tone",
                verdict="fail",
                note="tone fail",
            )
            record_failure_disposition_for_lens(
                db_path,
                failing_id,
                lens="tone",
                disposition="evict",
                note="evicted",
            )

            state = collect_runtime_state(
                repo_root=repo_root,
                db_path=db_path,
                process_commands=(),
            )

            self.assertEqual(state.batch_state, "closed")
            self.assertIsNone(state.active_boundary_output_id)
            self.assertEqual(state.active_route_pending, 0)
            self.assertEqual(state.active_tone_pending, 0)
            self.assertEqual(state.active_disposition_pending, 0)
            self.assertEqual(state.live_counts["pass"], 2)
            self.assertEqual(state.tone_counts["pass"], 1)
            self.assertEqual(state.tone_counts["fail"], 1)
            self.assertEqual(state.disposition_counts["evict"], 1)

    def test_collect_runtime_state_reports_interrupted_slice(self) -> None:
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            db_path = repo_root / ".local" / "evals.sqlite"
            init_db(db_path)

            closed_id = record_output(
                db_path,
                user_pick="paper",
                scorey_pick="rock",
                route_family="cross-object",
                round_text="closed row",
                source_mode="live",
                model="gpt-5-nano",
            )
            pending_id = record_output(
                db_path,
                user_pick="rock",
                scorey_pick="scissors",
                route_family="cross-object",
                round_text="pending row",
                source_mode="live",
                model="gpt-5-nano",
            )
            judge_output(db_path, closed_id, "pass", "route pass")
            judge_output_for_lens(
                db_path,
                closed_id,
                lens="tone",
                verdict="pass",
                note="tone pass",
            )

            state = collect_runtime_state(
                repo_root=repo_root,
                db_path=db_path,
                process_commands=(),
            )

            self.assertEqual(state.batch_state, "interrupted")
            self.assertEqual(state.active_boundary_output_id, pending_id - 1)
            self.assertEqual(state.active_slice_total, 1)
            self.assertEqual(state.active_route_pending, 1)
            self.assertEqual(state.active_tone_pending, 0)
            self.assertEqual(state.active_disposition_pending, 0)

    def test_collect_runtime_state_reports_running_sampler(self) -> None:
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            db_path = repo_root / ".local" / "evals.sqlite"
            init_db(db_path)

            state = collect_runtime_state(
                repo_root=repo_root,
                db_path=db_path,
                process_commands=(
                    "74885 /Users/tryskian/Github/scorey/.venv/bin/python "
                    "-m scorey eval-sample-live --duration-seconds 3600",
                ),
            )

            self.assertEqual(state.batch_state, "running")
            self.assertEqual(len(state.live_sampler_commands), 1)

    def test_collect_runtime_state_flags_unsymlinked_secondary_worktree_db(
        self,
    ) -> None:
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir) / ".codex" / "worktrees" / "scorey-lane"
            db_path = repo_root / ".local" / "evals.sqlite"
            init_db(db_path)

            state = collect_runtime_state(
                repo_root=repo_root,
                db_path=db_path,
                process_commands=(),
            )

            self.assertTrue(state.in_secondary_worktree)
            self.assertFalse(state.local_dir_is_symlink)
            self.assertTrue(state.split_db_risk)
