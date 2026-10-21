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
