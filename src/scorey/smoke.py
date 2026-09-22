"""Frozen, independent golden cases using Scorey's application request contract."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import time
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import version
from importlib.resources import files
from pathlib import Path
from typing import Any

import httpx
from agents import AgentOutputSchema, RunConfig, Runner
from agents.models.openai_provider import OpenAIProvider
from openai import AsyncOpenAI

from scorey.agent import SCOREY_INSTRUCTIONS, SCOREY_PROMPT_VERSION, build_live_agent
from scorey.agent import build_prompt as matchup_prompt
from scorey.config import ROOT, Settings, load_settings, route_family_for
from scorey.eval_gates import evaluate_research_beta_1, research_beta_1_pass_pairs
from scorey.pipeline import RoundFields, build_round_state, compose_round
from scorey.retrieval import FrozenMemory, evidence_path

SOURCE_FILES = (
    "src/scorey/agent.py",
    "src/scorey/config.py",
    "src/scorey/pipeline.py",
    "src/scorey/eval_gates.py",
    "src/scorey/retrieval.py",
    "src/scorey/vector_store.py",
    "src/scorey/smoke.py",
    "src/scorey/data/golden_cases.json",
    "src/scorey/data/principles.json",
    "pyproject.toml",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def provider_endpoint() -> str:
    url = httpx.URL(os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1")
    if (
        url.scheme not in ("https", "http")
        or not url.host
        or url.userinfo
        or url.query
        or url.fragment
    ):
        raise ValueError(
            "Provider endpoint must exclude credentials, query and fragment."
        )
    return str(url)


def write_bytes(path: Path, data: bytes) -> None:
    with path.open("xb") as handle:
        handle.write(data)
    path.chmod(0o444)


def write_json(path: Path, value: Any) -> None:
    write_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def golden_cases() -> dict[str, Any]:
    data = json.loads(files("scorey").joinpath("data/golden_cases.json").read_text())
    cases = data["cases"]
    pairs = [(c["scorey_pick"], c["user_pick"]) for c in cases]
    if (
        data["schema"] != "scorey.golden_cases.v1"
        or len(cases) != 6
        or set(pairs) != set(research_beta_1_pass_pairs())
        or len({c["id"] for c in cases}) != 6
        or any(
            not re.fullmatch(r"[a-z]+-[a-z]+", c["id"])
            or c["starting_score"] != 1
            or not c["purpose"].strip()
            for c in cases
        )
    ):
        raise ValueError("Golden cases must cover the six routes once at score 1.")
    return data


def prepare_run(folder: Path, settings: Settings) -> Path:
    """Freeze source, schema, settings and retrieval without a model request."""
    fixture = golden_cases()
    memory = FrozenMemory(settings) if settings.memory_enabled else None
    cases = []
    for case in fixture["cases"]:
        user, scorey = case["user_pick"], case["scorey_pick"]
        route = route_family_for(user, scorey)
        context = memory.retrieve(user, scorey) if memory else None
        cases.append(
            {
                **case,
                "route_family": route,
                "retrieval": asdict(context) if context else None,
                "prompt": matchup_prompt(
                    user, scorey, route, context=context.context if context else ""
                ),
            }
        )
    sources = {name: (ROOT / name).read_bytes() for name in SOURCE_FILES}
    if memory:
        for name in memory.payload["source_hashes"]:
            sources[name] = (ROOT / name).read_bytes()
    patch = subprocess.check_output(["git", "diff", "HEAD", "--"], cwd=ROOT)
    manifest = {
        "schema": "scorey.golden_smoke.v1",
        "created_at": utc_now(),
        "prompt_version": SCOREY_PROMPT_VERSION,
        "golden_cases_version": fixture["version"],
        "source_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_hashes": {name: digest(raw) for name, raw in sources.items()},
        "source_patch_sha256": digest(patch),
        "packages": {name: version(name) for name in ("openai", "openai-agents")},
        "provider_endpoint": provider_endpoint(),
        "settings": {
            **asdict(settings),
            "memory_db_path": evidence_path(Path(settings.memory_db_path)),
        },
        "instructions": SCOREY_INSTRUCTIONS,
        "output_schema": AgentOutputSchema(RoundFields).json_schema(),
        "cases": cases,
        "limits": {"max_attempts": 6, "timeout_seconds": 60, "max_retries": 0},
        "context": "One fresh request per case; no conversation or previous response.",
        "transport": "Agents SDK Responses API; non-streaming; tracing disabled.",
        "judgment": "Mechanical checks only; separate, attributed quality judgments.",
    }
    folder.mkdir(parents=True, exist_ok=False)
    for name, raw in sources.items():
        target = folder / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        write_bytes(target, raw)
    write_bytes(folder / "source.patch", patch)
    write_json(folder / "manifest.json", manifest)
    write_bytes(
        folder / "manifest.sha256",
        digest((folder / "manifest.json").read_bytes()).encode(),
    )
    return folder


def load_manifest(folder: Path) -> dict[str, Any]:
    raw = (folder / "manifest.json").read_bytes()
    if digest(raw) != (folder / "manifest.sha256").read_text().strip():
        raise ValueError("Manifest changed; prepare a new run.")
    manifest = json.loads(raw)
    if manifest["schema"] != "scorey.golden_smoke.v1":
        raise ValueError("Unsupported smoke manifest.")
    if len(manifest["cases"]) != 6 or manifest["limits"] != {
        "max_attempts": 6,
        "timeout_seconds": 60,
        "max_retries": 0,
    }:
        raise ValueError("Smoke must retain the six-case, one-attempt limits.")
    for name, expected in manifest["source_hashes"].items():
        if digest((ROOT / name).read_bytes()) != expected:
            raise ValueError(f"Source changed: {name}; prepare a new run.")
        if digest((folder / "source" / name).read_bytes()) != expected:
            raise ValueError(f"Source snapshot changed: {name}.")
    for name, expected in manifest["packages"].items():
        if version(name) != expected:
            raise ValueError(f"Package changed: {name}; prepare a new run.")
    if (
        digest((folder / "source.patch").read_bytes())
        != manifest["source_patch_sha256"]
    ):
        raise ValueError("Source patch changed.")
    return manifest


async def attempt(
    folder: Path,
    manifest: dict[str, Any],
    case: dict[str, Any],
    number: int,
    *,
    api_key: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    stem = f"{number:02d}-{case['id']}"
    issues: list[str] = []
    receipt: dict[str, Any] = {
        "schema": "scorey.smoke_attempt.v1",
        "case_id": case["id"],
        "attempt": number,
        "started_at": utc_now(),
        "status": "started",
        "request_file": None,
        "response_file": None,
        "quality_verdict": None,
        "mechanical_checks": {"ok": False, "issues": issues},
    }

    async def capture_request(request: httpx.Request) -> None:
        if receipt["request_file"] is not None:
            raise RuntimeError("Only one provider request is allowed per case.")
        path = folder / f"{stem}.request.json"
        body = await request.aread()
        write_bytes(path, body)
        receipt.update(request_file=path.name, request_sha256=digest(body))
        receipt.update(request_method=request.method, request_url=str(request.url))

    async def capture_response(response: httpx.Response) -> None:
        body = await response.aread()
        path = folder / f"{stem}.response.json"
        write_bytes(path, body)
        receipt.update(
            response_file=path.name,
            response_sha256=digest(body),
            http_status=response.status_code,
            request_id=response.headers.get("x-request-id"),
        )
        try:
            data = json.loads(body)
        except ValueError:
            issues.append("response_is_not_json")
            return
        receipt.update(
            response_id=data.get("id"),
            response_status=data.get("status"),
            usage=data.get("usage"),
            incomplete_details=data.get("incomplete_details"),
            returned_settings={
                k: data.get(k)
                for k in (
                    "model",
                    "reasoning",
                    "text",
                    "top_p",
                    "temperature",
                    "max_output_tokens",
                    "store",
                )
            },
        )
        if response.is_error:
            issues.append("provider_http_error")
        if data.get("status") != "completed":
            issues.append("response_not_completed")
        if any(
            part.get("type") == "refusal"
            for item in data.get("output", [])
            for part in item.get("content", [])
        ):
            issues.append("model_refusal")

    started = time.monotonic()
    try:
        settings = Settings(**manifest["settings"])
        async with httpx.AsyncClient(
            transport=transport,
            event_hooks={"request": [capture_request], "response": [capture_response]},
        ) as http_client:
            async with AsyncOpenAI(
                api_key=api_key,
                base_url=manifest["provider_endpoint"],
                http_client=http_client,
                max_retries=0,
                timeout=manifest["limits"]["timeout_seconds"],
            ) as client:
                result = await asyncio.wait_for(
                    Runner.run(
                        build_live_agent(settings),
                        case["prompt"],
                        max_turns=1,
                        run_config=RunConfig(
                            model_provider=OpenAIProvider(
                                openai_client=client,
                                use_responses=True,
                                use_responses_websocket=False,
                            ),
                            tracing_disabled=True,
                        ),
                    ),
                    timeout=manifest["limits"]["timeout_seconds"],
                )
        output = result.final_output
        fields = output if isinstance(output, RoundFields) else RoundFields(**output)
        receipt["generated_fields"] = asdict(fields)
        if any(value != value.lower() for value in asdict(fields).values()):
            issues.append("fields_not_lowercase")
        if re.search(r"\byou\b", fields.scoreboard_claim, re.IGNORECASE):
            issues.append("scoreboard_claim_contains_you")
        state = build_round_state(
            case["user_pick"],
            case["scorey_pick"],
            fields,
            scorey_score=case["starting_score"],
        )
        gate = evaluate_research_beta_1(state.user_pick, state.scorey_pick)
        receipt.update(
            normalized_round=asdict(state),
            round_text=compose_round(state),
            route_check=asdict(gate),
            status="completed",
        )
        if gate.verdict != "pass":
            issues.append("route_failed")
    except BaseException as error:
        receipt.update(
            status="failed",
            error={
                "type": type(error).__name__,
                "status_code": getattr(error, "status_code", None),
                "request_id": getattr(error, "request_id", None),
            },
        )
        issues.append("generation_or_recording_failed")
        if isinstance(error, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
            raise
    finally:
        receipt["elapsed_seconds"] = round(time.monotonic() - started, 3)
        receipt["mechanical_checks"]["ok"] = not issues
        write_json(folder / f"{stem}.receipt.json", receipt)
    return receipt


def write_review(folder: Path, receipts: list[dict[str, Any]]) -> None:
    lines = ["# Scorey golden smoke review", "", "Quality judgments are pending.", ""]
    for receipt in receipts:
        verdict = "PASS" if receipt["mechanical_checks"]["ok"] else "FAIL"
        lines += [
            f"## {receipt['case_id']}",
            "",
            f"Mechanical checks: {verdict}.",
            "",
            receipt.get(
                "round_text", "No complete round; inspect the attempt receipt."
            ),
            "",
        ]
    lines += [
        "Original requests, raw responses and receipts sit beside this review.",
        "Record attributed quality judgments separately in judgments.jsonl.",
        "",
    ]
    write_bytes(folder / "review.md", "\n".join(lines).encode())


async def run_smoke(
    folder: Path,
    *,
    api_key: str | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    manifest = load_manifest(folder)
    if (folder / "started.json").exists() or list(folder.glob("*.receipt.json")):
        raise ValueError("This run has already started; prepare a new run to repeat.")
    if not (api_key or os.getenv("OPENAI_API_KEY")):
        raise ValueError("The existing project OPENAI_API_KEY is required.")
    write_json(folder / "started.json", {"started_at": utc_now()})
    receipts: list[dict[str, Any]] = []
    stop_reason = "all_cases_attempted"
    try:
        for number, case in enumerate(manifest["cases"], 1):
            receipt = await attempt(
                folder, manifest, case, number, api_key=api_key, transport=transport
            )
            receipts.append(receipt)
            print(f"{case['id']}: {receipt['status']}", flush=True)
            if receipt.get("http_status") in {400, 401, 403, 404, 422, 429}:
                stop_reason = "configuration_or_capacity_error"
                break
    except BaseException:
        stop_reason = "interrupted"
        raise
    finally:
        # Include a receipt written by an interrupted attempt's finally block.
        receipts = [
            json.loads(p.read_text()) for p in sorted(folder.glob("*.receipt.json"))
        ]
        summary = {
            "finished_at": utc_now(),
            "stop_reason": stop_reason,
            "attempts": len(receipts),
            "mechanical_pass": sum(r["mechanical_checks"]["ok"] for r in receipts),
            "mechanical_fail": sum(not r["mechanical_checks"]["ok"] for r in receipts),
            "not_attempted": [
                c["id"]
                for c in manifest["cases"]
                if c["id"] not in {r["case_id"] for r in receipts}
            ],
            "quality_verdicts": "pending",
        }
        write_json(folder / "summary.json", summary)
        write_review(folder, receipts)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Freeze six cases without API calls.")
    prepare.add_argument("--output", type=Path)
    run = commands.add_parser("run", help="Run one frozen six-case smoke.")
    run.add_argument("folder", type=Path)
    args = parser.parse_args()
    try:
        settings = load_settings()
        if args.command == "prepare":
            folder = args.output or ROOT / ".local" / "smoke" / datetime.now(
                timezone.utc
            ).strftime("%Y%m%dT%H%M%S%fZ")
            prepare_run(folder, settings)
            print(f"Prepared: {evidence_path(folder)}")
            print("Six independent cases frozen; no model requests made.")
            return 0
        result = asyncio.run(run_smoke(args.folder))
        print(json.dumps(result, indent=2))
        return int(bool(result["mechanical_fail"] or result["not_attempted"]))
    except (ValueError, OSError) as error:
        print(f"Smoke setup failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
