# Portfolio Context and System Boundaries

**Observed on:** 2026-10-21  
**Purpose:** Give contributors and agents an accurate starting map of the user's related projects, their roles, shared goals, and boundaries. This is an orientation index, not a replacement for any repository's canonical specification, source code, or current runtime evidence. Refresh the relevant repository state before acting on it.

## Portfolio-level intent

Build a coherent family of practical systems that turn real needs into useful outcomes. Reuse strong capabilities and open standards where evidence supports reuse, but do not force every idea into one application, service, database, agent framework, or mega-repository.

The shared operating principles are:

- Start from a real user or business outcome and observable acceptance evidence.
- Treat the user's own projects as real first-consumer use cases, while keeping that evidence separate from proof of external demand or product-market fit.
- Support different kinds of contribution and work, not only software code; keep rights, funding, rewards, contribution evidence, acceptance, and customer obligations distinct.
- Prefer small, complete workflows over broad collections of unfinished features.
- Eliminate unnecessary requirements, redundant steps, and duplicate records before adding automation.
- Make trust boundaries explicit across identity providers, GitHub connections, databases, application runtimes, MCP clients, tool permissions and repositories. Access in one boundary does not imply access in another.
- Reuse only after checking the source revision, actual license, rights, security, maintenance, dependency burden, and compatibility.
- Keep conversation text as a working interface. Put durable decisions, specifications, source evidence, work state, test results and handoffs in the appropriate canonical repository.
- Make integrations, tools, APIs, MCPs and datasets earn their place by solving a demonstrated problem. Availability alone is not a reason to adopt them.

## System map

