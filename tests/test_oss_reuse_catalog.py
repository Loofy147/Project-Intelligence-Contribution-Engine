from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "docs" / "oss-reuse-catalog.json"
ALLOWED_LICENSES = {"MIT", "Apache-2.0"}
ALLOWED_ADOPTION_STATES = {
    "selected-runtime", "patterns-only", "archived-reference", "hold"
}


def test_reuse_catalog_has_unique_ids_and_a_reproducible_research_date() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    assert catalog["schema_version"] == 1
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", catalog["research_date"])
    components = catalog["components"]
    assert len(components) >= 8
    ids = [component["id"] for component in components]
    assert len(ids) == len(set(ids))


def test_every_component_has_license_scope_decision_and_evidence() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    for component in catalog["components"]:
        assert component["repository_url"].startswith("https://github.com/")
        assert component["license"]
        assert component["license_status"]
        assert component["adoption_status"] in ALLOWED_ADOPTION_STATES
        assert component["reuse_mode"]
        assert component["patterns"]
        assert component["rationale"]
        assert component["evidence_urls"]


def test_only_verified_permissive_components_can_be_runtime_selected() -> None:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    selected = [item for item in catalog["components"] if item["adoption_status"] == "selected-runtime"]
    assert selected
    for component in selected:
        assert component["license"] in ALLOWED_LICENSES
        assert component["license_status"] == "verified-permissive"
    litellm = next(item for item in catalog["components"] if item["id"] == "litellm")
    assert litellm["adoption_status"] == "hold"
    assert litellm["license_status"] == "scoped-license-hold"
