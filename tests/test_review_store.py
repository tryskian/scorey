from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest

from scorey.review_store import (
    CRITERIA_ID,
    ReviewError,
    digest,
    import_notes,
    import_smoke_run,
    load_dataset,
    new_event,
    read_notes,
    save_notes,
)


@pytest.fixture
def review_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    folder = tmp_path / "frozen-run"
    folder.mkdir()
    (folder / "source").mkdir()
    (folder / "source" / "contract.txt").write_bytes(b"original source")
    (folder / "source.patch").write_bytes(b"original patch")
    cases = []
    for ordinal, (scorey, user) in enumerate(
        (
            ("paper", "scissors"),
            ("rock", "paper"),
            ("scissors", "rock"),
            ("paper", "paper"),
            ("rock", "rock"),
            ("scissors", "scissors"),
        ),
        1,
    ):
        case_id = f"{scorey}-{user}"
        case = {
            "id": case_id,
            "scorey_pick": scorey,
            "user_pick": user,
            "route_family": "same-pick" if scorey == user else "cross-object",
            "starting_score": 1,
            "purpose": "test relation",
        }
        cases.append(case)
        stem = f"{ordinal:02d}-{case_id}"
        request = b'{ "input": "source text" }\n'
        response = json.dumps({"id": "resp-" + case_id, "output": []}).encode()
        (folder / f"{stem}.request.json").write_bytes(request)
        (folder / f"{stem}.response.json").write_bytes(response)
        receipt = {
            "schema": "scorey.smoke_attempt.v1",
            "case_id": case_id,
            "attempt": ordinal,
            "status": "completed",
            "started_at": "2026-09-21T12:00:00Z",
            "request_file": f"{stem}.request.json",
            "request_sha256": digest(request),
            "response_file": f"{stem}.response.json",
            "response_sha256": digest(response),
            "response_id": "resp-" + case_id,
            "mechanical_checks": {"ok": True},
            "route_check": {"verdict": "pass"},
            "normalized_round": case,
            "round_text": f"my {scorey} wins over your {user}",
            "elapsed_seconds": 0.5,
            "usage": {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14},
        }
        (folder / f"{stem}.receipt.json").write_text(json.dumps(receipt))
    manifest = {
        "schema": "scorey.golden_smoke.v1",
        "cases": cases,
        "source_hashes": {"contract.txt": digest(b"original source")},
        "source_patch_sha256": digest(b"original patch"),
        "settings": {"model": "test-model", "reasoning_effort": "medium"},
    }
    raw = json.dumps(manifest).encode()
    (folder / "manifest.json").write_bytes(raw)
    (folder / "manifest.sha256").write_text(digest(raw))
    criteria = tmp_path / "criteria.md"
    criteria.write_text(f"Question\n{CRITERIA_ID}\nFrozen criterion.")
    db = tmp_path / "evals.sqlite"
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("CREATE TABLE eval_outputs (id INTEGER PRIMARY KEY, note TEXT)")
        conn.execute("INSERT INTO eval_outputs VALUES (42, 'exact human wording')")
    return folder, db, criteria


def test_import_retains_bytes_and_history_and_is_idempotent(
    review_fixture: tuple[Path, Path, Path],
) -> None:
    folder, db, criteria = review_fixture
    assert import_smoke_run(folder, db, criteria) == folder.name
    assert import_smoke_run(folder, db, criteria) == folder.name
    dataset = load_dataset(db)
    assert dataset["criteria_text"] == criteria.read_text()
    assert len(dataset["cases"]) == 6
    assert dataset["events"] == []
    with closing(sqlite3.connect(db)) as conn, conn:
        assert conn.execute("SELECT * FROM eval_outputs").fetchall() == [
            (42, "exact human wording")
        ]
        row = conn.execute(
            "SELECT request_json FROM review_cases ORDER BY ordinal"
        ).fetchone()
        assert row is not None
        assert row[0] == (folder / "01-paper-scissors.request.json").read_bytes()
        assert (
            conn.execute("SELECT total_tokens FROM review_rounds").fetchall()
            == [(14,)] * 6
        )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE review_cases SET case_id='changed'")


def test_changed_artifact_rejected_before_import(
    review_fixture: tuple[Path, Path, Path],
) -> None:
    folder, db, criteria = review_fixture
    (folder / "06-scissors-scissors.response.json").write_bytes(b"changed")
    with pytest.raises(ReviewError, match="Changed evidence"):
        import_smoke_run(folder, db, criteria)
    with closing(sqlite3.connect(db)) as conn, conn:
        assert conn.execute("SELECT count(*) FROM eval_outputs").fetchone() == (1,)
        assert not conn.execute(
            "SELECT name FROM sqlite_master WHERE name='review_cases'"
        ).fetchall()


