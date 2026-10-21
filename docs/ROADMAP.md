# Roadmap

## M0 — Usable local search

- [x] Establish the product boundary and trust model.
- [x] Build a standard-library indexer with exclusions and file-size limits.
- [x] Store versioned local JSON index records and source digests.
- [x] Implement ranked keyword search and snippets.
- [x] Expose index/search through the CLI.
- [x] Add GitHub Actions CI.
- [x] Verify the CLI/test suite on Python 3.11 and 3.12.

## M1 — Project inventory

- [x] Add optional project registration manifests.
- [x] Detect common language extensions and project marker files without executing code.
- [x] Produce Markdown/JSON reports with source locations.
- [x] Separate observed tooling signals from inferred review hypotheses.

## M2 — Evidence-backed contribution drafts

- [x] Define a versioned task schema.
- [x] Include source evidence, source digests, review steps, dependencies and acceptance criteria where canonical registry records supply them.
- [x] Generate stable draft IDs from project identity and marker/record identity.
- [x] Generate drafts/projections only; no automatic issue publishing or bounty creation.
- [x] Add read-only source-evidence freshness checks and acceptance-criteria completeness reporting.
- [x] Add explicit allowlists for Markdown checklist files and typed JSON registry work-item sources.
- [x] Verify individual registry-record digests so unrelated registry edits do not stale other records.
- [ ] Measure heuristic precision/false positives against a broader benchmark corpus.
- [ ] Add explicit task approval states and a human-reviewed acceptance/closure protocol.

## M3 — Existing work sources

- [x] Add public GitHub issue snapshots; preserve canonical issue URLs and exclude pull requests from issue records.
- [x] Add public GitHub pull-request snapshots with branch references and draft status.
- [x] Build a read-only work-plan projection that keeps canonical issues, PR proposals, registry items and engine drafts separate.
- [x] Run inventory/issue/PR/work-plan evaluation against three real public project repositories in CI.
- [x] Consume Context Swarm's existing `swarm/registry.json` active work items by explicit manifest configuration; preserve canonical IDs/status/criteria and do not duplicate them as GitHub issues.
- [ ] Add explicit, evidence-based issue/PR linkage only when GitHub supplies a real relationship or a maintainer confirms it.
- [ ] Detect issue/task staleness from closed status, changed source and fresh source snapshots.
- [ ] Build a reviewed mapping from ContribQuest issues to accepted project/context records without cloning the issue backlog.
- [ ] Add private-repository support only after designing a least-privilege auth boundary; do not put tokens in source or local manifests.

## M4 — Better project-specific analysis

- [ ] Parse structured readiness gates and deferred decisions in documentation-heavy repositories such as Contribution Network and Context Swarm.
- [x] Consume declared repository-native work items from Context Swarm instead of inventing a competing backlog format.
- [ ] Correlate existing issues with PRs only from explicit references and checked commit/file evidence.
- [ ] Create a benchmark set with expected inventory and known open work.
- [ ] Measure keyword-search quality before considering embeddings or semantic retrieval.
- [ ] Revisit persistence only when evidence shows local JSON is insufficient.

## M5 — ContribQuest workflow integration

- [ ] Map reviewed tasks to existing ContribQuest issues/work items without duplicating canonical records.
- [ ] Track evidence lineage, acceptance criteria, responsible actor, validation results and freshness.
- [ ] Keep XP/bounty status downstream of verified completion.
- [ ] Keep all cross-repository writes disabled until permission scopes, preview, explicit confirmation, idempotency and rollback are implemented and tested.


## M6 — Optional AI review and reuse governance

- [x] Maintain a dated, license-scoped open-source reuse catalog with source links and explicit adoption decisions.
- [x] Add an opt-in OmniRoute adapter that transmits bounded task metadata rather than source files.
- [x] Validate model responses and keep recommendations separate from task status and external actions.
- [ ] Add labelled benchmark data and measure task-review precision/recall against human adjudication.
- [ ] Add durable token/cost budgets and usage accounting before describing the gateway as a spending-control boundary.

## Release gate

Do not mark a milestone complete without reproducible commands, CI evidence, known limitations and links to code/results. Green inventory CI alone does not establish correctness of the target application or prove a reported issue is still unresolved.
