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
