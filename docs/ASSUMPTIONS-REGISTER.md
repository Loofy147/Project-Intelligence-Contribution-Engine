# Assumptions Register

This is the canonical register for unresolved assumptions and questions that affect scope, architecture, or the next executable roadmap scenario. The roadmap links to these IDs; do not maintain a competing list in issues, chats, or handoff notes.

## Operating contract

- Every item with status `OPEN` **must** have a named accountable owner, a falsification method, the evidence that would settle it, and explicit outcomes that select a scenario. An empirical OPEN assumption does **not** block the gate whose purpose is to test it; the test outcome selects the scenario. Only a required owner decision or missing test input blocks execution.
- The accountable owner is the repository maintainer, **Loofy147**, unless a specific person is recorded here. Agents may gather evidence and run tests; they must not silently make an unresolved product-policy decision on the owner's behalf.
- Do not use dates or guessed time estimates as planning state. Use evidence, dependencies, owner decisions, and gate state.
- A claim is not resolved because a model agrees with it, the code exists, or one CI run is green. Record the evidence link/path and the observed result.
- For empirical assumptions, record `SUPPORTED`, `FALSIFIED`, or `INCONCLUSIVE` after the test. For policy questions, record the owner's selected answer and rationale. Do not change success thresholds after looking at results.
- If an OPEN item lacks an owner or falsification method, it is an invalid register entry and its dependent gate is BLOCKED.
- Never resolve an assumption by inferring a fact from similar issue titles, heuristic detections, or model output alone.

## Status definitions

- `OPEN`: unanswered; its owner and falsification method are mandatory.
- `SUPPORTED`: evidence supports the claim under the stated test conditions; this does not make the claim universally true.
- `FALSIFIED`: evidence contradicts the claim or the owner rejects the policy assumption.
- `INCONCLUSIVE`: insufficient coverage, ambiguous evidence, or an invalid test. The dependent gate remains blocked.
- `DEFERRED`: the owner explicitly chose not to answer because the capability is not currently needed. This is a scope decision, not proof that the assumption is true.

## OPEN register

### A-001 — Minimum quality required for heuristic task recommendations

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Is a minimum precision target of 0.90 an acceptable initial bar before heuristic-generated candidates may influence default ranking? Regardless of the answer, heuristic hypotheses remain review-only and never become execution-approved automatically.
- **Why it matters:** Avoids adding more heuristics or letting noisy inventory hypotheses steer work before false-positive costs are understood.
- **Falsification / decision method:** Before examining benchmark results, the owner must accept or replace the proposed 0.90 target and define the labelled unit and sampling rule. Then run a blinded, manually adjudicated benchmark and report precision, recall, false-positive examples, per-kind results, and uncertainty. The assumption is falsified if the owner rejects the proposed bar or if the predeclared precision criterion is not met.
- **Evidence required:** Versioned labelled fixture set, written label rules, exact command, machine-readable metrics, adjudication record, and CI link.
- **Scenario selection:**
  - `TARGET_ACCEPTED_AND_MET` → pass the quality gate for the tested corpus only; keep every candidate review-required.
  - `TARGET_ACCEPTED_BUT_MISSED` → tune or disable the failing heuristic category; rerun the benchmark before expanding coverage.
  - `TARGET_REJECTED` → keep the gate blocked until the owner records a replacement target; do not score first and choose a convenient threshold later.
  - `INCONCLUSIVE` → improve the corpus or label rules; do not promote the heuristic.

