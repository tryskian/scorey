"""One-round review UI. CSV and canonical SQLite are read-only sources."""

from __future__ import annotations

import copy
import csv
import fcntl
import hashlib
import html
import io
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WorkbenchError(ValueError):
    """A source or review file cannot safely be used."""


class SourceMismatchError(WorkbenchError):
    """CSV identity differs from canonical SQLite or a saved review source."""


class ConcurrentSaveError(WorkbenchError):
    """Another writer changed the saved review after this session loaded it."""


IDENTITY_FIELDS = (
    "id",
    "scorey_pick",
    "user_pick",
    "route_family",
    "round_text",
    "model",
    "created_at",
)
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
VERDICTS = ("Pending", "PASS", "FAIL")


def find_repo_root(start: Path | None = None) -> Path:
    """Find Scorey from this notebook's directory or any repository ancestor."""
    location = (start or Path.cwd()).resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if (candidate / "src" / "scorey").is_dir() and (
            candidate / "Makefile"
        ).is_file():
            return candidate
    raise WorkbenchError("Open this notebook from the Scorey repository.")


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verdict(value: str) -> str:
    if value in ("", "pending", "Pending"):
        return "Pending"
    if value in ("PASS", "FAIL"):
        return value
    raise WorkbenchError(f"Unknown human verdict {value!r}; use Pending, PASS or FAIL.")


