from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from project_intelligence.github_issues import (
    fetch_github_issues,
    render_issues_markdown,
    write_issue_snapshot,
)


class FakeResponse:
    def __init__(self, data: object):
        self.data = json.dumps(data).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.data


def test_fetch_issues_excludes_pull_requests_and_preserves_canonical_issue(monkeypatch, tmp_path: Path) -> None:
    payload = [
        {
            "number": 6,
            "title": "[P0] Add project-scoped data access",
            "state": "open",
            "html_url": "https://github.com/example/repo/issues/6",
            "created_at": "2026-10-01T10:00:00Z",
            "updated_at": "2026-10-02T10:00:00Z",
            "labels": [{"name": "security"}, {"name": "P0"}],
        },
        {
            "number": 7,
            "title": "A pull request must not be reported as an issue",
            "state": "open",
            "html_url": "https://github.com/example/repo/pull/7",
            "pull_request": {"url": "https://api.github.com/repos/example/repo/pulls/7"},
            "labels": [],
        },
    ]
    seen = []

    def fake_urlopen(request: Request, timeout: float):
        seen.append((request.full_url, request.get_method(), timeout))
        return FakeResponse(payload)

    monkeypatch.setattr("project_intelligence.github_issues.urlopen", fake_urlopen)
    snapshot = fetch_github_issues("example/repo", timeout=3.5)

    assert snapshot["summary"] == {
        "issues_found": 1,
        "open": 1,
        "closed": 0,
        "pull_requests_excluded": True,
    }
    issue = snapshot["issues"][0]
    assert issue["number"] == 6
    assert issue["url"] == "https://github.com/example/repo/issues/6"
    assert issue["labels"] == ["P0", "security"]
    assert seen == [(
        "https://api.github.com/repos/example/repo/issues?state=open&per_page=100&page=1",
        "GET",
        3.5,
    )]
    assert snapshot["policy"]["publish_or_write"] is False
    report = render_issues_markdown(snapshot)
    assert "The original GitHub issue is the canonical work record" in report
    output = write_issue_snapshot(snapshot, tmp_path / "issues.json")
    assert json.loads(output.read_text(encoding="utf-8"))["issues"][0]["number"] == 6


def test_fetch_issues_validates_repository_and_options() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"):
        fetch_github_issues("https://github.com/example/repo")
    with pytest.raises(ValueError, match="state"):
        fetch_github_issues("example/repo", state="merged")
    with pytest.raises(ValueError, match="page_size"):
        fetch_github_issues("example/repo", page_size=101)
    with pytest.raises(ValueError, match="timeout"):
        fetch_github_issues("example/repo", timeout=0)


def test_fetch_issues_rejects_non_list_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "project_intelligence.github_issues.urlopen",
        lambda *_args, **_kwargs: FakeResponse({"message": "bad response"}),
    )
    with pytest.raises(ValueError, match="issue list"):
        fetch_github_issues("example/repo")


def test_fetch_issues_maps_not_found(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise HTTPError("https://api.github.com", 404, "Not Found", {}, None)

    monkeypatch.setattr("project_intelligence.github_issues.urlopen", fail)
    with pytest.raises(ValueError, match="not found"):
        fetch_github_issues("example/repo")
