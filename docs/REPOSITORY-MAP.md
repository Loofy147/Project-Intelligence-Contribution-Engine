# Repository Map

This file is the quick navigation map. Read the linked source docs for full contracts before changing behavior.

## Root files and control points

| Path | Purpose | Read when |
|---|---|---|
| `AGENTS.md` | Mandatory rules for AI/coding agents | Before every task |
| `docs/OPERATING-CHARTER.md` | Cross-cutting professional responsibilities, research, evidence, integrations, authority and definition of done | Scoping any non-trivial task or reviewing quality |
| `docs/PORTFOLIO-CONTEXT.md` | Related system roles, canonical sources, portfolio alignment and cross-project authority boundaries | Work that crosses projects or integrations |
| `README.md` | Product boundary, installation, CLI examples | Starting work or changing a public workflow |
| `pyproject.toml` | Python version, package metadata, dev dependencies, `pie` entry point, pytest configuration | Changing packaging, runtime, commands, or tests |
| `CONTRIBUTING.md` | Contribution workflow | Preparing a code change |
| `LICENSE` | Repository license | Reusing or redistributing this repository |
| `.gitignore` | Excludes generated local indexes and development artifacts | Adding output/cache paths |

## Core package: `src/project_intelligence/`

| Module | Responsibility | First test(s) to inspect |
|---|---|---|
| `cli.py` | Command-line argument parsing and routing between operations | All tests for the command being changed; then `pie --help` |
| `indexer.py` | File discovery, exclusions, size/type limits, safe text indexing, file digests | `tests/test_engine.py` and indexing coverage in `tests/test_inventory_tasks.py` |
| `search.py` | Local ranked keyword search and snippets over the saved index | `tests/test_engine.py` |
| `inventory.py` | Project inventory and observed-vs-hypothesis signals | `tests/test_inventory_tasks.py` |
| `tasks.py` | Task draft construction, checklist/registry allowlists, evidence and freshness verification | `tests/test_inventory_tasks.py` |
| `github_issues.py` | Read-only public GitHub issue snapshot | `tests/test_github_issues.py` |
| `github_pulls.py` | Read-only public GitHub pull-request snapshot | `tests/test_github_pulls.py` |
| `workplan.py` | Read-only projection of issues, PRs, registry items and engine-generated drafts | `tests/test_workplan.py` |
| `snapshot_diff.py` | Compare previous/current issue and optional PR snapshots; report metadata changes without inference or writes | `tests/test_snapshot_diff.py` |
| `source_relations.py` | Read issue/PR timelines and preserve only explicit GitHub cross-reference events; separate external/unverified references | `tests/test_source_relations.py` |
| `ai_review.py` | Optional bounded metadata-only AI review, response validation, advisory report output | `tests/test_ai_review.py` |
| `__init__.py` | Package identity/version exports | Inspect import and packaging tests if changing it |

`tests/test_planning_contract.py` checks that every OPEN assumption retains an owner, falsification method, required evidence, and scenario outcomes, and that roadmap gate IDs/dependencies and assumption references remain structurally valid.

Test mappings are a starting point, not a guarantee that a behavior appears in only one file. Search for the function, data field, or CLI command across source and tests before editing.

## Documentation

| Path | Authority |
|---|---|
| `docs/ARCHITECTURE.md` | Current component responsibilities, data flow, trust boundaries, extension policy |
| `docs/ROADMAP.md` | Dependency graph of gates and scenario branches; no dates or linear milestone assumptions |
| `docs/PROJECT-MANIFEST.md` | `.project-intelligence.json` schema, checklist allowlist, typed registry mapping |
| `docs/AI-REVIEW-GATEWAY.md` | What data reaches the model gateway, limits, API contract, advisory-only semantics |
| `docs/REAL-PROJECT-EVALUATION.md` | Dated evaluation snapshots and work-source interpretation; historical run results may become stale |
| `docs/OSS-REUSE-RESEARCH.md` | Third-party project/license review and adoption decisions |
| `docs/oss-reuse-catalog.json` | Structured reuse catalog corresponding to the reuse research |
| `docs/EXECUTION-PLAYBOOK.md` | Deterministic workflow from gate selection to validation and handoff |
| `docs/ASSUMPTIONS-REGISTER.md` | Canonical OPEN assumptions, owner, falsification method, required evidence, and scenario outcomes |
| `docs/WORK-ITEM-TEMPLATE.md` | Standard structure for newly proposed work items |
| `docs/SESSION-HANDOFF-TEMPLATE.md` | Exact repository-state handoff for cross-session continuity |

## Optional integration: `integrations/omniroute-workbench/`

This is a separate local gateway around the upstream OmniRoute service; it is not a core dependency.

| Path | Purpose |
|---|---|
| `README.md` | Local setup, allowed routes, policy configuration, operational limits and test commands |
| `UPSTREAM.md` | Upstream version/license inspection notes; verify before claiming currentness |
| `compose.yaml` | Service configuration and host port binding |
| `Dockerfile` | Gateway image build |
| `config/` and application files | Runtime gateway policy and request handling; inspect the actual directory before making assumptions |
| `tests/` and package metadata | Fake-upstream tests and static/type checks; inspect actual files before running |

Keep the integration opt-in. Never expose it publicly or describe the in-memory rate limiter as a durable cost budget. For integration changes, follow its README and keep credentials out of tests and version control.

## CI workflows

- `.github/workflows/tests.yml`: core Python tests.
- `.github/workflows/evaluate-projects.yml`: checks out configured public project targets and uploads bounded evaluation artifacts. Verify its current target list and permissions before editing.
- `.github/workflows/omniroute-workbench.yml`: integration tests/checks. Verify its current triggers and working directory before editing.
- `.github/pull_request_template.md`: reviewer-facing acceptance and evidence checklist.

## Sources of truth and precedence

1. User's current explicit request.
2. Existing canonical issue/PR or a project's own registry record.
3. Code, tests and schema definitions for actual current behavior.
4. Architecture and feature contracts for intended behavior.
5. Roadmap for untracked work and sequencing.
6. Model suggestions and heuristic output as review-only hints.

If documentation conflicts with implementation, do not silently choose whichever is convenient. Confirm the observed discrepancy, check relevant tests and history if available, then fix the source of truth and update the affected docs in the same task.
