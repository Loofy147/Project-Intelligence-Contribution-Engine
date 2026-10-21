# Roadmap

## M0 — Usable local search

- [x] Define the product boundary and trust model.
- [x] Build a standard-library indexer with exclusions and file-size limits.
- [x] Store versioned local JSON index records and source digests.
- [x] Implement ranked keyword search and readable snippets.
- [x] Expose index and search through the CLI.
- [x] Add tests and GitHub Actions CI.
- [ ] Run the tests in a clean environment and record the actual result.

## M1 — Project inventory

- [ ] Add explicit project registration manifests.
- [ ] Detect common languages and project files without executing repository code.
- [ ] Produce a Markdown inventory report with source locations.
- [ ] Separate observed facts, inferred risks, and unverified hypotheses.

## M2 — Evidence-backed contribution tasks

- [ ] Define a versioned task schema.
- [ ] Require source evidence, acceptance criteria, dependencies, and validation steps.
- [ ] Add duplicate detection and task freshness checks based on source digests.
- [ ] Generate draft tasks only; require review before publication or assignment.

## M3 — Existing workflow integrations

- [ ] Map approved tasks to ContribQuest work items.
- [ ] Use existing GitHub issues/PRs as evidence rather than duplicating records unnecessarily.
- [ ] Add read-only GitHub inventory first; gate all write operations explicitly.
- [ ] Keep XP and bounty state downstream of verified task completion.

## M4 — Measured retrieval improvements

- [ ] Create a small evaluation set with expected search results.
- [ ] Measure keyword-search quality before adding semantic retrieval.
- [ ] Evaluate document chunking and local/hosted embeddings only if keyword search is insufficient.
- [ ] Revisit persistence only when index size or workflow requirements justify it.

## Release gate

Do not mark a milestone complete without reproducible commands, test output, known limitations, and links to the relevant code or evidence.