def _read_source(csv_path: Path, db_path: Path) -> tuple[tuple[dict, ...], dict]:
    try:
        csv_bytes = csv_path.read_bytes()
        records = list(
            csv.reader(io.StringIO(csv_bytes.decode("utf-8-sig"), newline=""))
        )
    except (OSError, UnicodeError, csv.Error) as exc:
        raise WorkbenchError(f"Could not read the review CSV: {exc}") from exc
    if records and records[0] == ["rows"]:
        records.pop(0)
    if not records or tuple(records.pop(0)) != CSV_FIELDS:
        raise WorkbenchError("CSV header does not match the Scorey review export.")
    rows = []
    seen = set()
    for record in records:
        if not record or not any(record):
            continue
        if len(record) != len(CSV_FIELDS):
            raise WorkbenchError("A CSV record has a missing or extra column.")
        row = dict(zip(CSV_FIELDS, record, strict=True))
        try:
            output_id = int(row["id"])
        except ValueError as exc:
            raise WorkbenchError(f"Invalid output ID: {row['id']!r}.") from exc
        if output_id <= 0 or output_id in seen:
            raise WorkbenchError(f"Invalid or duplicate output ID: {output_id}.")
        seen.add(output_id)
        row["id"] = output_id
        row["human_verdict"] = _verdict(row.pop("current_verdict"))
        row["human_notes"] = row.pop("Notes")
        rows.append(row)
    if not rows:
        raise WorkbenchError("The CSV contains no rounds to review.")

    try:
        with closing(sqlite3.connect(db_path.as_uri() + "?mode=ro", uri=True)) as db:
            db.execute("PRAGMA query_only = ON")
            db.row_factory = sqlite3.Row
            for row in rows:
                stored = db.execute(
                    "SELECT id, scorey_pick, user_pick, route_family, round_text, "
                    "model, "
                    "created_at, current_verdict FROM eval_outputs WHERE id = ?",
                    (row["id"],),
                ).fetchone()
                if stored is None:
                    raise SourceMismatchError(
                        f"Output {row['id']} is missing from the database."
                    )
                mismatches = [key for key in IDENTITY_FIELDS if row[key] != stored[key]]
                if mismatches:
                    raise SourceMismatchError(
                        f"Output {row['id']} differs from the database: "
                        f"{', '.join(mismatches)}. "
                        "Review was not loaded."
                    )
                row["route_verdict"] = stored["current_verdict"]
    except sqlite3.Error as exc:
        raise WorkbenchError(f"Could not read the canonical database: {exc}") from exc
    canonical = [{key: row[key] for key in IDENTITY_FIELDS} for row in rows]
    source = {
        "csv_name": csv_path.name,
        "csv_sha256": _digest(csv_bytes),
        "output_ids": [row["id"] for row in rows],
        "canonical_sha256": _digest(
            json.dumps(canonical, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ),
    }
    return tuple(rows), source


def _sidecar_bytes(path: Path) -> bytes | None:
    if path.is_symlink():
        raise WorkbenchError("The notes path must not be a symbolic link.")
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise WorkbenchError(f"Could not read saved notes: {exc}") from exc


def _check_reviews(reviews: Any, ids: list[int]) -> dict[str, dict[str, str]]:
    if not isinstance(reviews, dict) or set(reviews) != {str(value) for value in ids}:
        raise SourceMismatchError("Saved review IDs do not match the CSV rounds.")
    for output_id, review in reviews.items():
        if (
            not isinstance(review, dict)
            or set(review) != {"verdict", "notes"}
            or review["verdict"] not in VERDICTS
            or not isinstance(review["notes"], str)
        ):
            raise WorkbenchError(
                f"Saved review {output_id} has an invalid verdict or notes."
            )
    return reviews


@dataclass
class ReviewSession:
    rows: tuple[dict, ...]
    source: dict
    csv_path: Path
    db_path: Path
    notes_path: Path
    reviews: dict[str, dict[str, str]]
    expected_revision: str | None = None
    index: int = 0
    _saved_reviews: dict[str, dict[str, str]] = field(default_factory=dict, repr=False)

    @property
    def count(self) -> int:
        return len(self.rows)

    @property
    def current_row(self) -> dict:
        return self.rows[self.index]

    @property
    def current_review(self) -> dict[str, str]:
        return self.reviews[str(self.current_row["id"])]

    @property
    def dirty(self) -> bool:
        return self.reviews != self._saved_reviews

    def set_review(
        self, verdict: str, notes: str, output_id: int | None = None
    ) -> None:
        key = str(self.current_row["id"] if output_id is None else output_id)
        if key not in self.reviews:
            raise WorkbenchError(f"Output {key} is not part of this review.")
        if not isinstance(notes, str):
            raise WorkbenchError("Notes must be text.")
        self.reviews[key] = {"verdict": _verdict(verdict), "notes": notes}

    def navigate(self, delta: int) -> dict:
        self.index = min(max(self.index + delta, 0), self.count - 1)
        return self.current_row


def load_review(
    csv_path: Path, db_path: Path, notes_path: Path | None = None
) -> ReviewSession:
    """Validate canonical identity, then load human values and optional saved edits."""
    csv_path = Path(csv_path).resolve()
    db_path = Path(db_path).resolve()
    notes_path = (
        Path(notes_path)
        if notes_path
        else csv_path.parent / "scorey-review-workbench.notes.json"
    )
    if notes_path.is_symlink():
        raise WorkbenchError("The notes path must not be a symbolic link.")
    notes_path = notes_path.resolve()
    if notes_path in (csv_path, db_path) or not notes_path.name.endswith(".notes.json"):
        raise WorkbenchError("Choose a separate .notes.json file for saved reviews.")
    rows, source = _read_source(csv_path, db_path)
    reviews = {
        str(row["id"]): {"verdict": row["human_verdict"], "notes": row["human_notes"]}
        for row in rows
    }
    saved_bytes = _sidecar_bytes(notes_path)
    if saved_bytes is not None:
        try:
            saved = json.loads(saved_bytes)
        except (ValueError, UnicodeError) as exc:
            raise WorkbenchError(
                "Saved notes are not valid JSON; nothing was overwritten."
            ) from exc
        if not isinstance(saved, dict) or saved.get("schema_version") != 1:
            raise WorkbenchError("Saved notes use an unsupported format.")
        if saved.get("source") != source:
            raise SourceMismatchError(
                "Saved notes belong to a different or changed CSV source."
            )
        reviews = _check_reviews(saved.get("reviews"), source["output_ids"])
    return ReviewSession(
        rows=rows,
        source=source,
        csv_path=csv_path,
        db_path=db_path,
        notes_path=notes_path,
        reviews=reviews,
        expected_revision=_digest(saved_bytes) if saved_bytes is not None else None,
        _saved_reviews=copy.deepcopy(reviews),
    )


def save_review(session: ReviewSession) -> None:
    """Save only the notes sidecar, atomically, refusing stale or mismatched sources."""
    _check_reviews(session.reviews, session.source["output_ids"])
    _, current_source = _read_source(session.csv_path, session.db_path)
    if current_source != session.source:
        raise SourceMismatchError(
            "The source changed after loading. Notes were not saved."
        )
    if session.notes_path.resolve() in (session.csv_path, session.db_path):
        raise WorkbenchError("Saved notes must be separate from the CSV and database.")
    payload = {
        "schema_version": 1,
        "source": session.source,
        "reviews": session.reviews,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = None
    try:
        # A directory lock serializes cooperating workbenches without a lock sidecar.
        directory_fd = os.open(session.notes_path.parent, os.O_RDONLY)
        try:
            fcntl.flock(directory_fd, fcntl.LOCK_EX)
            current = _sidecar_bytes(session.notes_path)
            revision = _digest(current) if current is not None else None
            if revision != session.expected_revision:
                raise ConcurrentSaveError(
                    "Saved notes changed in another session. "
                    "Your edits are still here; "
                    "copy them before reloading to reconcile the other version."
                )
            with tempfile.NamedTemporaryFile(
                dir=session.notes_path.parent,
                prefix=".scorey-review-",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, session.notes_path)
            temporary = None
            session.expected_revision = _digest(data)
            session._saved_reviews = copy.deepcopy(session.reviews)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise WorkbenchError(
            f"Could not save notes; your edits are still here: {exc}"
        ) from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_workbench(session: ReviewSession):
    """Build an ipywidgets reader; navigation never saves or alters source files."""
    try:
        import ipywidgets as widgets
    except ImportError as exc:
        raise WorkbenchError(
            "Install the notebook requirements, then restart this kernel."
        ) from exc

    position = widgets.HTML()
    reading = widgets.HTML()
    status = widgets.HTML()
    previous = widgets.Button(description="Previous", icon="arrow-left")
    following = widgets.Button(description="Next", icon="arrow-right")
    save = widgets.Button(
        description="Save review", button_style="primary", icon="save"
    )
    verdict = widgets.Dropdown(
        options=VERDICTS,
        description="Your verdict",
        style={"description_width": "initial"},
        layout=widgets.Layout(width="250px"),
    )
    notes = widgets.Textarea(
        description="Your notes",
        style={"description_width": "initial"},
        placeholder="Your notes for this round…",
        layout=widgets.Layout(width="100%", min_height="190px", flex="1 1 auto"),
    )
    loading = False
    original_notes = ""
    displayed_notes = ""

    def update_status(message: str | None = None) -> None:
        if message is None:
            if session.dirty:
                message = (
                    "Unsaved changes. Navigation keeps your edits in this session."
                )
            elif session.expected_revision is None:
                message = (
                    "Loaded from your CSV. Save review creates a separate notes file."
                )
            else:
                message = "Saved. Your notes are in " + session.notes_path.name + "."
        status.value = (
            '<div role="status" aria-live="polite">' + html.escape(message) + "</div>"
        )

    def render() -> None:
        nonlocal loading, original_notes, displayed_notes
        loading = True
        row = session.current_row
        position.value = (
            f"<strong>Round {session.index + 1} of {session.count} "
            f"· ID {row['id']}</strong>"
        )
        reading.value = (
            '<div class="scorey-round" style="font-size:18px;line-height:1.6;'
            'white-space:pre-wrap;overflow-wrap:anywhere;width:100%">'
            + html.escape(row["round_text"])
            + '</div><p class="scorey-metadata">'
            + html.escape(row["model"])
            + " · Database routing: "
            + html.escape(row["route_verdict"])
            + " (separate from your verdict).</p>"
        )
        verdict.value = session.current_review["verdict"]
        original_notes = session.current_review["notes"]
        displayed_notes = original_notes.replace("\u2028", "\n").replace("\u2029", "\n")
        notes.value = displayed_notes
        previous.disabled = session.index == 0
        following.disabled = session.index == session.count - 1
        loading = False
        update_status()

    def changed(_change) -> None:
        if not loading:
            value = original_notes if notes.value == displayed_notes else notes.value
            session.set_review(verdict.value, value)
            update_status()

    def move(delta: int) -> None:
        session.navigate(delta)
        render()

    def persist(_button) -> None:
        try:
            save_review(session)
        except WorkbenchError as exc:
            update_status("Could not save: " + str(exc))
        else:
            update_status()

    verdict.observe(changed, names="value")
    notes.observe(changed, names="value")
    previous.on_click(lambda _button: move(-1))
    following.on_click(lambda _button: move(1))
    save.on_click(persist)
    controls = widgets.HBox(
        [previous, following], layout=widgets.Layout(flex_flow="row wrap")
    )
    controls.add_class("scorey-navigation")
    style = widgets.HTML("""<style>
    .scorey-review { color:var(--jp-ui-font-color1, inherit);
        width:100%; max-width:none; min-width:0; margin:0; gap:12px;
        min-height:calc(100dvh - 420px); box-sizing:border-box; }
    .scorey-review .scorey-navigation { gap:8px; }
    .scorey-review .widget-html-content { min-width:0; width:100%; }
    .scorey-review .scorey-metadata { font-size:13px; opacity:.75; margin:18px 0; }
    .scorey-review textarea { font-size:16px!important; line-height:1.5!important;
        font-family:var(--jp-ui-font-family, sans-serif)!important;
        flex:1 1 auto; min-height:150px; }
    .scorey-review .widget-textarea {
        flex-direction:column; align-items:stretch; margin:0;
    }
    .scorey-review .widget-textarea > label.widget-label {
        width:auto!important; text-align:left; margin:0 0 6px;
    }
    .scorey-review .widget-html { margin:0; }
    .scorey-review button { min-height:34px; }
    </style>""")
    panel = widgets.VBox(
        [
            style,
            position,
            controls,
            reading,
            verdict,
            notes,
            save,
            status,
        ],
        layout=widgets.Layout(width="100%"),
    )
    panel.add_class("scorey-review")
    render()
    return panel
