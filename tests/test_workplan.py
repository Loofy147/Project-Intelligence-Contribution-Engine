from __future__ import annotations
import json
from pathlib import Path
import pytest
from project_intelligence.workplan import build_workplan, load_snapshot, render_workplan_markdown

def test_workplan_sorts_declared_priorities_and_keeps_sources_separate() -> None:
    issues = {"schema_version": 1, "source": {"repository": "example/repo", "fetched_at": "now"},
      "issues": [
        {"number": 10, "title": "Unranked issue", "state": "open", "url": "https://github.com/example/repo/issues/10", "labels": [], "updated_at": None},
        {"number": 2, "title": "[P1] Review license", "state": "open", "url": "https://github.com/example/repo/issues/2", "labels": [], "updated_at": None},
        {"number": 1, "title": "[P0] Add authorization boundary", "state": "open", "url": "https://github.com/example/repo/issues/1", "labels": ["security"], "updated_at": None},
      ]}
    pulls = {"schema_version": 1, "source": {"repository": "example/repo", "fetched_at": "now"},
      "pull_requests": [{"number": 20, "title": "Draft review workflow", "state": "open", "url": "https://github.com/example/repo/pull/20", "draft": True, "head_ref": "feature/review", "base_ref": "main", "updated_at": None}]}
    tasks = {"tasks": [{"id": "task-1", "title": "Review tests", "classification": "hypothesis", "status": "draft", "evidence": {}}]}
    plan = build_workplan(issues, pulls, tasks)
    assert [item["number"] for item in plan["issues"]] == [1, 2, 10]
    assert plan["issues"][2]["priority"] == "unranked"
    assert plan["pull_requests"][0]["canonical_source"] == "github_pull_request"
    assert plan["draft_tasks"][0]["canonical_source"] == "engine_draft"
    assert plan["summary"]["automatic_bounty_creation"] is False
    assert "External records created: 0" in render_workplan_markdown(plan)

def test_workplan_rejects_mismatched_repository_snapshots() -> None:
    issues = {"source": {"repository": "example/one"}, "issues": []}
    pulls = {"source": {"repository": "example/two"}, "pull_requests": []}
    with pytest.raises(ValueError, match="same repository"): build_workplan(issues, pulls)

def test_load_snapshot_validates_schema_and_collection(tmp_path: Path) -> None:
    path = tmp_path / "issues.json"
    path.write_text(json.dumps({"schema_version": 2, "issues": [], "source": {"repository": "example/repo"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="schema version 1"): load_snapshot(path, "issues")
    path.write_text(json.dumps({"schema_version": 1, "issues": [], "source": {"repository": "example/repo"}}), encoding="utf-8")
    assert load_snapshot(path, "issues")["issues"] == []
