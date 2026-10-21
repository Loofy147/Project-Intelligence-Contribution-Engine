"""Read-only snapshots of public GitHub pull requests."""
from __future__ import annotations

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


def fetch_github_pull_requests(
    repository: str, *, state: str = "open", timeout: float = 20.0,
    page_size: int = 100, max_pages: int = 100,
) -> dict[str, Any]:
    """Fetch public pull request metadata via GET only."""
    if not _REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must be in OWNER/REPO form")
    if state not in {"open", "closed", "all"}:
        raise ValueError("state must be one of: open, closed, all")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    if not 1 <= page_size <= 100:
        raise ValueError("page_size must be between 1 and 100")
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")

    items: list[dict[str, Any]] = []
    pages_fetched = 0
    for page_number in range(1, max_pages + 1):
        url = f"{_API_ROOT}/{repository}/pulls?state={state}&per_page={page_size}&page={page_number}"
        request = Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": _USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        }, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                raise ValueError(f"GitHub repository or pull-request endpoint not found: {repository}") from exc
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
            raise ValueError("GitHub API response did not contain a pull-request list")
        pages_fetched += 1
        for item in payload:
            if not isinstance(item, dict):
                continue
            number, title, pr_state = item.get("number"), item.get("title"), item.get("state")
            if not isinstance(number, int) or number < 1 or not isinstance(title, str) or not title.strip():
                continue
            if pr_state not in {"open", "closed"}:
                continue
            canonical_url = f"https://github.com/{repository}/pull/{number}"
            head = item.get("head") if isinstance(item.get("head"), dict) else {}
            base = item.get("base") if isinstance(item.get("base"), dict) else {}
            labels = [
                label["name"] for label in item.get("labels", [])
                if isinstance(label, dict) and isinstance(label.get("name"), str)
            ]
            items.append({
                "number": number,
                "title": title.strip(),
                "state": pr_state,
                "url": canonical_url,
                "draft": bool(item.get("draft", False)),
                "head_ref": head.get("ref") if isinstance(head.get("ref"), str) else None,
                "head_sha": head.get("sha") if isinstance(head.get("sha"), str) else None,
                "base_ref": base.get("ref") if isinstance(base.get("ref"), str) else None,
                "labels": sorted(set(labels), key=str.casefold),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "source": "github_pull_request",
            })
        if len(payload) < page_size:
            break
    else:
        raise ValueError(f"GitHub pull-request pagination exceeded the configured {max_pages}-page safety limit")

    items.sort(key=lambda item: (item["number"], item["title"].casefold()))
    return {
        "schema_version": 1,
        "source": {
            "provider": "github", "repository": repository,
            "endpoint": f"{_API_ROOT}/{repository}/pulls",
            "query_state": state, "fetched_at": datetime.now(timezone.utc).isoformat(),
            "pages_fetched": pages_fetched, "read_only": True,
        },
        "summary": {
            "pull_requests_found": len(items),
            "open": sum(item["state"] == "open" for item in items),
            "closed": sum(item["state"] == "closed" for item in items),
            "drafts": sum(item["draft"] for item in items),
        },
        "pull_requests": items,
        "policy": {
            "source_of_truth": "GitHub pull request",
            "merge_or_write": False,
            "note": "Read-only snapshot. An open PR is a proposal, not proof of a completed or safe implementation.",
        },
    }


def render_pull_requests_markdown(snapshot: dict[str, Any]) -> str:
    source, summary = snapshot["source"], snapshot["summary"]
    lines = [
        f"# GitHub pull requests: {source['repository']}", "",
        f"- Query state: {source['query_state']}",
        f"- Snapshot fetched: {source['fetched_at']}",
        f"- Pull requests found: {summary['pull_requests_found']}",
        f"- Open: {summary['open']}", f"- Drafts: {summary['drafts']}", "",
        "> Read-only snapshot. Pull requests are proposals, not proof of a completed or safe implementation.", "",
    ]
    if not snapshot["pull_requests"]:
        lines.extend(["No pull requests found for the selected state.", ""])
    for item in snapshot["pull_requests"]:
        labels = ", ".join(item["labels"]) if item["labels"] else "unlabeled"
        draft = "draft" if item["draft"] else "not draft"
        lines.extend([
            f"## #{item['number']} — {item['title']}", "",
            f"- State: **{item['state']}** ({draft})",
            f"- Branch: {item['head_ref'] or 'unknown'} → {item['base_ref'] or 'unknown'}",
            f"- Labels: {labels}", f"- Updated: {item['updated_at'] or 'unknown'}",
            f"- Source: {item['url']}", "",
        ])
    return "\n".join(lines)


def write_pull_request_snapshot(snapshot: dict[str, Any], destination: str | Path, *, format: str = "json") -> Path:
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        content = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        content = render_pull_requests_markdown(snapshot)
    else:
        raise ValueError("Pull-request snapshot format must be 'json' or 'markdown'")
    path.write_text(content, encoding="utf-8", newline="\n")
    return path
