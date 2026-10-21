"""Read explicit GitHub timeline cross-references; never infer links from text."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_API_ROOT = "https://api.github.com/repos"
_USER_AGENT = "Project-Intelligence-Contribution-Engine"
_PAGE_SIZE = 100
_MAX_PAGES = 20


def _canonical_html_url(repository: str, record_type: str, number: int) -> str:
    segment = "pull" if record_type == "pull_request" else "issues"
    return f"https://github.com/{repository}/{segment}/{number}"


def _validate_targets(targets: list[dict[str, Any]], *, max_records: int) -> list[dict[str, Any]]:
    if not isinstance(targets, list):
        raise ValueError("Relationship targets must be a list")
    if not isinstance(max_records, int) or isinstance(max_records, bool) or not 1 <= max_records <= 500:
        raise ValueError("max_records must be between 1 and 500")
    if len(targets) > max_records:
        raise ValueError(
            f"Refusing to inspect {len(targets)} target records; limit is {max_records}. "
            "Raise --max-records explicitly to expand the audit."
        )

    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for record in targets:
        if not isinstance(record, dict):
            raise ValueError("Every relationship target must be an object")
        record_type = record.get("record_type")
        number = record.get("number")
        title = record.get("title", "")
        if record_type not in {"issue", "pull_request"}:
            raise ValueError("Target record_type must be 'issue' or 'pull_request'")
        if not isinstance(number, int) or isinstance(number, bool) or number < 1:
            raise ValueError("Target number must be a positive integer")
        if not isinstance(title, str):
            raise ValueError("Target title must be a string")
        key = (record_type, number)
        if key in seen:
            raise ValueError(f"Duplicate relationship target: {record_type} #{number}")
        seen.add(key)
        normalized.append({
            "record_type": record_type,
            "number": number,
            "title": title,
            "url": "",
        })
    return normalized


def _api_get_json(url: str, *, timeout: float) -> Any:
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": _USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            raise ValueError(f"GitHub timeline endpoint not found: {url}") from exc
        if exc.code == 403:
            raise ValueError("GitHub API denied the request or rate limit was reached; retry later") from exc
        raise ValueError(f"GitHub API returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise ValueError(f"Could not reach GitHub API: {exc.reason}") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("GitHub API returned invalid JSON") from exc
    except TimeoutError as exc:
        raise ValueError("GitHub API request timed out") from exc


def _event_repo_scope(source_issue: dict[str, Any], repository: str) -> tuple[str, str | None]:
    """Classify source-repository scope only from explicit repository metadata."""
    repository_url = source_issue.get("repository_url")
    expected_api_url = f"{_API_ROOT}/{repository}"
    if isinstance(repository_url, str) and repository_url.strip():
        if repository_url.rstrip("/").casefold() == expected_api_url.casefold():
            return "same_repository", repository_url
        return "external_repository", repository_url

    html_url = source_issue.get("html_url")
    if isinstance(html_url, str) and html_url.casefold().startswith(
        f"https://github.com/{repository}/".casefold()
    ):
        return "same_repository", None
    if isinstance(html_url, str) and html_url.startswith("https://"):
        return "external_or_unverified_repository", None
    return "unknown_repository", None


def _normalize_cross_reference(
    event: dict[str, Any],
    *,
    repository: str,
    target: dict[str, Any],
    timeline_url: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    source_container = event.get("source")
    source_issue = source_container.get("issue") if isinstance(source_container, dict) else None
    if not isinstance(source_issue, dict):
        return None, None

    source_number = source_issue.get("number")
    source_title = source_issue.get("title")
    source_url = source_issue.get("html_url")
    if (
        not isinstance(source_number, int) or isinstance(source_number, bool) or source_number < 1
        or not isinstance(source_title, str) or not isinstance(source_url, str)
        or not source_url.startswith("https://")
    ):
        return None, None

    scope, repository_url = _event_repo_scope(source_issue, repository)
    source_type = "pull_request" if isinstance(source_issue.get("pull_request"), dict) else "issue"
    source = {
        "record_type": source_type,
        "number": source_number,
        "title": source_title,
        "url": source_url,
        "repository_url": repository_url,
    }
    target_out = {
        "record_type": target["record_type"],
        "number": target["number"],
        "title": target["title"],
        "url": _canonical_html_url(repository, target["record_type"], target["number"]),
    }
    created_at = event.get("created_at")
    actor = event.get("actor")
    actor_login = actor.get("login") if isinstance(actor, dict) and isinstance(actor.get("login"), str) else None

    evidence = {
        "provider": "github",
        "kind": "timeline_cross_referenced_event",
        "event": "cross-referenced",
        "timeline_target_url": target_out["url"],
        "timeline_api_url": timeline_url,
        "created_at": created_at if isinstance(created_at, str) else None,
        "actor": actor_login,
        "scope": scope,
    }
    key_text = json.dumps({
        "repository": repository.casefold(),
        "source_type": source_type,
        "source_url": source_url,
        "target_type": target["record_type"],
        "target_number": target["number"],
        "created_at": evidence["created_at"],
        "actor": actor_login,
    }, sort_keys=True, separators=(",", ":"))
    relation = {
        "id": "ghref-" + hashlib.sha256(key_text.encode("utf-8")).hexdigest()[:16],
        "relationship_type": "explicit_cross_reference",
        "direction": "source_references_target",
        "source": source,
        "target": target_out,
        "evidence": evidence,
        "verification_state": "explicit_source_event_observed",
        "completion_state": "unknown_not_inferred",
        "interpretation_limit": (
            "GitHub recorded a cross-reference event. This does not prove that the source fixes, "
            "closes, resolves, or fully satisfies the target."
        ),
    }
    if scope == "same_repository":
        return relation, None

    external = {
        **relation,
        "classification": scope,
        "interpretation_limit": (
            "A cross-reference to a different or unverified repository is preserved as external context, "
            "not treated as an in-repository issue/PR relationship."
        ),
    }
    return None, external


def fetch_explicit_relationships(
    repository: str,
    targets: list[dict[str, Any]],
    *,
    timeout: float = 20.0,
    max_records: int = 50,
) -> dict[str, Any]:
    """Fetch timeline events for selected records and preserve actual cross-reference events.

    GitHub's event shape identifies source.issue as the record that referenced the target
    whose timeline was requested. Similar titles, body text, labels, or branch names never
    create a relationship.
    """
    if not isinstance(repository, str) or not _REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must be in OWNER/REPO form")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        raise ValueError("timeout must be positive")

    normalized_targets = _validate_targets(targets, max_records=max_records)
    relations: list[dict[str, Any]] = []
    external_references: list[dict[str, Any]] = []
    targets_scanned: list[dict[str, Any]] = []
    pages_fetched = 0

    for target in normalized_targets:
        target["url"] = _canonical_html_url(repository, target["record_type"], target["number"])
        target_events = 0
        for page_number in range(1, _MAX_PAGES + 1):
            timeline_url = (
                f"{_API_ROOT}/{repository}/issues/{target['number']}/timeline"
                f"?per_page={_PAGE_SIZE}&page={page_number}"
            )
            payload = _api_get_json(timeline_url, timeout=float(timeout))
            if not isinstance(payload, list):
                raise ValueError(
                    f"GitHub timeline response for {target['record_type']} #{target['number']} "
                    "did not contain an event list"
                )
            pages_fetched += 1
            for event in payload:
                if not isinstance(event, dict) or event.get("event") != "cross-referenced":
                    continue
                target_events += 1
                relation, external = _normalize_cross_reference(
                    event, repository=repository, target=target, timeline_url=timeline_url
                )
                if relation is not None:
                    relations.append(relation)
                if external is not None:
                    external_references.append(external)
            if len(payload) < _PAGE_SIZE:
                break
        else:
            raise ValueError(
                f"GitHub timeline pagination exceeded the {_MAX_PAGES}-page safety limit "
                f"for {target['record_type']} #{target['number']}"
            )
        targets_scanned.append({
            "record_type": target["record_type"],
            "number": target["number"],
            "title": target["title"],
            "url": target["url"],
            "cross_reference_events_observed": target_events,
        })

    relations.sort(key=lambda item: (
        item["source"]["record_type"], item["source"]["number"],
        item["target"]["record_type"], item["target"]["number"],
        item["evidence"]["created_at"] or "",
    ))
    external_references.sort(key=lambda item: (
        item["source"]["url"], item["target"]["url"], item["evidence"]["created_at"] or ""
    ))

    def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in items:
            if item["id"] not in seen:
                seen.add(item["id"])
                result.append(item)
        return result

    relations = dedupe(relations)
    external_references = dedupe(external_references)
    return {
        "schema_version": 1,
        "repository": repository,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "targets_scanned": targets_scanned,
        "summary": {
            "targets_scanned": len(targets_scanned),
            "timeline_pages_fetched": pages_fetched,
            "explicit_in_repository_relations": len(relations),
            "external_or_unverified_references": len(external_references),
            "title_similarity_links_created": 0,
            "inferred_relations_created": 0,
            "external_records_changed": 0,
        },
        "relationships": relations,
        "external_references": external_references,
        "policy": {
            "read_only": True,
            "evidence_source": "GitHub issue timeline cross-referenced events",
            "title_similarity_creates_relation": False,
            "missing_event_means_no_relationship": False,
            "relationship_means_completed_work": False,
            "note": (
                "Only selected target timelines were scanned. Missing events do not prove no relationship "
                "exists; external references are kept separate. A cross-reference is not evidence that a PR "
                "solves or closes an issue."
            ),
        },
    }


def render_relationships_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        f"# Explicit GitHub relationship audit: {report['repository']}",
        "",
        f"- Audit generated: {report['fetched_at']}",
        f"- Target timelines scanned: {summary['targets_scanned']}",
        f"- Timeline pages fetched: {summary['timeline_pages_fetched']}",
        f"- Explicit in-repository relationships: {summary['explicit_in_repository_relations']}",
        f"- External/unverified references: {summary['external_or_unverified_references']}",
        "- Title-similarity links created: 0",
        "- External records changed: 0",
        "",
        "> A recorded cross-reference proves only that GitHub observed a reference event. It does not prove that a PR fixes, closes, or fully satisfies an issue. This report is limited to the selected target timelines.",
        "",
        "## Input snapshot coverage",
        "",
    ]
    for source_snapshot in report.get("input_snapshots", []):
        lines.append(
            f"- Repository: {source_snapshot.get('repository')}; query state: "
            f"{source_snapshot.get('query_state') or 'unknown'}; fetched at: "
            f"{source_snapshot.get('fetched_at') or 'unknown'}; records: "
            f"{source_snapshot.get('record_count', 'unknown')}"
        )
    if not report.get("input_snapshots"):
        lines.append("The caller did not attach snapshot provenance.")
    lines.extend(["", "## Explicit in-repository relationships", ""])
    if not report["relationships"]:
        lines.extend(["No explicit in-repository cross-reference events were found in the selected timelines.", ""])
    for relation in report["relationships"]:
        source, target, evidence = relation["source"], relation["target"], relation["evidence"]
        lines.extend([
            f"### [{source['record_type']} #{source['number']} — {source['title']}]({source['url']})",
            "",
            f"- References: [{target['record_type']} #{target['number']} — {target['title']}]({target['url']})",
            "- Evidence: GitHub timeline 'cross-referenced' event",
            f"- Event time: {evidence['created_at'] or 'unknown'}",
            f"- Actor: {evidence['actor'] or 'unknown'}",
            f"- Audit target: {evidence['timeline_target_url']}",
            f"- Limit: {relation['interpretation_limit']}",
            "",
        ])
    lines.extend(["## External or unverified references", ""])
    if not report["external_references"]:
        lines.extend(["None observed in the selected timelines.", ""])
    for relation in report["external_references"]:
        source, target, evidence = relation["source"], relation["target"], relation["evidence"]
        lines.extend([
            f"- [{source['title']}]({source['url']}) → [{target['title']}]({target['url']})",
            f"  - Classification: '{relation['classification']}'; event time: {evidence['created_at'] or 'unknown'}",
        ])
    lines.extend([
        "",
        "## Coverage and policy",
        "",
        "- Only timelines belonging to the supplied issue/PR snapshots were scanned.",
        "- The absence of a timeline event is not evidence that no relationship exists.",
        "- Similar titles, shared labels, or shared branch names do not create relationships.",
        "- A cross-reference is not a completion/closure signal; inspect the canonical records and acceptance evidence separately.",
        "- No source record was changed.",
        "",
    ])
    return "\n".join(lines)


def write_relationship_report(
    report: dict[str, Any],
    destination: str | Path,
    *,
    format: str = "markdown",
) -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_relationships_markdown(report)
    else:
        raise ValueError("Relationship report format must be 'markdown' or 'json'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
