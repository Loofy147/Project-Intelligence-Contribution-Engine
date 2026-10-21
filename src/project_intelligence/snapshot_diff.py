"""Compare read-only GitHub snapshots without inventing lifecycle conclusions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _validate_snapshot(snapshot: dict[str, Any], collection: str, label: str) -> tuple[str, list[dict[str, Any]]]:
    if not isinstance(snapshot, dict) or snapshot.get("schema_version") != 1:
        raise ValueError(f"{label} snapshot must be a schema version 1 JSON object")
    source = snapshot.get("source")
    if not isinstance(source, dict) or not isinstance(source.get("repository"), str) or not source["repository"].strip():
        raise ValueError(f"{label} snapshot is missing source repository metadata")
    records = snapshot.get(collection)
    if not isinstance(records, list):
        raise ValueError(f"{label} snapshot is missing its '{collection}' list")
    repository = source["repository"].strip()
    seen: set[int] = set()
    normalized: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        number = record.get("number")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            continue
        if number in seen:
            raise ValueError(f"{label} snapshot contains duplicate canonical record number #{number}")
        seen.add(number)
        normalized.append(record)
    return repository, normalized


def _labels(value: Any) -> list[str] | Any:
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return sorted(set(value), key=str.casefold)
    return value


def _record_view(record: dict[str, Any], *, is_pull: bool) -> dict[str, Any]:
    fields = ["number", "title", "state", "url", "labels", "updated_at"]
    if is_pull:
        fields.extend(["draft", "head_ref", "head_sha", "base_ref"])
    result = {key: record.get(key) for key in fields}
    result["labels"] = _labels(result.get("labels", []))
    return result


def _compare_collection(
    previous_records: list[dict[str, Any]],
    current_records: list[dict[str, Any]],
    *,
    is_pull: bool,
) -> list[dict[str, Any]]:
    previous_by_number = {record["number"]: record for record in previous_records}
    current_by_number = {record["number"]: record for record in current_records}
    changes: list[dict[str, Any]] = []

    for number in sorted(set(previous_by_number) | set(current_by_number)):
        previous = previous_by_number.get(number)
        current = current_by_number.get(number)
        if previous is None:
            changes.append({
                "number": number,
                "event": "appeared_in_current_snapshot",
                "previous": None,
                "current": _record_view(current, is_pull=is_pull),  # type: ignore[arg-type]
                "changed_fields": [],
                "interpretation": "This record appears in the current snapshot; this does not by itself prove when or why it was created.",
            })
            continue
        if current is None:
            changes.append({
                "number": number,
                "event": "absent_from_current_snapshot",
                "previous": _record_view(previous, is_pull=is_pull),
                "current": None,
                "changed_fields": [],
                "interpretation": "The current query did not return this prior record. Do not infer closure, deletion, resolution, or completion from absence.",
            })
            continue

        before = _record_view(previous, is_pull=is_pull)
        after = _record_view(current, is_pull=is_pull)
        changed_fields = [
            field for field in before
            if field != "number" and before.get(field) != after.get(field)
        ]
        if not changed_fields:
            continue
        changes.append({
            "number": number,
            "event": "record_changed",
            "previous": before,
            "current": after,
            "changed_fields": changed_fields,
            "interpretation": "Only listed metadata fields differ between these snapshots; inspect the canonical source before drawing a completion or dependency conclusion.",
        })
    return changes


def compare_snapshots(
    previous_issues: dict[str, Any],
    current_issues: dict[str, Any],
    previous_pulls: dict[str, Any] | None = None,
    current_pulls: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare same-repository issue and optional PR snapshots by canonical number.

    Comparison is read-only. It never infers that an absent item was closed/deleted,
    links issues to PRs, or changes the underlying records.
    """
    if (previous_pulls is None) != (current_pulls is None):
        raise ValueError("Previous and current pull-request snapshots must be supplied together")

    previous_repo, previous_issue_records = _validate_snapshot(previous_issues, "issues", "Previous issue")
    current_repo, current_issue_records = _validate_snapshot(current_issues, "issues", "Current issue")
    if previous_repo.casefold() != current_repo.casefold():
        raise ValueError("Previous and current issue snapshots must refer to the same repository")

    previous_issue_source = previous_issues["source"]
    current_issue_source = current_issues["source"]
    previous_pull_source = current_pull_source = None
    issue_changes = _compare_collection(previous_issue_records, current_issue_records, is_pull=False)
    pull_changes: list[dict[str, Any]] = []

    if previous_pulls is not None and current_pulls is not None:
        previous_pull_repo, previous_pull_records = _validate_snapshot(previous_pulls, "pull_requests", "Previous pull-request")
        current_pull_repo, current_pull_records = _validate_snapshot(current_pulls, "pull_requests", "Current pull-request")
        if (
            previous_pull_repo.casefold() != current_pull_repo.casefold()
            or previous_pull_repo.casefold() != current_repo.casefold()
        ):
            raise ValueError("Issue and pull-request snapshots must refer to the same repository")
        previous_pull_source = previous_pulls["source"]
        current_pull_source = current_pulls["source"]
        pull_changes = _compare_collection(previous_pull_records, current_pull_records, is_pull=True)

    previous_states = [previous_issue_source.get("query_state")]
    current_states = [current_issue_source.get("query_state")]
    if previous_pull_source is not None and current_pull_source is not None:
        previous_states.append(previous_pull_source.get("query_state"))
        current_states.append(current_pull_source.get("query_state"))
    full_state = all(state == "all" for state in previous_states + current_states)
    coverage = "full_state_snapshots" if full_state else "filtered_or_unknown_query_coverage"

    def count(collection: list[dict[str, Any]], event: str) -> int:
        return sum(item["event"] == event for item in collection)

    return {
        "schema_version": 1,
        "repository": current_repo,
        "comparison": {
            "previous_issues_fetched_at": previous_issue_source.get("fetched_at"),
            "current_issues_fetched_at": current_issue_source.get("fetched_at"),
            "previous_pulls_fetched_at": previous_pull_source.get("fetched_at") if previous_pull_source else None,
            "current_pulls_fetched_at": current_pull_source.get("fetched_at") if current_pull_source else None,
            "previous_query_states": previous_states,
            "current_query_states": current_states,
            "coverage": coverage,
        },
        "summary": {
            "issue_records_changed": count(issue_changes, "record_changed"),
            "issue_records_appeared": count(issue_changes, "appeared_in_current_snapshot"),
            "issue_records_absent": count(issue_changes, "absent_from_current_snapshot"),
            "pull_request_records_changed": count(pull_changes, "record_changed"),
            "pull_request_records_appeared": count(pull_changes, "appeared_in_current_snapshot"),
            "pull_request_records_absent": count(pull_changes, "absent_from_current_snapshot"),
            "inferred_links_created": 0,
            "external_records_changed": 0,
        },
        "issues": issue_changes,
        "pull_requests": pull_changes,
        "policy": {
            "read_only": True,
            "issues_and_prs_linked_automatically": False,
            "absence_means_closed_or_deleted": False,
            "metadata_change_means_work_is_complete": False,
            "note": "A snapshot comparison highlights metadata differences only. Check current canonical records and acceptance evidence before changing task status.",
        },
    }


