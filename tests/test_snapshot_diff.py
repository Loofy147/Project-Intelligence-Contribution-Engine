from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_intelligence.snapshot_diff import (
    compare_snapshots,
    render_snapshot_diff_markdown,
    write_snapshot_diff,
)


def _issues(records, *, state="all", repository="example/repo", fetched="2026-10-21T00:00:00Z"):
    return {
        "schema_version": 1,
        "source": {
            "repository": repository,
            "query_state": state,
            "fetched_at": fetched,
        },
        "issues": records,
    }


def _pulls(records, *, state="all", repository="example/repo", fetched="2026-10-21T00:00:00Z"):
    return {
        "schema_version": 1,
        "source": {
            "repository": repository,
            "query_state": state,
            "fetched_at": fetched,
        },
        "pull_requests": records,
    }


def test_comparison_detects_issue_state_title_labels_and_updated_at_changes() -> None:
    previous = _issues([{
        "number": 1, "title": "Old title", "state": "open",
        "url": "https://github.com/example/repo/issues/1",
        "labels": ["bug"], "updated_at": "2026-10-01T00:00:00Z",
    }])
    current = _issues([{
        "number": 1, "title": "New title", "state": "closed",
        "url": "https://github.com/example/repo/issues/1",
        "labels": ["done"], "updated_at": "2026-10-02T00:00:00Z",
    }], fetched="2026-10-22T00:00:00Z")

    result = compare_snapshots(previous, current)
    assert result["summary"]["issue_records_changed"] == 1
    change = result["issues"][0]
    assert change["event"] == "record_changed"
    assert set(change["changed_fields"]) == {"title", "state", "labels", "updated_at"}
    assert change["previous"]["state"] == "open"
    assert change["current"]["state"] == "closed"
    assert result["comparison"]["coverage"] == "full_state_snapshots"
    assert result["summary"]["external_records_changed"] == 0


def test_comparison_reports_appearance_and_never_infers_deletion_or_closure() -> None:
    previous = _issues([
        {"number": 1, "title": "Old", "state": "open", "url": "u1", "labels": [], "updated_at": None},
        {"number": 2, "title": "May be filtered", "state": "open", "url": "u2", "labels": [], "updated_at": None},
    ], state="all")
    current = _issues([
        {"number": 1, "title": "Old", "state": "open", "url": "u1", "labels": [], "updated_at": None},
        {"number": 3, "title": "Newly observed", "state": "open", "url": "u3", "labels": [], "updated_at": None},
    ], state="open")

    result = compare_snapshots(previous, current)
    assert [(item["number"], item["event"]) for item in result["issues"]] == [
        (2, "absent_from_current_snapshot"),
        (3, "appeared_in_current_snapshot"),
    ]
    missing = result["issues"][0]
    assert "Do not infer closure" in missing["interpretation"]
    assert result["comparison"]["coverage"] == "filtered_or_unknown_query_coverage"
    report = render_snapshot_diff_markdown(result)
    assert "Absence from a query does not mean closed" in report
    assert "No external records were changed." in report


def test_comparison_detects_pull_request_head_revision_changes() -> None:
    previous_issue = _issues([])
    current_issue = _issues([])
    previous_pr = _pulls([{
        "number": 7, "title": "Proposal", "state": "open",
        "url": "https://github.com/example/repo/pull/7", "labels": [],
        "updated_at": "same", "draft": True, "head_ref": "feature",
        "head_sha": "abc", "base_ref": "main",
    }])
    current_pr = _pulls([{
        "number": 7, "title": "Proposal", "state": "open",
        "url": "https://github.com/example/repo/pull/7", "labels": [],
        "updated_at": "same", "draft": True, "head_ref": "feature",
        "head_sha": "def", "base_ref": "main",
    }])

    result = compare_snapshots(previous_issue, current_issue, previous_pr, current_pr)
    assert result["summary"]["pull_request_records_changed"] == 1
    assert result["pull_requests"][0]["changed_fields"] == ["head_sha"]


def test_comparison_rejects_mismatched_repositories_and_unpaired_pull_snapshots() -> None:
    with pytest.raises(ValueError, match="same repository"):
        compare_snapshots(_issues([]), _issues([], repository="other/repo"))

    with pytest.raises(ValueError, match="supplied together"):
        compare_snapshots(_issues([]), _issues([]), previous_pulls=_pulls([]))


def test_comparison_rejects_invalid_snapshots_and_duplicate_numbers() -> None:
    with pytest.raises(ValueError, match="schema version 1"):
        compare_snapshots({"schema_version": 2}, _issues([]))

    with pytest.raises(ValueError, match="duplicate canonical record"):
        compare_snapshots(
            _issues([
                {"number": 1, "title": "One"},
                {"number": 1, "title": "Duplicate"},
            ]),
            _issues([]),
        )


def test_comparison_rejects_pull_snapshot_from_another_repository() -> None:
    with pytest.raises(ValueError, match="same repository"):
        compare_snapshots(
            _issues([]),
            _issues([]),
            _pulls([], repository="other/repo"),
            _pulls([]),
        )


def test_write_snapshot_diff_supports_json_and_markdown(tmp_path: Path) -> None:
    result = compare_snapshots(_issues([]), _issues([]))
    json_path = write_snapshot_diff(result, tmp_path / "diff.json", format="json")
    md_path = write_snapshot_diff(result, tmp_path / "diff.md", format="markdown")

    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == 1
    assert "# Snapshot comparison: example/repo" in md_path.read_text(encoding="utf-8")
