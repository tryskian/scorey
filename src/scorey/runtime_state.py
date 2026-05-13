from __future__ import annotations

import sqlite3
import subprocess
from collections.abc import Sequence
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from scorey.config import EVAL_DB_PATH, ROOT
from scorey.eval_db import (
    connect,
    lens_counts,
    lens_failure_disposition_counts,
    prepare_db,
)


@dataclass(frozen=True)
class BatchMeta:
    path: Path
    start_live_count: int | None
    start_output_id: int | None
    started_at: str | None
    duration_seconds: float | None
    mode: str | None
    user_picks: str | None


@dataclass(frozen=True)
class RuntimeState:
    repo_root: Path
    eval_db_configured_path: Path
    eval_db_resolved_path: Path
    local_dir_is_symlink: bool
    in_secondary_worktree: bool
    split_db_risk: bool
    live_counts: dict[str, int]
    tone_counts: dict[str, int]
    disposition_counts: dict[str, int]
    active_boundary_output_id: int | None
    active_slice_total: int
    active_route_pending: int
    active_tone_pending: int
    active_disposition_pending: int
    live_sampler_commands: tuple[str, ...]
    batch_meta: BatchMeta | None
    batch_state: str


def parse_batch_meta(meta_path: Path) -> BatchMeta | None:
    if not meta_path.exists():
        return None

    values: dict[str, str] = {}
    for line in meta_path.read_text().splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    def maybe_int(key: str) -> int | None:
        value = values.get(key)
        if value is None or value == "":
            return None
        return int(value)

    def maybe_float(key: str) -> float | None:
        value = values.get(key)
        if value is None or value == "":
            return None
        return float(value)

    return BatchMeta(
        path=meta_path,
        start_live_count=maybe_int("start_live_count"),
        start_output_id=maybe_int("start_output_id"),
        started_at=values.get("started_at"),
        duration_seconds=maybe_float("duration_seconds"),
        mode=values.get("mode"),
        user_picks=values.get("user_picks"),
    )


def detect_live_sampler_commands(
    process_commands: Sequence[str] | None = None,
) -> tuple[str, ...]:
    if process_commands is None:
        completed = subprocess.run(
            ["ps", "-axo", "pid=,command="],
            check=True,
            capture_output=True,
            text=True,
        )
        process_commands = completed.stdout.splitlines()

    matches: list[str] = []
    for raw_line in process_commands:
        line = " ".join(raw_line.split())
        if not line:
            continue
        if (
            " scorey eval-sample-live " in f" {line} "
            or "-m scorey eval-sample-live" in line
        ):
            matches.append(line)
    return tuple(matches)


def _one_count(
    conn: sqlite3.Connection,
    sql: str,
    params: tuple[object, ...] = (),
) -> int:
    row = conn.execute(sql, params).fetchone()
    if row is None:
        return 0
    value = row[0]
    return int(value or 0)


def _first_pending_output_id(conn: sqlite3.Connection) -> int | None:
    queries = (
        """
        SELECT MIN(id)
        FROM eval_outputs
        WHERE source_mode = 'live' AND current_verdict = 'pending'
        """,
        """
        SELECT MIN(output.id)
        FROM eval_outputs output
        LEFT JOIN eval_lens_judgments lens_judgments
          ON lens_judgments.output_id = output.id
         AND lens_judgments.lens = 'tone'
        LEFT JOIN eval_lens_archives lens_archives
          ON lens_archives.output_id = output.id
         AND lens_archives.lens = 'tone'
        WHERE output.source_mode = 'live'
          AND output.current_verdict = 'pass'
          AND lens_judgments.output_id IS NULL
          AND lens_archives.output_id IS NULL
        """,
        """
        SELECT MIN(output.id)
        FROM eval_outputs output
        JOIN eval_lens_judgments lens_judgments
          ON lens_judgments.output_id = output.id
         AND lens_judgments.lens = 'tone'
         AND lens_judgments.verdict = 'fail'
        LEFT JOIN eval_lens_failure_dispositions failure_dispositions
          ON failure_dispositions.output_id = output.id
         AND failure_dispositions.lens = 'tone'
        LEFT JOIN eval_lens_failure_disposition_archives failure_archives
          ON failure_archives.output_id = output.id
         AND failure_archives.lens = 'tone'
        WHERE output.source_mode = 'live'
          AND output.current_verdict = 'pass'
          AND failure_dispositions.output_id IS NULL
          AND failure_archives.output_id IS NULL
        """,
    )

    first_ids = [_one_count(conn, sql) for sql in queries]
    non_zero = [value for value in first_ids if value > 0]
    if not non_zero:
        return None
    return min(non_zero)


