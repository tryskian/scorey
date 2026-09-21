"""Immutable local vector snapshots, independent of the evaluation database."""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def fingerprint(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def unit_vector(values: list[float], dimensions: int) -> tuple[float, ...]:
    if len(values) != dimensions or not all(math.isfinite(v) for v in values):
        raise ValueError("Invalid embedding dimensions or non-finite values.")
    norm = math.sqrt(sum(v * v for v in values))
    if not math.isfinite(norm) or norm <= 0:
        raise ValueError("Embedding must have a finite, positive norm.")
    return tuple(v / norm for v in values)


def save_index(path: Path, payload: dict[str, Any]) -> str:
    """Append a content-addressed snapshot. Existing snapshots never change."""
    encoded = canonical_json(payload)
    version = fingerprint(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as conn, conn:
        tables = {
            str(row[0])
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if tables - {"scorey_memory_indexes"}:
            raise ValueError("Memory needs its own database, separate from evals.")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS scorey_memory_indexes "
            "(version TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        existing = conn.execute(
            "SELECT payload FROM scorey_memory_indexes WHERE version=?", (version,)
        ).fetchone()
        if existing is not None and existing[0] != encoded:
            raise ValueError("Existing memory snapshot differs from its fingerprint.")
        conn.execute(
            "INSERT OR IGNORE INTO scorey_memory_indexes VALUES (?, ?)",
            (version, encoded),
        )
    return version


def read_index(path: Path, version: str) -> dict[str, Any]:
    if not version:
        raise ValueError("Set SCOREY_MEMORY_INDEX to a built snapshot ID.")
    try:
        with closing(
            sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        ) as conn:
            conn.execute("PRAGMA query_only=ON")
            row = conn.execute(
                "SELECT payload FROM scorey_memory_indexes WHERE version=?", (version,)
            ).fetchone()
    except sqlite3.Error as exc:
        raise ValueError("Memory index unavailable; run make memory-build.") from exc
    if row is None:
        raise ValueError("Pinned memory snapshot was not found.")
    payload = json.loads(row[0])
    if not isinstance(payload, dict) or fingerprint(payload) != version:
        raise ValueError("Memory snapshot integrity check failed.")
    return payload
