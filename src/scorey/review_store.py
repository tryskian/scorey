"""Source-bound smoke datasets and attributed review events, outside eval gates."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
CRITERIA_ID = "coherent-absurdity-review-1"
NOTES_SCHEMA = "scorey.review_notes.v1"


class ReviewError(ValueError):
    """Invalid, changed, or mismatched review evidence."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")


SCHEMA = """
CREATE TABLE IF NOT EXISTS review_datasets (
    dataset_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    manifest_json BLOB NOT NULL,
    criteria_id TEXT NOT NULL,
    criteria_sha256 TEXT NOT NULL,
    criteria_text BLOB NOT NULL,
    imported_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS review_cases (
    dataset_id TEXT NOT NULL REFERENCES review_datasets(dataset_id),
    case_id TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    case_json BLOB NOT NULL,
    receipt_json BLOB NOT NULL,
    receipt_sha256 TEXT NOT NULL,
    request_json BLOB,
    request_sha256 TEXT,
    response_json BLOB,
    response_sha256 TEXT,
    PRIMARY KEY (dataset_id, case_id),
    UNIQUE (dataset_id, ordinal)
);
CREATE TABLE IF NOT EXISTS review_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    dataset_id TEXT NOT NULL,
    case_id TEXT NOT NULL,
    author TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('human','assistant')),
    kind TEXT NOT NULL CHECK (kind IN ('observation','judgment')),
    verdict TEXT CHECK (verdict IN ('PASS','FAIL')),
    note TEXT NOT NULL,
    field_or_phrase TEXT NOT NULL,
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    event_json BLOB NOT NULL,
    CHECK ((kind='observation' AND verdict IS NULL)
        OR (kind='judgment' AND verdict IS NOT NULL)),
    FOREIGN KEY (dataset_id,case_id) REFERENCES review_cases(dataset_id,case_id)
);
CREATE VIEW IF NOT EXISTS review_rounds AS
SELECT c.dataset_id, c.case_id, c.ordinal,
    json_extract(c.case_json,'$.scorey_pick') AS scorey_pick,
    json_extract(c.case_json,'$.user_pick') AS user_pick,
    json_extract(c.case_json,'$.route_family') AS route_family,
    json_extract(c.case_json,'$.starting_score') AS starting_score,
    json_extract(c.receipt_json,'$.round_text') AS round_text,
    json_extract(d.manifest_json,'$.settings.model') AS requested_model,
    json_extract(d.manifest_json,'$.settings.reasoning_effort') AS reasoning_effort,
    json_extract(c.receipt_json,'$.returned_settings.model') AS returned_model,
    json_extract(c.receipt_json,'$.route_check.verdict') AS route_verdict,
    json_extract(c.receipt_json,'$.mechanical_checks.ok') AS mechanical_ok,
    json_extract(c.receipt_json,'$.elapsed_seconds') AS elapsed_seconds,
    json_extract(c.receipt_json,'$.usage.input_tokens') AS input_tokens,
    json_extract(c.receipt_json,'$.usage.output_tokens') AS output_tokens,
    json_extract(c.receipt_json,'$.usage.total_tokens') AS total_tokens,
    json_extract(c.receipt_json,'$.response_id') AS response_id,
    json_extract(c.receipt_json,'$.started_at') AS created_at,
    d.criteria_id, d.criteria_sha256, c.receipt_sha256
FROM review_cases c JOIN review_datasets d USING (dataset_id);
"""


def _connect(path: Path, *, readonly: bool = True) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + ("?mode=ro" if readonly else "?mode=rwc")
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    if readonly:
        conn.execute("PRAGMA query_only=ON")
    return conn