def _active_slice_counts(
    conn: sqlite3.Connection,
    boundary_output_id: int | None,
) -> tuple[int, int, int, int]:
    if boundary_output_id is None:
        return (0, 0, 0, 0)

    params = (boundary_output_id,)
    total = _one_count(
        conn,
        """
        SELECT COUNT(*)
        FROM eval_outputs
        WHERE source_mode = 'live' AND id > ?
        """,
        params,
    )
    route_pending = _one_count(
        conn,
        """
        SELECT COUNT(*)
        FROM eval_outputs
        WHERE source_mode = 'live'
          AND current_verdict = 'pending'
          AND id > ?
        """,
        params,
    )
    tone_pending = _one_count(
        conn,
        """
        SELECT COUNT(*)
        FROM eval_outputs output
        LEFT JOIN eval_lens_judgments lens_judgments
          ON lens_judgments.output_id = output.id
         AND lens_judgments.lens = 'tone'
        LEFT JOIN eval_lens_archives lens_archives
          ON lens_archives.output_id = output.id
         AND lens_archives.lens = 'tone'
        WHERE output.source_mode = 'live'
          AND output.current_verdict = 'pass'
          AND output.id > ?
          AND lens_judgments.output_id IS NULL
          AND lens_archives.output_id IS NULL
        """,
        params,
    )
    disposition_pending = _one_count(
        conn,
        """
        SELECT COUNT(*)
        FROM eval_outputs output
        JOIN eval_lens_judgments lens_judgments
          ON lens_judgments.output_id = output.id
         AND lens_judgments.lens = 'tone'
         AND lens_judgments.verdict = 'fail'
        LEFT JOIN eval_lens_failure_dispositions failure_dispositions
          ON failure_dispositions.output_id = output.id
         AND failure_dispositions.lens = 'tone'
        LEFT JOIN eval_lens_failure_disposition_archives failure_archives
          ON failure_archives.output_id = output.id
         AND failure_archives.lens = 'tone'
        WHERE output.source_mode = 'live'
          AND output.current_verdict = 'pass'
          AND output.id > ?
          AND failure_dispositions.output_id IS NULL
          AND failure_archives.output_id IS NULL
        """,
        params,
    )
    return (total, route_pending, tone_pending, disposition_pending)


