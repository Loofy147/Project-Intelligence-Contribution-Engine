# PIE Operating Adapter

## Authority

The portfolio-level operating standard already exists in Notion. It is the canonical procedure for recovering context, reconstructing verified state, identifying missing work, researching, executing authorized work, verifying postconditions, and updating canonical records:

- [Autonomous Project Intelligence & Engineering Standard](https://app.notion.com/p/4004508c33af817fb47fef96a8a69d43) — primary operating procedure.
- [Professional & Technical Collaboration Profile](https://app.notion.com/p/3ff4508c33af81a9aa47c4a3d5f920b4) — collaboration contract, goals, priorities and portfolio rules.
- [Integrated Operations OS](https://app.notion.com/p/3f84508c33af815a9a5dd587d3a46f04) — canonical portfolio control plane for objectives, initiatives, delivery work, decisions, research, risks, resources, integration/account metadata and change records.
- [Portfolio Architecture Register](https://app.notion.com/p/3ff4508c33af81b6897de99f19db86f9) and [Source Registers](https://app.notion.com/p/3f84508c33af8164af31c59cc3517f5b) — system identities, dependencies, readiness gates and the existing data registries.
- [HOS Change Signature v1](https://app.notion.com/p/3ff4508c33af81108658d24c4875ed68) — provenance and accountability requirements for each coherent implementation batch.

**This file is a PIE-specific adapter, not a second portfolio operating standard.** The Notion standard owns the general process. This file records only the local engineering constraints and the minimum instructions needed when work happens in this repository. Do not copy portfolio goals, account lists, research findings, work items or decision records here when they already have canonical records elsewhere.

## Context acquisition before clarification

Before asking the user for details, treating an omitted item as unknown, creating a work item, selecting a provider, or proposing a new architecture:

1. Recover the active request and relevant prior decisions from the current conversation and accessible context.
2. Search and fetch the Notion operating standard, collaboration profile, Integrated Operations OS and the most relevant existing baseline, handoff, initiative, work item, decision, research record, systems/integrations entry or HOS change record. Follow canonical links; do not rely on search snippets alone.
3. Inspect this repository's current README, `AGENTS.md`, architecture, roadmap, assumptions register, issue/PR/manifest records, current HEAD, tests and CI.
4. Verify account, tool and provider availability in the current connected-tool surface and the provider's actual permission boundary when relevant. Existing account/integration metadata is a locator, not proof of live authentication or authority. Never retrieve or expose secret values.
5. Reconcile facts according to authority and scope. Mark claims as observed, user-reported, assumption, hypothesis, decision or unknown. Treat historical handoffs and old CI runs as leads, not current proof.
6. Continue with the highest-value safe action. Ask only when required discovery fails and the unresolved choice materially changes the outcome, or explicit authorization is needed.

The user provides direction, constraints and desired outcomes. The operator is responsible for discovering the existing context and the professional work needed to achieve them. Do not require the user to enumerate routine responsibilities or repeat facts already present in the workspace.

## Source-of-truth boundaries

| Domain | Canonical source |
|---|---|
| Portfolio objectives, active initiatives, work items, cross-project decisions, research, risk, resources, integration/account metadata and change records | Existing Integrated Operations OS in Notion and its linked canonical registers |
| Contribution Network strategy and product/domain contract | [Contribution Network repository](https://github.com/Loofy147/contribution-network), especially its canonical specifications, ADRs and accepted records |
| App implementation | The target application's repository, tests, review history and CI |
| PIE implementation and read-only discovery behavior | This repository, current source revision, tests, workflow artifacts and relevant canonical work item |
| Provider state and actual account permissions | Live authorized provider/tool inspection, with source, timestamp and scope recorded |
| External standards, API behavior and licensing facts | Current primary documentation, source/license text and direct evidence |

A strategy/specification is not proof that an application implements it. A successful read is not proof of write permission. A connected ChatGPT/tool account is not the same identity or permission as an in-app user, a GitHub App installation, a PAT, an MCP client, or another provider account.

## PIE-specific operating constraints

- **Read-only by default:** inspect target repositories and external work systems without changing them. Write-capable behavior requires its own explicit gate, permissions, safeguards, tests and authorization.
- **Preserve canonical work:** existing issues, pull requests, repository-native registries, Notion initiatives and work items remain authoritative. Link to them; do not make competing backlogs or duplicate records.
- **Evidence before inference:** an inventory hypothesis, TODO search, model output, title similarity, filtered-query absence or cross-reference event does not prove missing capability, relationship absence, acceptance or completion.
- **Keep system boundaries separate:** PIE discovers and proposes reviewable work; it does not become the source of truth for the target project. Context-swarm state, ContribQuest business records, Personal OS local data and provider/runtime records have their own contracts and permissions.
- **Keep the core small:** no new database, runtime dependency, provider, paid model, background worker or broad permission without a demonstrated requirement and a reviewed trade-off.
- **Research before adoption:** inspect existing research first. For material gaps, verify current primary sources, actual license/rights, source revision, maintenance, security, compatibility, costs, failure modes and exit options. Record a decision, not just a list of links.
- **Use tools as capabilities:** use an API, MCP, database, dataset or connected service when it advances a demonstrated outcome. Verify the actual behavior and postconditions. Availability alone is not a reason to integrate it.
- **Bound consequential actions:** external writes, deployment, spending, destructive changes, permission changes, secret handling and irreversible effects follow their specific authorization and change-control requirements.
- **Keep work organized:** update the existing canonical record. For a coherent implementation batch, follow HOS Change Signature v1 and link the change record; record source revision, exact scope, authorization, evidence, limits, rollback, digest status and review state without inventing values.
- **No false background claims:** “always active” means these procedures apply whenever work is performed. Do not claim continuous monitoring or scheduled execution unless a real configured automation and its postconditions are verified.

## Execution and completion

Use [the Execution Playbook](EXECUTION-PLAYBOOK.md) for the step-by-step cycle, [the Roadmap](ROADMAP.md) for dependency gates and scenario selection, [the Assumptions Register](ASSUMPTIONS-REGISTER.md) for falsifiable open questions, and [the Session Handoff Template](SESSION-HANDOFF-TEMPLATE.md) for cross-session continuity.

A task is complete only when applicable acceptance criteria are checked against actual evidence, relevant failure paths are considered, tests and current CI are observed where available, the final diff is reviewed, affected documentation and canonical records are updated, and unverified behavior and remaining blockers are explicit.

For users adopting PIE outside this portfolio, use the same context-first and evidence-driven method with their own canonical operating system and project records. Do not assume access to this Notion workspace or depend on its private data.
