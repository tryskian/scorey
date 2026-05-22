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
DISPOSITIONS: tuple[str, ...] = ("retain", "evict")
PULSE_LABELS: tuple[str, ...] = ("anchor", "counted_seam", "excluded_noise")
COUNTED_PULSE_LABELS: tuple[str, ...] = ("anchor", "counted_seam")
PULSE_EXCLUSION_REASONS: tuple[str, ...] = (
    "operator_artifact",
    "off_target_failure",
)
PULSE_STATUSES: tuple[str, ...] = ("open", "closed")

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
    current_verdict TEXT NOT NULL DEFAULT 'pending'
        CHECK (current_verdict IN ('pass', 'fail', 'pending')),
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

CREATE TABLE IF NOT EXISTS eval_lens_failure_dispositions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    lens TEXT NOT NULL CHECK (lens IN ('tone')),
    disposition TEXT NOT NULL CHECK (disposition IN ('retain', 'evict')),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (output_id, lens)
);

CREATE TABLE IF NOT EXISTS eval_lens_failure_disposition_archives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    lens TEXT NOT NULL CHECK (lens IN ('tone')),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE (output_id, lens)
);

CREATE TABLE IF NOT EXISTS eval_pulses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_family TEXT NOT NULL,
    first_output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE RESTRICT,
    last_output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE RESTRICT,
    note TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'closed')),
    created_at TEXT NOT NULL,
    closed_at TEXT,
    CHECK (first_output_id <= last_output_id)
);

CREATE TABLE IF NOT EXISTS eval_pulse_judgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pulse_id INTEGER NOT NULL REFERENCES eval_pulses(id) ON DELETE CASCADE,
    output_id INTEGER NOT NULL REFERENCES eval_outputs(id) ON DELETE CASCADE,
    label TEXT NOT NULL
        CHECK (label IN ('anchor', 'counted_seam', 'excluded_noise')),
    reason TEXT NOT NULL DEFAULT ''
        CHECK (
            reason = ''
            OR reason IN (
                'operator_artifact',
                'off_target_failure'
            )
        ),
    created_at TEXT NOT NULL,
    UNIQUE (pulse_id, output_id)
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


def _needs_pending_verdict_migration(conn: sqlite3.Connection) -> bool:
    columns = conn.execute("PRAGMA table_info(eval_outputs)").fetchall()
    if not columns:
        return False

    current_verdict_column = next(
        (column for column in columns if column["name"] == "current_verdict"),
        None,
    )
    if current_verdict_column is None:
        return False

    if int(current_verdict_column["notnull"] or 0) == 0:
        return True

    default_value = current_verdict_column["dflt_value"]
    if default_value is None:
        return True

    normalised_default = str(default_value).strip("'\"").lower()
    if normalised_default != "pending":
        return True

    null_row = conn.execute(
        """
        SELECT 1
        FROM eval_outputs
        WHERE current_verdict IS NULL
        LIMIT 1
        """
    ).fetchone()
    return null_row is not None


