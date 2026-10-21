from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = ROOT / "docs" / "ASSUMPTIONS-REGISTER.md"
ROADMAP_PATH = ROOT / "docs" / "ROADMAP.md"

_VALID_ASSUMPTION_STATES = {"OPEN", "SUPPORTED", "FALSIFIED", "INCONCLUSIVE", "DEFERRED"}
_VALID_GATE_STATES = {"PASSED", "READY", "IN_PROGRESS", "BLOCKED", "FAILED", "DEFERRED"}


def _field(block: str, name: str) -> str | None:
    # Parse one Markdown bullet at a time so an empty value cannot borrow the next line.
    prefix = f"- **{name}:**"
    for line in block.splitlines():
        if line.startswith(prefix):
            value = line[len(prefix):].strip()
            return value or None
    return None

def validate_assumptions_register(text: str) -> list[str]:
    errors: list[str] = []
    headings = list(re.finditer(r"^### (A-\d{3}) — .+$", text, re.MULTILINE))
    if not headings:
        return ["No assumption entries found"]

    ids = [match.group(1) for match in headings]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    errors.extend(f"Duplicate assumption ID: {item}" for item in duplicates)

    for index, match in enumerate(headings):
        item_id = match.group(1)
        end = headings[index + 1].start() if index + 1 < len(headings) else text.find("## Resolved design constraints", match.end())
        if end < match.end():
            end = len(text)
        block = text[match.start():end]
        state = _field(block, "Status")
        if state not in _VALID_ASSUMPTION_STATES:
            errors.append(f"{item_id}: invalid or missing status")
            continue
        if not _field(block, "Owner"):
            errors.append(f"{item_id}: missing owner")
        if state == "OPEN":
            field_aliases = (
                ("Falsification method", ("Falsification method", "Falsification / decision method")),
                ("Evidence required", ("Evidence required",)),
                ("Scenario selection", ("Scenario selection",)),
            )
            for display_name, aliases in field_aliases:
                if display_name == "Scenario selection":
                    has_heading = any(
                        line.strip() == "- **Scenario selection:**"
                        for line in block.splitlines()
                    )
                    if not has_heading:
                        errors.append(f"{item_id}: OPEN item missing {display_name}")
                elif not any(_field(block, alias) for alias in aliases):
                    errors.append(f"{item_id}: OPEN item missing {display_name}")
            scenario_start = block.find("**Scenario selection:**")
            scenario_text = block[scenario_start:] if scenario_start >= 0 else ""
            if "→" not in scenario_text or not re.search(r"[A-Z][A-Z0-9_]{2,}", scenario_text):
                errors.append(f"{item_id}: OPEN item has no named scenario outcome")
        else:
            if not _field(block, "Evidence recorded"):
                errors.append(f"{item_id}: non-OPEN item missing recorded evidence")
            if not _field(block, "Scenario selected"):
                errors.append(f"{item_id}: non-OPEN item missing selected scenario")
    return errors