def test_frozen_criteria_and_receipts_cannot_be_replaced(
    review_fixture: tuple[Path, Path, Path],
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    original = criteria.read_bytes()
    criteria.write_bytes(original + b" changed")
    with pytest.raises(ReviewError, match="different evidence or criteria"):
        import_smoke_run(folder, db, criteria)
    criteria.write_bytes(original)
    receipt = folder / "01-paper-scissors.receipt.json"
    receipt.write_bytes(receipt.read_bytes() + b"\n")
    with pytest.raises(ReviewError, match="case evidence changed"):
        import_smoke_run(folder, db, criteria)


def test_observations_and_judgments_keep_authors_and_revisions(
    review_fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    data = load_dataset(db)
    notes = tmp_path / "review.notes.json"
    assistant = new_event(
        data,
        "paper-scissors",
        "Codex primary",
        "observation",
        "The relation is legible.",
        role="assistant",
    )
    human = new_event(
        data,
        "paper-scissors",
        "Peanut",
        "judgment",
        "I love the premise.",
        verdict="FAIL",
        field_or_phrase="premise",
    )
    revision = save_notes(notes, data, [assistant, human], None)
    assert import_notes(db, notes) == 2
    assert import_notes(db, notes) == 0
    correction = new_event(
        data,
        "paper-scissors",
        "Peanut",
        "judgment",
        "Revised after discussion.",
        verdict="PASS",
    )
    save_notes(notes, data, [assistant, human, correction], revision)
    assert import_notes(db, notes) == 1
    saved = load_dataset(db)["events"]
    assert saved == [assistant, human, correction]
    assert saved[0]["verdict"] is None
    assert saved[1]["note"] == "I love the premise."
    with closing(sqlite3.connect(db)) as conn, conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM review_events")


def test_notes_reject_stale_or_rewritten_events_and_wrong_source(
    review_fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    data = load_dataset(db)
    notes = tmp_path / "review.notes.json"
    event = new_event(data, "paper-scissors", "Peanut", "observation", "A note.")
    revision = save_notes(notes, data, [event], None)
    with pytest.raises(ReviewError, match="another session"):
        save_notes(notes, data, [event], None)
    with pytest.raises(ReviewError, match="Earlier notes"):
        save_notes(notes, data, [{**event, "note": "replacement"}], revision)
    wrong = {**data, "criteria_sha256": "wrong"}
    with pytest.raises(ReviewError, match="another dataset or criterion"):
        read_notes(notes, wrong)
    with pytest.raises(ReviewError, match="outside the original"):
        save_notes(folder / "review.notes.json", data, [event], None)


def test_conflicting_event_import_rolls_back_entire_batch(
    review_fixture: tuple[Path, Path, Path],
    tmp_path: Path,
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    data = load_dataset(db)
    first = new_event(data, "paper-scissors", "Peanut", "observation", "original")
    notes = tmp_path / "first.notes.json"
    save_notes(notes, data, [first], None)
    import_notes(db, notes)
    second = new_event(
        data, "rock-paper", "Codex primary", "observation", "new", role="assistant"
    )
    conflict = tmp_path / "conflict.notes.json"
    save_notes(conflict, data, [second, {**first, "note": "changed"}], None)
    with pytest.raises(ReviewError, match="imported event changed"):
        import_notes(db, conflict)
    assert load_dataset(db)["events"] == [first]


@pytest.mark.parametrize(
    "overrides",
    [
        {"kind": "observation", "verdict": "PASS"},
        {"kind": "judgment", "verdict": None},
        {"kind": "observation", "note": ""},
        {"kind": "judgment", "verdict": "PASS", "note": None},
    ],
)
def test_event_semantics(
    review_fixture: tuple[Path, Path, Path], overrides: dict[str, Any]
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    values = {"kind": "observation", "note": "Some wording.", **overrides}
    with pytest.raises(ReviewError):
        new_event(load_dataset(db), "paper-scissors", "Peanut", **values)


def test_verdict_without_repeated_reason_survives_save_and_import(
    review_fixture: tuple[Path, Path, Path], tmp_path: Path
) -> None:
    folder, db, criteria = review_fixture
    import_smoke_run(folder, db, criteria)
    data = load_dataset(db)
    events = [
        new_event(
            data,
            "paper-scissors",
            "Peanut",
            "judgment",
            "One shared issue.",
            verdict="FAIL",
        ),
        new_event(data, "rock-paper", "Peanut", "judgment", "", verdict="FAIL"),
    ]
    notes = tmp_path / "review.notes.json"
    save_notes(notes, data, events, None)
    assert read_notes(notes, data)[0] == events
    assert import_notes(db, notes) == 2
    assert import_notes(db, notes) == 0
    assert load_dataset(db)["events"] == events
