from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from scorey.config import EVAL_DB_PATH, USER_PICKS
from scorey.pipeline import RoundState

VERDICTS: tuple[str, ...] = ("pass", "fail")
LIST_VERDICTS: tuple[str, ...] = VERDICTS + ("pending",)
SOURCE_MODES: tuple[str, ...] = ("local", "live")
ROUTE_FAMILIES: tuple[str, ...] = ("cross-object", "same-pick")
LENSES: tuple[str, ...] = ("tone",)

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

CREATE TABLE IF NOT EXISTS eval_lens_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    lens TEXT NOT NULL CHECK (lens IN ('tone')),
    verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (output_id, lens)
);

CREATE TABLE IF NOT EXISTS eval_lens_archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    lens TEXT NOT NULL CHECK (lens IN ('tone')),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (output_id, lens)
);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_eval_db_path() -> Path:
    return EVAL_DB_PATH


def _normalise_user_picks(user_picks: tuple[str, ...] | None) -> tuple[str, ...] | None:
    if user_picks is None:
        return None
    if not user_picks:
        return None
    invalid = [pick for pick in user_picks if pick not in USER_PICKS]
    if invalid:
        invalid_text = ", ".join(invalid)
        raise ValueError(f"Unsupported user picks: {invalid_text}.")
    return user_picks


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
    if verdict is not None and verdict not in LIST_VERDICTS:
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
        elif verdict in VERDICTS:
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
                WHERE current_verdict IS NULL
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
        return list(cursor.fetchall())


def get_output(db_path: Path | None, output_id: int) -> sqlite3.Row:
    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        row = conn.execute(
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
            WHERE id = ?
            """,
            (output_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Output id {output_id} does not exist.")
        return row


def list_review_sample(
    db_path: Path | None,
    *,
    limit: int = 12,
) -> list[sqlite3.Row]:
    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        rows = conn.execute(
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
            WHERE current_verdict IS NULL
            ORDER BY id DESC
            """
        ).fetchall()

    sample: list[sqlite3.Row] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (str(row["model"]), str(row["scorey_pick"]), str(row["user_pick"]))
        if key in seen:
            continue
        seen.add(key)
        sample.append(row)
        if len(sample) >= limit:
            break
    return sample


def list_lens_review_sample(
    db_path: Path | None,
    *,
    lens: str,
    limit: int = 12,
    source_mode: str | None = None,
    user_picks: tuple[str, ...] | None = None,
) -> list[sqlite3.Row]:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")
    if limit < 1:
        raise ValueError("Limit must be at least 1.")
    if source_mode is not None and source_mode not in SOURCE_MODES:
        raise ValueError(f"Unsupported source mode '{source_mode}'.")
    resolved_user_picks = _normalise_user_picks(user_picks)

    where = [
        "current_verdict = 'pass'",
        """
        NOT EXISTS (
            SELECT 1
            FROM eval_lens_judgments lens_judgments
            WHERE lens_judgments.output_id = eval_outputs.id
              AND lens_judgments.lens = ?
        )
        AND NOT EXISTS (
            SELECT 1
            FROM eval_lens_archives lens_archives
            WHERE lens_archives.output_id = eval_outputs.id
              AND lens_archives.lens = ?
        )
        """.strip(),
    ]
    params: list[str] = [lens, lens]
    if source_mode is not None:
        where.append("source_mode = ?")
        params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        where.append(f"user_pick IN ({placeholders})")
        params.extend(resolved_user_picks)

    query = f"""
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
        WHERE {" AND ".join(where)}
        ORDER BY id DESC
    """

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        rows = conn.execute(query, tuple(params)).fetchall()

    sample: list[sqlite3.Row] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (str(row["model"]), str(row["scorey_pick"]), str(row["user_pick"]))
        if key in seen:
            continue
        seen.add(key)
        sample.append(row)
        if len(sample) >= limit:
            break
    return sample


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


def judge_output_for_lens(
    db_path: Path | None,
    output_id: int,
    *,
    lens: str,
    verdict: str,
    note: str,
) -> None:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")
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
            INSERT INTO eval_lens_judgments (
                output_id,
                lens,
                verdict,
                note,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (output_id, lens, verdict, note, utc_now()),
        )