### A-002 — Benchmark corpus generalizes beyond the current smoke-test projects

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Do the current three public target projects plus proposed fixtures cover the source types and repository shapes needed to support quality claims?
- **Why it matters:** A benchmark can pass while failing on other languages, project layouts, task sources, or documentation styles.
- **Falsification method:** Stratify results by repository, language/technology markers, source type (marker, explicit checklist, typed registry, inventory hypothesis), and positive/negative label. Hold out at least one repository or source family. The claim is falsified if quality conclusions change materially on holdout, a source family is missing, or adjudicators find systematic uncovered false positives.
- **Evidence required:** Corpus inventory, label definitions, per-stratum metrics, holdout result, and list of uncovered cases.
- **Scenario selection:**
  - `COVERAGE_ADEQUATE` → use results only within the measured envelope and add regression fixtures for known failures.
  - `COVERAGE_GAP` → add the missing strata before claiming general quality or widening the feature.
  - `INCONCLUSIVE` → keep the quality gate blocked.

### A-003 — Keyword search meets a useful quality bar without semantic retrieval

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Is the current explainable keyword-search ranking sufficient for the intended repository-discovery tasks, or does it miss relevant evidence often enough to justify a different retrieval method?
- **Why it matters:** Embeddings or another retrieval service add complexity and dependencies; the need should be measured first.
- **Falsification method:** Create query-to-relevant-document gold labels from representative repositories, predeclare quality metrics and a minimum acceptable result, and compare current ranked results with human judgement. The claim is falsified when the predeclared result is missed on the intended task mix.
- **Evidence required:** Query set, labelled relevant documents, reproducible ranking output, per-query failures, and an owner decision on whether the observed misses affect the product goal.
- **Scenario selection:**
  - `KEYWORD_BAR_MET` → keep local keyword retrieval; do not add semantic dependencies.
  - `KEYWORD_BAR_MISSED` → first improve tokenization/ranking and retest; evaluate semantic retrieval only if a measured gap remains.
  - `INCONCLUSIVE` → expand the query set; no retrieval architecture change.

### A-004 — Optional AI review adds enough value to justify its maintenance and cost

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Does metadata-only AI review improve task triage quality or human review effort versus the non-AI workflow by enough to justify keeping it as a recommended path?
- **Why it matters:** The integration is optional and must not become an assumed dependency or an unmeasured cost-control mechanism.
- **Falsification method:** Run a blinded paired comparison on the same labelled task set, with and without AI recommendations. Measure agreement with human adjudication, missed/incorrect decisions, review effort, latency, and actual token/cost data where available. Agree what improvement counts before scoring. The claim is falsified if the agreed net-benefit criterion is not met, or if the evidence cannot reliably distinguish benefit from noise.
- **Evidence required:** Same-task comparison, frozen model/configuration, human labels, quality/effort metrics, observed cost data, and explicit decision.
- **Scenario selection:**
  - `AI_VALUE_PROVEN` → keep the adapter opt-in and design durable budgets before any spending-control claims.
  - `AI_VALUE_NOT_PROVEN` → keep it experimental or de-emphasize it; prioritize non-AI evidence improvements.
  - `INCONCLUSIVE` → no expansion or additional paid routing dependency.

### A-005 — Explicit evidence is available to link related GitHub issues and pull requests

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Can issue/PR relationships be represented reliably from explicit GitHub cross-references or maintainer-confirmed mappings, without guessing from text similarity?
- **Why it matters:** False links can cause an open issue to be incorrectly treated as solved by a draft, unmerged, or unrelated PR.
- **Falsification method:** Audit a sample of candidate relationships using authoritative GitHub cross-reference metadata or explicit maintainer mapping. Treat absence of such evidence as a negative result for automatic linking. The claim is falsified for any proposed automatic linker that emits a relationship unsupported by a canonical reference or recorded maintainer decision.
- **Evidence required:** Source IDs/URLs, type of relationship evidence, sampled false-link audit, and tests that reject title-only matches.
- **Scenario selection:**
  - `EXPLICIT_RELATIONS_AVAILABLE` → implement only the verified relationship types and preserve provenance.
  - `EXPLICIT_RELATIONS_SPARSE` → keep issue and PR records separate; allow a reviewed mapping only when a maintainer provides it.
  - `INCONCLUSIVE` → no automatic relationship inference.