def _initialize(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    for table in ("review_datasets", "review_cases", "review_events"):
        for action in ("UPDATE", "DELETE"):
            conn.execute(
                f"CREATE TRIGGER IF NOT EXISTS {table}_no_{action.lower()} "
                f"BEFORE {action} ON {table} BEGIN "
                "SELECT RAISE(ABORT, 'Review evidence is append-only'); END"
            )


def _inside(folder: Path, name: str) -> Path:
    path = (folder / name).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ReviewError("Evidence path leaves the run directory.")
    return path


def _read_hashed(folder: Path, name: str, expected: str) -> bytes:
    raw = _inside(folder, name).read_bytes()
    if digest(raw) != expected:
        raise ReviewError(f"Changed evidence: {name}")
    return raw


def import_smoke_run(run_dir: Path, db_path: Path, criteria_path: Path) -> str:
    """Import original bytes atomically; identical reimports are no-ops."""
    folder = run_dir.resolve()
    manifest_raw = _read_hashed(
        folder, "manifest.json", (folder / "manifest.sha256").read_text().strip()
    )
    manifest = json.loads(manifest_raw)
    if manifest.get("schema") != "scorey.golden_smoke.v1":
        raise ReviewError("Unsupported smoke manifest.")
    cases = manifest["cases"]
    if len(cases) != 6 or len({c["id"] for c in cases}) != 6:
        raise ReviewError("Expected six distinct frozen cases.")
    for name, expected in manifest["source_hashes"].items():
        _read_hashed(folder, "source/" + name, expected)
    _read_hashed(folder, "source.patch", manifest["source_patch_sha256"])
    criteria = criteria_path.read_bytes()
    if CRITERIA_ID not in criteria.decode("utf-8"):
        raise ReviewError("The review criterion is missing from this document.")
    records = []
    for ordinal, case in enumerate(cases, 1):
        raw = _inside(folder, f"{ordinal:02d}-{case['id']}.receipt.json").read_bytes()
        receipt = json.loads(raw)
        if (
            receipt.get("schema") != "scorey.smoke_attempt.v1"
            or receipt.get("case_id") != case["id"]
            or receipt.get("attempt") != ordinal
        ):
            raise ReviewError("Receipt identity differs from the manifest.")
        payloads: list[bytes | str | None] = []
        for kind in ("request", "response"):
            name, expected = receipt.get(f"{kind}_file"), receipt.get(f"{kind}_sha256")
            if bool(name) != bool(expected):
                raise ReviewError("Incomplete source hash binding.")
            data = _read_hashed(folder, name, expected) if name else None
            payloads.extend((data, expected))
            if kind == "response" and data and receipt.get("response_id"):
                if json.loads(data).get("id") != receipt["response_id"]:
                    raise ReviewError("Response ID differs from receipt.")
        if receipt.get("normalized_round"):
            for key in ("scorey_pick", "user_pick", "route_family"):
                if receipt["normalized_round"][key] != case[key]:
                    raise ReviewError("Round picks differ from the frozen case.")
        records.append(
            (
                folder.name,
                case["id"],
                ordinal,
                encoded(case),
                raw,
                digest(raw),
                *payloads,
            )
        )
    with closing(_connect(db_path, readonly=False)) as conn:
        _initialize(conn)
        with conn:
            old = conn.execute(
                "SELECT * FROM review_datasets WHERE dataset_id=?", (folder.name,)
            ).fetchone()
            if old:
                if (
                    old["manifest_json"] != manifest_raw
                    or old["criteria_text"] != criteria
                ):
                    raise ReviewError(
                        "Dataset already exists with different evidence or criteria."
                    )
                stored = conn.execute(
                    "SELECT * FROM review_cases WHERE dataset_id=? ORDER BY ordinal",
                    (folder.name,),
                ).fetchall()
                if [tuple(row) for row in stored] != records:
                    raise ReviewError("Dataset case evidence changed.")
                return folder.name
            conn.execute(
                "INSERT INTO review_datasets VALUES (?,?,?,?,?,?,?,?)",
                (
                    folder.name,
                    str(folder),
                    digest(manifest_raw),
                    manifest_raw,
                    CRITERIA_ID,
                    digest(criteria),
                    criteria,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.executemany(
                "INSERT INTO review_cases VALUES (?,?,?,?,?,?,?,?,?,?)", records
            )
    return folder.name


def load_dataset(db_path: Path, dataset_id: str | None = None) -> dict[str, Any]:
    """Read frozen evidence and attributed event history without initializing SQLite."""
    try:
        with closing(_connect(db_path)) as conn:
            row = conn.execute(
                "SELECT * FROM review_datasets "
                + (
                    "WHERE dataset_id=?"
                    if dataset_id
                    else "ORDER BY imported_at DESC LIMIT 1"
                ),
                (dataset_id,) if dataset_id else (),
            ).fetchone()
            if row is None:
                raise ReviewError(
                    "No imported smoke dataset. Run smoke-review-import first."
                )
            result = dict(row)
            result["manifest"] = json.loads(result.pop("manifest_json"))
            result["criteria_text"] = bytes(result["criteria_text"]).decode("utf-8")
            result["cases"] = []
            for stored in conn.execute(
                "SELECT * FROM review_cases WHERE dataset_id=? ORDER BY ordinal",
                (result["dataset_id"],),
            ):
                case = dict(stored)
                case["case"] = json.loads(case.pop("case_json"))
                case["receipt"] = json.loads(case.pop("receipt_json"))
                case.pop("request_json")
                case.pop("response_json")
                result["cases"].append(case)
            result["events"] = [
                json.loads(r[0])
                for r in conn.execute(
                    "SELECT event_json FROM review_events "
                    "WHERE dataset_id=? ORDER BY id",
                    (result["dataset_id"],),
                )
            ]
            return result
    except sqlite3.Error as exc:
        raise ReviewError(f"Could not read review dataset: {exc}") from exc


def _binding(dataset: dict[str, Any]) -> dict[str, str]:
    return {
        key: dataset[key]
        for key in ("dataset_id", "manifest_sha256", "criteria_id", "criteria_sha256")
    }


def _validate_event(event: dict[str, Any], dataset: dict[str, Any]) -> None:
    cases = {c["case_id"]: c for c in dataset["cases"]}
    if not isinstance(event, dict) or event.get("case_id") not in cases:
        raise ReviewError("Review event has an unknown case.")
    case = cases[event["case_id"]]
    for key, value in _binding(dataset).items():
        if event.get(key) != value:
            raise ReviewError("Review event belongs to different evidence or criteria.")
    if event.get("receipt_sha256") != case["receipt_sha256"] or event.get(
        "response_id"
    ) != case["receipt"].get("response_id"):
        raise ReviewError("Review event refers to a different response.")
    for key in ("event_id", "author", "source", "created_at"):
        if not isinstance(event.get(key), str) or not event[key].strip():
            raise ReviewError(f"Review event requires {key}.")
    try:
        timestamp = datetime.fromisoformat(event["created_at"])
    except ValueError as exc:
        raise ReviewError("Review time must be an ISO timestamp.") from exc
    if timestamp.utcoffset() is None:
        raise ReviewError("Review time requires a timezone.")
    if not isinstance(event.get("field_or_phrase"), str):
        raise ReviewError("Field or phrase must be text.")
    if not isinstance(event.get("note"), str):
        raise ReviewError("Review note must be text.")
    if event.get("role") not in ("human", "assistant"):
        raise ReviewError("Review role must be human or assistant.")
    if event.get("kind") == "observation":
        if not event["note"].strip():
            raise ReviewError("An observation requires a note.")
        if event.get("verdict") is not None:
            raise ReviewError("An observation does not carry a verdict.")
    elif event.get("kind") == "judgment":
        if event.get("verdict") not in ("PASS", "FAIL"):
            raise ReviewError("A judgment requires PASS or FAIL.")
        if case["receipt"].get("status") != "completed":
            raise ReviewError("Incomplete responses cannot receive a semantic verdict.")
        if not case["receipt"].get("mechanical_checks", {}).get("ok"):
            raise ReviewError(
                "Mechanical admission is required before quality judgment."
            )
        if case["receipt"].get("route_check", {}).get("verdict") != "pass":
            raise ReviewError("Route admission is required before quality judgment.")
    else:
        raise ReviewError("Unknown review event kind.")


def new_event(
    dataset: dict[str, Any],
    case_id: str,
    author: str,
    kind: str,
    note: str,
    *,
    role: str = "human",
    verdict: str | None = None,
    field_or_phrase: str = "",
    source: str = "notebook",
) -> dict[str, Any]:
    cases = {c["case_id"]: c for c in dataset["cases"]}
    if case_id not in cases:
        raise ReviewError("Unknown review case.")
    case = cases[case_id]
    event = {
        **_binding(dataset),
        "event_id": str(uuid4()),
        "case_id": case_id,
        "receipt_sha256": case["receipt_sha256"],
        "response_id": case["receipt"].get("response_id"),
        "author": author,
        "role": role,
        "kind": kind,
        "verdict": verdict,
        "note": note,
        "field_or_phrase": field_or_phrase,
        "source": source,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _validate_event(event, dataset)
    return event


def read_notes(
    path: Path, dataset: dict[str, Any]
) -> tuple[list[dict[str, Any]], str | None]:
    if path.is_symlink():
        raise ReviewError("Notes must not be a symbolic link.")
    if not path.exists():
        return [], None
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        raise ReviewError("Notes are not valid JSON.") from exc
    if not isinstance(payload, dict) or payload.get("schema") != NOTES_SCHEMA:
        raise ReviewError("Unsupported review notes format.")
    if payload.get("source") != _binding(dataset):
        raise ReviewError("Notes belong to another dataset or criterion.")
    events = payload.get("events")
    if not isinstance(events, list):
        raise ReviewError("Review events must be a list.")
    seen = set()
    for event in events:
        _validate_event(event, dataset)
        if event["event_id"] in seen:
            raise ReviewError("Duplicate review event.")
        seen.add(event["event_id"])
    return events, digest(raw)


def save_notes(
    path: Path,
    dataset: dict[str, Any],
    events: list[dict[str, Any]],
    expected_revision: str | None,
) -> str:
    """Append a sidecar atomically, rejecting stale saves and historical rewrites."""
    if not path.name.endswith(".notes.json") or path.is_symlink():
        raise ReviewError("Choose a separate .notes.json file.")
    if path.resolve().is_relative_to(Path(dataset["source_path"]).resolve()):
        raise ReviewError("Keep notes outside the original smoke evidence folder.")
    for event in events:
        _validate_event(event, dataset)
    if len({e["event_id"] for e in events}) != len(events):
        raise ReviewError("Duplicate review event.")
    temp: str | None = None
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        previous, revision = read_notes(path, dataset)
        if revision != expected_revision:
            raise ReviewError("Notes changed in another session. Reload before saving.")
        if events[: len(previous)] != previous:
            raise ReviewError("Earlier notes are preserved; append a correction.")
        raw = encoded(
            {"schema": NOTES_SCHEMA, "source": _binding(dataset), "events": events}
        )
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
            temp = f.name
            f.write(raw + b"\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
        temp = None
        return digest(raw + b"\n")
    finally:
        os.close(fd)
        if temp:
            Path(temp).unlink(missing_ok=True)


def import_notes(db_path: Path, path: Path) -> int:
    """Explicitly sync source-bound sidecar events; changed event IDs are rejected."""
    payload = json.loads(path.read_bytes())
    dataset = load_dataset(db_path, payload["source"]["dataset_id"])
    events, _ = read_notes(path, dataset)
    added = 0
    with closing(_connect(db_path, readonly=False)) as conn, conn:
        for event in events:
            raw = encoded(event)
            old = conn.execute(
                "SELECT event_json FROM review_events WHERE event_id=?",
                (event["event_id"],),
            ).fetchone()
            if old:
                if old[0] != raw:
                    raise ReviewError("An imported event changed; append a new event.")
                continue
            fields = (
                "event_id",
                "dataset_id",
                "case_id",
                "author",
                "role",
                "kind",
                "verdict",
                "note",
                "field_or_phrase",
                "source",
                "created_at",
            )
            conn.execute(
                "INSERT INTO review_events (" + ",".join(fields) + ",event_json) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                tuple(event[key] for key in fields) + (raw,),
            )
            added += 1
    return added


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / ".local/evals.sqlite")
    commands = parser.add_subparsers(dest="command", required=True)
    imp = commands.add_parser("import")
    imp.add_argument("run", type=Path)
    imp.add_argument(
        "--criteria",
        type=Path,
        default=ROOT / "docs/research/420_PB-COHERENT_ABSURDITY.md",
    )
    notes = commands.add_parser("import-notes")
    notes.add_argument("notes", type=Path)
    show = commands.add_parser("show")
    show.add_argument("dataset", nargs="?")
    args = parser.parse_args()
    try:
        if args.command == "import":
            print(import_smoke_run(args.run, args.db, args.criteria))
        elif args.command == "import-notes":
            print(json.dumps({"imported_events": import_notes(args.db, args.notes)}))
        else:
            data = load_dataset(args.db, args.dataset)
            print(
                json.dumps(
                    {
                        "dataset_id": data["dataset_id"],
                        "cases": len(data["cases"]),
                        "events": len(data["events"]),
                        "criteria_id": data["criteria_id"],
                    }
                )
            )
    except (ReviewError, OSError, sqlite3.Error, KeyError, ValueError) as exc:
        parser.exit(2, f"Review error: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
