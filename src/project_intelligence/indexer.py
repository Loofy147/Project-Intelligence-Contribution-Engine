"""Safe, local-only repository text indexing."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INDEX_SCHEMA_VERSION = 1
DEFAULT_MAX_FILE_BYTES = 500_000

EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "node_modules",
        "vendor",
        "dist",
        "build",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".next",
        ".nuxt",
        "coverage",
        ".project-intelligence",
    }
)

SENSITIVE_DIRS = frozenset({".ssh", ".aws", ".gnupg", "credential-store"})
SENSITIVE_NAMES = frozenset(
    {
        ".netrc",
        ".npmrc",
        ".pypirc",
        ".git-credentials",
        "id_rsa",
        "id_ed25519",
        "credentials",
        "credentials.json",
        "secrets.json",
        "service-account.json",
    }
)
SENSITIVE_SUFFIXES = frozenset(
    {".pem", ".key", ".p12", ".pfx", ".keystore", ".jks"}
)


def _is_sensitive_path(relative_path: Path) -> bool:
    parts = [part.lower() for part in relative_path.parts]
    name = parts[-1] if parts else ""

    if any(part in SENSITIVE_DIRS for part in parts[:-1]):
        return True
    if name in SENSITIVE_NAMES or name.startswith(".env"):
        return True
    if Path(name).suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    if any(marker in name for marker in ("secret", "credential", "private-key")):
        return True
    return False


def _excluded_by_directory(relative_path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in relative_path.parts)


def scan_documents(
    root: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    exclude_paths: set[Path] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Return readable text documents and a count of skipped files.

    Paths stored in the index are relative to root. Symlinks, likely secret files,
    binary files, oversized files, and generated directories are skipped.
    """
    root_path = Path(root).expanduser().resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"Project root is not a directory: {root_path}")
    if max_file_bytes <= 0:
        raise ValueError("max_file_bytes must be a positive integer")

    excluded_resolved = {p.expanduser().resolve() for p in (exclude_paths or set())}
    documents: list[dict[str, Any]] = []
    skipped = 0

    for candidate in sorted(root_path.rglob("*")):
        try:
            relative = candidate.relative_to(root_path)
        except ValueError:
            skipped += 1
            continue

        if _excluded_by_directory(relative):
            if candidate.is_dir() and not candidate.is_symlink():
                # rglob may still yield children, each is filtered by relative parts.
                continue
            skipped += 1
            continue

        if candidate.is_dir():
            continue
        if candidate.is_symlink():
            skipped += 1
            continue
        if not candidate.is_file():
            continue
        if _is_sensitive_path(relative):
            skipped += 1
            continue
        if candidate.resolve() in excluded_resolved:
            skipped += 1
            continue

        try:
            size = candidate.stat().st_size
            if size > max_file_bytes:
                skipped += 1
                continue
            raw = candidate.read_bytes()
        except OSError:
            skipped += 1
            continue

        if b"\x00" in raw:
            skipped += 1
            continue

        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            skipped += 1
            continue

        relative_posix = relative.as_posix()
        documents.append(
            {
                "path": relative_posix,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "content": content,
            }
        )

    documents.sort(key=lambda document: document["path"])
    return documents, skipped


def build_index(
    root: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build and optionally persist a versioned JSON index."""
    root_path = Path(root).expanduser().resolve()
    output = Path(output_path).expanduser().resolve() if output_path is not None else None
    excluded = {output} if output is not None else set()
    documents, skipped = scan_documents(
        root_path,
        max_file_bytes=max_file_bytes,
        exclude_paths=excluded,
    )

    index: dict[str, Any] = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "root": str(root_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files_indexed": len(documents),
        "files_skipped": skipped,
        "documents": documents,
    }
    if output is not None:
        write_index(index, output)
    return index


def write_index(index: dict[str, Any], destination: str | Path) -> Path:
    """Persist an index as UTF-8 JSON."""
    path = Path(destination).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def load_index(source: str | Path) -> dict[str, Any]:
    """Load an index and reject incompatible or malformed top-level data."""
    path = Path(source).expanduser()
    with path.open("r", encoding="utf-8") as handle:
        index = json.load(handle)

    if not isinstance(index, dict):
        raise ValueError("Index must contain a JSON object")
    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported index schema version: {index.get('schema_version')!r}"
        )
    if not isinstance(index.get("documents"), list):
        raise ValueError("Index is missing a documents list")
    for item in index["documents"]:
        if not isinstance(item, dict) or not isinstance(item.get("content"), str):
            raise ValueError("Index contains a malformed document record")
    return index
