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
CHECKBOX_RE = re.compile(r"^ {0,3}(?:[-*+]|\d+\.)\s+\[\s\]\s+(?P<title>.+?)\s*$")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s+(?P<title>.+?)\s*#*\s*$")


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


def _checklist_tasks(index: dict[str, Any], project: dict[str, Any]) -> list[dict[str, Any]]:
    """Read only unchecked items from manifest-declared Markdown planning files."""
    configured_paths = set(project.get("checklist_paths", []))
    if not configured_paths:
        return []
    indexed_paths = {
        document.get("path")
        for document in index.get("documents", [])
        if isinstance(document, dict)
    }
    missing = configured_paths - indexed_paths
    if missing:
        raise ValueError("Configured checklist files were not found in index: " + ", ".join(sorted(missing)))

    tasks = []
    for document in index.get("documents", []):
        path = document.get("path") if isinstance(document, dict) else None
        content = document.get("content") if isinstance(document, dict) else None
        if path not in configured_paths or not isinstance(content, str):
            continue
        source_digest = document.get("sha256")
        section = "Document start"
        inside_fence = False
        for line_number, raw_line in enumerate(content.splitlines(), start=1):
            stripped = raw_line.lstrip()
            if stripped.startswith(chr(96) * 3) or stripped.startswith("~~~"):
                inside_fence = not inside_fence
                continue
            if inside_fence:
                continue
            heading_match = HEADING_RE.match(raw_line)
            if heading_match:
                section = heading_match.group("title").strip()
                continue
            match = CHECKBOX_RE.match(raw_line)
            if not match:
                continue
            item_text = _redact_excerpt(match.group("title").strip())
            task_key = f"checklist:{path}:{line_number}:{item_text}"
            tasks.append({
                "schema_version": 1,
                "id": _stable_id(project["id"], task_key),
                "project_id": project["id"],
                "project_name": project["name"],
                "title": item_text[:160],
                "kind": "checklist_follow_up",
                "classification": "observed",
                "observed_fact": f"An unchecked Markdown checklist item is present at {path}:{line_number}.",
                "hypothesis": "The selected planning file records this item as unchecked; verify that it is still in scope and not deferred before implementation.",
                "confidence": "explicit_unchecked_checklist",
                "evidence": {
                    "type": "checklist_item",
                    "path": path,
                    "line_number": line_number,
                    "source_sha256": source_digest,
                    "section": section,
                    "text": item_text,
                },
                "acceptance_criteria": [],
                "validation_steps": [
                    "Confirm the checklist item is current and within the active project scope.",
                    "Define measurable completion evidence if the item is too broad.",
                    "Run the relevant validation before checking the item off.",
                ],
                "dependencies": [],
                "status": "draft",
                "requires_review": True,
            })
    return tasks