def _migrate_pending_verdict_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.executescript(
        """
        CREATE TABLE eval_outputs_new (
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
            current_verdict TEXT NOT NULL DEFAULT 'pending'
                CHECK (current_verdict IN ('pass', 'fail', 'pending')),
            current_note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE eval_judgments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_id INTEGER NOT NULL
                REFERENCES eval_outputs_new(id) ON DELETE CASCADE,
            verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        );

        CREATE TABLE eval_lens_judgments_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_id INTEGER NOT NULL
                REFERENCES eval_outputs_new(id) ON DELETE CASCADE,
            lens TEXT NOT NULL CHECK (lens IN ('tone')),
            verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE (output_id, lens)
        );

        CREATE TABLE eval_lens_archives_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_id INTEGER NOT NULL
                REFERENCES eval_outputs_new(id) ON DELETE CASCADE,
            lens TEXT NOT NULL CHECK (lens IN ('tone')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE (output_id, lens)
        );

        CREATE TABLE eval_lens_failure_dispositions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_id INTEGER NOT NULL
                REFERENCES eval_outputs_new(id) ON DELETE CASCADE,
            lens TEXT NOT NULL CHECK (lens IN ('tone')),
            disposition TEXT NOT NULL CHECK (disposition IN ('retain', 'evict')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE (output_id, lens)
        );

        CREATE TABLE eval_lens_failure_disposition_archives_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            output_id INTEGER NOT NULL
                REFERENCES eval_outputs_new(id) ON DELETE CASCADE,
            lens TEXT NOT NULL CHECK (lens IN ('tone')),
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            UNIQUE (output_id, lens)
        );

        INSERT INTO eval_outputs_new (
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
        )
        SELECT
            id,
            user_pick,
            scorey_pick,
            route_family,
            round_text,
            source_mode,
            model,
            COALESCE(current_verdict, 'pending'),
            current_note,
            created_at
        FROM eval_outputs;

        INSERT INTO eval_judgments_new (id, output_id, verdict, note, created_at)
        SELECT id, output_id, verdict, note, created_at
        FROM eval_judgments;

        INSERT INTO eval_lens_judgments_new (
            id,
            output_id,
            lens,
            verdict,
            note,
            created_at
        )
        SELECT id, output_id, lens, verdict, note, created_at
        FROM eval_lens_judgments;

        INSERT INTO eval_lens_archives_new (id, output_id, lens, note, created_at)
        SELECT id, output_id, lens, note, created_at
        FROM eval_lens_archives;

        INSERT INTO eval_lens_failure_dispositions_new (
            id,
            output_id,
            lens,
            disposition,
            note,
            created_at
        )
        SELECT id, output_id, lens, disposition, note, created_at
        FROM eval_lens_failure_dispositions;

        INSERT INTO eval_lens_failure_disposition_archives_new (
            id,
            output_id,
            lens,
            note,
            created_at
        )
        SELECT id, output_id, lens, note, created_at
        FROM eval_lens_failure_disposition_archives;

        DROP TABLE eval_lens_failure_disposition_archives;
        DROP TABLE eval_lens_failure_dispositions;
        DROP TABLE eval_lens_archives;
        DROP TABLE eval_lens_judgments;
        DROP TABLE eval_judgments;
        DROP TABLE eval_outputs;

        ALTER TABLE eval_outputs_new RENAME TO eval_outputs;
        ALTER TABLE eval_judgments_new RENAME TO eval_judgments;
        ALTER TABLE eval_lens_judgments_new RENAME TO eval_lens_judgments;
        ALTER TABLE eval_lens_archives_new RENAME TO eval_lens_archives;
        ALTER TABLE eval_lens_failure_dispositions_new
            RENAME TO eval_lens_failure_dispositions;
        ALTER TABLE eval_lens_failure_disposition_archives_new
            RENAME TO eval_lens_failure_disposition_archives;
        """
    )
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")

    problems = conn.execute("PRAGMA foreign_key_check").fetchall()
    if problems:
        raise RuntimeError("Foreign key check failed after pending verdict migration.")


def prepare_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    if _needs_pending_verdict_migration(conn):
        _migrate_pending_verdict_schema(conn)


def init_db(db_path: Path | None = None) -> Path:
    resolved = default_eval_db_path() if db_path is None else db_path
    with closing(connect(resolved)) as conn, conn:
        prepare_db(conn)
    return resolved


def _validate_pulse_label(label: str) -> None:
    if label not in PULSE_LABELS:
        raise ValueError(f"Unsupported pulse label '{label}'.")


def _validate_pulse_reason(label: str, reason: str, current_verdict: str) -> None:
    if current_verdict != "pass":
        raise ValueError("Only route-pass rows may enter a Scorey pulse.")

    if label == "excluded_noise":
        if reason not in PULSE_EXCLUSION_REASONS:
            supported = ", ".join(PULSE_EXCLUSION_REASONS)
            raise ValueError(
                f"Excluded pulse rows require one of these reasons: {supported}."
            )
        return

    if reason:
        raise ValueError("Pulse reasons are only valid for the excluded_noise label.")


def _get_pulse_row(conn: sqlite3.Connection, pulse_id: int) -> sqlite3.Row:
    pulse = conn.execute(
        """
        SELECT
            id,
            target_family,
            first_output_id,
            last_output_id,
            note,
            status,
            created_at,
            closed_at
        FROM eval_pulses
        WHERE id = ?
        """,
        (pulse_id,),
    ).fetchone()
    if pulse is None:
        raise ValueError(f"Pulse id {pulse_id} does not exist.")
    return pulse


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
        prepare_db(conn)
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


