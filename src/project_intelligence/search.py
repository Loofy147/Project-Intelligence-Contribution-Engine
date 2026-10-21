"""Ranked keyword search over a local project index."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """Split text into lowercase alphanumeric terms."""
    return [match.lower() for match in TOKEN_RE.findall(text)]


def _snippet(content: str, terms: list[str], width: int = 180) -> str:
    """Create a compact single-line excerpt near the first query-term match."""
    normalized = " ".join(content.split())
    lower = normalized.lower()
    positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    if not positions:
        return normalized[:width] + ("…" if len(normalized) > width else "")

    position = min(positions)
    start = max(0, position - width // 3)
    end = min(len(normalized), start + width)
    excerpt = normalized[start:end]
    if start > 0:
        excerpt = "…" + excerpt
    if end < len(normalized):
        excerpt += "…"
    return excerpt


def search_index(
    index: dict[str, Any],
    query: str,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search documents with an explainable TF-IDF-style ranking."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    query_terms = tokenize(query)
    if not query_terms:
        raise ValueError("query must contain at least one letter or number")

    documents = index.get("documents", [])
    if not isinstance(documents, list):
        raise ValueError("index documents must be a list")

    query_counts = Counter(query_terms)
    term_documents: list[tuple[dict[str, Any], list[str], str]] = []
    document_frequency: Counter[str] = Counter()

    for document in documents:
        if not isinstance(document, dict):
            continue
        content = document.get("content")
        path = document.get("path")
        if not isinstance(content, str) or not isinstance(path, str):
            continue
        terms = tokenize(content)
        term_documents.append((document, terms, path))
        document_frequency.update(set(terms))

    total_documents = len(term_documents)
    scored: list[dict[str, Any]] = []

    for document, terms, path in term_documents:
        frequencies = Counter(terms)
        score = 0.0
        for term, query_frequency in query_counts.items():
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            df = document_frequency[term]
            inverse_frequency = math.log(
                1.0 + (total_documents - df + 0.5) / (df + 0.5)
            )
            term_frequency = 1.0 + math.log(frequency)
            query_weight = 1.0 + math.log(query_frequency)
            score += term_frequency * inverse_frequency * query_weight

        path_terms = set(tokenize(path))
        score += 0.75 * sum(1 for term in query_counts if term in path_terms)

        phrase = " ".join(query_terms)
        searchable_text = " ".join(document.get("content", "").lower().split())
        normalized_path = " ".join(path.lower().replace("_", " ").replace("-", " ").split())
        if len(query_terms) > 1 and phrase in searchable_text:
            score += 2.0
        if len(query_terms) > 1 and phrase in normalized_path:
            score += 1.0

        if score <= 0:
            continue

        scored.append(
            {
                "path": path,
                "score": round(score, 6),
                "sha256": document.get("sha256"),
                "snippet": _snippet(document.get("content", ""), list(query_counts)),
            }
        )

    scored.sort(key=lambda result: (-result["score"], result["path"]))
    return scored[:limit]
