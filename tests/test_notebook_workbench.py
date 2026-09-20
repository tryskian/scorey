import csv
import importlib.util
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, skipUnless

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "output"
    / "jupyter-notebook"
    / "scorey_review_workbench.py"
)
SPEC = importlib.util.spec_from_file_location("scorey_review_workbench", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
workbench = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = workbench
SPEC.loader.exec_module(workbench)

CSV_FIELDS = (
    "id",
    "scorey_pick",
    "user_pick",
    "route_family",
    "round_text",
    "model",
    "current_verdict",
    "created_at",
    "Notes",
)


class NotebookWorkbenchTests(TestCase):
    def setUp(self) -> None:
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.csv_path = self.root / "old-six-review.csv"
        self.db_path = self.root / "evals.sqlite"
        self.notes_path = self.root / "human-review.notes.json"
        self.original_notes = "  I love ”so”, not ”and”\u2028next line\r\nlast line\n  "
        self.records = [
            {
                "id": "20449",
                "scorey_pick": "paper",
                "user_pick": "scissors",
                "route_family": "cross-object",
                "round_text": "you: scissors\nme: paper\n\nunchanged ”scene”\n",
                "model": "gpt-5.6-luna",
                "current_verdict": "FAIL",
                "created_at": "2026-09-20T01:04:02.917640+00:00",
                "Notes": self.original_notes,
            },
            {
                "id": "20451",
                "scorey_pick": "scissors",
                "user_pick": "rock",
                "route_family": "cross-object",
                "round_text": "you: rock\nme: scissors\n\nit’s delightful!\n",
                "model": "gpt-5.6-luna",
                "current_verdict": "PASS",
                "created_at": "2026-09-20T01:04:05.698216+00:00",
                "Notes": "HILARIOUS!",
            },
        ]
        self.write_csv()
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute(
                "CREATE TABLE eval_outputs (id INTEGER PRIMARY KEY, scorey_pick TEXT, "
                "user_pick TEXT, route_family TEXT, round_text TEXT, model TEXT, "
                "current_verdict TEXT, created_at TEXT)"
            )
            for record in self.records:
                db.execute(
                    "INSERT INTO eval_outputs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        int(record["id"]),
                        record["scorey_pick"],
                        record["user_pick"],
                        record["route_family"],
                        record["round_text"],
                        record["model"],
                        "pending",
                        record["created_at"],
                    ),
                )

    def write_csv(self, records: list[dict[str, str]] | None = None) -> None:
        with self.csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\r\n")
            writer.writerow(["rows"])
            writer.writerow(CSV_FIELDS)
            for record in self.records if records is None else records:
                writer.writerow([record[key] for key in CSV_FIELDS])

    def test_numbers_header_and_human_judgments_preserve_source_text(self) -> None:
        csv_before, db_before = self.csv_path.read_bytes(), self.db_path.read_bytes()
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)

        self.assertEqual([row["id"] for row in session.rows], [20449, 20451])
        self.assertEqual(session.current_review["verdict"], "FAIL")
        self.assertEqual(session.rows[1]["human_verdict"], "PASS")
        self.assertEqual(
            [row["route_verdict"] for row in session.rows], ["pending", "pending"]
        )
        self.assertEqual(session.current_review["notes"], self.original_notes)
        self.assertEqual(session.rows[0]["human_notes"], self.original_notes)
        self.assertEqual(session.rows[0]["round_text"], self.records[0]["round_text"])
        self.assertFalse(session.dirty)
        self.assertFalse(self.notes_path.exists())
        self.assertEqual(self.csv_path.read_bytes(), csv_before)
        self.assertEqual(self.db_path.read_bytes(), db_before)

    def test_any_canonical_identity_difference_refuses_load(self) -> None:
        for field in (
            "scorey_pick",
            "user_pick",
            "route_family",
            "round_text",
            "model",
            "created_at",
        ):
            with self.subTest(field=field):
                changed = [dict(record) for record in self.records]
                changed[0][field] += " changed"
                self.write_csv(changed)
                with self.assertRaises(workbench.SourceMismatchError):
                    workbench.load_review(self.csv_path, self.db_path, self.notes_path)
                self.assertFalse(self.notes_path.exists())

    def test_missing_or_duplicate_ids_refuse_load(self) -> None:
        missing = [dict(self.records[0])]
        missing[0]["id"] = "20443"
        self.write_csv(missing)
        with self.assertRaises(workbench.SourceMismatchError):
            workbench.load_review(self.csv_path, self.db_path, self.notes_path)

        self.write_csv([self.records[0], self.records[0]])
        with self.assertRaises(workbench.WorkbenchError):
            workbench.load_review(self.csv_path, self.db_path, self.notes_path)

    def test_navigation_keeps_edits_until_explicit_sidecar_save(self) -> None:
        csv_before, db_before = self.csv_path.read_bytes(), self.db_path.read_bytes()
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        edited_notes = self.original_notes + "\n  another ”thought”\u2028kept  "
        session.set_review("PASS", edited_notes)
        self.assertTrue(session.dirty)
        session.navigate(1)
        self.assertEqual(session.current_row["id"], 20451)
        self.assertEqual(session.current_review["notes"], "HILARIOUS!")
        session.set_review("Pending", "not decided\n")
        session.navigate(-1)
        self.assertEqual(
            session.current_review, {"verdict": "PASS", "notes": edited_notes}
        )
        self.assertEqual(session.current_row["human_notes"], self.original_notes)
        self.assertEqual(session.current_row["human_verdict"], "FAIL")
        self.assertFalse(self.notes_path.exists())
        session.navigate(-50)
        self.assertEqual(session.index, 0)
        session.navigate(50)
        self.assertEqual(session.index, 1)

        workbench.save_review(session)
        self.assertFalse(session.dirty)
        restored = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        self.assertEqual(restored.reviews, session.reviews)
        self.assertEqual(restored.current_review["notes"], edited_notes)
        self.assertEqual(restored.rows[0]["human_notes"], self.original_notes)
        self.assertEqual(restored.rows[0]["route_verdict"], "pending")
        self.assertEqual(self.csv_path.read_bytes(), csv_before)
        self.assertEqual(self.db_path.read_bytes(), db_before)

    def test_stale_save_cannot_replace_other_session_notes(self) -> None:
        first = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        stale = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        first.set_review("FAIL", "first writer\u2028preserved")
        workbench.save_review(first)
        saved = self.notes_path.read_bytes()
        stale.set_review("PASS", "other writer's unsaved idea")
        with self.assertRaises(workbench.ConcurrentSaveError):
            workbench.save_review(stale)
        self.assertEqual(self.notes_path.read_bytes(), saved)
        self.assertTrue(stale.dirty)
        self.assertEqual(stale.current_review["notes"], "other writer's unsaved idea")

        previously_loaded = workbench.load_review(
            self.csv_path, self.db_path, self.notes_path
        )
        first.set_review("FAIL", "updated first writer")
        workbench.save_review(first)
        newer = self.notes_path.read_bytes()
        with self.assertRaises(workbench.ConcurrentSaveError):
            workbench.save_review(previously_loaded)
        self.assertEqual(self.notes_path.read_bytes(), newer)

    def test_invalid_sidecar_is_not_overwritten_on_load_or_save(self) -> None:
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        corrupt = b'{"reviews": incomplete'
        self.notes_path.write_bytes(corrupt)
        with self.assertRaises(workbench.WorkbenchError):
            workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        with self.assertRaises(workbench.ConcurrentSaveError):
            workbench.save_review(session)
        self.assertEqual(self.notes_path.read_bytes(), corrupt)

    def test_sidecar_with_wrong_source_ids_or_invalid_review_refuses_load(self) -> None:
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        workbench.save_review(session)
        original = self.notes_path.read_text(encoding="utf-8")
        for corruption in ("source", "ids", "verdict", "notes"):
            with self.subTest(corruption=corruption):
                payload = json.loads(original)
                if corruption == "source":
                    payload["source"]["csv_sha256"] = "wrong source"
                elif corruption == "ids":
                    del payload["reviews"]["20451"]
                elif corruption == "verdict":
                    payload["reviews"]["20449"]["verdict"] = "engineer approved"
                else:
                    payload["reviews"]["20449"]["notes"] = ["not text"]
                invalid = json.dumps(payload).encode("utf-8")
                self.notes_path.write_bytes(invalid)
                with self.assertRaises(workbench.WorkbenchError):
                    workbench.load_review(self.csv_path, self.db_path, self.notes_path)
                self.assertEqual(self.notes_path.read_bytes(), invalid)

    def test_changed_csv_after_load_refuses_save_without_losing_edits(self) -> None:
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        session.set_review("PASS", "unsaved assessment")
        changed = [dict(record) for record in self.records]
        changed[0]["Notes"] = "externally edited source"
        self.write_csv(changed)
        with self.assertRaises(workbench.SourceMismatchError):
            workbench.save_review(session)
        self.assertTrue(session.dirty)
        self.assertEqual(session.current_review["notes"], "unsaved assessment")
        self.assertFalse(self.notes_path.exists())

    def test_changed_canonical_text_after_load_refuses_save(self) -> None:
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        with closing(sqlite3.connect(self.db_path)) as db, db:
            db.execute(
                "UPDATE eval_outputs SET round_text = 'changed' WHERE id = 20449"
            )
        with self.assertRaises(workbench.SourceMismatchError):
            workbench.save_review(session)
        self.assertFalse(self.notes_path.exists())

    @skipUnless(importlib.util.find_spec("ipywidgets"), "ipywidgets is optional")
    def test_widget_display_preserves_original_notes_until_intentionally_edited(
        self,
    ) -> None:
        widgets = importlib.import_module("ipywidgets")
        original = self.original_notes + "\u2029another paragraph"
        self.records[0]["Notes"] = original
        self.write_csv()
        csv_before, db_before = self.csv_path.read_bytes(), self.db_path.read_bytes()
        session = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        panel = workbench.build_workbench(session)
        descendants = []
        pending = [panel]
        while pending:
            widget = pending.pop()
            descendants.append(widget)
            pending.extend(getattr(widget, "children", ()))
            self.addCleanup(widget.close)
        notes = next(item for item in descendants if isinstance(item, widgets.Textarea))
        verdict = next(
            item for item in descendants if isinstance(item, widgets.Dropdown)
        )
        buttons = {
            item.description: item
            for item in descendants
            if isinstance(item, widgets.Button)
        }
        displayed = original.replace("\u2028", "\n").replace("\u2029", "\n")
        self.assertEqual(notes.value, displayed)
        self.assertEqual(notes.description, "Your notes")
        self.assertFalse(session.dirty)
        self.assertTrue(buttons["Previous"].disabled)

        verdict.value = "PASS"
        self.assertEqual(session.current_review, {"verdict": "PASS", "notes": original})
        buttons["Next"].click()
        self.assertEqual(session.current_row["id"], 20451)
        self.assertEqual(notes.value, "HILARIOUS!")
        self.assertTrue(buttons["Next"].disabled)
        buttons["Previous"].click()
        self.assertEqual(notes.value, displayed)
        self.assertEqual(verdict.value, "PASS")
        self.assertFalse(self.notes_path.exists())
        buttons["Save review"].click()
        self.assertFalse(session.dirty)
        restored = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        self.assertEqual(restored.current_review["notes"], original)

        edited = "My intentional edit\n”so” stays delightful!\n"
        notes.value = edited
        self.assertTrue(session.dirty)
        buttons["Next"].click()
        buttons["Previous"].click()
        self.assertEqual(notes.value, edited)
        buttons["Save review"].click()
        restored = workbench.load_review(self.csv_path, self.db_path, self.notes_path)
        self.assertEqual(restored.current_review["notes"], edited)
        self.assertEqual(restored.current_review["verdict"], "PASS")
        self.assertEqual(restored.current_row["human_notes"], original)
        self.assertEqual(self.csv_path.read_bytes(), csv_before)
        self.assertEqual(self.db_path.read_bytes(), db_before)
