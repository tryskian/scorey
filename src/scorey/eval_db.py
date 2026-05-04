from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from scorey.config import EVAL_DB_PATH, USER_PICKS
from scorey.pipeline import RoundState

VERDICTS: tuple[str, ...] = ("pass", "fail")
SOURCE_MODES: tuple[str, ...] = ("local", "live")
ROUTE_FAMILIES: tuple[str, ...] = ("cross-object", "same-pick")

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_pick TEXT NOT NULL
        CHECK (user_pick IN ('rock', 'paper', 'scissors')),
    scorey_pick TEXT NOT NULL
        CHECK (scorey_pick IN ('rock', 'paper', 'scissors')),
    route_family TEXT NOT NULL
        CHECK (route_family IN ('cross-object', 'same-pick')),
    round_text TEXT NOT NULL,
    source_mode TEXT NOT NULL
        CHECK (source_mode IN ('local', 'live')),
    model TEXT NOT NULL,
    current_verdict TEXT DEFAULT NULL
        CHECK (current_verdict IN ('pass', 'fail') OR current_verdict IS NULL),
    current_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_eval_db_path() -> Path:
    return EVAL_DB_PATH


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    resolved = default_eval_db_path() if db_path is None else db_path
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> Path:
    resolved = default_eval_db_path() if db_path is None else db_path
    with closing(connect(resolved)) as conn, conn:
        conn.executescript(SCHEMA)
    return resolved


def record_output(
    db_path: Path | None,
    *,
    user_pick: str,
    scorey_pick: str,
    route_family: str,
    round_text: str,
    source_mode: str,
    model: str,
) -> int:
    if user_pick not in USER_PICKS:
        raise ValueError(f"Unsupported user pick '{user_pick}'.")
    if scorey_pick not in USER_PICKS:
        raise ValueError(f"Unsupported Scorey pick '{scorey_pick}'.")
    if route_family not in ROUTE_FAMILIES:
        raise ValueError(f"Unsupported route family '{route_family}'.")
    if source_mode not in SOURCE_MODES:
        raise ValueError(f"Unsupported source mode '{source_mode}'.")
    if not round_text.strip():
        raise ValueError("Round text must be non-empty.")
    if not model.strip():
        raise ValueError("Model must be non-empty.")

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        cursor = conn.execute(
            """
            INSERT INTO eval_outputs (
                user_pick,
                scorey_pick,
                route_family,
                round_text,
                source_mode,
                model,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_pick,
                scorey_pick,
                route_family,
                round_text,
                source_mode,
                model,
                utc_now(),
            ),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve inserted output id.")
        return cursor.lastrowid


def record_round_state(
    db_path: Path | None,
    round_state: RoundState,
    round_text: str,
    *,
    source_mode: str,
    model: str,
) -> int:
    return record_output(
        db_path,
        user_pick=round_state.user_pick,
        scorey_pick=round_state.scorey_pick,
        route_family=round_state.route_family,
        round_text=round_text,
        source_mode=source_mode,
        model=model,
    )


def list_outputs(
    db_path: Path | None,
    *,
    limit: int = 20,
    verdict: str | None = None,
) -> list[sqlite3.Row]:
    if limit < 1:
        raise ValueError("Limit must be at least 1.")
    if verdict is not None and verdict not in VERDICTS:
        raise ValueError(f"Unsupported verdict '{verdict}'.")

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        if verdict is None:
            cursor = conn.execute(
                """
                SELECT
                    id,
                    user_pick,
                    scorey_pick,
                    route_family,
                    round_text,
                    source_mode,
                    model,
                    current_verdict,
                    current_note,
                    created_at
                FROM eval_outputs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
        else:
            cursor = conn.execute(
                """
                SELECT
                    id,
                    user_pick,
                    scorey_pick,
                    route_family,
                    round_text,
                    source_mode,
                    model,
                    current_verdict,
                    current_note,
                    created_at
                FROM eval_outputs
                WHERE current_verdict = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (verdict, limit),
            )
        return list(cursor.fetchall())


def judge_output(
    db_path: Path | None,
    output_id: int,
    verdict: str,
    note: str,
) -> None:
    if verdict not in VERDICTS:
        raise ValueError(f"Unsupported verdict '{verdict}'.")

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        row = conn.execute(
            "SELECT id FROM eval_outputs WHERE id = ?",
            (output_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Output id {output_id} does not exist.")

        conn.execute(
            """
            INSERT INTO eval_judgments (
                output_id,
                verdict,
                note,
                created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (output_id, verdict, note, utc_now()),
        )
        conn.execute(
            """
            UPDATE eval_outputs
            SET current_verdict = ?, current_note = ?
            WHERE id = ?
            """,
            (verdict, note, output_id),
        )


def counts(db_path: Path | None) -> dict[str, int]:
    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN current_verdict = 'pass' THEN 1 ELSE 0 END) AS pass,
                SUM(CASE WHEN current_verdict = 'fail' THEN 1 ELSE 0 END) AS fail,
                SUM(CASE WHEN current_verdict IS NULL THEN 1 ELSE 0 END) AS pending
            FROM eval_outputs
            """
        ).fetchone()
        if totals is None:
            return {"total": 0, "pass": 0, "fail": 0, "pending": 0}
        return {
            "total": int(totals["total"]),
            "pass": int(totals["pass"] or 0),
            "fail": int(totals["fail"] or 0),
            "pending": int(totals["pending"] or 0),
        }
