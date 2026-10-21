"""Read-only work-plan projection over canonical issues, PRs, and draft findings."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_PRIORITY_RE = re.compile(r"^\s*\[(P[0-3])\]\s*", re.IGNORECASE)
_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "unranked": 4}


def load_snapshot(path: str | Path, collection_key: str) -> dict[str, Any]:
    snapshot_path = Path(path).expanduser()
    try:
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read snapshot {snapshot_path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError(f"{collection_key} snapshot must be a schema version 1 JSON object")
    if not isinstance(data.get("source"), dict) or not isinstance(data["source"].get("repository"), str):
        raise ValueError(f"{collection_key} snapshot is missing source repository metadata")
    if not isinstance(data.get(collection_key), list):
        raise ValueError(f"{collection_key} snapshot is missing its list")
    return data


def build_workplan(issue_snapshot: dict[str, Any], pull_snapshot: dict[str, Any] | None = None,
                   task_set: dict[str, Any] | None = None) -> dict[str, Any]:
    """Project source records into priority groups without duplicating or changing them."""
    repository = issue_snapshot["source"]["repository"]
    if pull_snapshot and pull_snapshot["source"]["repository"].casefold() != repository.casefold():
        raise ValueError("Issue and pull-request snapshots must refer to the same repository")

    issues = []
    for source in issue_snapshot["issues"]:
        if not isinstance(source, dict):
            continue
        title, number, url = source.get("title"), source.get("number"), source.get("url")
        if not isinstance(title, str) or not isinstance(number, int) or not isinstance(url, str):
            continue
        match = _PRIORITY_RE.match(title)
        priority = match.group(1).upper() if match else "unranked"
        issues.append({
            "number": number, "title": title, "state": source.get("state", "unknown"),
            "url": url, "labels": source.get("labels", []), "updated_at": source.get("updated_at"),
            "priority": priority,
            "priority_basis": "explicit_title_prefix" if match else "not_specified",
            "canonical_source": "github_issue",
        })
    issues.sort(key=lambda item: (_PRIORITY_ORDER[item["priority"]], item["number"]))

    pulls = []
    if pull_snapshot:
        for source in pull_snapshot["pull_requests"]:
            if not isinstance(source, dict):
                continue
            number, title, url = source.get("number"), source.get("title"), source.get("url")
            if not isinstance(number, int) or not isinstance(title, str) or not isinstance(url, str):
                continue
            pulls.append({
                "number": number, "title": title, "state": source.get("state", "unknown"),
                "url": url, "draft": bool(source.get("draft", False)),
                "head_ref": source.get("head_ref"), "base_ref": source.get("base_ref"),
                "updated_at": source.get("updated_at"), "canonical_source": "github_pull_request",
            })
    pulls.sort(key=lambda item: (item["draft"], item["number"]))

    drafts = []
    if task_set:
        for task in task_set.get("tasks", []):
            if isinstance(task, dict):
                drafts.append({
                    "id": task.get("id"), "title": task.get("title", ""),
                    "classification": task.get("classification", "unclassified"),
                    "status": task.get("status", "draft"), "evidence": task.get("evidence", {}),
                    "canonical_source": "engine_draft", "requires_review": True,
                })

    priority_counts = {priority: sum(item["priority"] == priority for item in issues)
                       for priority in ("P0", "P1", "P2", "P3", "unranked")}
    return {
        "schema_version": 1, "repository": repository,
        "source_snapshots": {
            "issues_fetched_at": issue_snapshot["source"].get("fetched_at"),
            "pull_requests_fetched_at": pull_snapshot["source"].get("fetched_at") if pull_snapshot else None,
        },
        "summary": {
            "existing_issues": len(issues), "issues_by_priority": priority_counts,
            "existing_pull_requests": len(pulls), "draft_tasks": len(drafts),
            "created_external_records": 0, "automatic_bounty_creation": False,
        },
        "issues": issues, "pull_requests": pulls, "draft_tasks": drafts,
        "policy": {
            "issues_are_canonical": True, "pull_requests_are_proposals": True,
            "draft_tasks_are_noncanonical_until_approved": True,
            "automatic_writes": False, "automatic_bounties": False,
            "priority_note": "P0–P3 is parsed only from a leading issue-title prefix; unranked means no priority was declared.",
            "linking_note": "No issue/PR relationship is inferred from similar wording. Verify explicit links before claiming overlap.",
        },
    }


def render_workplan_markdown(plan: dict[str, Any]) -> str:
    summary, priorities = plan["summary"], plan["summary"]["issues_by_priority"]
    lines = [
        f"# Work plan: {plan['repository']}", "",
        f"- Existing issues: {summary['existing_issues']}",
        f"- Priority counts: P0={priorities['P0']}, P1={priorities['P1']}, P2={priorities['P2']}, P3={priorities['P3']}, unranked={priorities['unranked']}",
        f"- Existing pull requests: {summary['existing_pull_requests']}",
        f"- Draft findings: {summary['draft_tasks']}", "- External records created: 0", "",
        "> This is a read-only view. Priority is copied from explicit issue-title prefixes. No work is created, changed, closed, merged, assigned, or funded.", "",
        "## Existing issues — canonical work records", "",
    ]
    if not plan["issues"]:
        lines.append("No issues in the selected snapshot.")
    current = None
    for issue in plan["issues"]:
        if issue["priority"] != current:
            current = issue["priority"]
            lines.extend([f"### {current if current != 'unranked' else 'Unranked'}", ""])
        labels = ", ".join(issue["labels"]) if issue["labels"] else "unlabeled"
        lines.append(f"- [#{issue['number']} — {issue['title']}]({issue['url']}) ({issue['state']}; {labels})")
    lines.extend(["", "## Pull requests — proposed changes", ""])
    if not plan["pull_requests"]:
        lines.append("No pull requests in the selected snapshot.")
    for pr in plan["pull_requests"]:
        status = "draft" if pr["draft"] else "not draft"
        lines.append(f"- [#{pr['number']} — {pr['title']}]({pr['url']}) ({pr['state']}; {status}; {pr['head_ref'] or 'unknown'} → {pr['base_ref'] or 'unknown'})")
    lines.extend(["", "## Draft findings — require review", ""])
    if not plan["draft_tasks"]:
        lines.append("No source-marker or inventory-hypothesis drafts were generated by the current scan.")
    for task in plan["draft_tasks"]:
        lines.append(f"- {task['title']} (classification: {task['classification']}; status: {task['status']}; review required)")
    lines.extend([
        "", "## Rules", "",
        "- Do not duplicate a canonical GitHub issue as a second task by default.",
        "- Do not infer issue/PR linkage from similar titles; verify source links.",
        "- A draft hypothesis is not a confirmed defect and never becomes a bounty automatically.", "",
    ])
    return "\n".join(lines)


def write_workplan(plan: dict[str, Any], destination: str | Path, *, format: str = "markdown") -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_workplan_markdown(plan)
    else:
        raise ValueError("Workplan format must be 'json' or 'markdown'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
