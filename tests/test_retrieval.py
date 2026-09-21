from __future__ import annotations

import json
import sqlite3
from contextlib import closing, redirect_stdout
from dataclasses import replace
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from scorey.agent import build_prompt, generate_live_round_fields
from scorey.config import ROOT, Settings, load_settings
from scorey.eval_db import init_db
from scorey.eval_sampling import sample_live_eval_outputs, sample_local_eval_outputs
from scorey.main import build_live_round_state, build_round_text
from scorey.memory import command_memory
from scorey.pipeline import RoundFields
from scorey.retrieval import FrozenMemory, build_index, load_corpus
from scorey.vector_store import fingerprint, read_index, save_index


def embeddings(texts: list[str], model: str) -> list[list[float]]:
    return [[1.0, 0.1 + i / 10] for i, _ in enumerate(texts)]


def result() -> SimpleNamespace:
    return SimpleNamespace(
        final_output=RoundFields("sturdy", "crumpled", "lose"),
        raw_responses=[SimpleNamespace(response_id="response-test")],
    )


class MemoryTests(TestCase):
    def setUp(self) -> None:
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        source = self.root / "docs/diagrams/PIPELINE.md"
        source.parent.mkdir(parents=True)
        source.write_text((ROOT / "docs/diagrams/PIPELINE.md").read_text())
        source_root = patch("scorey.retrieval.ROOT", self.root)
        source_root.start()
        self.addCleanup(source_root.stop)
        self.settings = Settings(
            app_name="Scorey",
            model="test-model",
            memory_enabled=True,
            memory_db_path=str(self.root / "memory.sqlite"),
        )
        version = build_index(self.settings, embedder=embeddings)
        self.settings = replace(self.settings, memory_index=version)

    def test_build_checks_sources_and_retrieval_is_local_and_pair_specific(
        self,
    ) -> None:
        memory = FrozenMemory(self.settings)
        with patch(
            "scorey.retrieval.embed_texts", side_effect=AssertionError("network")
        ):
            same = memory.retrieve("paper", "paper")
            cross = memory.retrieve("paper", "rock")
        for context in (same, cross):
            self.assertLessEqual(len(context.context), self.settings.memory_max_chars)
            self.assertLessEqual(len(context.matches), self.settings.memory_top_k)
            for note in context.matches:
                self.assertIn(note["route"], ("all", context.route_family))
                self.assertIn(note["text"], context.context)
                self.assertTrue(note["source_hash"])
        altered = [{**n, "text": "An unsupported new rule."} for n in load_corpus()]
        with patch("scorey.retrieval.load_corpus", return_value=altered):
            with self.assertRaisesRegex(ValueError, "no longer matches"):
                build_index(self.settings, embedder=embeddings)

    def test_snapshot_is_immutable_and_remains_usable_when_another_is_built(
        self,
    ) -> None:
        original = FrozenMemory(self.settings)
        expected = original.retrieve("rock", "rock").matches
        newer = build_index(
            self.settings, embedder=lambda texts, model: [[0.5, 1.0]] * len(texts)
        )
        self.assertNotEqual(newer, self.settings.memory_index)
        self.assertEqual(original.retrieve("rock", "rock").matches, expected)
        self.assertEqual(
            FrozenMemory(self.settings).retrieve("rock", "rock").matches, expected
        )

    def test_stale_corpus_and_embedding_model_are_errors(self) -> None:
        with self.assertRaisesRegex(ValueError, "embedding model"):
            FrozenMemory(replace(self.settings, memory_embedding_model="different"))
        with patch("scorey.retrieval.load_corpus", return_value=[]):
            with self.assertRaisesRegex(ValueError, "corpus changed"):
                FrozenMemory(self.settings)

    def test_new_operation_checks_sources_but_running_snapshot_stays_frozen(
        self,
    ) -> None:
        relative = "docs/diagrams/PIPELINE.md"
        source = self.root / relative
        with patch("scorey.retrieval.ROOT", self.root):
            memory = FrozenMemory(self.settings)
            expected = memory.retrieve("rock", "rock").matches
            source.write_text(source.read_text() + "\nA later document change.\n")
            with self.assertRaisesRegex(ValueError, "sources changed"):
                FrozenMemory(self.settings)
            self.assertEqual(memory.retrieve("rock", "rock").matches, expected)
            source.write_text("The original principle was removed.\n")
            with self.assertRaisesRegex(ValueError, "no longer matches"):
                FrozenMemory(self.settings)

    def test_normalised_picks_work_with_memory_and_live_generation(self) -> None:
        memory = FrozenMemory(self.settings)
        context = memory.retrieve(" Rock ", " SCISSORS ")
        self.assertEqual(context.user_pick, "rock")
        self.assertEqual(context.scorey_pick, "scissors")
        with patch("agents.Runner.run_sync", return_value=result()) as runner:
            generate_live_round_fields(
                self.settings,
                " Rock ",
                " SCISSORS ",
                "cross-object",
                retrieval_context=context,
            )
        self.assertIn(
            "User pick: rock\nScorey pick: scissors", runner.call_args.args[1]
        )

    def test_both_live_entrypoints_derive_same_pick_from_normalised_values(
        self,
    ) -> None:
        with (
            patch("scorey.main.load_settings", return_value=self.settings),
            patch("scorey.main.require_openai_api_key"),
            patch("scorey.main.choose_scorey_pick", return_value="rock"),
            patch("agents.Runner.run_sync", return_value=result()) as runner,
        ):
            text = build_round_text(" Rock ", local=False, scorey_score=1)
            state = build_live_round_state(
                " Rock ", settings=self.settings, scorey_pick="rock", scorey_score=1
            )
        self.assertIn("you: rock\nme: rock", text)
        self.assertEqual(state.route_family, "same-pick")
        self.assertEqual(runner.call_count, 2)
        self.assertIn("Route family: same-pick", runner.call_args.args[1])

    def test_missing_snapshot_never_creates_a_database_and_tampering_is_detected(
        self,
    ) -> None:
        missing = self.root / "absent.sqlite"
        with self.assertRaisesRegex(ValueError, "unavailable"):
            read_index(missing, "missing")
        self.assertFalse(missing.exists())
        with closing(sqlite3.connect(self.settings.memory_db_path)) as db, db:
            db.execute("UPDATE scorey_memory_indexes SET payload='{}'")
        with self.assertRaisesRegex(ValueError, "integrity"):
            FrozenMemory(self.settings)

    def test_invalid_embeddings_and_using_eval_store_are_rejected(self) -> None:
        for vector in ([0.0, 0.0], [float("nan"), 1.0], [float("inf"), 1.0]):

            def invalid_embeddings(
                texts: list[str], model: str, v: list[float] = vector
            ) -> list[list[float]]:
                return [v] * len(texts)

            with self.subTest(vector=vector):
                with self.assertRaises(ValueError):
                    build_index(
                        self.settings,
                        embedder=invalid_embeddings,
                    )
        with self.assertRaisesRegex(ValueError, "dimensions"):
            build_index(
                self.settings,
                embedder=lambda texts, model: [[1.0]] + [[1.0, 2.0]] * (len(texts) - 1),
            )
        path = self.root / "evals.sqlite"
        with closing(sqlite3.connect(path)) as db, db:
            db.execute("CREATE TABLE eval_outputs (id INTEGER PRIMARY KEY)")
        with self.assertRaisesRegex(ValueError, "separate"):
            save_index(path, {"example": "only"})
        with closing(sqlite3.connect(path)) as db, db:
            self.assertEqual(
                db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall(),
                [("eval_outputs",)],
            )

    def test_context_budget_preserves_whole_notes_and_reports_empty(self) -> None:
        memory = FrozenMemory(replace(self.settings, memory_max_chars=1))
        context = memory.retrieve("rock", "rock")
        self.assertEqual(context.status, "empty")
        self.assertEqual(context.context, "")
        self.assertEqual(context.matches, ())

    def test_generation_records_exact_prompt_context_and_outputs(self) -> None:
        with patch("agents.Runner.run_sync", return_value=result()) as runner:
            fields = generate_live_round_fields(
                self.settings, "paper", "rock", "cross-object"
            )
        self.assertEqual(fields, result().final_output)
        receipts = list((self.root / "memory-receipts").glob("*.json"))
        self.assertEqual(len(receipts), 1)
        receipt = json.loads(receipts[0].read_text())
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["path_base"], "repository root")
        self.assertEqual(receipt["settings"]["memory_db_path"], "memory.sqlite")
        self.assertEqual(receipt["prompt"], runner.call_args.args[1])
        self.assertEqual(receipt["retrieval"]["index"], self.settings.memory_index)
        self.assertIn("instructions", receipt)
        self.assertEqual(receipt["fields"]["scoreboard_claim"], "lose")
        self.assertEqual(receipt["response_ids"], ["response-test"])
        self.assertIn(receipt["retrieval"]["context"], receipt["prompt"])

    def test_generation_failure_retains_the_condition_and_does_not_fallback(
        self,
    ) -> None:
        with patch(
            "agents.Runner.run_sync", side_effect=RuntimeError("failed")
        ) as runner:
            with self.assertRaisesRegex(RuntimeError, "failed"):
                generate_live_round_fields(self.settings, "rock", "rock", "same-pick")
        runner.assert_called_once()
        receipt = json.loads(
            next((self.root / "memory-receipts").glob("*.json")).read_text()
        )
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["error_type"], "RuntimeError")
        self.assertEqual(receipt["retrieval"]["index"], self.settings.memory_index)

    def test_wrong_pair_context_is_rejected_before_generation(self) -> None:
        context = FrozenMemory(self.settings).retrieve("rock", "rock")
        with patch("agents.Runner.run_sync") as runner:
            with self.assertRaisesRegex(ValueError, "does not match"):
                generate_live_round_fields(
                    self.settings,
                    "paper",
                    "paper",
                    "same-pick",
                    retrieval_context=context,
                )
        runner.assert_not_called()

    def test_disabled_generation_preserves_prompt_and_does_not_open_memory(
        self,
    ) -> None:
        settings = replace(self.settings, memory_enabled=False)
        with patch(
            "scorey.agent.FrozenMemory", side_effect=AssertionError("memory opened")
        ):
            with patch("agents.Runner.run_sync", return_value=result()) as runner:
                generate_live_round_fields(settings, "paper", "paper", "same-pick")
        self.assertEqual(
            runner.call_args.args[1], build_prompt("paper", "paper", "same-pick")
        )
        self.assertFalse((self.root / "memory-receipts").exists())

    def test_live_sampler_binds_receipts_and_freezes_index_for_the_batch(self) -> None:
        db_path = self.root / "evals.sqlite"
        calls = 0

        def generate(*args: object, **kwargs: object) -> SimpleNamespace:
            nonlocal calls
            calls += 1
            if calls == 1:
                build_index(
                    self.settings,
                    embedder=lambda texts, model: [[0.5, 1.0]] * len(texts),
                )
            return result()

        with patch("scorey.eval_db.EVAL_DB_PATH", db_path):
            with patch(
                "scorey.eval_sampling.load_settings", return_value=self.settings
            ):
                with patch("scorey.eval_sampling.require_openai_api_key"):
                    with patch("agents.Runner.run_sync", side_effect=generate):
                        summary = sample_live_eval_outputs(
                            count=2, pair_cycle=(("rock", "paper"), ("paper", "paper"))
                        )
        self.assertEqual(summary.recorded, 2)
        with closing(sqlite3.connect(db_path)) as db:
            rows = db.execute(
                "SELECT id,round_text,current_verdict FROM eval_outputs ORDER BY id"
            ).fetchall()
        for output_id, text, verdict in rows:
            receipt = json.loads(
                (self.root / "evals.sqlite.retrieval" / f"{output_id}.json").read_text()
            )
            self.assertEqual(receipt["output_id"], output_id)
            self.assertEqual(receipt["eval_db"], "evals.sqlite")
            generation_path = self.root / receipt["generation_receipt"]
            self.assertTrue(generation_path.is_file())
            self.assertFalse(Path(receipt["generation_receipt"]).is_absolute())
            self.assertEqual(receipt["round_text_hash"], fingerprint(text))
            self.assertEqual(receipt["retrieval"]["index"], self.settings.memory_index)
            self.assertEqual(verdict, "pending")

    def test_local_sampler_never_loads_memory(self) -> None:
        with patch("scorey.eval_db.EVAL_DB_PATH", self.root / "evals.sqlite"):
            with patch(
                "scorey.eval_sampling.FrozenMemory",
                side_effect=AssertionError("memory"),
            ):
                summary = sample_local_eval_outputs(
                    count=6, pattern="research-beta-1-coverage"
                )
        self.assertEqual(summary.recorded, 6)
        self.assertFalse((self.root / "memory-receipts").exists())

    def test_failed_evidence_write_rolls_back_the_eval_row(self) -> None:
        db_path = self.root / "evals.sqlite"
        (self.root / "evals.sqlite.retrieval").write_text("Blocked directory")
        with (
            patch("scorey.eval_db.EVAL_DB_PATH", db_path),
            patch("scorey.eval_sampling.load_settings", return_value=self.settings),
            patch("scorey.eval_sampling.require_openai_api_key"),
            patch("agents.Runner.run_sync", return_value=result()),
        ):
            with self.assertRaises(FileExistsError):
                sample_live_eval_outputs(count=1)
        with closing(sqlite3.connect(db_path)) as db:
            self.assertEqual(
                db.execute("SELECT count(*) FROM eval_outputs").fetchone(), (0,)
            )
        receipt = json.loads(
            next((self.root / "memory-receipts").glob("*.json")).read_text()
        )
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["fields"], result().final_output.__dict__)

    def test_status_and_preview_need_no_credentials_or_embedding_calls(self) -> None:
        with (
            patch("scorey.memory.load_settings", return_value=self.settings),
            patch(
                "scorey.memory.require_openai_api_key",
                side_effect=AssertionError("key"),
            ),
            patch("scorey.memory.build_index", side_effect=AssertionError("build")),
        ):
            with redirect_stdout(StringIO()) as stream:
                self.assertEqual(command_memory("memory-status"), 0)
            self.assertEqual(
                json.loads(stream.getvalue())["index"], self.settings.memory_index
            )
            with redirect_stdout(StringIO()) as stream:
                self.assertEqual(command_memory("memory-preview", "paper", "paper"), 0)
            self.assertEqual(json.loads(stream.getvalue())["route_family"], "same-pick")

    def test_commit_failure_cleans_sidecar_and_next_attempt_can_record(self) -> None:
        db_path = self.root / "evals.sqlite"
        init_db(db_path)

        def short_connection(path: Path | None = None) -> sqlite3.Connection:
            conn = sqlite3.connect(db_path, timeout=0.01)
            conn.row_factory = sqlite3.Row
            return conn

        with (
            patch("scorey.eval_db.EVAL_DB_PATH", db_path),
            patch("scorey.eval_db.connect", side_effect=short_connection),
            patch("scorey.eval_sampling.load_settings", return_value=self.settings),
            patch("scorey.eval_sampling.require_openai_api_key"),
            patch("agents.Runner.run_sync", return_value=result()),
        ):
            with closing(sqlite3.connect(db_path)) as reader:
                reader.execute("BEGIN")
                reader.execute("SELECT * FROM eval_outputs").fetchall()
                with self.assertRaisesRegex(sqlite3.OperationalError, "locked"):
                    sample_live_eval_outputs(count=1)
                self.assertEqual(
                    reader.execute("SELECT count(*) FROM eval_outputs").fetchone(), (0,)
                )
            self.assertEqual(
                list((self.root / "evals.sqlite.retrieval").glob("*.json")), []
            )
            summary = sample_live_eval_outputs(count=1)
        self.assertEqual(summary.first_output_id, 1)
        self.assertTrue((self.root / "evals.sqlite.retrieval/1.json").exists())

    def test_memory_configuration_rejects_invalid_limits_and_flag(self) -> None:
        for overrides in (
            {"SCOREY_MEMORY_TOP_K": "0"},
            {"SCOREY_MEMORY_MAX_CHARS": "0"},
            {"SCOREY_MEMORY_ENABLED": "maybe"},
        ):
            with patch.dict("os.environ", overrides, clear=True):
                with patch("scorey.config.load_dotenv", None):
                    with self.assertRaises(ValueError):
                        load_settings()