def archive_output_for_lens(
    db_path: Path | None,
    output_id: int,
    *,
    lens: str,
    note: str,
) -> None:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        row = conn.execute(
            """
            SELECT id, current_verdict
            FROM eval_outputs
            WHERE id = ?
            """,
            (output_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Output id {output_id} does not exist.")
        if row["current_verdict"] != "pass":
            raise ValueError(
                "Output id "
                f"{output_id} is not route-pass and cannot be archived for {lens}."
            )

        judged = conn.execute(
            """
            SELECT 1
            FROM eval_lens_judgments
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if judged is not None:
            raise ValueError(
                "Output id "
                f"{output_id} already has a {lens} verdict and cannot be archived."
            )

        conn.execute(
            """
            INSERT INTO eval_lens_archives (
                output_id,
                lens,
                note,
                created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (output_id, lens, note, utc_now()),
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


def lens_counts(
    db_path: Path | None,
    *,
    lens: str,
    source_mode: str | None = None,
    user_picks: tuple[str, ...] | None = None,
) -> dict[str, int]:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")
    if source_mode is not None and source_mode not in SOURCE_MODES:
        raise ValueError(f"Unsupported source mode '{source_mode}'.")
    resolved_user_picks = _normalise_user_picks(user_picks)

    eligible_where = ["current_verdict = 'pass'"]
    params: list[str] = []
    if source_mode is not None:
        eligible_where.append("source_mode = ?")
        params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        eligible_where.append(f"user_pick IN ({placeholders})")
        params.extend(resolved_user_picks)

    eligible_sql = f"""
        SELECT COUNT(*) AS total
        FROM eval_outputs
        WHERE {" AND ".join(eligible_where)}
    """
    judgment_where = [
        "output.current_verdict = 'pass'",
        "lens_judgments.lens = ?",
    ]
    judgment_params: list[str] = [lens]
    if source_mode is not None:
        judgment_where.append("output.source_mode = ?")
        judgment_params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        judgment_where.append(f"output.user_pick IN ({placeholders})")
        judgment_params.extend(resolved_user_picks)

    judgments_sql = f"""
        SELECT
            lens_judgments.verdict AS verdict,
            COUNT(*) AS count
        FROM eval_lens_judgments lens_judgments
        JOIN eval_outputs output
          ON output.id = lens_judgments.output_id
        WHERE {" AND ".join(judgment_where)}
        GROUP BY lens_judgments.verdict
    """

    archive_where = [
        "output.current_verdict = 'pass'",
        "lens_archives.lens = ?",
        "lens_judgments.output_id IS NULL",
    ]
    archive_params: list[str] = [lens]
    if source_mode is not None:
        archive_where.append("output.source_mode = ?")
        archive_params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        archive_where.append(f"output.user_pick IN ({placeholders})")
        archive_params.extend(resolved_user_picks)

    archives_sql = f"""
        SELECT COUNT(*) AS archived
        FROM eval_lens_archives lens_archives
        JOIN eval_outputs output
          ON output.id = lens_archives.output_id
        LEFT JOIN eval_lens_judgments lens_judgments
          ON lens_judgments.output_id = output.id
         AND lens_judgments.lens = lens_archives.lens
        WHERE {" AND ".join(archive_where)}
    """

    with closing(connect(db_path)) as conn, conn:
        conn.executescript(SCHEMA)
        total_row = conn.execute(eligible_sql, tuple(params)).fetchone()
        total = int(total_row["total"] or 0) if total_row is not None else 0
        verdict_rows = conn.execute(judgments_sql, tuple(judgment_params)).fetchall()
        archive_row = conn.execute(archives_sql, tuple(archive_params)).fetchone()

    pass_count = 0
    fail_count = 0
    for row in verdict_rows:
        if row["verdict"] == "pass":
            pass_count = int(row["count"] or 0)
        elif row["verdict"] == "fail":
            fail_count = int(row["count"] or 0)

    archived_count = int(archive_row["archived"] or 0) if archive_row is not None else 0

    return {
        "total": total,
        "pass": pass_count,
        "fail": fail_count,
        "pending": total - pass_count - fail_count - archived_count,
        "archived": archived_count,
    }