def collect_runtime_state(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    meta_path: Path | None = None,
    process_commands: Sequence[str] | None = None,
) -> RuntimeState:
    resolved_repo_root = (ROOT if repo_root is None else repo_root).resolve()
    configured_db_path = EVAL_DB_PATH if db_path is None else db_path
    resolved_db_path = configured_db_path.resolve(strict=False)
    local_dir = resolved_repo_root / ".local"
    local_dir_is_symlink = local_dir.is_symlink()
    in_secondary_worktree = "/.codex/worktrees/" in str(resolved_repo_root)
    split_db_risk = in_secondary_worktree and not local_dir_is_symlink

    with closing(connect(configured_db_path)) as conn, conn:
        prepare_db(conn)
        live_counts_row = conn.execute(
            """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN current_verdict = 'pass' THEN 1 ELSE 0 END) AS pass,
                SUM(CASE WHEN current_verdict = 'fail' THEN 1 ELSE 0 END) AS fail,
                SUM(CASE WHEN current_verdict = 'pending' THEN 1 ELSE 0 END) AS pending
            FROM eval_outputs
            WHERE source_mode = 'live'
            """
        ).fetchone()
        first_pending_output_id = _first_pending_output_id(conn)
        active_boundary_output_id = (
            None if first_pending_output_id is None else first_pending_output_id - 1
        )
        (
            active_slice_total,
            active_route_pending,
            active_tone_pending,
            active_disposition_pending,
        ) = _active_slice_counts(conn, active_boundary_output_id)

    live_counts = {
        "total": int(live_counts_row["total"] or 0)
        if live_counts_row is not None
        else 0,
        "pass": int(live_counts_row["pass"] or 0) if live_counts_row is not None else 0,
        "fail": int(live_counts_row["fail"] or 0) if live_counts_row is not None else 0,
        "pending": int(live_counts_row["pending"] or 0)
        if live_counts_row is not None
        else 0,
    }
    tone_counts = lens_counts(configured_db_path, lens="tone", source_mode="live")
    disposition_counts = lens_failure_disposition_counts(
        configured_db_path,
        lens="tone",
        source_mode="live",
    )
    sampler_commands = detect_live_sampler_commands(process_commands)
    resolved_meta_path = (
        resolved_repo_root / ".local" / "live_eval_batch.meta"
        if meta_path is None
        else meta_path
    )
    batch_meta = parse_batch_meta(resolved_meta_path)

    if sampler_commands:
        batch_state = "running"
    elif (
        active_route_pending > 0
        or active_tone_pending > 0
        or active_disposition_pending > 0
    ):
        batch_state = "interrupted"
    else:
        batch_state = "closed"

    return RuntimeState(
        repo_root=resolved_repo_root,
        eval_db_configured_path=configured_db_path,
        eval_db_resolved_path=resolved_db_path,
        local_dir_is_symlink=local_dir_is_symlink,
        in_secondary_worktree=in_secondary_worktree,
        split_db_risk=split_db_risk,
        live_counts=live_counts,
        tone_counts=tone_counts,
        disposition_counts=disposition_counts,
        active_boundary_output_id=active_boundary_output_id,
        active_slice_total=active_slice_total,
        active_route_pending=active_route_pending,
        active_tone_pending=active_tone_pending,
        active_disposition_pending=active_disposition_pending,
        live_sampler_commands=sampler_commands,
        batch_meta=batch_meta,
        batch_state=batch_state,
    )


def format_runtime_state_lines(state: RuntimeState) -> list[str]:
    lines = [
        "== Runtime ==",
        f"eval_db: {state.eval_db_configured_path}",
        f"eval_db_resolved: {state.eval_db_resolved_path}",
        f"live_batch: {state.batch_state}",
        (
            "worktree_db: split-risk"
            if state.split_db_risk
            else (
                "worktree_db: canonical-symlink"
                if state.in_secondary_worktree and state.local_dir_is_symlink
                else "worktree_db: canonical"
            )
        ),
    ]
    if state.batch_meta is None:
        lines.append("batch_meta: missing")
    else:
        meta_parts = [f"path={state.batch_meta.path}"]
        if state.batch_meta.start_output_id is not None:
            meta_parts.append(f"boundary={state.batch_meta.start_output_id}")
        if state.batch_meta.mode:
            meta_parts.append(f"mode={state.batch_meta.mode}")
        if state.batch_meta.user_picks:
            meta_parts.append(f"user_picks={state.batch_meta.user_picks}")
        lines.append("batch_meta: " + " ".join(meta_parts))
    if state.live_sampler_commands:
        lines.append(f"live_sampler: running ({len(state.live_sampler_commands)})")
        for command in state.live_sampler_commands:
            lines.append(f"  - {command}")
    else:
        lines.append("live_sampler: off")
    boundary_text = (
        "none"
        if state.active_boundary_output_id is None
        else str(state.active_boundary_output_id)
    )
    lines.append(
        "active_slice: "
        f"boundary={boundary_text} total={state.active_slice_total} "
        f"route_pending={state.active_route_pending} "
        f"tone_pending={state.active_tone_pending} "
        f"disposition_pending={state.active_disposition_pending}"
    )
    lines.append(
        "live_counts: "
        f"total={state.live_counts['total']} "
        f"pass={state.live_counts['pass']} "
        f"fail={state.live_counts['fail']} "
        f"pending={state.live_counts['pending']}"
    )
    lines.append(
        "tone_counts: "
        f"total={state.tone_counts['total']} "
        f"pass={state.tone_counts['pass']} "
        f"fail={state.tone_counts['fail']} "
        f"archived={state.tone_counts['archived']} "
        f"pending={state.tone_counts['pending']}"
    )
    lines.append(
        "disposition_counts: "
        f"total={state.disposition_counts['total']} "
        f"retain={state.disposition_counts['retain']} "
        f"evict={state.disposition_counts['evict']} "
        f"archived={state.disposition_counts['archived']} "
        f"pending={state.disposition_counts['pending']}"
    )
    return lines
