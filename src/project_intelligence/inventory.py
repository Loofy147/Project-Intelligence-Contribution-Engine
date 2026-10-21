"""Project inventory, lightweight detection, and Markdown reporting.

All detections are file-name/extension heuristics. They do not execute project
code and should be treated as inventory signals, not proof of completeness.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from typing import Any

MANIFEST_NAME = ".project-intelligence.json"
MANIFEST_SCHEMA_VERSION = 1

LANGUAGE_BY_SUFFIX = {
    ".py": "Python", ".pyi": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".mts": "TypeScript", ".cts": "TypeScript",
    ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".kts": "Kotlin", ".c": "C", ".h": "C/C++", ".cc": "C++",
    ".cpp": "C++", ".hpp": "C++", ".cs": "C#", ".fs": "F#",
    ".rb": "Ruby", ".php": "PHP", ".swift": "Swift", ".m": "Objective-C",
    ".mm": "Objective-C++", ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".ps1": "PowerShell", ".sql": "SQL", ".html": "HTML", ".htm": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".less": "Less",
}

ROOT_MARKERS = {
    "pyproject.toml": "Python project/build configuration",
    "setup.py": "Python packaging script",
    "requirements.txt": "Python dependency list",
    "package.json": "Node.js package manifest",
    "tsconfig.json": "TypeScript configuration",
    "Cargo.toml": "Rust package manifest",
    "go.mod": "Go module manifest",
    "pom.xml": "Maven project configuration",
    "build.gradle": "Gradle project configuration",
    "build.gradle.kts": "Gradle Kotlin DSL configuration",
    "Gemfile": "Ruby dependency manifest",
    "composer.json": "PHP Composer manifest",
    "mix.exs": "Elixir project configuration",
    "pubspec.yaml": "Dart/Flutter package manifest",
    "Makefile": "Make task definitions",
    "Dockerfile": "Container build definition",
    "pytest.ini": "Pytest configuration",
    "tox.ini": "Tox test environment configuration",
}

CI_MARKERS = {
    ".gitlab-ci.yml": "GitLab CI configuration",
    "azure-pipelines.yml": "Azure Pipelines configuration",
    "Jenkinsfile": "Jenkins pipeline definition",
}
ALLOWED_MANIFEST_FIELDS = {
    "schema_version", "id", "name", "description", "repository_url", "tags"
}


def _is_relative_path_match(path: str, patterns: tuple[str, ...]) -> bool:
    lowered = path.lower()
    return any(re.search(pattern, lowered) for pattern in patterns)


def _load_manifest(root: Path, manifest_path: str | Path | None) -> tuple[dict[str, Any], str | None]:
    if manifest_path is None:
        path = root / MANIFEST_NAME
    else:
        candidate = Path(manifest_path).expanduser()
        path = candidate if candidate.is_absolute() else root / candidate

    if not path.exists():
        name = root.name or "project"
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"
        identity_hash = hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:8]
        return {
            "id": f"local-{slug}-{identity_hash}",
            "name": name,
            "description": "",
            "repository_url": "",
            "tags": [],
        }, None

    if not path.is_file():
        raise ValueError(f"Project manifest is not a file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read project manifest {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Project manifest must be a JSON object")
    unknown = set(data) - ALLOWED_MANIFEST_FIELDS
    if unknown:
        raise ValueError("Unknown project manifest fields: " + ", ".join(sorted(unknown)))
    if data.get("schema_version", MANIFEST_SCHEMA_VERSION) != MANIFEST_SCHEMA_VERSION:
        raise ValueError("Unsupported project manifest schema version")

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Project manifest requires a non-empty 'name'")

    description = data.get("description", "")
    if not isinstance(description, str):
        raise ValueError("Project manifest 'description' must be a string")

    project_id = data.get("id")
    if project_id is None:
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "project"
        project_id = slug
    if not isinstance(project_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,119}", project_id):
        raise ValueError("Project manifest 'id' contains unsupported characters")

    repository_url = data.get("repository_url", "")
    if not isinstance(repository_url, str):
        raise ValueError("Project manifest 'repository_url' must be a string")
    if repository_url:
        parsed = urlparse(repository_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("Project manifest 'repository_url' must be an HTTPS URL")

    tags = data.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ValueError("Project manifest 'tags' must be a list of strings")

    return {
        "id": project_id,
        "name": name.strip(),
        "description": description.strip(),
        "repository_url": repository_url,
        "tags": [tag.strip() for tag in tags if tag.strip()],
    }, path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name


def build_inventory(
    root: str | Path,
    index: dict[str, Any],
    *,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a portable project inventory from an index and optional manifest."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise ValueError(f"Project root is not a directory: {root_path}")

    project, manifest_relative_path = _load_manifest(root_path, manifest_path)
    documents = index.get("documents", [])
    paths = sorted(
        document["path"]
        for document in documents
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    )
    sizes = {
        document["path"]: int(document.get("bytes", 0))
        for document in documents
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }
    digests = {
        document["path"]: document.get("sha256")
        for document in documents
        if isinstance(document, dict) and isinstance(document.get("path"), str)
    }

    language_files: dict[str, list[str]] = {}
    for path in paths:
        language = LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower())
        if language:
            language_files.setdefault(language, []).append(path)
    language_counts = Counter({name: len(items) for name, items in language_files.items()})
    languages = [
        {"name": name, "file_count": count, "paths": sorted(language_files[name])}
        for name, count in sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    markers = []
    for path in paths:
        pure = Path(path)
        basename = pure.name
        signal = ROOT_MARKERS.get(basename)
        if signal:
            markers.append({"path": path, "signal": signal, "classification": "observed"})
        if path.startswith(".github/workflows/") and pure.suffix.lower() in {".yml", ".yaml"}:
            markers.append({
                "path": path,
                "signal": "GitHub Actions workflow",
                "classification": "observed",
            })
        if basename in CI_MARKERS:
            markers.append({
                "path": path,
                "signal": CI_MARKERS[basename],
                "classification": "observed",
            })
    # Stable de-duplication in case a filename has more than one marker rule.
    unique_markers = {(item["path"], item["signal"]): item for item in markers}
    technology_signals = [
        unique_markers[key] for key in sorted(unique_markers)
    ]

    root_names = {Path(path).name.lower() for path in paths if "/" not in path}
    has_readme = any(name in {"readme", "readme.md", "readme.rst", "readme.txt"} for name in root_names)
    test_patterns = (
        r"(^|/)(tests?|specs?)/",
        r"(^|/)test_[^/]+\.py$",
        r"(^|/)[^/]+_test\.go$",
        r"(^|/)[^/]+\.(test|spec)\.[a-z0-9]+$",
    )
    test_paths = [
        path for path in paths
        if _is_relative_path_match(path, test_patterns)
    ]
    ci_paths = [
        item["path"] for item in technology_signals
        if "workflow" in item["signal"].lower()
        or "ci configuration" in item["signal"].lower()
        or "pipeline" in item["signal"].lower()
    ]

    review_signals = []
    if not has_readme:
        review_signals.append({
            "signal_id": "review-readme",
            "classification": "hypothesis",
            "title": "Review whether a top-level README is needed",
            "observed_fact": "No conventional top-level README filename was found in the indexed paths.",
            "hypothesis": "Project onboarding documentation may be missing, or it may use a nonstandard name/location.",
            "evidence": {"checked_paths": ["README", "README.md", "README.rst", "README.txt"]},
        })
    if not test_paths:
        review_signals.append({
            "signal_id": "review-tests",
            "classification": "hypothesis",
            "title": "Review test coverage and validation strategy",
            "observed_fact": f"No conventional test/spec path pattern was detected across {len(paths)} indexed files.",
            "hypothesis": "Automated tests may be missing, external, or named using a convention this inventory does not recognize.",
            "evidence": {
                "checked_patterns": [
                    "tests/ or test/ directories",
                    "specs/ or spec/ directories",
                    "test_*.py",
                    "*_test.go",
                    "*.test.* and *.spec.*",
                ],
            },
        })
    if not ci_paths:
        review_signals.append({
            "signal_id": "review-ci",
            "classification": "hypothesis",
            "title": "Review automated quality checks",
            "observed_fact": "No recognized CI workflow or pipeline configuration was found among indexed paths.",
            "hypothesis": "Automated checks may be configured externally or use a convention this inventory does not recognize.",
            "evidence": {
                "checked_patterns": [
                    ".github/workflows/*.yml",
                    ".github/workflows/*.yaml",
                    ".gitlab-ci.yml",
                    "azure-pipelines.yml",
                    "Jenkinsfile",
                ],
            },
        })

    git_marker = root_path / ".git"
    total_bytes = sum(sizes.values())
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": {
            **project,
            "manifest_path": manifest_relative_path,
            "root_label": root_path.name or "project",
            "git_repository_detected": git_marker.exists(),
        },
        "summary": {
            "files_indexed": len(paths),
            "files_skipped": int(index.get("files_skipped", 0)),
            "total_indexed_bytes": total_bytes,
            "language_count": len(languages),
            "test_files_detected": len(test_paths),
            "ci_files_detected": len(ci_paths),
        },
        "languages": languages,
        "technology_signals": technology_signals,
        "review_signals": review_signals,
        "files": [
            {"path": path, "bytes": sizes.get(path, 0), "sha256": digests.get(path)}
            for path in paths
        ],
    }


def render_inventory_markdown(inventory: dict[str, Any], *, max_files: int = 100) -> str:
    """Render the inventory without absolute machine paths or source contents."""
    project = inventory["project"]
    summary = inventory["summary"]
    lines = [
        f"# Project inventory: {project['name']}",
        "",
        f"- Project ID: `{project['id']}`",
        f"- Root label: `{project['root_label']}`",
        f"- Git repository detected: {'yes' if project['git_repository_detected'] else 'no'}",
        f"- Generated: {inventory['generated_at']}",
        f"- Indexed files: {summary['files_indexed']}",
        f"- Skipped files: {summary['files_skipped']}",
        f"- Approximate indexed text size: {summary['total_indexed_bytes']} bytes",
    ]
    if project.get("description"):
        lines.extend(["", project["description"]])
    if project.get("repository_url"):
        lines.extend(["", f"Repository: {project['repository_url']}"])
    if project.get("tags"):
        lines.extend(["", "Tags: " + ", ".join(f"`{tag}`" for tag in project["tags"])])

    lines.extend(["", "## Language inventory", ""])
    if inventory["languages"]:
        lines.extend(["| Language | Files |", "|---|---:|"])
        for item in inventory["languages"]:
            lines.append(f"| {item['name']} | {item['file_count']} |")
    else:
        lines.append("No recognized programming-language extensions were detected.")

    lines.extend(["", "## Technology and tooling signals", ""])
    if inventory["technology_signals"]:
        for item in inventory["technology_signals"]:
            lines.append(f"- **Observed:** `{item['path']}` — {item['signal']}")
    else:
        lines.append("No recognized project/tooling marker files were detected.")

    lines.extend(["", "## Review candidates (hypotheses)", ""])
    if inventory["review_signals"]:
        for item in inventory["review_signals"]:
            lines.append(f"### {item['title']}")
            lines.append(f"- **Observed fact:** {item['observed_fact']}")
            lines.append(f"- **Hypothesis:** {item['hypothesis']}")
    else:
        lines.append("No conventional inventory review signals were raised. This does not prove the project is complete.")

    lines.extend(["", "## Indexed file manifest", ""])
    files = inventory["files"]
    for item in files[:max_files]:
        lines.append(f"- `{item['path']}` ({item['bytes']} bytes; SHA-256: `{item['sha256']}`)")
    if len(files) > max_files:
        lines.append(f"- … and {len(files) - max_files} additional files omitted from this report.")
    lines.extend([
        "",
        "> This is a file-based inventory, not a semantic code audit. Detected markers are observations; review candidates are hypotheses that require human validation.",
        "",
    ])
    return "\n".join(lines)


def write_inventory(inventory: dict[str, Any], destination: str | Path, *, format: str = "markdown") -> Path:
    """Write an inventory report as Markdown or JSON."""
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if format == "json":
        text = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    elif format == "markdown":
        text = render_inventory_markdown(inventory)
    else:
        raise ValueError("Inventory format must be 'markdown' or 'json'")
    path.write_text(text, encoding="utf-8", newline="\n")
    return path
