from __future__ import annotations
import json
from urllib.request import Request
import pytest
from project_intelligence.github_pulls import fetch_github_pull_requests, render_pull_requests_markdown

class FakeResponse:
    def __init__(self, data: object): self.data = json.dumps(data).encode()
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def read(self) -> bytes: return self.data

def test_fetch_pull_requests_preserves_refs_and_draft_state(monkeypatch) -> None:
    payload = [{
        "number": 17, "title": "Propose license", "state": "open", "draft": True,
        "html_url": "https://github.com/example/repo/pull/17",
        "head": {"ref": "licensing/proposal", "sha": "abc123"},
        "base": {"ref": "main", "sha": "def456"},
        "labels": [{"name": "legal-review"}], "updated_at": "2026-10-15T12:00:00Z",
    }]
    seen = []
    def fake_urlopen(request: Request, timeout: float):
        seen.append((request.full_url, request.get_method(), timeout))
        return FakeResponse(payload)
    monkeypatch.setattr("project_intelligence.github_pulls.urlopen", fake_urlopen)
    snapshot = fetch_github_pull_requests("example/repo", timeout=4)
    assert snapshot["summary"] == {"pull_requests_found": 1, "open": 1, "closed": 0, "drafts": 1}
    pr = snapshot["pull_requests"][0]
    assert pr["url"] == "https://github.com/example/repo/pull/17"
    assert pr["head_ref"] == "licensing/proposal" and pr["base_ref"] == "main"
    assert pr["draft"] is True and seen[0][1:] == ("GET", 4)
    assert "not proof of a completed or safe implementation" in render_pull_requests_markdown(snapshot)

def test_pull_request_fetch_validates_arguments() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"): fetch_github_pull_requests("https://github.com/example/repo")
    with pytest.raises(ValueError, match="state"): fetch_github_pull_requests("example/repo", state="merged")
    with pytest.raises(ValueError, match="timeout"): fetch_github_pull_requests("example/repo", timeout=-1)
