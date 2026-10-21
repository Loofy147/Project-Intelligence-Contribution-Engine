from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request

import pytest

from project_intelligence.source_relations import (
    fetch_explicit_relationships,
    render_relationships_markdown,
    write_relationship_report,
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


def _event(source: dict, *, created_at="2026-10-21T12:00:00Z", event="cross-referenced"):
    return {
        "event": event,
        "created_at": created_at,
        "actor": {"login": "maintainer"},
        "source": {"type": "issue", "issue": source},
    }


def _source(number: int, title: str, url: str, repository_url: str, *, is_pr=False):
    value = {
        "number": number,
        "title": title,
        "html_url": url,
        "repository_url": repository_url,
    }
    if is_pr:
        value["pull_request"] = {"url": f"https://api.github.com/repos/example/repo/pulls/{number}"}
    return value


def test_relationship_audit_uses_only_explicit_same_repository_cross_reference_events(monkeypatch):
    same_repo_pr = _source(
        27, "Ledger implementation", "https://github.com/example/repo/pull/27",
        "https://api.github.com/repos/example/repo", is_pr=True,
    )
    external_issue = _source(
        1294, "Automated bounty alert", "https://github.com/other/project/issues/1294",
        "https://api.github.com/repos/other/project",
    )
    payload = [
        _event(same_repo_pr),
        _event(external_issue, created_at="2026-10-21T13:00:00Z"),
        _event(same_repo_pr),  # exact duplicate event must not duplicate the directed relation
        _event(_source(8, "Comment event is not a cross-reference", "https://github.com/example/repo/issues/8",
                       "https://api.github.com/repos/example/repo"), event="commented"),
        {"event": "cross-referenced", "source": {"type": "issue"}},  # incomplete source evidence
    ]
    seen = []

    def fake_urlopen(request: Request, timeout: float):
        seen.append((request.full_url, request.get_method(), timeout))
        return FakeResponse(payload)

    monkeypatch.setattr("project_intelligence.source_relations.urlopen", fake_urlopen)
    result = fetch_explicit_relationships("example/repo", [
        {"record_type": "issue", "number": 3, "title": "Exactly-once XP"},
    ], timeout=4.5)

    assert len(seen) == 1
    assert seen[0] == (
        "https://api.github.com/repos/example/repo/issues/3/timeline?per_page=100&page=1",
        "GET",
        4.5,
    )
    assert result["summary"]["explicit_in_repository_relations"] == 1
    assert result["summary"]["external_or_unverified_references"] == 1
    assert result["summary"]["inferred_relations_created"] == 0
    relation = result["relationships"][0]
    assert relation["source"]["record_type"] == "pull_request"
    assert relation["source"]["number"] == 27
    assert relation["target"]["record_type"] == "issue"
    assert relation["target"]["number"] == 3
    assert relation["evidence"]["kind"] == "timeline_cross_referenced_event"
    assert "does not prove" in relation["interpretation_limit"]
    assert result["external_references"][0]["classification"] == "external_repository"
    assert result["policy"]["title_similarity_creates_relation"] is False


def test_pr_timeline_can_preserve_reverse_explicit_reference_direction(monkeypatch):
    payload = [_event(_source(
        3, "Exactly-once XP", "https://github.com/example/repo/issues/3",
        "https://api.github.com/repos/example/repo",
    ))]
    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse(payload),
    )
    result = fetch_explicit_relationships("example/repo", [
        {"record_type": "pull_request", "number": 27, "title": "Ledger implementation"},
    ])
    relation = result["relationships"][0]
    assert relation["source"]["record_type"] == "issue"
    assert relation["source"]["number"] == 3
    assert relation["target"]["record_type"] == "pull_request"
    assert relation["target"]["number"] == 27


def test_no_cross_reference_event_does_not_generate_relationship(monkeypatch):
    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse([
            _event(_source(
                8, "Similar words: XP ledger", "https://github.com/example/repo/issues/8",
                "https://api.github.com/repos/example/repo",
            ), event="commented"),
        ]),
    )
    result = fetch_explicit_relationships("example/repo", [
        {"record_type": "issue", "number": 3, "title": "Exactly-once XP ledger"},
    ])
    assert result["relationships"] == []
    assert result["external_references"] == []
    assert result["summary"]["explicit_in_repository_relations"] == 0