| System | Portfolio role | Current boundary observed in the canonical repository |
|---|---|---|
| [Integrated Operations OS (Notion)](https://app.notion.com/p/3f84508c33af815a9a5dd587d3a46f04) | Canonical portfolio operating control plane for goals, initiatives, work items, decisions, risks, evidence, resources, integration/account inventories, asset provenance and HOS change records. | This is the existing organization layer, not a new system to recreate inside PIE. Search/fetch its linked canonical records before asking for context, creating task copies, choosing providers or repeating prior research. The [Professional & Technical Collaboration Profile](https://app.notion.com/p/3ff4508c33af81a9aa47c4a3d5f920b4), [Operating Guide](https://app.notion.com/p/3f84508c33af819da661f3726ae407c6), [Asset Inventory](https://app.notion.com/p/3ff4508c33af81aa9bbcfbe26e8bcd05), [Provider API Integration Registry](https://app.notion.com/p/b85f0c4d583d4a41bb0134e01968f5a8), portfolio register, project baselines and handoffs are discovery starting points, not proof that each underlying service is currently authorized. Apply the [HOS Change Signature v1 standard](https://app.notion.com/p/3ff4508c33af81108658d24c4875ed68) to every coherent implementation batch. |
| [Contribution Network](https://github.com/Loofy147/contribution-network) | Strategic and operating source of truth for the contribution-network business model, portfolio rules, lifecycle, value/rewards, governance and engineering primitives. The project itself is Project 0 and the first real consumer. | The repository describes a cross-niche coordination model in which the project is the unit of coordination, contributions are participation units, and the accepted outcome is the unit of delivery. Founder self-use supports dogfooding but does not by itself prove external demand or commercial economics. |
| [Contributions Centre / ContribQuest](https://github.com/Loofy147/Contribution-bounties-centre-) | Current application prototype and first consumer implementation for contribution work, acceptance evidence and XP. | The README reports an AppDeploy-based prototype, not a verified standalone production build. The AppDeploy SDK/client dependencies are not declared in the checked-in package manifest; live owner/contributor flows, authorization, persistence, XP idempotency and other end-to-end acceptance still require verification. The repository says no license has been selected. Listings are not escrow or guaranteed payouts. |
| [Project Intelligence & Contribution Engine (PIE)](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine) | Reusable, local-first engineering and research instrument for inspecting project evidence and turning verified gaps into reviewable contribution work. | Read-only by default toward scanned repositories and external systems. Produces evidence-linked task drafts, public GitHub snapshots, work-plan projections, metadata comparisons and explicit-reference audits. It must preserve canonical issue/PR/registry records rather than create a competing backlog. |
| [Swarm Context System](https://github.com/Loofy147/Context-swarm) | Repository-native context-state and workflow maturity system. Its primary unit is versioned context state and its transitions, not autonomous agents. | Current operating model uses committed files and Git history as canonical state. No backend, persistent service, or background worker is required in the present phase. Inputs must preserve provenance, and proposals are validated against exact base versions before accepted state changes. |
| [From Everything to Apps](https://github.com/Loofy147/From-everything-to-apps) | Personal OS and reusable-app portfolio: extract small capabilities from reference projects, then independently engineer reliable, portable applications and a common local access layer. | README labels many parts prototype/candidate. The Personal OS has local data and credential-reference metadata, not a true secret manager or cross-device identity/sync layer. The credential inventory must not accept actual secret values. App-specific gaps, tests and license status must be rechecked in that repository. |
| [OmniRoute Workbench integration](https://github.com/Loofy147/Project-Intelligence-Contribution-Engine/tree/main/integrations/omniroute-workbench) | Optional, bounded metadata-only AI review path used by PIE. | Not the engine's source of truth, not required for the local-first core, and not execution authorization. Use only when a measured task benefits from the review and its cost, inputs and output boundaries are acceptable. |
| [Future contribution-cloud control plane](https://github.com/contribution-cloud/Contributions-centre) | Reserved future portfolio/repository control plane for repository inventory and authorized lifecycle operations. | The strategic repository and current app README explicitly defer the transition. Do not initialize, migrate work into, or introduce dependencies on it until the first-consumer readiness gates pass and the actual access boundary is verified. |

## Authority and dependency rules

1. **Strategy versus implementation:** The Contribution Network's strategic documents govern network-level business and lifecycle decisions. The Contributions Centre repository governs the current app implementation. If they conflict, do not silently assume the running app already implements the strategic specification; record the gap and route it through an explicit gate.
2. **Engineering discovery versus canonical work:** PIE discovers evidence and prepares reviewable work. An existing issue, PR, project registry item, or accepted contribution record remains canonical. PIE must link to it instead of claiming ownership or completion.
3. **Context versus execution:** Swarm Context System can organize inputs, context states, dependencies, evidence and proposals. Its current repository-native phase does not imply live system access, automatic commits, or external writes unless a concrete run and permission boundary prove them.
4. **Personal OS versus secret infrastructure:** From Everything to Apps may organize credential references and related work; metadata storage is not the same as secure secret storage, credential rotation, or provider-side API access. Do not store real key/token values in application local storage or ordinary exports.
5. **Reusable components versus platform coupling:** Shared packages should emerge from repeated, demonstrated needs and stable contracts. Keep domain logic portable and providers behind explicit adapters. Do not force projects to depend on every sibling system.
6. **Identity and authorization:** A successful GitHub tool connection, app login, ChatGPT connector, MCP client, or second GitHub account is a separate authority boundary. Verify each target and permission directly.
7. **Status and readiness:** Source-level tests, prototype success and self-verification are different evidence levels. Follow each project's readiness gates. Do not transfer “passed” status from one repository to another.
8. **Portfolio integration:** Any cross-project integration needs an explicit owner, canonical data mapping, source provenance, permissions, failure/retry semantics, idempotency as appropriate, acceptance tests, and a documented fallback. Start read-only when that can satisfy the use case.

## How to use this map

For every non-trivial task, retrieve the existing context before asking the user to repeat it. Start from the [Integrated Operations OS](https://app.notion.com/p/3f84508c33af815a9a5dd587d3a46f04) and [Professional & Technical Collaboration Profile](https://app.notion.com/p/3ff4508c33af81a9aa47c4a3d5f920b4); fetch the project-specific baseline/handoff, work item, decision, asset/integration record and relevant research, then verify source and current state.

When a request spans more than one project:

1. Re-read the relevant canonical README, architecture/specification, dependency map, roadmap and open assumptions from each target repository.
2. Establish current branch/HEAD, current CI and runtime evidence. Treat this map's observed status as potentially stale.
3. Identify which repository owns the decision, which system owns the data, and which system only produces a derived view or proposal.
4. Look for existing implementations and canonical records before creating anything new.
5. Record the minimal explicit interface between systems and its permissions. Do not implement a cross-repository write merely because read access exists.
6. Update this map only when a durable role or boundary changes; update project-specific status in that project's own canonical docs.

## Primary context sources

- [Integrated Operations OS — Master Template](https://app.notion.com/p/3f84508c33af815a9a5dd587d3a46f04)
- [Professional & Technical Collaboration Profile](https://app.notion.com/p/3ff4508c33af81a9aa47c4a3d5f920b4)
- [HOS Change Signature v1 — Add-ons & Implementations](https://app.notion.com/p/3ff4508c33af81108658d24c4875ed68)
- [ContribQuest & Contribution Network — Clean Baseline v1.0](https://app.notion.com/p/3f94508c33af81c9b11ceaca80f769d1)
- [Cross-Conversation Handoff — ContribQuest Analytics, MCP & Release Readiness](https://app.notion.com/p/3fb4508c33af81938d63e4d1598678eb)
- [Platform Ecosystem Investigation & Reuse Plan](https://app.notion.com/p/3f94508c33af8150ab23c27ea1da0542)
- [Portfolio Architecture Register — Systems & Verification Gates](https://app.notion.com/p/3ff4508c33af81b6897de99f19db86f9)
- [Asset Inventory — Metadata Census & Provenance Rules](https://app.notion.com/p/3ff4508c33af81aa9bbcfbe26e8bcd05)
- [Provider API Integration Registry](https://app.notion.com/p/b85f0c4d583d4a41bb0134e01968f5a8)
- [Contribution Network — First-Consumer Project Charter](https://github.com/Loofy147/contribution-network/blob/main/docs/10-first-consumer-project-charter.md)
- [Contribution Network — Engineering Primitives and Integration Architecture](https://github.com/Loofy147/contribution-network/blob/main/docs/11-engineering-primitives.md)
- [Contributions Centre — Portfolio Alignment](https://github.com/Loofy147/Contribution-bounties-centre-/blob/main/docs/portfolio-alignment.md)
- [From Everything to Apps — Engineering Standards](https://github.com/Loofy147/From-everything-to-apps/blob/main/docs/engineering-standards.md)
- [Swarm Context System — Repository-native Operating Model](https://github.com/Loofy147/Context-swarm/blob/main/spec/swarm-operating-model.md)
- [PIE — Professional Operating Charter](OPERATING-CHARTER.md)
