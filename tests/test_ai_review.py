from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request

import pytest

from project_intelligence.ai_review import review_tasks


PROJECT_KEY = "project-key-" + "a" * 48


def _task_file(tmp_path: Path) -> Path:
    path = tmp_path / "tasks.json"
    path.write_text(json.dumps({
        "schema_version": 1,
        "project": {"id": "demo", "name": "Demo Project"},
        "tasks": [{
            "id": "task-1",
            "title": "Review configuration handling",
            "kind": "marker_follow_up",
            "classification": "observed",
            "confidence": "direct_source_marker",
            "observed_fact": "A TODO marker was detected.",
            "hypothesis": "The marker may still be relevant.",
            "evidence": {
                "type": "source_line",
                "path": "src/config.py",
                "line_number": 12,
                "source_sha256": "d" * 64,
                "excerpt": "NEVER SEND THIS SOURCE EXCERPT",
                "source_item_id": "record-1",
                "source_status": "ready",
            },
            "acceptance_criteria": ["A test covers the input boundary."],
            "status": "draft",
        }],
    }), encoding="utf-8")
    return path


def _gateway_response(task_id: str = "task-1") -> bytes:
    result = {
        "reviews": [{
            "task_id": task_id,
            "priority": "P2",
            "decision": "keep",
            "rationale": "The evidence describes a concrete follow-up that merits human review.",
            "missing_evidence": ["Confirm the marker is still relevant."],
            "recommended_acceptance_criteria": ["Add a test for the validated boundary."],
        }]
    }
    return json.dumps({"choices": [{"message": {"content": json.dumps(result)}}]}).encode()


class _Response:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit: int) -> bytes:
        return self.body[:limit]


def test_ai_review_posts_only_allowlisted_metadata_and_writes_advisories(tmp_path: Path) -> None:
    source = _task_file(tmp_path)
    destination = tmp_path / "review.json"
    captured: dict[str, object] = {}

    def fake_opener(request: Request, timeout: float):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return _Response(_gateway_response())

    result = review_tasks(
        source,
        destination,
        api_key=PROJECT_KEY,
        opener=fake_opener,
    )

    assert captured["url"] == "http://127.0.0.1:20129/v1/chat/completions"
    headers = {key.lower(): value for key, value in captured["headers"].items()}
    assert headers["authorization"] == "Bearer " + PROJECT_KEY
    assert headers["x-task-class"] == "reasoning"
    sent = captured["body"]
    assert "NEVER SEND THIS SOURCE EXCERPT" not in json.dumps(sent)
    assert "evidence" in sent["messages"][1]["content"]
    assert result["reviews"][0]["task_id"] == "task-1"
    assert result["reviews"][0]["status"] == "recommendation_only"
    saved = json.loads(destination.read_text(encoding="utf-8"))
    assert saved["policy"].startswith("AI output is untrusted advisory data.")
    assert saved["reviews"] == result["reviews"]


def test_remote_gateway_requires_explicit_opt_in(tmp_path: Path) -> None:
    source = _task_file(tmp_path)
    calls = []

    def fake_opener(*args, **kwargs):
        calls.append(True)
        return _Response(_gateway_response())

    with pytest.raises(ValueError, match="Remote AI gateways are disabled"):
        review_tasks(
            source,
            tmp_path / "review.json",
            base_url="https://example.com/v1",
            api_key=PROJECT_KEY,
            opener=fake_opener,
        )
    assert calls == []


def test_rejects_unknown_task_ids_without_writing_output(tmp_path: Path) -> None:
    source = _task_file(tmp_path)
    destination = tmp_path / "review.json"

    def fake_opener(request: Request, timeout: float):
        return _Response(_gateway_response("invented-task-id"))

    with pytest.raises(ValueError, match="unknown or duplicate"):
        review_tasks(source, destination, api_key=PROJECT_KEY, opener=fake_opener)
    assert not destination.exists()


def test_requires_api_key_and_preserves_source_task_file(tmp_path: Path, monkeypatch) -> None:
    source = _task_file(tmp_path)
    monkeypatch.delenv("PIE_AI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="PIE_AI_API_KEY"):
        review_tasks(source, tmp_path / "review.json", opener=lambda *args, **kwargs: None)
    with pytest.raises(ValueError, match="must not overwrite"):
        review_tasks(source, source, api_key=PROJECT_KEY, opener=lambda *args, **kwargs: None)
    assert source.exists()


def test_requires_exact_review_coverage(tmp_path: Path) -> None:
    source = _task_file(tmp_path)
    destination = tmp_path / "review.json"

    def fake_opener(request: Request, timeout: float):
        payload = {"choices": [{"message": {"content": json.dumps({"reviews": []})}}]}
        return _Response(json.dumps(payload).encode())

    with pytest.raises(ValueError, match="exactly one recommendation"):
        review_tasks(source, destination, api_key=PROJECT_KEY, opener=fake_opener)
    assert not destination.exists()
