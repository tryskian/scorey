"""Source-linked principles and frozen, pair-aware retrieval for live rounds."""

from __future__ import annotations

import json
import os
import tempfile
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

from scorey.config import ROOT, Settings, normalise_pick, route_family_for
from scorey.eval_gates import research_beta_1_pass_pairs
from scorey.vector_store import fingerprint, read_index, save_index, unit_vector

QUERY_VERSION = 1
Embedder = Callable[[list[str], str], list[list[float]]]


def load_corpus() -> list[dict[str, Any]]:
    data = json.loads(files("scorey").joinpath("data/principles.json").read_text())
    notes = data["principles"]
    if not notes or len({n["id"] for n in notes}) != len(notes):
        raise ValueError("Memory principles need unique IDs and a nonempty corpus.")
    for note in notes:
        if (
            note.get("kind") != "principle"
            or not note.get("text", "").strip()
            or not note.get("source", "").startswith("docs/")
            or note.get("route") not in ("all", "same-pick", "cross-object")
        ):
            raise ValueError("Invalid source-linked principle.")
    return notes


def pair_query(user_pick: str, scorey_pick: str) -> str:
    user_pick, scorey_pick = normalise_pick(user_pick), normalise_pick(scorey_pick)
    route = route_family_for(user_pick, scorey_pick)
    return (
        f"Scorey's {scorey_pick} wins against the user's {user_pick}. "
        f"Route: {route}. Relevant principles for a compact, playful, "
        "pick-specific unfair explanation and losing-side scoreboard claim."
    )


def embed_texts(texts: list[str], model: str) -> list[list[float]]:
    from openai import OpenAI

    with OpenAI(timeout=30, max_retries=0) as client:
        result = client.embeddings.create(
            model=model, input=texts, encoding_format="float"
        )
    ordered = sorted(result.data, key=lambda item: item.index)
    if [item.index for item in ordered] != list(range(len(texts))):
        raise ValueError("Embedding response does not cover every requested input.")
    return [item.embedding for item in ordered]


def source_hashes(notes: list[dict[str, Any]]) -> dict[str, str]:
    """Validate exact excerpts against current documents before loading a run."""
    sources: dict[str, str] = {}
    for note in notes:
        relative = note["source"].split("#", 1)[0]
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT.resolve()):
            raise ValueError("Memory sources must stay inside the repository.")
        text = path.read_text()
        if " ".join(note["text"].split()) not in " ".join(text.split()):
            raise ValueError(f"Principle {note['id']} no longer matches its source.")
        sources[relative] = fingerprint(text)
    return sources


def build_index(settings: Settings, *, embedder: Embedder = embed_texts) -> str:
    notes = load_corpus()
    sources = source_hashes(notes)
    queries = [pair_query(u, s) for s, u in research_beta_1_pass_pairs()]
    vectors = embedder(
        [n["text"] for n in notes] + queries, settings.memory_embedding_model
    )
    if len(vectors) != len(notes) + len(queries) or not vectors or not vectors[0]:
        raise ValueError("Embedding count does not match the corpus and queries.")
    dimensions = len(vectors[0])
    for vector in vectors:
        unit_vector(vector, dimensions)
    payload = {
        "schema": 1,
        "query_version": QUERY_VERSION,
        "corpus_hash": fingerprint(notes),
        "embedding_model": settings.memory_embedding_model,
        "dimensions": dimensions,
        "notes": notes,
        "source_hashes": sources,
        "vectors": vectors[: len(notes)],
        "queries": dict(zip(queries, vectors[len(notes) :], strict=True)),
    }
    return save_index(Path(settings.memory_db_path), payload)


@dataclass(frozen=True)
class RetrievalContext:
    index: str
    embedding_model: str
    corpus_hash: str
    user_pick: str
    scorey_pick: str
    route_family: str
    query: str
    status: str
    context: str
    matches: tuple[dict[str, Any], ...]
    top_k: int
    max_chars: int
    elapsed_seconds: float