def create_pulse(
    db_path: Path | None,
    *,
    target_family: str,
    first_output_id: int,
    last_output_id: int,
    note: str = "",
) -> int:
    if not target_family.strip():
        raise ValueError("Pulse target family must be non-empty.")
    if first_output_id > last_output_id:
        raise ValueError("Pulse first output id must be less than or equal to last.")

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)

        first_row = conn.execute(
            "SELECT id FROM eval_outputs WHERE id = ?",
            (first_output_id,),
        ).fetchone()
        if first_row is None:
            raise ValueError(f"Output id {first_output_id} does not exist.")

        last_row = conn.execute(
            "SELECT id FROM eval_outputs WHERE id = ?",
            (last_output_id,),
        ).fetchone()
        if last_row is None:
            raise ValueError(f"Output id {last_output_id} does not exist.")

        range_counts = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN current_verdict = 'pending' THEN 1 ELSE 0 END)
                    AS pending,
                SUM(CASE WHEN current_verdict = 'pass' THEN 1 ELSE 0 END)
                    AS route_pass
            FROM eval_outputs
            WHERE id BETWEEN ? AND ?
            """,
            (first_output_id, last_output_id),
        ).fetchone()
        total = int(range_counts["total"] or 0) if range_counts is not None else 0
        pending = int(range_counts["pending"] or 0) if range_counts is not None else 0
        route_pass = (
            int(range_counts["route_pass"] or 0) if range_counts is not None else 0
        )
        if total == 0:
            raise ValueError("Pulse range does not contain any eval outputs.")
        if pending:
            raise ValueError(
                "Pulse range still contains route-pending rows and cannot open yet."
            )
        if route_pass != total:
            raise ValueError("Scorey pulses must open over a fully route-pass range.")

        existing_tone_lane = conn.execute(
            """
            SELECT 1
            FROM eval_outputs output
            LEFT JOIN eval_lens_judgments lens_judgments
              ON lens_judgments.output_id = output.id
             AND lens_judgments.lens = 'tone'
            LEFT JOIN eval_lens_archives lens_archives
              ON lens_archives.output_id = output.id
             AND lens_archives.lens = 'tone'
            LEFT JOIN eval_lens_failure_dispositions failure_dispositions
              ON failure_dispositions.output_id = output.id
             AND failure_dispositions.lens = 'tone'
            LEFT JOIN eval_lens_failure_disposition_archives failure_archives
              ON failure_archives.output_id = output.id
             AND failure_archives.lens = 'tone'
            WHERE output.id BETWEEN ? AND ?
              AND (
                    lens_judgments.output_id IS NOT NULL
                 OR lens_archives.output_id IS NOT NULL
                 OR failure_dispositions.output_id IS NOT NULL
                 OR failure_archives.output_id IS NOT NULL
              )
            LIMIT 1
            """,
            (first_output_id, last_output_id),
        ).fetchone()
        if existing_tone_lane is not None:
            raise ValueError(
                "Scorey pulses must open over rows that are still outside "
                "the tone lane."
            )

        existing = conn.execute(
            """
            SELECT id
            FROM eval_pulses
            WHERE target_family = ?
              AND first_output_id = ?
              AND last_output_id = ?
              AND status = 'open'
            """,
            (target_family, first_output_id, last_output_id),
        ).fetchone()
        if existing is not None:
            raise ValueError(
                "An open pulse already exists for this target family and range."
            )

        cursor = conn.execute(
            """
            INSERT INTO eval_pulses (
                target_family,
                first_output_id,
                last_output_id,
                note,
                status,
                created_at
            ) VALUES (?, ?, ?, ?, 'open', ?)
            """,
            (target_family, first_output_id, last_output_id, note, utc_now()),
        )
        if cursor.lastrowid is None:
            raise RuntimeError("Failed to retrieve inserted pulse id.")
        return cursor.lastrowid


def list_pulse_review_sample(
    db_path: Path | None,
    *,
    pulse_id: int,
    limit: int = 12,
) -> list[sqlite3.Row]:
    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
        pulse = _get_pulse_row(conn, pulse_id)
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
            WHERE id BETWEEN ? AND ?
              AND NOT EXISTS (
                    SELECT 1
                    FROM eval_pulse_judgments pulse_judgments
                    WHERE pulse_judgments.pulse_id = ?
                      AND pulse_judgments.output_id = eval_outputs.id
              )
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                int(pulse["first_output_id"]),
                int(pulse["last_output_id"]),
                pulse_id,
                limit,
            ),
        ).fetchall()
    return list(rows)


def judge_output_for_pulse(
    db_path: Path | None,
    pulse_id: int,
    output_id: int,
    *,
    label: str,
    reason: str = "",
) -> None:
    _validate_pulse_label(label)

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
        pulse = _get_pulse_row(conn, pulse_id)
        if pulse["status"] != "open":
            raise ValueError(f"Pulse id {pulse_id} is closed and cannot take labels.")

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
        if not (
            int(pulse["first_output_id"]) <= output_id <= int(pulse["last_output_id"])
        ):
            raise ValueError(
                f"Output id {output_id} is outside pulse {pulse_id}'s range."
            )
        current_verdict = str(row["current_verdict"])
        if current_verdict == "pending":
            raise ValueError(
                f"Output id {output_id} is still route-pending and cannot join a pulse."
            )

        _validate_pulse_reason(label, reason, current_verdict)

        conn.execute(
            """
            INSERT INTO eval_pulse_judgments (
                pulse_id,
                output_id,
                label,
                reason,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (pulse_id, output_id, label, reason, utc_now()),
        )


