import copy
import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest import TestCase, skipUnless
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "output/jupyter-notebook/scorey_smoke_review.py"
)
SPEC = importlib.util.spec_from_file_location("scorey_smoke_review", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
workbench = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = workbench
SPEC.loader.exec_module(workbench)


def sample_dataset() -> dict:
    cases = []
    for ordinal, (case_id, scorey, user) in enumerate(
        (("paper-scissors", "paper", "scissors"), ("rock-rock", "rock", "rock")), 1
    ):
        case = {
            "id": case_id,
            "scorey_pick": scorey,
            "user_pick": user,
            "route_family": "same-pick" if scorey == user else "cross-object",
            "starting_score": 1,
            "purpose": "Explain the relationship.",
            "prompt": "Actual frozen prompt.",
        }
        receipt = {
            "case_id": case_id,
            "round_text": f"you: {user}\nme: {scorey}\n\n”Exact” <source>\n",
            "response_id": f"resp_{ordinal}",
            "status": "completed",
            "quality_verdict": None,
            "elapsed_seconds": 3.2,
            "usage": {"input_tokens": 100, "output_tokens": 40, "total_tokens": 140},
            "route_check": {"verdict": "pass", "reason": "valid route"},
            "mechanical_checks": {"ok": True, "issues": []},
            "normalized_round": {"scorey_score": 1},
            "returned_settings": {"model": "returned-model", "temperature": 1.0},
        }
        cases.append(
            {
                "case_id": case_id,
                "ordinal": ordinal,
                "case": case,
                "receipt": receipt,
                "receipt_sha256": str(ordinal) * 64,
                "request_sha256": "3" * 64,
                "response_sha256": "4" * 64,
            }
        )
    return {
        "dataset_id": "test-frozen-run",
        "manifest_sha256": "5" * 64,
        "criteria_id": "coherent-absurdity-review-1",
        "criteria_sha256": "6" * 64,
        "criteria_text": "Does the invented relationship make the unfair win follow?",
        "manifest": {
            "settings": {"model": "requested-model", "reasoning_effort": "medium"},
            "instructions": "Actual frozen instructions.",
        },
        "cases": cases,
        "events": [],
    }


class SmokeReviewWorkbenchTests(TestCase):
    def setUp(self) -> None:
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.db_path = self.root / "evals.sqlite"
        self.db_path.write_bytes(b"read-only source placeholder")
        self.notes_path = self.root / "review.notes.json"
        self.dataset = sample_dataset()
        self.dataset["source_path"] = str(self.root / "frozen")
        mock_load = patch.object(
            workbench,
            "load_dataset",
            side_effect=lambda *_: copy.deepcopy(self.dataset),
        )
        self.load_dataset = mock_load.start()
        self.addCleanup(mock_load.stop)

    def load(self) -> Any:
        return workbench.load_review(self.db_path, self.notes_path)

    def test_initial_quality_pending_despite_mechanical_pass_and_read_only_load(
        self,
    ) -> None:
        source = self.db_path.read_bytes()
        session = self.load()
        self.assertEqual(session.current_review["verdict"], "Pending")
        self.assertEqual(session.events, [])
        self.assertFalse(session.dirty)
        self.assertFalse(self.notes_path.exists())
        self.assertEqual(self.db_path.read_bytes(), source)
        rendered = workbench.round_html(session.dataset, session.current_case)
        self.assertIn("&lt;source&gt;", rendered)
        self.assertNotIn("<source>", rendered)
        self.assertIn("140 total", rendered)
        self.assertIn("requested-model", rendered)
        self.assertIn("returned-model", rendered)
        self.assertIn("Automated route check", rendered)
        self.assertIn("Checks passed", rendered)
        self.assertNotIn("PASS", rendered)

    def test_navigation_and_independent_observation_save_preserve_attribution(
        self,
    ) -> None:
        session = self.load()
        exact = "  Good premise ”but”\u2028needs a connection.\n  "
        session.update(observation=exact, observation_phrase="”but”")
        session.navigate(1)
        session.update(verdict="FAIL", reason="The copies are only ranked.")
        session.navigate(-1)
        self.assertEqual(session.current_review["observation"], exact)
        self.assertFalse(self.notes_path.exists())
        source = self.db_path.read_bytes()
        workbench.save_review(session)
        self.assertFalse(session.dirty)
        self.assertEqual(self.db_path.read_bytes(), source)
        restored = self.load()
        self.assertEqual(restored.current_review["verdict"], "Pending")
        self.assertEqual(restored.current_review["observation"], exact)
        first = restored.events[0]
        self.assertEqual(first["author"], "Peanut")
        self.assertEqual(first["role"], "human")
        self.assertEqual(first["kind"], "observation")
        self.assertIsNone(first["verdict"])
        self.assertEqual(first["field_or_phrase"], "”but”")
        restored.navigate(1)
        self.assertEqual(restored.current_review["verdict"], "FAIL")

    def test_revisions_append_and_assistant_notes_never_become_human_defaults(
        self,
    ) -> None:
        assistant = workbench.new_event(
            self.dataset,
            "paper-scissors",
            "Scorey engineer",
            "observation",
            "The winning condition is unclear.",
            role="assistant",
        )
        self.dataset["events"] = [assistant]
        session = self.load()
        self.assertEqual(session.current_review["observation"], "")
        session.update(
            verdict="FAIL", reason="I love the premise but it is incoherent."
        )
        workbench.save_review(session)
        original = copy.deepcopy(session.events)
        session.update(verdict="PASS", reason="A second reading makes the link clear.")
        workbench.save_review(session)
        self.assertEqual(session.events[:2], original)
        self.assertEqual(len(session.events), 3)
        self.assertEqual(self.dataset["events"], [assistant])
        restored = self.load()
        self.assertEqual(restored.current_review["verdict"], "PASS")
        self.assertEqual(restored.events[0], assistant)

    def test_stale_save_keeps_edits_and_does_not_overwrite_other_notes(self) -> None:
        first, second = self.load(), self.load()
        first.update(observation="First observer's note")
        workbench.save_review(first)
        saved = self.notes_path.read_bytes()
        second.update(observation="Other unsaved note")
        with self.assertRaises(workbench.ReviewError):
            workbench.save_review(second)
        self.assertTrue(second.dirty)
        self.assertEqual(second.current_review["observation"], "Other unsaved note")
        self.assertEqual(self.notes_path.read_bytes(), saved)

    def test_observation_edit_preserves_existing_judgment_and_other_author(
        self,
    ) -> None:
        self.dataset["events"] = [
            workbench.new_event(
                self.dataset,
                "paper-scissors",
                "Peanut",
                "judgment",
                "A clear connection.",
                verdict="PASS",
                field_or_phrase="winning_state",
            ),
            workbench.new_event(
                self.dataset,
                "paper-scissors",
                "Peanut",
                "observation",
                "An assistant using the same display name.",
                role="assistant",
            ),
        ]
        original = copy.deepcopy(self.dataset["events"])
        session = self.load()
        self.assertEqual(session.current_review["observation"], "")
        session.update(observation="The phrasing repeats across rounds.")
        workbench.save_review(session)
        self.assertEqual(session.events[:2], original)
        self.assertEqual(session.events[-1]["kind"], "observation")
        self.assertIsNone(session.events[-1]["verdict"])
        self.assertEqual(self.load().current_review["verdict"], "PASS")
        self.assertEqual(self.load().current_review["reason"], "A clear connection.")

    def test_duplicate_imported_sidecar_event_is_displayed_once(self) -> None:
        session = self.load()
        session.update(observation="Original observation.")
        workbench.save_review(session)
        self.dataset["events"] = copy.deepcopy(session.events)
        restored = self.load()
        self.assertEqual(len(restored.events), 1)
        before = self.notes_path.read_bytes()
        workbench.save_review(restored)
        self.assertEqual(self.notes_path.read_bytes(), before)

    def test_pending_reason_cannot_silently_become_a_judgment_or_erase_one(
        self,
    ) -> None:
        session = self.load()
        session.update(reason="Only a draft judgment.")
        with self.assertRaises(workbench.ReviewError):
            workbench.save_review(session)
        self.assertFalse(self.notes_path.exists())
        session.update(verdict="FAIL")
        workbench.save_review(session)
        saved = self.notes_path.read_bytes()
        session.update(verdict="Pending")
        with self.assertRaises(workbench.ReviewError):
            workbench.save_review(session)
        self.assertEqual(self.notes_path.read_bytes(), saved)

    @skipUnless(importlib.util.find_spec("ipywidgets"), "ipywidgets is optional")
    def test_widgets_keep_exact_notes_and_show_separate_attributed_history(
        self,
    ) -> None:
        widgets = importlib.import_module("ipywidgets")

        exact = "  ”premise”\u2028a second thought\u2029last line\n"
        self.dataset["events"] = [
            workbench.new_event(
                self.dataset,
                "paper-scissors",
                "Peanut",
                "observation",
                exact,
            ),
            workbench.new_event(
                self.dataset,
                "paper-scissors",
                "Scorey engineer",
                "observation",
                "<script>not executable</script>",
                role="assistant",
            ),
        ]
        session = self.load()
        panel = workbench.build_workbench(session)
        descendants, pending = [], [panel]
        while pending:
            widget = pending.pop()
            descendants.append(widget)
            pending.extend(getattr(widget, "children", ()))
            self.addCleanup(widget.close)
        buttons = {
            item.description: item
            for item in descendants
            if isinstance(item, widgets.Button)
        }
        inputs = {
            item.description: item
            for item in descendants
            if isinstance(item, (widgets.Textarea, widgets.Text, widgets.Dropdown))
        }
        self.assertEqual(inputs["Your verdict"].value, "Pending")
        self.assertFalse(session.dirty)
        inputs["Your verdict"].value = "PASS"
        inputs["Your reason (optional)"].value = "Clear relationship."
        self.assertEqual(session.current_review["observation"], exact)
        buttons["Next"].click()
        self.assertEqual(inputs["Your observations"].value, "")
        buttons["Previous"].click()
        self.assertEqual(inputs["Your verdict"].value, "PASS")
        buttons["Save all reviews"].click()
        self.assertFalse(session.dirty)
        self.assertEqual(self.load().current_review["observation"], exact)
        rendered = "\n".join(
            item.value for item in descendants if isinstance(item, widgets.HTML)
        )
        self.assertIn("Scorey engineer", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("Frozen criterion", rendered)
        self.assertIn("not set in the frozen configuration", rendered)

    def test_one_save_keeps_verdicts_without_repeating_notes(self) -> None:
        session = self.load()
        session.update(verdict="FAIL", reason="Not Scorey's voice.")
        session.navigate(1)
        session.update(verdict="FAIL", field_or_phrase="just terrible.")
        workbench.save_review(session)
        self.assertFalse(session.dirty)
        restored = self.load()
        self.assertEqual(restored.current_review["reason"], "Not Scorey's voice.")
        restored.navigate(1)
        self.assertEqual(restored.current_review["verdict"], "FAIL")
        self.assertEqual(restored.current_review["reason"], "")
        self.assertEqual(restored.current_review["field_or_phrase"], "just terrible.")
        original = self.notes_path.read_bytes()
        workbench.save_review(restored)
        self.assertEqual(self.notes_path.read_bytes(), original)

    def test_notebook_has_read_only_setup_and_no_preassigned_judgments(self) -> None:
        path = MODULE_PATH.with_name("scorey-coherent-absurdity-review.ipynb")
        notebook = json.loads(path.read_text())
        code = "\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        )
        self.assertIn("load_review(DB_PATH", code)
        self.assertNotIn("save_review(", code)
        self.assertNotIn("responses.create", code)
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                compile("".join(cell["source"]), "notebook", "exec")
                self.assertEqual(cell["outputs"], [])