def _canonical_record_digest(record: dict[str, Any]) -> str:
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _registry_work_item_tasks(index: dict[str, Any], project: dict[str, Any]) -> list[dict[str, Any]]:
    """Project nonterminal records from explicitly configured project registries."""
    indexed = {
        document["path"]: document
        for document in index.get("documents", [])
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }
    tasks = []
    for config in project.get("registry_work_item_sources", []):
        path = config["path"]
        document = indexed.get(path)
        if document is None:
            raise ValueError(f"Configured registry source was not indexed: {path}")
        try:
            parsed = json.loads(document["content"])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(f"Configured registry source is not valid JSON: {path}") from exc
        records = parsed.get(config["collection"]) if isinstance(parsed, dict) else None
        if not isinstance(records, list):
            raise ValueError(f"Registry source {path} has no list collection {config['collection']!r}")

        active_statuses = set(config["active_statuses"])
        seen_ids = set()
        for position, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            raw_status = record.get(config["status_field"])
            status = raw_status.strip() if isinstance(raw_status, str) else ""
            if status.casefold() not in active_statuses:
                continue
            raw_id = record.get(config["id_field"])
            raw_title = record.get(config["title_field"])
            if not isinstance(raw_id, (str, int)) or isinstance(raw_id, bool) or not str(raw_id).strip():
                raise ValueError(f"Active registry item in {path} has no stable identifier")
            if not isinstance(raw_title, str) or not raw_title.strip():
                raise ValueError(f"Active registry item in {path} has no title")
            source_id = str(raw_id).strip()
            if source_id in seen_ids:
                raise ValueError(f"Duplicate active registry item ID {source_id!r} in {path}")
            seen_ids.add(source_id)

            criteria = record.get(config["acceptance_criteria_field"], [])
            if criteria is None:
                criteria = []
            if not isinstance(criteria, list) or any(not isinstance(item, str) for item in criteria):
                raise ValueError(f"Registry item {source_id!r} acceptance criteria must be a list of strings")
            dependencies = record.get(config["dependencies_field"], [])
            if dependencies is None:
                dependencies = []
            if not isinstance(dependencies, list) or any(not isinstance(item, str) for item in dependencies):
                raise ValueError(f"Registry item {source_id!r} dependencies must be a list of strings")
            priority = record.get(config["priority_field"])
            kind = record.get(config["kind_field"])
            required_evidence = record.get(config["required_evidence_field"], [])
            if required_evidence is None:
                required_evidence = []
            if not isinstance(required_evidence, list) or any(not isinstance(item, str) for item in required_evidence):
                raise ValueError(f"Registry item {source_id!r} required evidence must be a list of strings")

            pointer = f"/{config['collection']}/{position}"
            item_digest = _canonical_record_digest(record)
            task_key = f"registry:{path}:{config['collection']}:{source_id}"
            priority_level = priority.get("level") if isinstance(priority, dict) else priority
            priority_rationale = priority.get("rationale") if isinstance(priority, dict) else None
            tasks.append({
                "schema_version": 1,
                "id": _stable_id(project["id"], task_key),
                "project_id": project["id"],
                "project_name": project["name"],
                "title": raw_title.strip()[:200],
                "kind": "registry_work_item",
                "classification": "observed",
                "canonical_source": "repository_registry",
                "source_work_item_id": source_id,
                "source_status": status,
                "observed_fact": f"Registry {path} records work item {source_id!r} with status {status!r}.",
                "hypothesis": "The configured registry marks this item as nonterminal. Confirm scope, dependencies, and current evidence before advancing its source status.",
                "confidence": "repository_native_work_item_status",
                "evidence": {
                    "type": "registry_work_item",
                    "path": path,
                    "source_sha256": document.get("sha256"),
                    "collection": config["collection"],
                    "json_pointer": pointer,
                    "id_field": config["id_field"],
                    "source_item_id": source_id,
                    "source_item_sha256": item_digest,
                    "title_field": config["title_field"],
                    "source_title": raw_title.strip(),
                    "status_field": config["status_field"],
                    "source_status": status,
                    "active_statuses": sorted(active_statuses),
                },
                "acceptance_criteria": [item.strip() for item in criteria if item.strip()],
                "validation_steps": [
                    "Review the canonical registry item and its source references.",
                    "Verify each recorded dependency and the item's active status.",
                    "Keep a proposed change in review until its acceptance criteria have evidence.",
                ],
                "dependencies": dependencies,
                "required_evidence": [item.strip() for item in required_evidence if item.strip()],
                "priority": priority if priority is not None else {},
                "priority_level": priority_level,
                "priority_rationale": priority_rationale,
                "source_kind": kind if isinstance(kind, str) else "",
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
    project = inventory["project"]
    marker_tasks = _marker_tasks(index, project)
    checklist_tasks = _checklist_tasks(index, project)
    registry_tasks = _registry_work_item_tasks(index, project)
    hypothesis_tasks = _hypothesis_tasks(inventory)
    tasks = marker_tasks + checklist_tasks + registry_tasks + hypothesis_tasks
    kind_order = {
        "registry_work_item": 0,
        "marker_follow_up": 1,
        "checklist_follow_up": 2,
        "inventory_review": 3,
    }
    tasks.sort(key=lambda item: (
        0 if item["classification"] == "observed" else 1,
        kind_order.get(item.get("kind"), 9),
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
            "observed_marker_tasks": sum(item["kind"] == "marker_follow_up" for item in tasks),
            "observed_checklist_tasks": sum(item["kind"] == "checklist_follow_up" for item in tasks),
            "registry_work_item_tasks": sum(item["kind"] == "registry_work_item" for item in tasks),
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
        elif evidence_type == "checklist_item":
            current = current_documents.get(evidence.get("path"))
            if current is None:
                freshness, reason = "stale", "checklist_file_missing"
            elif current.get("sha256") != evidence.get("source_sha256"):
                freshness, reason = "stale", "checklist_file_changed"
            else:
                lines = current.get("content", "").splitlines()
                line_number = evidence.get("line_number")
                if not isinstance(line_number, int) or line_number < 1 or line_number > len(lines):
                    freshness, reason = "stale", "checklist_item_missing"
                else:
                    match = CHECKBOX_RE.match(lines[line_number - 1])
                    if not match or _redact_excerpt(match.group("title").strip()) != evidence.get("text"):
                        freshness, reason = "stale", "checklist_item_no_longer_matches"
        elif evidence_type == "registry_work_item":
            current = current_documents.get(evidence.get("path"))
            if current is None:
                freshness, reason = "stale", "registry_file_missing"
            else:
                try:
                    registry = json.loads(current.get("content", ""))
                    records = registry.get(evidence.get("collection")) if isinstance(registry, dict) else None
                except json.JSONDecodeError:
                    records = None
                if not isinstance(records, list):
                    freshness, reason = "stale", "registry_collection_missing"
                else:
                    record = next(
                        (
                            item for item in records
                            if isinstance(item, dict)
                            and str(item.get(evidence.get("id_field"))) == evidence.get("source_item_id")
                        ),
                        None,
                    )
                    if record is None:
                        freshness, reason = "stale", "registry_item_missing"
                    elif _canonical_record_digest(record) != evidence.get("source_item_sha256"):
                        freshness, reason = "stale", "registry_item_changed"
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
        f"- Source marker tasks: {task_set['summary']['observed_marker_tasks']}",
        f"- Explicit checklist items: {task_set['summary'].get('observed_checklist_tasks', 0)}",
        f"- Canonical registry work-item projections: {task_set['summary'].get('registry_work_item_tasks', 0)}",
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
        if evidence.get("type") == "registry_work_item":
            lines.extend([
                f"- Canonical source ID: `{evidence.get('source_item_id')}`",
                f"- Source status: `{evidence.get('source_status')}`",
                f"- Registry evidence: `{evidence.get('path')}#{evidence.get('json_pointer')}`",
                f"- Record SHA-256: `{evidence.get('source_item_sha256')}`",
            ])
        elif evidence.get("type") == "checklist_item":
            lines.extend([
                f"- Evidence: `{evidence['path']}:{evidence['line_number']}`",
                f"- Section: {evidence.get('section', 'unknown')}",
                f"- Source SHA-256: `{evidence.get('source_sha256')}`",
            ])
        elif evidence.get("type") == "source_line":
            lines.extend([
                f"- Evidence: `{evidence['path']}:{evidence['line_number']}`",
                f"- Source SHA-256: `{evidence.get('source_sha256')}`",
                "",
                "~~~text",
                evidence.get("excerpt", ""),
                "~~~",
            ])
        elif evidence.get("type") == "inventory_observation":
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