def pulse_summary(db_path: Path | None, pulse_id: int) -> dict[str, object]:
    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
        pulse = _get_pulse_row(conn, pulse_id)

        raw_row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM eval_outputs
            WHERE id BETWEEN ? AND ?
            """,
            (pulse["first_output_id"], pulse["last_output_id"]),
        ).fetchone()
        raw_total = int(raw_row["total"] or 0) if raw_row is not None else 0

        label_rows = conn.execute(
            """
            SELECT
                label,
                COUNT(*) AS count
            FROM eval_pulse_judgments
            WHERE pulse_id = ?
            GROUP BY label
            """,
            (pulse_id,),
        ).fetchall()
        reason_rows = conn.execute(
            """
            SELECT
                reason,
                COUNT(*) AS count
            FROM eval_pulse_judgments
            WHERE pulse_id = ?
              AND label = 'excluded_noise'
            GROUP BY reason
            """,
            (pulse_id,),
        ).fetchall()

    label_counts = {label: 0 for label in PULSE_LABELS}
    for row in label_rows:
        label_counts[str(row["label"])] = int(row["count"] or 0)

    excluded_by_reason = {reason: 0 for reason in PULSE_EXCLUSION_REASONS}
    for row in reason_rows:
        excluded_by_reason[str(row["reason"])] = int(row["count"] or 0)

    counted_total = sum(label_counts[label] for label in COUNTED_PULSE_LABELS)
    pending = raw_total - sum(label_counts.values())
    if pending > 0:
        verdict = "pending"
    elif label_counts["anchor"] > label_counts["counted_seam"]:
        verdict = "pass"
    else:
        verdict = "fail"

    return {
        "id": int(pulse["id"]),
        "target_family": str(pulse["target_family"]),
        "first_output_id": int(pulse["first_output_id"]),
        "last_output_id": int(pulse["last_output_id"]),
        "note": str(pulse["note"]),
        "status": str(pulse["status"]),
        "created_at": str(pulse["created_at"]),
        "closed_at": None if pulse["closed_at"] is None else str(pulse["closed_at"]),
        "raw_total": raw_total,
        "anchor": label_counts["anchor"],
        "counted_seam": label_counts["counted_seam"],
        "excluded_noise": label_counts["excluded_noise"],
        "excluded_by_reason": excluded_by_reason,
        "counted_total": counted_total,
        "pending": pending,
        "verdict": verdict,
    }


def close_pulse(db_path: Path | None, pulse_id: int) -> dict[str, object]:
    summary = pulse_summary(db_path, pulse_id)
    pending = summary["pending"]
    if not isinstance(pending, int):
        raise RuntimeError("Pulse summary pending count must be an int.")
    if pending > 0:
        raise ValueError(
            f"Pulse id {pulse_id} still has pending rows and cannot close yet."
        )

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
        pulse = _get_pulse_row(conn, pulse_id)
        tone_archive_note = (
            "settled by pulse "
            f"{pulse_id} ({summary['target_family']}, verdict={summary['verdict']})"
        )
        conn.execute(
            """
            INSERT INTO eval_lens_archives (
                output_id,
                lens,
                note,
                created_at
            )
            SELECT
                output.id,
                'tone',
                ?,
                ?
            FROM eval_outputs output
            LEFT JOIN eval_lens_judgments lens_judgments
              ON lens_judgments.output_id = output.id
             AND lens_judgments.lens = 'tone'
            LEFT JOIN eval_lens_archives lens_archives
              ON lens_archives.output_id = output.id
             AND lens_archives.lens = 'tone'
            WHERE output.id BETWEEN ? AND ?
              AND output.current_verdict = 'pass'
              AND lens_judgments.output_id IS NULL
              AND lens_archives.output_id IS NULL
            """,
            (
                tone_archive_note,
                utc_now(),
                int(pulse["first_output_id"]),
                int(pulse["last_output_id"]),
            ),
        )
        if pulse["status"] != "closed":
            conn.execute(
                """
                UPDATE eval_pulses
                SET status = 'closed', closed_at = ?
                WHERE id = ?
                """,
                (utc_now(), pulse_id),
            )
    return pulse_summary(db_path, pulse_id)


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
        prepare_db(conn)
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
                WHERE current_verdict = 'pending'
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
        return list(cursor.fetchall())


def get_output(db_path: Path | None, output_id: int) -> sqlite3.Row:
    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
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
        prepare_db(conn)
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
            WHERE current_verdict = 'pending'
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
        prepare_db(conn)
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


def list_lens_failure_disposition_sample(
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
        EXISTS (
            SELECT 1
            FROM eval_lens_judgments lens_judgments
            WHERE lens_judgments.output_id = eval_outputs.id
              AND lens_judgments.lens = ?
              AND lens_judgments.verdict = 'fail'
        )
        AND NOT EXISTS (
            SELECT 1
            FROM eval_lens_failure_dispositions failure_dispositions
            WHERE failure_dispositions.output_id = eval_outputs.id
              AND failure_dispositions.lens = ?
        )
        AND NOT EXISTS (
            SELECT 1
            FROM eval_lens_failure_disposition_archives failure_disposition_archives
            WHERE failure_disposition_archives.output_id = eval_outputs.id
              AND failure_disposition_archives.lens = ?
        )
        """.strip(),
    ]
    params: list[str] = [lens, lens, lens]
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
        prepare_db(conn)
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
        prepare_db(conn)
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
        prepare_db(conn)
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
        prepare_db(conn)
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


