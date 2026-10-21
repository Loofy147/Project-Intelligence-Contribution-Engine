"""Evidence-backed draft contribution tasks; never publish tasks automatically."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

MARKER_RE = re.compile(
    r"\b(?P<marker>TODO|FIXME|XXX|HACK)\b(?:\s*[:\-–—]\s*|\s+)(?P<reason>.*)",
    re.IGNORECASE,
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|token|password|secret|authorization)\b"
    r"\s*[:=]\s*(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
BEARER_RE = re.compile(r"(?i)\bBearer\s+[^\s,;]+")


def _redact_excerpt(value: str, *, max_length: int = 280) -> str:
    """Reduce accidental credential disclosure in evidence excerpts."""
    value = SECRET_ASSIGNMENT_RE.sub(r"\1=[REDACTED]", value)
    value = BEARER_RE.sub("Bearer [REDACTED]", value)
    value = " ".join(value.split())
    return value[:max_length] + ("…" if len(value) > max_length else "")


def _stable_id(project_id: str, key: str) -> str:
    digest = hashlib.sha256(f"{project_id}\0{key}".encode("utf-8")).hexdigest()[:12]
    return f"task-{digest}"


def _marker_tasks(index: dict[str, Any], project: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = []
    for document in index.get("documents", []):
        if not isinstance(document, dict):
            continue
        path = document.get("path")
        content = document.get("content")
        if not isinstance(path, str) or not isinstance(content, str):
            continue
        source_digest = document.get("sha256")
        for line_number, raw_line in enumerate(content.splitlines(), start=1):
            match = MARKER_RE.search(raw_line)
            if not match:
                continue
            marker = match.group("marker").upper()
            reason = _redact_excerpt(match.group("reason").strip())
            excerpt = _redact_excerpt(raw_line.strip())
            title = (
                f"Review {marker} marker: {reason}"
                if reason
                else f"Review {marker} marker in {path}:{line_number}"
            )[:160]
            # Keep the identity stable if unrelated lines in the same file change.
            task_key = f"marker:{path}:{line_number}:{marker}:{reason}"
            tasks.append({
                "schema_version": 1,
                "id": _stable_id(project["id"], task_key),
                "project_id": project["id"],
                "project_name": project["name"],
                "title": title,
                "kind": "marker_follow_up",
                "classification": "observed",
                "observed_fact": f"A {marker} marker is present at {path}:{line_number}.",
                "hypothesis": "The marker may describe unfinished or problematic work; verify that it is current and actionable before implementation.",
                "confidence": "direct_source_marker",
                "evidence": {
                    "type": "source_line",
                    "path": path,
                    "line_number": line_number,
                    "source_sha256": source_digest,
                    "excerpt": excerpt,
                    "marker": marker,
                },
                "acceptance_criteria": [],
                "validation_steps": [
                    "Open the referenced source line and confirm the marker is still relevant.",
                    "Define testable acceptance criteria before implementation.",
                    "Run the project's relevant validation checks before marking the task complete.",
                ],
                "dependencies": [],
                "status": "draft",
                "requires_review": True,
            })
    return tasks


def _hypothesis_tasks(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    project = inventory["project"]
    tasks = []
    for signal in inventory.get("review_signals", []):
        task_key = f"hypothesis:{signal['signal_id']}"
        tasks.append({
            "schema_version": 1,
            "id": _stable_id(project["id"], task_key),
            "project_id": project["id"],
            "project_name": project["name"],
            "title": signal["title"],
            "kind": "inventory_review",
            "classification": "hypothesis",
            "observed_fact": signal["observed_fact"],
            "hypothesis": signal["hypothesis"],
            "confidence": "heuristic_review_candidate",
            "evidence": {
                "type": "inventory_observation",
                "signal_id": signal["signal_id"],
                **signal.get("evidence", {}),
                "inventory_file_count": inventory["summary"]["files_indexed"],
            },
            "acceptance_criteria": [],
            "validation_steps": [
                "Inspect the project and confirm whether an equivalent capability exists.",
                "If the gap is confirmed, define scope and testable acceptance criteria.",
                "If the gap is not confirmed, record the reason and dismiss this draft.",
            ],
            "dependencies": [],
            "status": "draft",
            "requires_review": True,
        })
    return tasks


def generate_draft_tasks(index: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    """Produce reviewable tasks from explicit markers and classified hypotheses."""
    tasks = _marker_tasks(index, inventory["project"]) + _hypothesis_tasks(inventory)
    tasks.sort(key=lambda item: (
        0 if item["classification"] == "observed" else 1,
        item["evidence"].get("path", item["evidence"].get("signal_id", "")),
        item["evidence"].get("line_number", 0),
        item["id"],
    ))
    return {
        "schema_version": 1,
        "project": {
            "id": inventory["project"]["id"],
            "name": inventory["project"]["name"],
            "repository_url": inventory["project"].get("repository_url", ""),
        },
        "source": {
            "generated_from_files": inventory["summary"]["files_indexed"],
            "inventory_generated_at": inventory["generated_at"],
        },
        "summary": {
            "total_drafts": len(tasks),
            "observed_marker_tasks": sum(item["classification"] == "observed" for item in tasks),
            "hypothesis_review_tasks": sum(item["classification"] == "hypothesis" for item in tasks),
            "published": 0,
        },
        "tasks": tasks,
        "policy": {
            "automatic_publication": False,
            "automatic_bounty_creation": False,
            "human_review_required": True,
            "note": "These are drafts, not verified defects or ready-to-fund bounties. Define acceptance criteria before execution.",
        },
    }


def load_task_set(source: str | Path) -> dict[str, Any]:
    """Load and minimally validate a versioned task draft file."""
    path = Path(source).expanduser()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read task file {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Task file must be a schema version 1 JSON object")
    if not isinstance(data.get("project"), dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("Task file is missing a project object or tasks list")
    for task in data["tasks"]:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise ValueError("Task file contains a malformed task record")
        if not isinstance(task.get("evidence"), dict):
            raise ValueError("Task file contains a task without an evidence object")
    return data


def verify_task_set(
    index: dict[str, Any],
    inventory: dict[str, Any],
    task_set: dict[str, Any],
) -> dict[str, Any]:
    """Compare stored task evidence to a fresh scan; never modify the task file."""
    current_documents = {
        document["path"]: document
        for document in index.get("documents", [])
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }
    current_signals = {
        signal["signal_id"]
        for signal in inventory.get("review_signals", [])
        if isinstance(signal, dict) and isinstance(signal.get("signal_id"), str)
    }
    current_project_id = inventory["project"]["id"]
    recorded_project_id = task_set.get("project", {}).get("id")
    project_mismatch = recorded_project_id != current_project_id

    results = []
    for task in task_set["tasks"]:
        evidence = task["evidence"]
        evidence_type = evidence.get("type")
        freshness = "fresh"
        reason = "evidence_matches_current_scan"

        if project_mismatch:
            freshness, reason = "stale", "project_identity_mismatch"
        elif evidence_type == "source_line":
            path = evidence.get("path")
            current = current_documents.get(path)
            if current is None:
                freshness, reason = "stale", "source_file_missing"
            elif current.get("sha256") != evidence.get("source_sha256"):
                freshness, reason = "stale", "source_file_changed"
            else:
                lines = current.get("content", "").splitlines()
                line_number = evidence.get("line_number")
                if not isinstance(line_number, int) or line_number < 1 or line_number > len(lines):
                    freshness, reason = "stale", "source_line_missing"
                else:
                    match = MARKER_RE.search(lines[line_number - 1])
                    if not match or match.group("marker").upper() != evidence.get("marker"):
                        freshness, reason = "stale", "source_marker_no_longer_matches"
        elif evidence_type == "inventory_observation":
            signal_id = evidence.get("signal_id")
            if signal_id not in current_signals:
                freshness, reason = "stale", "hypothesis_no_longer_detected"
        else:
            freshness, reason = "unverified", "unsupported_evidence_type"

        criteria = task.get("acceptance_criteria")
        criteria_complete = (
            isinstance(criteria, list)
            and len(criteria) > 0
            and all(isinstance(item, str) and item.strip() for item in criteria)
        )
        results.append({
            "task_id": task["id"],
            "title": task.get("title", ""),
            "freshness": freshness,
            "reason": reason,
            "acceptance_criteria_complete": criteria_complete,
            "review_blockers": (
                [] if criteria_complete else ["acceptance_criteria_missing_or_incomplete"]
            ),
            "eligible_for_execution": (
                freshness == "fresh"
                and criteria_complete
                and task.get("status") == "approved"
                and task.get("requires_review") is False
            ),
        })

    fresh_count = sum(item["freshness"] == "fresh" for item in results)
    stale_count = sum(item["freshness"] == "stale" for item in results)
    unverified_count = sum(item["freshness"] == "unverified" for item in results)
    criteria_missing_count = sum(not item["acceptance_criteria_complete"] for item in results)
    return {
        "schema_version": 1,
        "project_id": current_project_id,
        "task_file_project_id": recorded_project_id,
        "summary": {
            "total_tasks": len(results),
            "fresh": fresh_count,
            "stale": stale_count,
            "unverified": unverified_count,
            "missing_acceptance_criteria": criteria_missing_count,
            "eligible_for_execution": sum(item["eligible_for_execution"] for item in results),
        },
        "results": results,
        "policy": "Verification is read-only. Stale evidence must be reviewed; fresh drafts still require acceptance criteria and explicit approval before execution.",
    }


def render_tasks_markdown(task_set: dict[str, Any]) -> str:
    """Render draft tasks in a compact review format."""
    lines = [
        f"# Draft contribution tasks: {task_set['project']['name']}",
        "",
        f"- Drafts: {task_set['summary']['total_drafts']}",
        f"- Observed marker tasks: {task_set['summary']['observed_marker_tasks']}",
        f"- Hypothesis review tasks: {task_set['summary']['hypothesis_review_tasks']}",
        "- Published: 0",
        "",
        "> Every item requires review. Inventory heuristics are not confirmed defects. Define acceptance criteria before implementation or bounty creation.",
        "",
    ]
    for task in task_set["tasks"]:
        lines.extend([
            f"## {task['title']}",
            "",
            f"- ID: `{task['id']}`",
            f"- Classification: **{task['classification']}**",
            f"- Status: `{task['status']}`",
            f"- Observed fact: {task['observed_fact']}",
            f"- Hypothesis: {task['hypothesis']}",
        ])
        evidence = task["evidence"]
        if evidence.get("type") == "source_line":
            lines.extend([
                f"- Evidence: `{evidence['path']}:{evidence['line_number']}`",
                f"- Source SHA-256: `{evidence.get('source_sha256')}`",
                "",
                "~~~text",
                evidence.get("excerpt", ""),
                "~~~",
            ])
        else:
            lines.extend([
                f"- Evidence type: inventory observation (`{evidence.get('signal_id', '')}`)",
            ])
        lines.extend([
            "",
            "### Required before implementation",
            "",
            "- [ ] Human reviewer confirms the finding is current.",
            "- [ ] Scope and acceptance criteria are written.",
            "- [ ] Dependencies and validation commands are identified.",
            "",
        ])
    return "\n".join(lines)


def write_tasks(task_set: dict[str, Any], destination: str | Path, *, format: str = "json") -> Path:
    """Write task drafts as JSON or Markdown."""
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(task_set, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_tasks_markdown(task_set)
    else:
        raise ValueError("Task format must be 'json' or 'markdown'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