def validate_roadmap(text: str, assumption_ids: set[str]) -> list[str]:
    errors: list[str] = []
    headings = list(re.finditer(r"^### (GATE-[0-9]{2}) — .+$", text, re.MULTILINE))
    if not headings:
        return ["No roadmap gates found"]

    gate_ids = [match.group(1) for match in headings]
    gate_set = set(gate_ids)
    if len(gate_set) != len(gate_ids):
        errors.append("Duplicate gate ID")

    blocks: dict[str, str] = {}
    for index, match in enumerate(headings):
        if index + 1 < len(headings):
            block_end = headings[index + 1].start()
        else:
            block_end = text.find("## Capability baseline", match.end())
            if block_end < match.end():
                block_end = text.find("## Release gate", match.end())
            if block_end < match.end():
                block_end = len(text)
        blocks[match.group(1)] = text[match.start():block_end]

    gate_states = {gate_id: _field(block, "State") for gate_id, block in blocks.items()}
    graph_start = text.find("## Dependency graph")
    graph_end = text.find("## Gate register", graph_start + 1) if graph_start >= 0 else -1
    if graph_start >= 0 and graph_end > graph_start:
        graph_ids = set(re.findall(r"GATE-[0-9]{2}", text[graph_start:graph_end]))
        errors.extend(f"Dependency graph references undeclared gate {item}" for item in sorted(graph_ids - gate_set))

    for gate_id, block in blocks.items():
        state = gate_states[gate_id]
        if state not in _VALID_GATE_STATES:
            errors.append(f"{gate_id}: invalid or missing state")
        if not _field(block, "Owner"):
            errors.append(f"{gate_id}: missing owner")
        dependencies = _field(block, "Dependencies")
        if dependencies is None:
            errors.append(f"{gate_id}: missing dependency declaration")
        else:
            referenced_gates = set(re.findall(r"GATE-[0-9]{2}", dependencies))
            if gate_id in referenced_gates:
                errors.append(f"{gate_id}: gate cannot depend on itself")
            errors.extend(
                f"{gate_id}: dependency {dependency} is undeclared"
                for dependency in sorted(referenced_gates - gate_set)
            )
            if state == "READY":
                # A semicolon separates optional/conditional dependencies from mandatory ones.
                mandatory_text = dependencies.split(";", 1)[0]
                mandatory_gates = set(re.findall(r"GATE-[0-9]{2}", mandatory_text))
                for dependency in sorted(mandatory_gates):
                    if dependency in gate_set and gate_states.get(dependency) != "PASSED":
                        errors.append(f"{gate_id}: READY gate dependency {dependency} is not PASSED")
        referenced_assumptions = set(re.findall(r"A-[0-9]{3}", block))
        errors.extend(
            f"{gate_id}: assumption {assumption} is undeclared"
            for assumption in sorted(referenced_assumptions - assumption_ids)
        )

    referenced_assumptions = set(re.findall(r"A-[0-9]{3}", text))
    errors.extend(
        f"Roadmap references undeclared assumption {assumption}"
        for assumption in sorted(referenced_assumptions - assumption_ids)
    )
    return errors

def test_committed_assumptions_register_satisfies_contract() -> None:
    register = REGISTER_PATH.read_text(encoding="utf-8")
    errors = validate_assumptions_register(register)
    assert errors == [], "\n".join(errors)


def test_committed_roadmap_has_valid_gate_states_and_references() -> None:
    register = REGISTER_PATH.read_text(encoding="utf-8")
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    assumptions = set(re.findall(r"^### (A-\d{3}) — .+$", register, re.MULTILINE))
    errors = validate_roadmap(roadmap, assumptions)
    assert errors == [], "\n".join(errors)


def test_ready_gate_requires_mandatory_dependencies_to_be_passed() -> None:
    roadmap = """# Roadmap

## Dependency graph
GATE-00
GATE-01

## Gate register

### GATE-00 — Baseline

- **State:** BLOCKED
- **Owner:** Maintainer
- **Dependencies:** None

### GATE-01 — Dependent capability

- **State:** READY
- **Owner:** Maintainer
- **Dependencies:** GATE-00
"""
    errors = validate_roadmap(roadmap, set())
    assert any("READY gate dependency GATE-00 is not PASSED" in item for item in errors)


def test_open_assumption_without_owner_or_falsification_fails_contract() -> None:
    bad_register = """# Assumptions Register

### A-900 — Broken assumption

- **Status:** OPEN
- **Owner:**
- **Question/claim:** Something may be true.
- **Evidence required:**
- **Scenario selection:**
"""
    errors = validate_assumptions_register(bad_register)
    assert any("missing owner" in item for item in errors)
    assert any("Falsification method" in item for item in errors)
    assert any("Evidence required" in item for item in errors)
    assert any("scenario outcome" in item for item in errors)


def test_roadmap_rejects_self_and_undeclared_dependencies() -> None:
    bad_roadmap = """# Roadmap

## Dependency graph
GATE-99

## Gate register

### GATE-00 — Broken gate

- **State:** READY
- **Owner:** Maintainer
- **Dependencies:** GATE-00 and GATE-99
"""
    errors = validate_roadmap(bad_roadmap, set())
    assert any("cannot depend on itself" in item for item in errors)
    assert any("dependency GATE-99 is undeclared" in item for item in errors)
    assert any("references undeclared gate GATE-99" in item for item in errors)