def render_snapshot_diff_markdown(diff: dict[str, Any]) -> str:
    comparison = diff["comparison"]
    summary = diff["summary"]
    lines = [
        f"# Snapshot comparison: {diff['repository']}",
        "",
        f"- Coverage: **{comparison['coverage']}**",
        f"- Previous source query state(s): {', '.join(str(item) for item in comparison['previous_query_states'])}",
        f"- Current source query state(s): {', '.join(str(item) for item in comparison['current_query_states'])}",
        f"- Changed issue records: {summary['issue_records_changed']}",
        f"- Issue records appearing in current snapshot: {summary['issue_records_appeared']}",
        f"- Issue records absent from current snapshot: {summary['issue_records_absent']}",
        f"- Changed pull-request records: {summary['pull_request_records_changed']}",
        f"- Pull-request records appearing in current snapshot: {summary['pull_request_records_appeared']}",
        f"- Pull-request records absent from current snapshot: {summary['pull_request_records_absent']}",
        "",
        "> Read-only comparison. Absence from a query does not mean closed, deleted, resolved, or complete. Similar titles never establish an issue/PR relationship.",
        "",
    ]

    for title, collection in (("Issues", diff["issues"]), ("Pull requests", diff["pull_requests"])):
        lines.extend([f"## {title}", ""])
        if not collection:
            lines.extend(["No metadata differences observed.", ""])
            continue
        for item in collection:
            record = item.get("current") or item.get("previous") or {}
            url = record.get("url")
            label = f"#{item['number']} — {record.get('title') or 'untitled record'}"
            if isinstance(url, str):
                label = f"[{label}]({url})"
            lines.extend([f"### {label}", "", f"- Event: `{item['event']}`"])
            if item["changed_fields"]:
                lines.append("- Changed fields: " + ", ".join(f"`{field}`" for field in item["changed_fields"]))
            lines.extend([f"- Interpretation: {item['interpretation']}", ""])
    lines.extend([
        "## Policy",
        "",
        "- No external records were changed.",
        "- No issue/PR relationships were inferred.",
        "- Verify canonical source state and completion criteria independently.",
        "",
    ])
    return "\n".join(lines)


def write_snapshot_diff(diff: dict[str, Any], destination: str | Path, *, format: str = "markdown") -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(diff, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_snapshot_diff_markdown(diff)
    else:
        raise ValueError("Snapshot diff format must be 'markdown' or 'json'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
