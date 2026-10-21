# Work Item Template

Use this template when a genuinely new work item must be proposed. If an existing issue, pull request, or repository-native registry item already represents the task, update or work against that canonical record instead of duplicating it.

## Title

Use an action plus the behavior/outcome, for example: `Measure task-draft false positives against a labelled benchmark`.

## Problem and evidence

- **Observed behavior/problem:**
- **Evidence:** exact file/function/line, reproducible input/output, failing test, external source record, or workflow URL.
- **What is not yet known:** label assumptions explicitly. Do not state that a capability is absent just because a heuristic did not detect it.

## Expected result

Describe the externally observable behavior or measurable result after the change.

## Acceptance criteria

- [ ] Criterion 1: measurable and independently verifiable.
- [ ] Criterion 2:
- [ ] Failure/edge case:
- [ ] Documentation or schema update, when applicable:

Criteria should describe outcomes, not vague activity such as “improve quality” or “make robust.”

## Scope

**Expected files/modules:**
- `path/to/file` — intended change.

**Explicitly out of scope:**
- Features, services, broad refactors, external writes, or follow-up tasks excluded from this work.

## Dependencies, assumptions, and constraints

- **Roadmap gate(s):** [stable gate IDs; verify dependencies are PASSED]
- **Assumption IDs:** [register IDs; include only relevant assumptions]
- **Decision scenario:** [the named outcome that makes this task applicable]
- **Owner:** [named accountable owner]
- **Falsification method:** [reproducible evidence that would disprove the task's key assumption]



- **Dependencies:** canonical issue/task IDs; use source links.
- **Security/privacy:** secrets, source content, network, authorization, or external side effects involved.
- **Compatibility:** schemas, stable IDs, persisted formats, Python version or CLI interface.
- **License/provenance:** any third-party code or assets to be introduced.

## Validation plan

| Acceptance criterion | Test/check | Required evidence |
|---|---|---|
| Criterion 1 | Exact automated or manual check | Test name, command output, CI link, or sample artifact |
| Criterion 2 | Exact automated or manual check | Test name, command output, CI link, or sample artifact |

## Completion record

- **Implemented:**
- **Files changed:**
- **Commands run and results:**
- **CI evidence:**
- **Known limitations / not run:**
- **Remaining work:**
- **Source-of-truth status:** identify the canonical item; do not mark it accepted/closed merely because implementation code exists.
