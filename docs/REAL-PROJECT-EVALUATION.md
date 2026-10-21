# Real-project evaluation — baseline

**Evaluation workflow:** [run 39613265159](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39613265159)  
**Engine revision:** `1313a3675f19b39001dddc53a06bdc44eb4bfdc7`  
**Method:** CI checked out each public target repository at its then-current main head without persisting checkout credentials, then ran the Python CLI. This is a file inventory, not a semantic code audit.

## Results

| Project | Files indexed | Files skipped | Detected code-language files | Marker tasks | Inventory hypotheses |
|---|---:|---:|---|---:|---:|
| [Contribution Network Bounties](https://github.com/Loofy147/contribution-network) | 18 | 55 | JavaScript: 1 | 0 | 0 |
| [Context Swarm](https://github.com/Loofy147/Context-swarm) | 68 | 112 | Python: 15; SQL: 1 | 0 | 0 |
| [ContribQuest WorkLink](https://github.com/Loofy147/Contribution-bounties-centre-) | 42 | 83 | TypeScript: 8; JavaScript: 5; CSS: 2; HTML: 1 | 0 | 0 |

Skipped counts include ineligible paths and directories; they are not defect counts. Language counts reflect known file extensions, not complete framework detection. All three projects had conventional README, test, and CI markers, so no missing-README/test/CI hypotheses were produced.

## What this proved

- The actual Python CLI ran against three fresh public checkouts, generated inventories and task reports, and verified the resulting task snapshots in CI.
- It did not create tasks from generic mentions of TODO/FIXME in documentation.
- No explicit source-marker tasks were found in these snapshots. This is a limitation of marker-based work discovery, not proof that no work remains.

## Critical finding: the issue tracker is the active backlog

The ContribQuest repository had nine open issues at review time, including P0 issues for reproducible build, two-account acceptance testing, exactly-once XP transitions, GitHub app permissions, and project-scoped data access. These issues were invisible to a source checkout, which is why source-marker discovery returned zero tasks.

Do not clone these issues into a parallel task system by default. The next integration snapshots existing issues read-only, preserving their canonical URLs and metadata. The original GitHub issue remains the source of truth unless an explicitly reviewed reconciliation establishes otherwise.

## Project-specific interpretation

### Contribution Network Bounties

This repository is primarily strategy, governance, rights, value/reward, and engineering-specification documentation. Its unfinished work is expressed through decisions, evidence gaps, and explicit gates rather than source comments. It had no open issues in the reviewed query. A later structured gate extractor should read explicit status markers, not infer that a concept is absent.

### Context Swarm

This repository already contains schemas, executable reference logic, persisted registry/source records, cycle definitions, test fixtures, and CI. Its documentation explicitly defers runtime/backend infrastructure. That deferral must not be classified as a missing implementation. Integrations should consume the existing registry, current cycle, dependency map, and readiness gates rather than invent a parallel backlog.

### ContribQuest WorkLink

This is the application repository and had the clearest existing backlog. Start by importing its existing issues and reviewing them against current code and open PRs. The inventory alone does not prove that an issue is fixed or still open in the latest commit.

## Guardrails

- Target repositories were read-only; no target code, issue, or PR was altered.
- No issue was created or closed; no task was turned into a bounty.
- Inventory hypotheses require human review.
- A project must never be reported complete merely because no conventional TODO comments were detected.


## Follow-up evaluation — issue/PR-aware work plan

**Workflow:** [read-only real-project evaluation run](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39615742718)  
**Engine revision:** `35f920701863203d4b2c7b043f04a905c208ee8b)  
**Validation:** [Python test workflow](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39615742620) and [OmniRoute integration tests](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39615742662) also succeeded.

The workflow checked the public repositories at their current `main` heads using target checkouts with `persist-credentials: false`. It did not alter target repositories or GitHub records.

| Project | Files indexed | Open issues | Open PRs | Declared issue priority |
|---|---:|---:|---:|---|
| [Contribution Network Bounties](https://github.com/Loofy147/contribution-network) | 18 | 0 | 0 | None found |
| [Context Swarm](https://github.com/Loofy147/Context-swarm) | 68 | 0 | 0 | None found |
| [ContribQuest WorkLink](https://github.com/Loofy147/Contribution-bounties-centre-) | 42 | 9 | 9 | 5 P0; 4 P1 |

The marker/hypothesis generator produced zero drafts for all three scans, which demonstrates that source-comment detection is insufficient as a backlog-discovery mechanism. The issue/PR snapshots now expose canonical project work without duplicating it.

### ContribQuest canonical issues

Priority is parsed **only** from an explicit leading `[P0]`–`[P3]` prefix in the current issue title. It is source metadata, not an independent risk score.

**P0**
- [#1 — Reproducible development/build path](https://github.com/Loofy147/Contribution-bounties-centre-/issues/1): establish whether the supported target is AppDeploy-only or a reproducible local path; the repository documents platform-injected dependencies and clean-checkout reproducibility as outstanding.
- [#2 — Two-account end-to-end acceptance workflow](https://github.com/Loofy147/Contribution-bounties-centre-/issues/2): run real owner/contributor flows against an identified deployed version, including invalid direct-API transitions.
- [#3 — Exactly-once XP awards and safe review transitions](https://github.com/Loofy147/Contribution-bounties-centre-/issues/3): prove concurrent/retried acceptance cannot duplicate XP or corrupt state.
- [#5 — Least-privilege GitHub App connection](https://github.com/Loofy147/Contribution-bounties-centre-/issues/5): selected-repository access, state/replay protection, credential isolation and revocation.
- [#6 — Project-scoped data access and membership boundaries](https://github.com/Loofy147/Contribution-bounties-centre-/issues/6): finish endpoint-by-endpoint scope checks and negative cross-project isolation tests before broadening multi-project access.

**P1**
- [#4 — Project license and contribution terms](https://github.com/Loofy147/Contribution-bounties-centre-/issues/4): owner decision after reviewing first-party source provenance and third-party dependency rights.
- [#7 — Audit events and idempotent XP ledger](https://github.com/Loofy147/Contribution-bounties-centre-/issues/7): durable event/award lineage and safe retry/failure handling.
- [#8 — Authorized read-only Network MCP tools](https://github.com/Loofy147/Contribution-bounties-centre-/issues/8): depends on project-scope authorization and shared domain services; do not expose unrestricted data access.
- [#21 — Public Open Graph description](https://github.com/Loofy147/Contribution-bounties-centre-/issues/21): trace the deployed metadata source and verify the public page after approved copy is deployed.

### Open PR proposals are separate from issues

The snapshot contained nine open PRs, including:
- [PR #17 — AGPL-3.0-or-later proposal](https://github.com/Loofy147/Contribution-bounties-centre-/pull/17), **draft**. Its own conditions require the owner to verify first-party provenance and license rights before merge. Do not merge it automatically.
- [PR #20 — Independent review workflow](https://github.com/Loofy147/Contribution-bounties-centre-/pull/20), open, not merged. It proposes shared contribution/review functionality, but its existence does not establish that issues #2, #3, #6, or #7 are satisfied.
- [PRs #9–13 and #25–26](https://github.com/Loofy147/Contribution-bounties-centre-/pulls), dependency upgrades. Major-version changes should be tested for compatibility and not merged merely because Dependabot opened them.

No issue-to-PR relationship is inferred from similar titles. Verify links, changed files and checks before deciding overlap or closure.

### Recommended execution order

1. **#1 build/runtime contract:** establish the actual supported runtime and prove a clean-checkout install/build/test path.
2. **#5 and #6 access boundaries:** complete selected-repository GitHub authorization and project/resource isolation.
3. **#3 and #7 state integrity:** prove exactly-once XP and durable audit/ledger semantics with retry, concurrency and fault tests.
4. **#2 live end-to-end workflow:** verify separate owner and contributor identities plus direct-API rejection cases against a recorded deployment/source pairing.
5. **#4 licensing:** make the owner decision after rights/provenance review; treat PR #17 as a proposal, not an approval.
6. **#8 MCP read-only surface:** expose bounded project-scoped tools only after shared authorization controls pass their tests.
7. **#21 public metadata:** identify the real deployed metadata source, apply approved copy, and verify the deployed preview.

This is a proposed order derived from current issue descriptions, repository docs, and visible PR state—not a claim that every issue is wholly unimplemented. Existing GitHub issues remain the canonical work records.
