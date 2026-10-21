"""Read-only snapshots of public GitHub issues.

Issue bodies are intentionally omitted: titles, labels, state, timestamps, and the
canonical source URL identify existing work without mirroring extra remote content.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
API_ROOT = "https://api.github.com/repos"
USER_AGENT = "Project-Intelligence-Contribution-Engine"


def fetch_github_issues(
    repository: str,
    *,
    state: str = "open",
    timeout: float = 20.0,
    page_size: int = 100,
    max_pages: int = 100,
) -> dict[str, Any]:
    """Fetch a paginated public issue snapshot with HTTP GET only."""
    if not REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must be in OWNER/REPO form")
    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be one of: open, closed, all")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if not 1 <= page_size <= 100:
        raise ValueError("page_size must be between 1 and 100")
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    issues: list[dict[str, Any]] = []
    pages_fetched = 0
    for page_number in range(1, max_pages + 1):
        url = (
            f"{API_ROOT}/{repository}/issues"
            f"?state={state}&per_page={page_size}&page={page_number}"
        )
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": USER_AGENT,
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method="GET",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                raise ValueError(f"GitHub repository or issues endpoint not found: {repository}") from exc
            if exc.code == 403:
                raise ValueError("GitHub API denied the request or rate limit was reached; retry later") from exc
            raise ValueError(f"GitHub API returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ValueError(f"Could not reach GitHub API: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("GitHub API returned invalid JSON") from exc
        except TimeoutError as exc:
            raise ValueError("GitHub API request timed out") from exc

        if not isinstance(payload, list):
            raise ValueError("GitHub API response did not contain an issue list")
        pages_fetched += 1

        for item in payload:
            if not isinstance(item, dict) or "pull_request" in item:
                continue
            number = item.get("number")
            title = item.get("title")
            issue_state = item.get("state")
            if (
                not isinstance(number, int)
                or number < 1
                or not isinstance(title, str)
                or not title.strip()
                or issue_state not in {"open", "closed"}
            ):
                continue

            canonical_url = f"https://github.com/{repository}/issues/{number}"
            html_url = item.get("html_url")
            if html_url != canonical_url:
                html_url = canonical_url
            labels = [
                label["name"]
                for label in item.get("labels", [])
                if isinstance(label, dict) and isinstance(label.get("name"), str)
            ]
            issues.append({
                "number": number,
                "title": title.strip(),
                "state": issue_state,
                "url": html_url,
                "labels": sorted(set(labels), key=str.casefold),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "source": "github_issue",
            })

        if len(payload) < page_size:
            break
    else:
        raise ValueError(
            f"GitHub issue pagination exceeded the configured {max_pages}-page safety limit"
        )

    issues.sort(key=lambda item: (item["number"], item["title"].casefold()))
    return {
        "schema_version": 1,
        "source": {
            "provider": "github",
            "repository": repository,
            "endpoint": f"{API_ROOT}/{repository}/issues",
            "query_state": state,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "pages_fetched": pages_fetched,
            "read_only": True,
        },
        "summary": {
            "issues_found": len(issues),
            "open": sum(item["state"] == "open" for item in issues),
            "closed": sum(item["state"] == "closed" for item in issues),
            "pull_requests_excluded": True,
        },
        "issues": issues,
        "policy": {
            "source_of_truth": "GitHub issue",
            "create_duplicate_tasks": False,
            "publish_or_write": False,
            "note": "Read-only snapshot. Keep the source issue URL as the canonical work record.",
        },
    }


def render_issues_markdown(snapshot: dict[str, Any]) -> str:
    """Render a compact source-linked issue index."""
    source = snapshot["source"]
    summary = snapshot["summary"]
    lines = [
        f"# GitHub issues: {source['repository']}",
        "",
        f"- Query state: {source['query_state']}",
        f"- Snapshot fetched: {source['fetched_at']}",
        f"- Issues found: {summary['issues_found']}",
        f"- Open: {summary['open']}",
        f"- Closed: {summary['closed']}",
        "",
        "> Read-only snapshot. The original GitHub issue is the canonical work record; do not create a duplicate by default.",
        "",
    ]
    if not snapshot["issues"]:
        lines.extend(["No issues found for the selected state.", ""])
    for issue in snapshot["issues"]:
        labels = ", ".join(issue["labels"]) if issue["labels"] else "unlabeled"
        lines.extend([
            f"## #{issue['number']} — {issue['title']}",
            "",
            f"- State: **{issue['state']}**",
            f"- Labels: {labels}",
            f"- Updated: {issue['updated_at'] or 'unknown'}",
            f"- Source: {issue['url']}",
            "",
        ])
    return "\n".join(lines)


def write_issue_snapshot(
    snapshot: dict[str, Any],
    destination: str | Path,
    *,
    format: str = "json",
) -> Path:
    """Write the issue snapshot as JSON or Markdown."""
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_issues_markdown(snapshot)
    else:
        raise ValueError("Issue snapshot format must be 'json' or 'markdown'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
