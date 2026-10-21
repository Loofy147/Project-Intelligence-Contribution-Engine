# Dependency-Gated Roadmap

This roadmap is a dependency graph, not a calendar. Gate IDs are stable references, **not an implied sequence or date**. There are no target dates or time estimates. Progress is driven by evidence, resolved assumptions, and dependencies.

The canonical unresolved-question record is the [Assumptions Register](ASSUMPTIONS-REGISTER.md). A gate must not invent an answer to an OPEN assumption. When a registered answer or experiment produces an outcome, select the corresponding scenario below and continue along that branch.

## How to use this roadmap

A gate is a testable capability or decision boundary. Each gate declares an owner, dependencies, entry conditions, exit evidence, and the outcomes that determine what happens next.

### Gate states

- `PASSED`: every exit criterion is backed by inspected evidence.
- `READY`: every dependency is PASSED and no required policy decision is OPEN.
- `IN_PROGRESS`: work is underway; the exit criteria are not yet proven.
- `BLOCKED`: a dependency, evidence gap, or required owner decision prevents execution.
- `FAILED`: a test of the gate did not meet its predeclared acceptance criteria; repair or a different scenario is required.
- `DEFERRED`: an explicit scope decision says not to pursue this gate now. It is not equivalent to PASSED.

### Execution and scenario rules

1. Recheck the actual repository, tests, source records, and current CI. A past green run is historical evidence, not proof about the current head.
2. A gate is READY only when all dependency gates are PASSED. An OPEN assumption blocks a gate only when that assumption is a required decision or input for the gate.
3. Among READY gates, choose in this order: (a) safety/data-integrity risks, (b) the gate that unblocks the most downstream gates, (c) the smallest end-to-end test that yields decisive evidence, then (d) the stable gate ID as a tie-breaker.
4. Freeze test labels, sampling rules, and acceptance thresholds before scoring a benchmark. Never move the threshold after viewing results to make a gate pass.
5. Resolve an assumption only by its registered falsification method and evidence. Record outcome, evidence reference, and owner decision in [the register](ASSUMPTIONS-REGISTER.md).
6. Mark a gate PASSED only after its exit criteria are checked individually. Source code existing, a generated report, a green unrelated workflow, or an AI recommendation is not sufficient.
7. If a gate fails, follow its declared branch. Do not continue down a branch that depends on a failed gate unless its dependency is explicitly revised with evidence.
8. Update this roadmap and the assumptions register in the same change when gate states, dependencies, outcomes, or underlying assumptions change.

## Dependency graph

```text
GATE-00 Current baseline (PASSED)
  ├── GATE-01 Heuristic task-candidate quality (BLOCKED by the policy target in A-001; evaluates A-002)
  │     ├── GATE-04 Human approval and closure protocol
  │     ├── GATE-05 Structured readiness parsing (also depends on GATE-02)
  │     └── GATE-06 AI review value experiment (evaluates A-004)
  ├── GATE-02 Source snapshot comparison and freshness (PASSED)
  │     └── GATE-03 Explicit issue/PR relationships (PASSED; evaluates A-005)
  ├── GATE-11 Keyword-search quality (BLOCKED by the policy target in A-003)
  ├── GATE-07 Private-repository scope decision (BLOCKED until target scope is explicit; evaluates A-006)
  └── GATE-08 Persistence decision (DEFERRED until a concrete requirement is demonstrated; monitors A-007)

GATE-03 + GATE-04 + applicable access decision
  └── GATE-09 ContribQuest read-only workflow integration
        └── GATE-10 External writes (DEFERRED; separate approval and safety gate)

GATE-01 and GATE-11 are separate evidence gates. GATE-06 runs the A-004 experiment only after GATE-01 passes.
GATE-08 is reopened only when a reproducible persistence requirement exists.
```

The graph is authoritative; the display above is a navigation aid. Where dependency statements in a gate disagree with this graphic, fix the disagreement before selecting work.

## Gate register

### GATE-00 — Establish a reproducible, read-only baseline

- **State:** PASSED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** None
- **Evidence already established:** Core test workflow passed on merged repository head [`82a1306`](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39656752392); OmniRoute Workbench workflow passed on the same head [`82a1306`](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39656752378). The repository has local indexing/search, inventory, evidence-backed task drafts, source-evidence freshness checks, public GitHub snapshots, typed registry projections, read-only work plans, and an optional metadata-only AI adapter.
- **Exit criteria:** Core behavior and its current trust boundaries are documented; tests and workflows exist; no target repository writes occur.
- **Limits:** These checks prove the engine's checked behavior only. They do not prove target application correctness, heuristic quality, model utility, or live deployment acceptance.

