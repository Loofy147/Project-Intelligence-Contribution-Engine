# Roadmap

## M0 — Usable local search

- [x] Define the product boundary and trust model.
- [x] Build a standard-library indexer with exclusions and file-size limits.
- [x] Store versioned local JSON index records and source digests.
- [x] Implement ranked keyword search and readable snippets.
- [x] Expose index and search through the CLI.
- [x] Add tests and GitHub Actions CI.
- [x] Verify the initial CLI/test suite on Python 3.11 and 3.12 in GitHub Actions.

## M1 — Project inventory

- [x] Add explicit project registration manifests.
- [x] Detect common languages and project files without executing repository code.
- [x] Produce a Markdown or JSON inventory report with source locations.
- [x] Separate observed tooling signals from inferred review hypotheses.

## M2 — Evidence-backed contribution task drafts

- [x] Define a versioned task schema.
- [x] Include source evidence, source digests, review steps, dependencies, and empty acceptance criteria until reviewed.
- [x] Generate stable draft IDs from project identity and observed evidence.
- [x] Generate draft tasks only; do not publish or create bounties automatically.
- [ ] Add a broader benchmark corpus to measure heuristic precision and false positives.
- [x] Add read-only task evidence freshness verification and acceptance-criteria completeness checks.

## M3 — Existing workflow integrations

- [x] Add an explicit read-only public GitHub issue snapshot command; preserve canonical issue URLs and exclude pull requests.
- [ ] Reconcile reviewed issue/task evidence into ContribQuest without duplicating the source issue.
- [ ] Reuse existing GitHub issues/PRs as evidence rather than duplicating records unnecessarily.
- [ ] Add read-only GitHub inventory first; gate all write operations explicitly.
- [ ] Keep XP and bounty state downstream of verified task completion.

## M4 — Measured retrieval improvements

- [ ] Create a small evaluation set with expected search results.
- [ ] Measure keyword-search quality before adding semantic retrieval.
- [ ] Evaluate document chunking and local/hosted embeddings only if keyword search is insufficient.
- [ ] Revisit persistence only when index size or workflow requirements justify it.

## Release gate

Do not mark a milestone complete without reproducible commands, test output, known limitations, and links to the relevant code or evidence.
