"""Operator commands for building and inspecting Scorey's principle memory."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace

from scorey.config import load_settings, require_openai_api_key
from scorey.retrieval import FrozenMemory, build_index


def command_memory(command: str, user_pick: str = "", scorey_pick: str = "") -> int:
    try:
        settings = load_settings()
        if command == "memory-build":
            require_openai_api_key()
            version = build_index(settings)
            settings = replace(settings, memory_index=version)
        if command == "memory-status" and not settings.memory_index:
            print(json.dumps({"enabled": settings.memory_enabled, "index": None}))
            return 1 if settings.memory_enabled else 0
        memory = FrozenMemory(settings)
        if command == "memory-preview":
            print(json.dumps(asdict(memory.retrieve(user_pick, scorey_pick)), indent=2))
        else:
            print(
                json.dumps(
                    {
                        "enabled": settings.memory_enabled,
                        "index": settings.memory_index,
                        "embedding_model": memory.payload["embedding_model"],
                        "dimensions": memory.payload["dimensions"],
                        "corpus_hash": memory.payload["corpus_hash"],
                        "principles": len(memory.payload["notes"]),
                        "pair_queries": len(memory.queries),
                        "database": settings.memory_db_path,
                    },
                    indent=2,
                )
            )
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Memory operation failed ({type(error).__name__}).", file=sys.stderr)
        return 1