def record_failure_disposition_for_lens(
    db_path: Path | None,
    output_id: int,
    *,
    lens: str,
    disposition: str,
    note: str,
) -> None:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")
    if disposition not in DISPOSITIONS:
        raise ValueError(f"Unsupported disposition '{disposition}'.")

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
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
                f"{output_id} is not route-pass and cannot record {lens} disposition."
            )

        judged = conn.execute(
            """
            SELECT verdict
            FROM eval_lens_judgments
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if judged is None or judged["verdict"] != "fail":
            raise ValueError(
                "Output id "
                f"{output_id} must have a failed {lens} verdict before disposition."
            )

        archived = conn.execute(
            """
            SELECT 1
            FROM eval_lens_archives
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if archived is not None:
            raise ValueError(
                "Output id "
                f"{output_id} is archived for {lens} and cannot take a disposition."
            )

        conn.execute(
            """
            INSERT INTO eval_lens_failure_dispositions (
                output_id,
                lens,
                disposition,
                note,
                created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (output_id, lens, disposition, note, utc_now()),
        )


def archive_failure_disposition_for_lens(
    db_path: Path | None,
    output_id: int,
    *,
    lens: str,
    note: str,
) -> None:
    if lens not in LENSES:
        raise ValueError(f"Unsupported lens '{lens}'.")

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
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
                f"{output_id} is not route-pass and cannot archive {lens} disposition."
            )

        judged = conn.execute(
            """
            SELECT verdict
            FROM eval_lens_judgments
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if judged is None or judged["verdict"] != "fail":
            raise ValueError(
                "Output id "
                f"{output_id} must have a failed {lens} verdict before "
                "disposition archive."
            )

        disposed = conn.execute(
            """
            SELECT 1
            FROM eval_lens_failure_dispositions
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if disposed is not None:
            raise ValueError(
                "Output id "
                f"{output_id} already has a {lens} disposition and cannot be archived."
            )

        archived = conn.execute(
            """
            SELECT 1
            FROM eval_lens_failure_disposition_archives
            WHERE output_id = ? AND lens = ?
            """,
            (output_id, lens),
        ).fetchone()
        if archived is not None:
            raise ValueError(
                f"Output id {output_id} already has an archived {lens} disposition."
            )

        conn.execute(
            """
            INSERT INTO eval_lens_failure_disposition_archives (
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
        prepare_db(conn)
        totals = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN current_verdict = 'pass' THEN 1 ELSE 0 END) AS pass,
                SUM(CASE WHEN current_verdict = 'fail' THEN 1 ELSE 0 END) AS fail,
                SUM(CASE WHEN current_verdict = 'pending' THEN 1 ELSE 0 END) AS pending
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
        prepare_db(conn)
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


def lens_failure_disposition_counts(
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

    total_where = [
        "output.current_verdict = 'pass'",
        "lens_judgments.lens = ?",
        "lens_judgments.verdict = 'fail'",
    ]
    total_params: list[str] = [lens]
    if source_mode is not None:
        total_where.append("output.source_mode = ?")
        total_params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        total_where.append(f"output.user_pick IN ({placeholders})")
        total_params.extend(resolved_user_picks)

    totals_sql = f"""
        SELECT COUNT(*) AS total
        FROM eval_lens_judgments lens_judgments
        JOIN eval_outputs output
          ON output.id = lens_judgments.output_id
        WHERE {" AND ".join(total_where)}
    """

    disposition_where = [
        "output.current_verdict = 'pass'",
        "failure_dispositions.lens = ?",
    ]
    disposition_params: list[str] = [lens]
    if source_mode is not None:
        disposition_where.append("output.source_mode = ?")
        disposition_params.append(source_mode)
    if resolved_user_picks is not None:
        placeholders = ", ".join("?" for _ in resolved_user_picks)
        disposition_where.append(f"output.user_pick IN ({placeholders})")
        disposition_params.extend(resolved_user_picks)

    dispositions_sql = f"""
        SELECT
            failure_dispositions.disposition AS disposition,
            COUNT(*) AS count
        FROM eval_lens_failure_dispositions failure_dispositions
        JOIN eval_outputs output
          ON output.id = failure_dispositions.output_id
        WHERE {" AND ".join(disposition_where)}
        GROUP BY failure_dispositions.disposition
    """

    archive_where = [
        "output.current_verdict = 'pass'",
        "failure_disposition_archives.lens = ?",
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
        FROM eval_lens_failure_disposition_archives failure_disposition_archives
        JOIN eval_outputs output
          ON output.id = failure_disposition_archives.output_id
        WHERE {" AND ".join(archive_where)}
    """

    with closing(connect(db_path)) as conn, conn:
        prepare_db(conn)
        total_row = conn.execute(totals_sql, tuple(total_params)).fetchone()
        total = int(total_row["total"] or 0) if total_row is not None else 0
        disposition_rows = conn.execute(
            dispositions_sql,
            tuple(disposition_params),
        ).fetchall()
        archive_row = conn.execute(archives_sql, tuple(archive_params)).fetchone()

    retain_count = 0
    evict_count = 0
    for row in disposition_rows:
        if row["disposition"] == "retain":
            retain_count = int(row["count"] or 0)
        elif row["disposition"] == "evict":
            evict_count = int(row["count"] or 0)
    archived_count = int(archive_row["archived"] or 0) if archive_row is not None else 0

    return {
        "total": total,
        "retain": retain_count,
        "evict": evict_count,
        "pending": total - retain_count - evict_count - archived_count,
        "archived": archived_count,
    }