def test_unverified_source_repository_does_not_become_internal_link(monkeypatch):
    source = {
        "number": 8, "title": "Unverified source",
        "html_url": "https://github.com/example/repo/issues/8",
    }
    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse([_event(source)]),
    )
    result = fetch_explicit_relationships("example/repo", [
        {"record_type": "issue", "number": 3, "title": "Target"},
    ])
    assert result["relationships"] == []
    assert result["external_references"][0]["classification"] == "external_or_unverified_repository"


def test_relationship_audit_validates_repository_targets_and_limits():
    with pytest.raises(ValueError, match="OWNER/REPO"):
        fetch_explicit_relationships("https://github.com/example/repo", [])
    with pytest.raises(ValueError, match="timeout"):
        fetch_explicit_relationships("example/repo", [], timeout=0)
    with pytest.raises(ValueError, match="limit"):
        fetch_explicit_relationships("example/repo", [
            {"record_type": "issue", "number": 1, "title": "One"},
            {"record_type": "issue", "number": 2, "title": "Two"},
        ], max_records=1)
    with pytest.raises(ValueError, match="Duplicate relationship target"):
        fetch_explicit_relationships("example/repo", [
            {"record_type": "issue", "number": 1, "title": "One"},
            {"record_type": "issue", "number": 1, "title": "Duplicate"},
        ])
    with pytest.raises(ValueError, match="positive integer"):
        fetch_explicit_relationships("example/repo", [
            {"record_type": "issue", "number": True, "title": "Bool is not an integer ID"},
        ])


def test_relationship_audit_maps_rate_limit_and_bad_payload(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise HTTPError("https://api.github.com", 403, "Forbidden", {}, None)
    monkeypatch.setattr("project_intelligence.source_relations.urlopen", forbidden)
    with pytest.raises(ValueError, match="rate limit"):
        fetch_explicit_relationships("example/repo", [
            {"record_type": "issue", "number": 1, "title": "One"},
        ])

    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse({"message": "not an event list"}),
    )
    with pytest.raises(ValueError, match="event list"):
        fetch_explicit_relationships("example/repo", [
            {"record_type": "pull_request", "number": 2, "title": "Two"},
        ])


def test_relationship_report_writes_json_and_markdown(tmp_path: Path, monkeypatch):
    source = _source(27, "Cross-referencing PR", "https://github.com/example/repo/pull/27",
                     "https://api.github.com/repos/example/repo", is_pr=True)
    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse([_event(source)]),
    )
    report = fetch_explicit_relationships("example/repo", [
        {"record_type": "issue", "number": 3, "title": "Target issue"},
    ])
    json_path = write_relationship_report(report, tmp_path / "nested" / "relations.json", format="json")
    md_path = write_relationship_report(report, tmp_path / "nested" / "relations.md", format="markdown")
    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["relationships"][0]["source"]["number"] == 27
    markdown = md_path.read_text(encoding="utf-8")
    assert "# Explicit GitHub relationship audit: example/repo" in markdown
    assert "No source record was changed." in markdown



def test_cli_github_relations_reads_snapshot_and_writes_reports(tmp_path: Path, monkeypatch, capsys):
    from project_intelligence.cli import main

    issues = {
        "schema_version": 1,
        "source": {
            "provider": "github",
            "repository": "example/repo",
            "endpoint": "https://api.github.com/repos/example/repo/issues",
            "query_state": "open",
            "fetched_at": "2026-10-21T00:00:00Z",
        },
        "issues": [{"number": 3, "title": "Target issue"}],
    }
    issue_path = tmp_path / "issues.json"
    issue_path.write_text(json.dumps(issues), encoding="utf-8")
    source = _source(
        27, "Cross-referencing PR", "https://github.com/example/repo/pull/27",
        "https://api.github.com/repos/example/repo", is_pr=True,
    )
    monkeypatch.setattr(
        "project_intelligence.source_relations.urlopen",
        lambda *_args, **_kwargs: FakeResponse([_event(source)]),
    )
    json_output, markdown_output = tmp_path / "reports" / "relations.json", tmp_path / "reports" / "relations.md"

    exit_code = main([
        "github-relations",
        "--issues", str(issue_path),
        "--json-output", str(json_output),
        "--markdown-output", str(markdown_output),
    ])

    assert exit_code == 0
    saved = json.loads(json_output.read_text(encoding="utf-8"))
    assert saved["input_snapshots"][0]["query_state"] == "open"
    assert saved["relationships"][0]["verification_state"] == "explicit_source_event_observed"
    assert saved["relationships"][0]["completion_state"] == "unknown_not_inferred"
    assert "Input snapshot coverage" in markdown_output.read_text(encoding="utf-8")
    assert "No relation is inferred from title similarity" in capsys.readouterr().out