class FrozenMemory:
    """Load a pinned snapshot once; retrieval then uses only local vectors."""

    def __init__(self, settings: Settings) -> None:
        if settings.memory_top_k < 1 or settings.memory_max_chars < 1:
            raise ValueError("Memory result and context limits must be positive.")
        self.settings = settings
        self.payload = read_index(Path(settings.memory_db_path), settings.memory_index)
        p = self.payload
        if p.get("schema") != 1 or p.get("query_version") != QUERY_VERSION:
            raise ValueError("Memory index schema/query version changed; rebuild it.")
        notes = load_corpus()
        if p.get("corpus_hash") != fingerprint(notes):
            raise ValueError("Memory corpus changed; build and pin a new snapshot.")
        if p.get("embedding_model") != settings.memory_embedding_model:
            raise ValueError("Memory embedding model differs from the pinned index.")
        if p.get("notes") != notes or len(p["notes"]) != len(p["vectors"]):
            raise ValueError("Memory snapshot corpus is inconsistent.")
        if p.get("source_hashes") != source_hashes(notes):
            raise ValueError("Memory sources changed; build and pin a new snapshot.")
        self.vectors = [unit_vector(v, p["dimensions"]) for v in p["vectors"]]
        self.queries = {
            q: unit_vector(v, p["dimensions"]) for q, v in p["queries"].items()
        }
        expected = {pair_query(u, s) for s, u in research_beta_1_pass_pairs()}
        if set(self.queries) != expected:
            raise ValueError("Memory snapshot must cover all six pair queries.")

    def retrieve(self, user_pick: str, scorey_pick: str) -> RetrievalContext:
        start = time.monotonic()
        user_pick, scorey_pick = normalise_pick(user_pick), normalise_pick(scorey_pick)
        query = pair_query(user_pick, scorey_pick)
        route = route_family_for(user_pick, scorey_pick)
        vector = self.queries[query]
        candidates = []
        for note, embedding in zip(self.payload["notes"], self.vectors, strict=True):
            if note["route"] in ("all", route):
                score = sum(a * b for a, b in zip(vector, embedding, strict=True))
                candidates.append((score, note))
        candidates.sort(key=lambda item: (-item[0], item[1]["id"]))
        matches: list[dict[str, Any]] = []
        context = ""
        for score, note in candidates:
            if len(matches) == self.settings.memory_top_k:
                break
            fragment = f"[{note['id']}] {note['text']}\n"
            if len(context) + len(fragment) > self.settings.memory_max_chars:
                continue
            context += fragment
            source = note["source"].split("#", 1)[0]
            matches.append(
                {
                    **note,
                    "score": score,
                    "source_hash": self.payload["source_hashes"][source],
                }
            )
        return RetrievalContext(
            index=self.settings.memory_index,
            embedding_model=self.payload["embedding_model"],
            corpus_hash=self.payload["corpus_hash"],
            user_pick=user_pick,
            scorey_pick=scorey_pick,
            route_family=route,
            query=query,
            status="matched" if matches else "empty",
            context=context.rstrip(),
            matches=tuple(matches),
            top_k=self.settings.memory_top_k,
            max_chars=self.settings.memory_max_chars,
            elapsed_seconds=time.monotonic() - start,
        )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(payload, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def evidence_path(path: Path) -> str:
    """Record locations relative to the checkout, including external stores."""
    return Path(os.path.relpath(path.resolve(), ROOT.resolve())).as_posix()


def generation_receipt(
    settings: Settings,
    context: RetrievalContext,
    prompt: str,
    instructions: str,
) -> tuple[Path, dict[str, Any]]:
    generation_id = uuid.uuid4().hex
    path = (
        Path(settings.memory_db_path).parent
        / "memory-receipts"
        / f"{generation_id}.json"
    )
    receipt = {
        "generation_id": generation_id,
        "status": "prepared",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "path_base": "repository root",
        "settings": {
            **asdict(settings),
            "memory_db_path": evidence_path(Path(settings.memory_db_path)),
        },
        "retrieval": asdict(context),
        "prompt": prompt,
        "instructions": instructions,
    }
    write_json(path, receipt)
    return path, receipt


def bind_eval_receipt(
    db_path: Path, output_id: int, receipt_path: Path, text: str
) -> Path:
    receipt = json.loads(receipt_path.read_text())
    if receipt["status"] != "completed":
        raise ValueError("Only a completed generation can be bound to an eval row.")
    receipt.update(
        eval_db=evidence_path(db_path),
        output_id=output_id,
        round_text_hash=fingerprint(text),
        generation_receipt=evidence_path(receipt_path),
        binding="Verify the committed output ID and round_text_hash in eval_db.",
    )
    destination = db_path.with_name(db_path.name + ".retrieval") / f"{output_id}.json"
    if destination.exists():
        raise ValueError(f"Retrieval evidence already exists for output {output_id}.")
    write_json(destination, receipt)
    return destination