### A-006 — Private-repository support is required for the intended evaluation scope

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Does a required project need private-repository access for the engine to serve its intended workflow?
- **Why it matters:** Authentication and private data handling create meaningful security obligations; the core currently uses public, unauthenticated GitHub reads.
- **Falsification method:** Compare the explicitly required target-project list with public accessibility and whether a sanitized fixture can cover the needed behavior. The claim is falsified if all required work can be evaluated from public metadata or owner-approved sanitized fixtures.
- **Evidence required:** Named required project/use case, access limitation, sanitized-data alternative assessment, and owner decision.
- **Scenario selection:**
  - `PRIVATE_ACCESS_REQUIRED` → design least-privilege auth, token handling, redaction, revocation, and tests as a separate gate before implementation.
  - `PUBLIC_OR_SANITIZED_SCOPE_SUFFICIENT` → defer private-repository credentials and keep core read-only/public.
  - `INCONCLUSIVE` → no token support.

### A-007 — Local JSON persistence is insufficient for a demonstrated requirement

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Is local JSON no longer adequate for the current single-user, local-first workflow?
- **Why it matters:** A database or service increases operational complexity and is out of scope unless a concrete failure demands it.
- **Falsification method:** Reproduce a requirement that local files cannot safely satisfy, such as concurrent writers, durable shared audit, multi-user coordination, cross-machine state, or a data-size/latency limit. Record a reproducible scenario and why file-based design cannot meet it. The assumption is falsified if no such requirement can be reproduced for the intended workflow.
- **Evidence required:** Minimal reproduction, expected behavior, observed failure, and comparison with a simpler file-based fix.
- **Scenario selection:**
  - `PERSISTENCE_GAP_PROVEN` → write an architecture decision record and design migration/recovery before choosing a database.
  - `LOCAL_JSON_SUFFICIENT` → stay local-first; no database/server.
  - `INCONCLUSIVE` → retain the current architecture.

### A-008 — Generic structured-readiness parsing is preferable to per-project rules

- **Status:** OPEN
- **Owner:** Loofy147 (repository maintainer)
- **Question/claim:** Do readiness gates, deferred decisions, dependencies, and assumptions recur in sufficiently consistent forms across target repositories to support a safe generic parser?
- **Why it matters:** Documentation-heavy projects may use similar concepts but different formats; overgeneralization can turn specifications into false tasks.
- **Falsification method:** Label those constructs in the named documentation-heavy repositories, compare their structures, and test a proposed parser against held-out docs. The assumption is falsified when formats are inconsistent, extraction misses material meaning, or review-required false positives outweigh the reusable coverage.
- **Evidence required:** Small labelled corpus, exact source pointers, parser precision/recall, held-out examples, and a list of unsupported structures.
- **Scenario selection:**
  - `PATTERNS_RECUR` → implement narrow schema/grammar with explicit opt-in paths and evidence pointers.
  - `PATTERNS_DIVERGE` → prefer repository-native adapters or registry projections; do not build a universal crawler.
  - `INCONCLUSIVE` → stay manual and gather examples.

## Resolved design constraints (not OPEN assumptions)

- Core scanning remains read-only toward target repositories. Source evidence supports this in [Architecture](ARCHITECTURE.md) and current CLI contracts.
- A draft or model recommendation never authorizes execution, external writes, bounty creation, XP awards, or merging. Freshness alone is not approval.
- Existing GitHub issues and project-native registries remain canonical; a PR is a proposal, not proof of accepted work.
- Remote model review is optional, metadata-bounded, and advisory. Its in-memory rate limiter is not a durable cost budget.
- External writes remain disabled until separately designed permission scopes, preview, explicit confirmation, idempotency, and rollback are tested.

These are current repository guardrails. Changing one requires an explicit owner decision and a documented design review; do not reclassify it as an ordinary implementation detail.