### GATE-01 — Measure heuristic and retrieval quality

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-00
- **Policy decision blocking execution:** [A-001](ASSUMPTIONS-REGISTER.md#a-001--minimum-quality-required-for-heuristic-task-recommendations).
- **Empirical assumption evaluated inside this gate:** [A-002](ASSUMPTIONS-REGISTER.md#a-002--benchmark-corpus-generalizes-beyond-the-current-smoke-test-projects).
- **Separate retrieval gate:** [A-003](ASSUMPTIONS-REGISTER.md#a-003--keyword-search-meets-a-useful-quality-bar-without-semantic-retrieval) is handled by GATE-11 and does not block the heuristic benchmark.
- **Purpose:** Distinguish reliable observed candidates from noisy inventory hypotheses; determine whether keyword ranking satisfies the intended discovery task before changing retrieval architecture.
- **Entry conditions:** Owner has frozen the heuristic precision acceptance target before scoring; benchmark labels and sampling rules are defined; benchmark fixtures cover positive and negative cases and source types.
- **Exit evidence:** Versioned benchmark corpus and label rules; reproducible command; machine-readable precision/recall and search metrics; per-repository/per-kind results; false-positive examples; held-out test; explicit decision.
- **Scenario branches:**
  - Target met and corpus coverage adequate → pass only for the measured envelope; add failed cases as regression fixtures.
  - Heuristic target missed → tune/disable affected heuristic categories; rerun the frozen benchmark.
  - Keyword quality missed → improve the current explainable ranker first; consider a new retrieval method only if the measured gap remains.
  - Threshold rejected, sample inadequate, or evidence inconclusive → remain BLOCKED; no promotion or architecture expansion.
- **Never infer:** No TODO marker does not prove no open work; an inventory hypothesis does not prove a missing capability.

### GATE-02 — Compare source snapshots and expose freshness changes

- **State:** PASSED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-00
- **Evidence:** Core test workflow, including CLI help and Python 3.11/3.12, passed on [commit `017556c5`](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39659054424); OmniRoute Workbench checks passed on the same commit ([workflow](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39659054383)). The CI-passing commit contains the complete comparator implementation and CLI integration; the later change that records this state is documentation-only.
- **Purpose:** Make source changes visible across consecutive GitHub issue/PR snapshots without pretending that absence from a filtered query means closure, deletion, or completion.
- **Implementation boundary:** Read-only comparison of same-repository, schema-valid snapshots. Preserve the canonical issue/PR IDs and URLs. Report observed changes such as state, title, labels, updated timestamp, and PR head SHA. When a filtered snapshot omits a prior record, say that it is absent from the query; do not label it closed. Report snapshot coverage.
- **Exit criteria:**
  - Reject mismatched repositories, invalid schema/collection, and incomplete input pairs.
  - Detect changes between matching canonical records.
  - Do not infer deletion, issue/PR linkage, or task completion from absence or similar titles.
  - Include unit tests for stable records, state changes, updated timestamps, PR head changes, and incomplete query coverage.
  - Expose a documented read-only CLI command and examples.
  - Core tests and CLI help pass; output clearly identifies what it does not prove.
- **Gate result:** All listed exit criteria passed on the cited CI head. Snapshot comparison is metadata-only; it does not determine issue/PR relationships or completion.
- **Next READY gate:** GATE-03 audits whether explicit, canonical relationship evidence is available.

### GATE-03 — Link issues and pull requests only with explicit evidence

- **State:** PASSED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-02
- **Assumption evaluated by this gate:** [A-005](ASSUMPTIONS-REGISTER.md#a-005--explicit-evidence-is-available-to-link-related-github-issues-and-pull-requests). It is a test objective, not a prerequisite for running the audit.
- **Purpose:** Correlate source records only where GitHub provides a canonical relationship or the maintainer records an explicit mapping.
- **Implementation:** `pie github-relations` reads only the timelines of records in supplied issue/PR snapshots and preserves explicit `cross-referenced` events. It separates sources from other repositories or without a verifiable repository identity.
- **Evidence:** Core tests and CLI-help check passed on code-complete commit [`1c5b0e37`](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39660428573); Workbench checks passed on the same commit [workflow](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39660428561). Live API spot-checks observed PR #27 as an explicit cross-reference on [issue #3 timeline](https://api.github.com/repos/Loofy147/Contribution-bounties-centre-/issues/3/timeline) and [issue #7 timeline](https://api.github.com/repos/Loofy147/Contribution-bounties-centre-/issues/7/timeline). An external bot reference was kept distinct on [issue #21 timeline](https://api.github.com/repos/Loofy147/Contribution-bounties-centre-/issues/21/timeline).
- **Exit criteria:** Relationship type, source/target IDs, URLs, event evidence, and verification state are preserved. Tests prove title similarity alone cannot create a link. A missing relation remains “unknown,” not “unrelated” or “resolved.” All met for the implemented GitHub timeline event type; this is not an exhaustive guarantee of all possible relationships across every repository.
- **Scenario selected:** `EXPLICIT_RELATIONS_AVAILABLE`, scope-limited to canonical GitHub timeline cross-reference events. Do not infer resolution, completion, or relation absence from missing events.

### GATE-04 — Define human approval, execution eligibility, and closure

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-01 and GATE-02
- **Purpose:** Make the difference between detected, reviewed, approved, in progress, blocked, completed, rejected, and stale work explicit. Canonical-source status must not be overwritten by a derived projection.
- **Exit criteria:** State transition contract, actor authority, evidence needed to approve/close, stale-evidence behavior, and retry/idempotency behavior are documented and tested. Missing criteria or stale source blocks approval/closure. Model output and freshness never approve work by themselves.
- **Downstream rule:** XP, bounty state, external publishing, and merge actions stay downstream of verified completion and separate authorization.

### GATE-05 — Interpret readiness/deferred decisions and project-specific evidence safely

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-01 and GATE-02
- **Assumption evaluated by this gate:** [A-008](ASSUMPTIONS-REGISTER.md#a-008--generic-structured-readiness-parsing-is-preferable-to-per-project-rules).
- **Purpose:** Extract readiness gates, dependencies, deferred decisions, and assumptions from documentation-heavy projects without treating every checkbox or prose statement as active work.
- **Exit criteria:** Small labelled corpus, source pointers, held-out evaluation, stale-evidence behavior, and explicit opt-in paths. Any parsed item remains review-required and linked to its source.
- **Scenario branches:** If stable patterns recur, add a narrow opt-in parser. If formats differ, prefer repository-native registries/adapters. If evidence is weak, keep manual review rather than building a universal crawler.

### GATE-06 — Prove or reject the incremental value of optional AI review

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-01
- **Assumption evaluated by this gate:** [A-004](ASSUMPTIONS-REGISTER.md#a-004--optional-ai-review-adds-enough-value-to-justify-its-maintenance-and-cost).
- **Purpose:** Compare model-assisted recommendations with the same tasks reviewed without AI.
- **Exit criteria:** Frozen model/configuration, blinded paired task set, human adjudication, quality/effort comparison, latency and observed cost where available, and an explicit owner decision.
- **Scenario branches:** If incremental value is proven, keep AI optional and separately design durable cost controls before making budget guarantees. If not proven, keep experimental or de-emphasize it. If inconclusive, do not add model dependencies or expand paid routing.

### GATE-07 — Decide whether private-repository access is actually required

- **State:** BLOCKED (scope decision required)
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-00
- **Assumption to resolve:** [A-006](ASSUMPTIONS-REGISTER.md#a-006--private-repository-support-is-required-for-the-intended-evaluation-scope).
- **Blocking input:** The owner must confirm the target-project scope against which “required” will be judged. The existence of a future possible private use case is not enough.
- **Purpose:** Avoid adding credential and privacy risks without a required use case.
- **Exit criteria:** Named required target, access need, sanitized fixture alternative, and owner decision.
- **Scenario branches:** If private access is required, design least privilege, key storage, revocation, redaction, and tests before implementation. If public/sanitized scope is sufficient, explicitly defer auth and keep public read-only behavior.

### GATE-08 — Decide whether local JSON persistence is insufficient

- **State:** DEFERRED until a concrete requirement is demonstrated
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-00
- **Assumption to monitor:** [A-007](ASSUMPTIONS-REGISTER.md#a-007--local-json-persistence-is-insufficient-for-a-demonstrated-requirement).
- **Purpose:** Preserve the local-first dependency-light core unless a concrete, reproducible requirement disproves the current approach.
- **Reopen condition:** A named use case reproduces a concurrency, multi-user, audit durability, cross-machine, size, or latency requirement that local files cannot safely satisfy.
- **Exit criteria:** Reproducible failure, explicit requirement, evaluation of a simpler file-based fix, and an architecture decision record.
- **Scenario branches:** If a real persistence gap is proven, design migration, backup, recovery, and data ownership before choosing storage. If no gap can be reproduced for the intended use case, retain local JSON. No database is added on speculation.

### GATE-09 — Integrate with ContribQuest as a read-only, source-linked workflow

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-03 and GATE-04; GATE-07 only if the required target becomes private
- **Purpose:** Map reviewed candidates to existing ContribQuest work without cloning issues, then carry evidence lineage, acceptance criteria, responsible actor, validation, and freshness through the workflow.
- **Exit criteria:** Source IDs preserved, candidate-to-canonical mapping reviewed, duplicate creation prevented, stale evidence rejected, and XP/bounty eligibility remains downstream of verified completion. Test both allowed and rejected transitions.
- **Boundary:** Read-only integration is the default. No external issue, task, bounty, XP, or repository state is changed by an inventory or recommendation.

### GATE-10 — Consider write-capable cross-repository automation

- **State:** DEFERRED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-09 plus an explicit owner decision to pursue writes
- **Entry condition:** A demonstrated use case cannot be met by a read-only workflow.
- **Required safeguards:** Least-privilege scopes, target/repository allowlist, human-readable preview, explicit confirmation, idempotency keys, audit evidence, failure/rollback behavior, secret handling, and rejection tests for unauthorized operations.
- **Exit criteria:** Security contract and negative tests pass; dry-run evidence demonstrates the exact proposed effect before any write; external acceptance tests prove correct scoped behavior. No part of this gate is implied by passing core tests.
- **Scenario branches:** If no necessary write use case exists, remain DEFERRED. If approved, design/test a narrow write operation separately; never enable generic repo automation by default.


### GATE-11 — Measure keyword-search quality before changing retrieval architecture

- **State:** BLOCKED
- **Owner:** Loofy147 (repository maintainer)
- **Dependencies:** GATE-00
- **Policy decision blocking execution:** [A-003](ASSUMPTIONS-REGISTER.md#a-003--keyword-search-meets-a-useful-quality-bar-without-semantic-retrieval). Freeze the minimum acceptable query-quality result and the gold-label rules before inspecting the scored results.
- **Purpose:** Determine whether the current explainable keyword ranker is sufficient for intended repository-discovery tasks.
- **Exit evidence:** Query-to-relevant-document labels, a reproducible evaluation command, ranking results, per-query failures, defined quality metrics, and an owner decision.
- **Scenario branches:**
  - `KEYWORD_BAR_MET` → keep the dependency-light ranker; do not add embeddings or a new retrieval service.
  - `KEYWORD_BAR_MISSED` → improve tokenization/ranking and repeat the same evaluation; only study semantic retrieval if a material measured gap remains.
  - `INCONCLUSIVE` → add representative queries and keep the retrieval architecture unchanged.

## Capability baseline already established

These capabilities are implemented and tested; they are not separate future gates:

- Standard-library local indexing and ranked keyword search.
- Lightweight project inventory and separate observed signals from hypotheses.
- Evidence-backed marker drafts, manifest-allowlisted Markdown checklists and typed JSON registry projections.
- Task-source freshness checks and missing-acceptance-criteria reporting.
- Read-only public GitHub issue and pull-request snapshots and separate work-plan projection.
- Optional metadata-only AI review through the separately documented OmniRoute Workbench.
- License-scoped open-source reuse catalog and source links.

See [Architecture](ARCHITECTURE.md), [Project Manifest](PROJECT-MANIFEST.md), [AI Review Gateway](AI-REVIEW-GATEWAY.md), and [Real-project Evaluation](REAL-PROJECT-EVALUATION.md). Historical evaluation data must be checked against current source revisions and workflow runs before it is treated as current evidence.

## Release gate

A gate is not complete until its exit criteria, reproducible commands, observed results, known limitations, and evidence links are recorded. Test and report the scenario result, then update both this roadmap and every affected assumptions-register item in the same change. Never convert a proposal, hypothesis, open PR, or AI recommendation into accepted work by inference.
