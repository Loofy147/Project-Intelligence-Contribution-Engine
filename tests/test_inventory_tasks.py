from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_intelligence.indexer import build_index
from project_intelligence.inventory import build_inventory, render_inventory_markdown
from project_intelligence.tasks import (
    generate_draft_tasks,
    render_tasks_markdown,
    verify_task_set,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _snapshot(root: Path):
    index = build_index(root)
    inventory = build_inventory(root, index)
    return index, inventory


def test_inventory_reads_manifest_detects_languages_and_reports_hypotheses(tmp_path: Path) -> None:
    _write(
        tmp_path / ".project-intelligence.json",
        json.dumps({
            "schema_version": 1,
            "id": "example-project",
            "name": "Example Project",
            "description": "A sample for inventory tests.",
            "repository_url": "https://github.com/example/project",
            "tags": ["python", "inventory"],
        }),
    )
    _write(tmp_path / "src" / "app.py", "def main():\n    return True\n")
    _write(tmp_path / "package.json", '{"name":"sample"}\n')

    index, inventory = _snapshot(tmp_path)

    assert inventory["project"]["id"] == "example-project"
    assert inventory["project"]["name"] == "Example Project"
    assert {item["name"] for item in inventory["languages"]} == {"Python"}
    assert any(item["signal"] == "Node.js package manifest" for item in inventory["technology_signals"])
    assert {item["signal_id"] for item in inventory["review_signals"]} == {
        "review-readme", "review-tests", "review-ci"
    }
    report = render_inventory_markdown(inventory)
    assert "Review candidates (hypotheses)" in report
    assert str(tmp_path) not in report


def test_invalid_manifest_fails_closed(tmp_path: Path) -> None:
    _write(tmp_path / ".project-intelligence.json", '{"name":"x","repository_url":"file:///etc/passwd"}')
    with pytest.raises(ValueError, match="HTTPS"):
        build_inventory(tmp_path, build_index(tmp_path))


def test_tasks_distinguish_observations_from_hypotheses_and_are_stable(tmp_path: Path) -> None:
    marker = "TO" + "DO: validate input"
    _write(tmp_path / "src" / "app.py", f"# {marker}\nprint('ready')\n")
    _write(tmp_path / "README.md", "Project readme.\n")
    _write(tmp_path / "tests" / "test_app.py", "def test_placeholder(): pass\n")
    _write(tmp_path / ".github" / "workflows" / "tests.yml", "name: tests\non: push\n")

    index, inventory = _snapshot(tmp_path)
    tasks_one = generate_draft_tasks(index, inventory)
    tasks_two = generate_draft_tasks(index, inventory)

    assert tasks_one == tasks_two
    assert tasks_one["summary"]["observed_marker_tasks"] == 1
    assert tasks_one["summary"]["hypothesis_review_tasks"] == 0
    task = tasks_one["tasks"][0]
    assert task["classification"] == "observed"
    assert task["evidence"]["path"] == "src/app.py"
    assert task["evidence"]["line_number"] == 1
    assert task["status"] == "draft"
    assert task["requires_review"] is True
    assert task["acceptance_criteria"] == []
    assert tasks_one["policy"]["automatic_bounty_creation"] is False
    assert "Observed fact" in render_tasks_markdown(tasks_one)


def test_tasks_generate_hypothesis_review_items_without_claiming_defects(tmp_path: Path) -> None:
    _write(tmp_path / "module.py", "def run(): return 1\n")
    index, inventory = _snapshot(tmp_path)
    tasks = generate_draft_tasks(index, inventory)

    assert tasks["summary"]["hypothesis_review_tasks"] == 3
    assert all(task["classification"] == "hypothesis" for task in tasks["tasks"])
    assert all(task["requires_review"] for task in tasks["tasks"])
    assert "may be missing" in " ".join(task["hypothesis"] for task in tasks["tasks"])


def test_manifest_rejects_unknown_fields(tmp_path: Path) -> None:
    _write(tmp_path / ".project-intelligence.json", '{"name":"x","owner_token":"do-not-accept"}')
    with pytest.raises(ValueError, match="Unknown"):
        build_inventory(tmp_path, build_index(tmp_path))


def test_task_verification_detects_changed_source_and_flags_missing_criteria(tmp_path: Path) -> None:
    marker = "TO" + "DO: validate input"
    source = tmp_path / "src" / "app.py"
    _write(source, f"# {marker}\nprint('ready')\n")
    _write(tmp_path / "README.md", "Project readme.\n")
    _write(tmp_path / "tests" / "test_app.py", "def test_placeholder(): pass\n")
    _write(tmp_path / ".github" / "workflows" / "tests.yml", "name: tests\non: push\n")

    original_index, original_inventory = _snapshot(tmp_path)
    task_set = generate_draft_tasks(original_index, original_inventory)
    first_id = task_set["tasks"][0]["id"]

    fresh_report = verify_task_set(original_index, original_inventory, task_set)
    assert fresh_report["summary"]["fresh"] == 1
    assert fresh_report["summary"]["stale"] == 0
    assert fresh_report["summary"]["missing_acceptance_criteria"] == 1

    # An unrelated source-line change must not change the task's stable identifier,
    # but its source digest must invalidate the stored evidence snapshot.
    _write(source, f"# {marker}\nprint('changed')\n")
    changed_index, changed_inventory = _snapshot(tmp_path)
    regenerated = generate_draft_tasks(changed_index, changed_inventory)
    assert regenerated["tasks"][0]["id"] == first_id

    stale_report = verify_task_set(changed_index, changed_inventory, task_set)
    assert stale_report["summary"]["stale"] == 1
    assert stale_report["results"][0]["reason"] == "source_file_changed"


def test_hypothesis_task_stales_when_inventory_no_longer_raises_signal(tmp_path: Path) -> None:
    _write(tmp_path / "module.py", "def run(): return 1\n")
    index_before, inventory_before = _snapshot(tmp_path)
    old_tasks = generate_draft_tasks(index_before, inventory_before)
    assert old_tasks["summary"]["hypothesis_review_tasks"] == 3

    _write(tmp_path / "README.md", "Project readme.\n")
    _write(tmp_path / "tests" / "test_app.py", "def test_placeholder(): pass\n")
    _write(tmp_path / ".github" / "workflows" / "tests.yml", "name: tests\non: push\n")
    index_after, inventory_after = _snapshot(tmp_path)

    report = verify_task_set(index_after, inventory_after, old_tasks)
    assert report["summary"]["stale"] == 3
    assert all(item["reason"] == "hypothesis_no_longer_detected" for item in report["results"])
