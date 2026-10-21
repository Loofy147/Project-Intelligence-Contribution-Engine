from __future__ import annotations

import json
from pathlib import Path

import pytest

from project_intelligence.indexer import build_index, load_index
from project_intelligence.search import search_index


def test_scans_text_and_skips_common_sensitive_and_generated_paths(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "Project repository inventory and contribution tasks.", encoding="utf-8"
    )
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "auth.py").write_text(
        "Validate the OAuth callback and verify the state value.", encoding="utf-8"
    )
    (tmp_path / ".env").write_text("API_TOKEN=must-not-be-indexed", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "vendor.py").write_text(
        "unrelated vendored content", encoding="utf-8"
    )
    (tmp_path / "private.key").write_text("private-key-material", encoding="utf-8")

    index = build_index(tmp_path)
    paths = {document["path"] for document in index["documents"]}

    assert paths == {"README.md", "src/auth.py"}
    assert "API_TOKEN=must-not-be-indexed" not in json.dumps(index)
    assert index["files_indexed"] == 2
    assert index["files_skipped"] >= 3


def test_search_returns_ranked_results_with_path_and_snippet(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs" / "oauth-callback.md").write_text(
        "OAuth callback validation requires checking the state parameter.",
        encoding="utf-8",
    )
    (tmp_path / "src" / "auth.py").write_text(
        "The authentication module validates OAuth state.", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text(
        "A small project inventory and search tool.", encoding="utf-8"
    )

    index = build_index(tmp_path)
    results = search_index(index, "OAuth callback")

    assert results
    assert results[0]["path"] == "docs/oauth-callback.md"
    assert "OAuth callback" in results[0]["snippet"]
    assert all(result["score"] > 0 for result in results)


def test_index_round_trip(tmp_path: Path) -> None:
    (tmp_path / "guide.md").write_text("Evidence before recommendations.", encoding="utf-8")
    output = tmp_path / ".project-intelligence" / "index.json"

    built = build_index(tmp_path, output_path=output)
    loaded = load_index(output)

    assert built["schema_version"] == loaded["schema_version"] == 1
    assert [item["path"] for item in loaded["documents"]] == ["guide.md"]


def test_search_validates_query_and_limit() -> None:
    with pytest.raises(ValueError):
        search_index({"documents": []}, " !!! ")
    with pytest.raises(ValueError):
        search_index({"documents": []}, "search", limit=0)
