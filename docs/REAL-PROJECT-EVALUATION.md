# Real-project evaluation

## Latest run

**Evaluation workflow:** [run 39618171520](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39618171520)  
**Engine revision:** `b7837bff1e41e2896e9aa79c4e67bb35f6a144c0`  
**Test workflow:** [run 39618171773](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39618171773)  
**OmniRoute workflow:** [run 39618171639](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39618171639)

All three workflows succeeded. The evaluation matrix checked out the public target repositories without persisting target-repository credentials (`persist-credentials: false`) and ran the actual CLI. Target repositories were read-only; only this engine repository was changed.

| Project | Files indexed | Open issues | Open PRs | Generated engine records | Canonical work items from registry |
|---|---:|---:|---:|---:|---:|
| [Contribution Network Bounties](https://github.com/Loofy147/contribution-network) | 18 | 0 | 0 | 0 | 0 |
| [Context Swarm](https://github.com/Loofy147/Context-swarm) | 68 | 0 | 0 | 0 | 2 |
| [ContribQuest WorkLink](https://github.com/Loofy147/Contribution-bounties-centre-) | 42 | 9 | 9 | 0 | 0 |

The phrase “generated engine records” above excludes canonical registry work-item projections. The Context Swarm workplan contains **two** existing ready records, each verified fresh:
- `SCS-MATURE-008` — Validate capability boundaries against exact connected tools as real tasks require them. Evidence pointer: `swarm/registry.json#/work_items/7`.
- `SCS-MATURE-013` — Compute context impact from changed source revisions and propose stale-state updates. Evidence pointer: `swarm/registry.json#/work_items/12`.

The verification report for those two projections was: `2 fresh, 0 stale, 0 unverified; 0 missing acceptance criteria; 0 eligible for execution`. Eligibility remains zero because records are still review-required; the engine does not infer approval from evidence freshness.

## What the evaluation proves—and does not prove

- The CLI and tests passed on Python 3.11 and 3.12.
- The read-only workflow successfully generated inventories, GitHub issue/PR snapshots, tasks, freshness checks and issue-first work plans for all three current public checkouts.
- Context Swarm’s registry items were sourced from its existing typed `swarm/registry.json`; they were not copied into a new backlog or turned into GitHub issues.
- No source-marker or explicitly configured checklist tasks were found in these checkouts. This is not proof that no unfinished work exists; the ContribQuest GitHub issues and Context Swarm’s typed registry are the stronger work sources for those repositories.
- The Markdown checklist extractor remains opt-in. The evaluation does not parse every checkbox from every document, and it deliberately does not turn Context Swarm’s deferred runtime acceptance checklist into current tasks.

## ContribQuest canonical backlog

The current public issue snapshot shows nine open issues: five titles declare P0 and four declare P1. These are source priorities, not an independently computed risk score.

**P0**
- [#1 — Reproducible development/build path](https://github.com/Loofy147/Contribution-bounties-centre-/issues/1)
- [#2 — Two-account end-to-end acceptance workflow](https://github.com/Loofy147/Contribution-bounties-centre-/issues/2)
- [#3 — Exactly-once XP awards and safe review transitions](https://github.com/Loofy147/Contribution-bounties-centre-/issues/3)
- [#5 — Least-privilege GitHub App connection](https://github.com/Loofy147/Contribution-bounties-centre-/issues/5)
- [#6 — Project-scoped data access and membership boundaries](https://github.com/Loofy147/Contribution-bounties-centre-/issues/6)

**P1**
- [#4 — Project license and contribution terms](https://github.com/Loofy147/Contribution-bounties-centre-/issues/4)
- [#7 — Audit events and idempotent XP ledger](https://github.com/Loofy147/Contribution-bounties-centre-/issues/7)
- [#8 — Authorized read-only Network MCP tools](https://github.com/Loofy147/Contribution-bounties-centre-/issues/8)
- [#21 — Public Open Graph description](https://github.com/Loofy147/Contribution-bounties-centre-/issues/21)

The latest open PR snapshot had nine PRs including:
- [PR #17 — AGPL-3.0-or-later proposal](https://github.com/Loofy147/Contribution-bounties-centre-/pull/17), draft and gated on the owner's source-rights/provenance review.
- [PR #20 — Independent review workflow](https://github.com/Loofy147/Contribution-bounties-centre-/pull/20), open but unmerged. Its presence does not prove any related P0 issue is satisfied.
- [PRs #9–13 and #25–26](https://github.com/Loofy147/Contribution-bounties-centre-/pulls), dependency-upgrade proposals that require compatibility validation, especially major versions.

No issue-to-PR relationship is inferred from matching words. Verify GitHub cross-references, changed files and checks before claiming that a PR resolves an issue.

## Proposed implementation order

1. **#1 build/runtime contract:** establish the actual supported runtime and prove a clean-checkout install/build/test path.
2. **#5 and #6 access boundaries:** complete selected-repository GitHub authorization and project/resource isolation.
3. **#3 and #7 state integrity:** prove exactly-once XP and durable audit/ledger semantics with retry, concurrency and fault tests.
4. **#2 live end-to-end workflow:** verify separate owner and contributor identities plus direct-API rejection cases against a recorded deployment/source pairing.
5. **#4 licensing:** make the owner decision after rights/provenance review; treat PR #17 as a proposal, not approval.
6. **#8 MCP read-only surface:** expose bounded project-scoped tools only after shared authorization controls pass their tests.
7. **#21 public metadata:** identify the actual deployed metadata source, apply approved copy and verify the deployed preview.

This is a proposed order derived from current issue descriptions, repository docs and visible PR state—not a claim that every issue is wholly unimplemented. Existing GitHub issues remain the canonical work records.

## Guardrails

- Target repositories were read-only; no target code, issue or PR was altered.
- No issue was created or closed; no PR was merged; no task became a bounty.
- Inventory hypotheses and unchecked checklist items require review.
- Registry projections remain anchored to the source registry and do not mutate source status.
- A project must never be reported complete merely because no conventional TODO comments were detected.


## Continuation recheck — 2026-10-21

**Previously tested engine revision (before this report refresh):** `488245ad0cb74463bb0dc670aac43db45a5e11e5`. The current `tests`, `evaluate-real-projects`, and `omniroute-workbench` workflows succeeded on this commit:
- [Engine tests](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39621316820)
- [Real-project evaluation](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39621316825)
- [OmniRoute Workbench tests](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/actions/runs/39621316851)

The target `main` branches were rechecked without changing them:

| Repository | Current reviewed main commit | Open issues | Open PRs | Latest observed CI |
|---|---|---:|---:|---|
| [Contribution Network](https://github.com/Loofy147/contribution-network) | `8fe5f3482a3104468eb6bbc7c425bbc73202ca35` | 0 | 0 | Documentation CI and secret scanning passed on current head |
| [Context Swarm](https://github.com/Loofy147/Context-swarm) | `e73d521e8d246691888d656419457d5b0eedd055` | 0 | 0 | [SCS contract run](https://github.com/Loofy147/Context-swarm/actions/runs/38961625386) passed |
| [ContribQuest WorkLink](https://github.com/Loofy147/Contribution-bounties-centre-) | `773edc70f418a619ed8575aeda2ce30fe131cedb` | 9 | 11 | Existing main CI is green; the two new proposals have green PR checks |

The ContribQuest open issue count and issue-title priority declarations remain unchanged: five P0 and four P1. Its open PR count increased from nine to eleven because the two draft proposals below were added. These proposals are not merged and do not close their related P0/P1 issues.

### New draft proposals

**[PR #27 — Atomic idempotent community XP ledger and audit events](https://github.com/Loofy147/Contribution-bounties-centre-/pull/27)**  
Head `ea602ef2ba8ea8420c3197cf5119b8d6df8a2421`. Its repository-contract, CodeQL and secret-scanning checks passed:
- [Contract](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39648777469)
- [CodeQL](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39648777425)
- [Secret scan](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39648777356)

The branch proposes deterministic `community_xp_<contribution-id>` ledger keys and audit events in the same transaction as community submission, resubmission and review transitions. This is **source-level evidence only**. It does not establish database atomicity/concurrency behavior in live AppDeploy. Issues #3 and #7 remain open pending concurrent acceptance tests, retry after an unknown outcome, transaction-conflict tests, verification of persisted rows, and an explicit strategy for historical accepted work that predates the ledger.

**[PR #28 — Pin frontend dependencies and use npm ci in CI](https://github.com/Loofy147/Contribution-bounties-centre-/pull/28)**  
Head `2c273e186795aa65aa47987c175505cec99f55f3`. Its repository-contract, CodeQL and secret-scanning checks passed:
- [Contract](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39649967118)
- [CodeQL](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39649967101)
- [Secret scan](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39649967201)

The lockfile was generated using Node 22 and validated through `npm ci`, TypeScript validation, the AppDeploy-externalized Vite build, artifact smoke test and contract suite in [bootstrap run 39649570566](https://github.com/Loofy147/Contribution-bounties-centre-/actions/runs/39649570566). The temporary workflow that published the file was removed from its helper branch after success.

This resolves a reproducibility gap for the **frontend validation toolchain**, not for a self-hosted app runtime. The production backend still depends on platform-injected `@appdeploy/sdk`; the local validation frontend leaves `@appdeploy/client` external. Keep issue #1 open until the intended runtime contract and its live source/deployment relationship are documented and verified.

### Current safe next actions

1. Review and decide whether to accept PR #28; its automated checks cover locked installation and frontend validation, but not an independent AppDeploy deployment.
2. Keep PR #27 draft until the AppDeploy database behavior is tested for concurrent acceptance, retries after unknown outcomes and transaction-conflict paths.
3. Continue access-boundary verification without assuming workspace membership scopes global bounty listings: the current product contract says bounties are global, and workspace privacy would require an explicit data-model/authorization change.
4. Keep the original GitHub issue as the canonical work record. Do not auto-close P0/P1 issues merely because the associated branch checks pass.

No target `main` repository was changed during this recheck; only the engine's evaluation report is being refreshed.
