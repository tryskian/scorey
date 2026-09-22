from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import httpx
import pytest

from scorey.agent import SCOREY_INSTRUCTIONS
from scorey.config import Settings
from scorey.retrieval import build_index
from scorey.smoke import digest, load_manifest, prepare_run, run_smoke


@pytest.fixture
def prepared(tmp_path: Path) -> Path:
    return prepare_run(
        tmp_path / "smoke",
        Settings("Scorey", "test-model", "medium", "detailed", "low", 0.98),
    )


def response_body(
    *, status: str = "completed", refusal: bool = False, claim: str = "lose"
) -> bytes:
    content = (
        {"type": "refusal", "refusal": "refused"}
        if refusal
        else {
            "type": "output_text",
            "annotations": [],
            "text": json.dumps(
                {
                    "response": {
                        "winning_state": "  a pretend champion! ",
                        "worse_state": "busy celebrating second place",
                        "scoreboard_claim": claim,
                    }
                }
            ),
        }
    )
    return json.dumps(
        {
            "id": "resp_test",
            "object": "response",
            "created_at": 1,
            "model": "test-model",
            "status": status,
            "output": [
                {
                    "id": "msg_test",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [content],
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
            "incomplete_details": (
                {"reason": "max_output_tokens"} if status == "incomplete" else None
            ),
            "parallel_tool_calls": False,
            "tools": [],
            "tool_choice": "auto",
        },
        indent=2,
    ).encode()


def test_real_sdk_records_six_independent_requests_and_raw_output(
    prepared: Path,
) -> None:
    requests: list[dict[str, Any]] = []
    raw = response_body()

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, content=raw, headers={"x-request-id": "req_test"})

    summary = asyncio.run(
        run_smoke(
            prepared, api_key="unit-test-key", transport=httpx.MockTransport(respond)
        )
    )
    manifest = load_manifest(prepared)
    assert len(requests) == summary["mechanical_pass"] == 6
    assert summary["not_attempted"] == []
    for request, case in zip(requests, manifest["cases"], strict=True):
        assert request["instructions"] == SCOREY_INSTRUCTIONS
        assert request["input"] == [{"role": "user", "content": case["prompt"]}]
        assert "previous_response_id" not in request
        assert "conversation" not in request
        assert request["reasoning"] == {"effort": "medium", "summary": "detailed"}
        assert request["text"]["verbosity"] == "low"
        assert request["text"]["format"]["schema"] == manifest["output_schema"]
        assert request["text"]["format"]["strict"] is True
        assert request["top_p"] == 0.98
        # The SDK omits stream for Runner.run; streaming uses a different path.
        assert request.get("stream", False) is False
        assert case["purpose"] not in request["input"][0]["content"]
    for path in prepared.glob("*.receipt.json"):
        receipt = json.loads(path.read_text())
        assert (prepared / receipt["response_file"]).read_bytes() == raw
        assert receipt["response_sha256"] == digest(raw)
        assert receipt["generated_fields"]["winning_state"] == "  a pretend champion! "
        assert receipt["normalized_round"]["winning_state"] == "a pretend champion"
        assert receipt["normalized_round"]["scorey_score"] == 1
        assert "me: 1, you: lose" in receipt["round_text"]
        assert receipt["quality_verdict"] is None
        assert receipt["request_id"] == "req_test"
    with pytest.raises(ValueError, match="already started"):
        asyncio.run(run_smoke(prepared, api_key="unit-test-key"))


@pytest.mark.parametrize(
    ("options", "issue"),
    [
        ({"status": "incomplete"}, "response_not_completed"),
        ({"refusal": True}, "model_refusal"),
        ({"claim": "you lose"}, "scoreboard_claim_contains_you"),
    ],
)
def test_bad_outputs_preserve_evidence(
    prepared: Path, options: dict[str, Any], issue: str
) -> None:
    raw = response_body(**options)
    transport = httpx.MockTransport(lambda _: httpx.Response(200, content=raw))
    summary = asyncio.run(
        run_smoke(prepared, api_key="unit-test-key", transport=transport)
    )
    assert summary["mechanical_fail"] == 6
    for path in prepared.glob("*.receipt.json"):
        receipt = json.loads(path.read_text())
        assert issue in receipt["mechanical_checks"]["issues"]
        assert (prepared / receipt["response_file"]).read_bytes() == raw
        assert receipt["quality_verdict"] is None


def test_network_failures_are_recorded_without_retries(prepared: Path) -> None:
    requests = []

    def disconnect(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        raise httpx.ConnectError("test failure", request=request)

    summary = asyncio.run(
        run_smoke(
            prepared, api_key="unit-test-key", transport=httpx.MockTransport(disconnect)
        )
    )
    assert len(requests) == summary["mechanical_fail"] == 6
    for path in prepared.glob("*.receipt.json"):
        receipt = json.loads(path.read_text())
        assert receipt["status"] == "failed"
        assert (prepared / receipt["request_file"]).is_file()
        assert receipt["response_file"] is None
        assert receipt["quality_verdict"] is None


def test_configuration_failure_stops_remaining_calls(prepared: Path) -> None:
    transport = httpx.MockTransport(
        lambda _: httpx.Response(400, json={"error": {"message": "test failure"}})
    )
    summary = asyncio.run(
        run_smoke(prepared, api_key="unit-test-key", transport=transport)
    )
    assert summary["attempts"] == 1
    assert len(summary["not_attempted"]) == 5
    assert summary["stop_reason"] == "configuration_or_capacity_error"


def test_tampered_manifest_cannot_start(prepared: Path) -> None:
    path = prepared / "manifest.json"
    path.chmod(0o644)
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Manifest changed"):
        asyncio.run(run_smoke(prepared, api_key="unit-test-key"))
    assert not (prepared / "started.json").exists()


def test_prepare_cannot_overwrite_existing_run(prepared: Path) -> None:
    with pytest.raises(FileExistsError):
        prepare_run(prepared, Settings("Scorey", "test-model"))


def test_provider_endpoint_stays_frozen(
    prepared: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    expected = load_manifest(prepared)["provider_endpoint"].rstrip("/") + "/responses"
    monkeypatch.setenv("OPENAI_BASE_URL", "https://changed.invalid/v1")
    endpoints = []

    def respond(request: httpx.Request) -> httpx.Response:
        endpoints.append(str(request.url))
        return httpx.Response(200, content=response_body())

    asyncio.run(
        run_smoke(
            prepared, api_key="unit-test-key", transport=httpx.MockTransport(respond)
        )
    )
    assert endpoints == [expected] * 6


def test_retrieval_is_frozen_without_writing_canonical_evidence(tmp_path: Path) -> None:
    settings = Settings(
        "Scorey",
        "test-model",
        memory_enabled=True,
        memory_db_path=str(tmp_path / "memory.sqlite"),
    )
    index = build_index(settings, embedder=lambda texts, _: [[1.0, 0.5]] * len(texts))
    settings = replace(settings, memory_index=index)
    before = Path(settings.memory_db_path).read_bytes()
    prepared = prepare_run(tmp_path / "smoke", settings)
    manifest = load_manifest(prepared)
    assert Path(settings.memory_db_path).read_bytes() == before
    for case in manifest["cases"]:
        context = case["retrieval"]
        assert context["index"] == index
        assert context["matches"]
        assert context["context"] in case["prompt"]
    # Execution needs only the frozen prompts, not a live memory database.
    Path(settings.memory_db_path).unlink()
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, content=response_body())
    )
    summary = asyncio.run(
        run_smoke(prepared, api_key="unit-test-key", transport=transport)
    )
    assert summary["mechanical_pass"] == 6
    assert before
    assert not Path(settings.memory_db_path).exists()


def test_cancellation_preserves_attempt_and_marks_remaining_cases(
    prepared: Path,
) -> None:
    async def cancel(request: httpx.Request) -> httpx.Response:
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(
            run_smoke(
                prepared, api_key="unit-test-key", transport=httpx.MockTransport(cancel)
            )
        )
    summary = json.loads((prepared / "summary.json").read_text())
    assert summary["attempts"] == summary["mechanical_fail"] == 1
    assert summary["stop_reason"] == "interrupted"
    assert len(summary["not_attempted"]) == 5
