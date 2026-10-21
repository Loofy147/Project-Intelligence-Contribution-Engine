# Architecture

## Current components

- **Indexer**: discovers eligible text files, applies exclusions and size limits, and emits a versioned local JSON index.
- **Search**: tokenizes content, computes an explainable TF-IDF-style score, and returns paths and snippets.
- **Inventory**: detects language extensions and conventional project/tooling manifests without executing project code. Optional metadata lives in `.project-intelligence.json`.
- **Task drafts**: converts explicit TODO/FIXME/XXX/HACK source markers to observed-fact drafts and inventory review signals to hypotheses.
- **Task verification**: compares stored source digests and line markers against a fresh scan, then reports stale/unverified evidence and missing acceptance criteria.
- **GitHub issue/PR readers**: fetch public list endpoints via HTTP GET and capture titles, labels, states, timestamps, branch references, and canonical source URLs. Bodies are not mirrored.
- **Work-plan projection**: sorts existing issues by an explicit leading `[P0]`–`[P3]` title prefix, and keeps issues, proposed PRs, and local draft findings separate.
- **CLI**: exposes index, search, inventory, GitHub snapshot, work-plan, task-draft, and evidence-verification operations.

## Data flow

1. Scan the explicitly selected local project.
2. Skip common generated directories, symlinks, oversized files, binary files, and likely credential-bearing paths.
3. Produce root-relative file metadata, content digests, and a local text index.
4. Derive inventory signals using file names and conventional directory patterns.
5. Generate stable draft identifiers from project identity and marker location/reason.
6. Verify saved task evidence against a fresh project scan.
7. When explicitly requested, fetch public GitHub issue/PR metadata and preserve original external identifiers and URLs.
8. Build a read-only work-plan view without creating or changing any external records.

## Task semantics and authority

- `observed` means a marker was present at a specific file and line in an indexed snapshot; it does not prove the work remains actionable.
- `hypothesis` means an inventory heuristic did not find a conventional marker; it does not prove the capability is absent.
- Drafts include evidence, source digests where available, review steps, and empty acceptance criteria until a human defines them.
- `pie verify-tasks` flags stale source digests or inventory hypotheses that are no longer detected.
- Missing acceptance criteria are blockers; freshness alone never implies approval.
- Existing GitHub issues remain canonical work records. Pull requests remain proposed changes. The engine does not infer that a PR resolves an issue merely because their titles look similar.
- Generated drafts cannot publish issues, assign work, create bounties, award XP, merge PRs, or edit scanned source code.

## Trust and safety boundaries

- Source scanning is read-only.
- Common secret-bearing paths and types are excluded, but the rules are defense in depth, not a guarantee.
- A local JSON index contains copied project source text. Keep it local, ignore it in Git, and review before sharing.
- Task excerpt output applies basic credential-pattern redaction; do not treat it as complete secret scanning.
- Report output avoids absolute local paths by default.
- Inventory is a filename/extension heuristic, not a semantic audit.
- Indexing and search remain local-only. The explicit `pie github-issues` and `pie github-pulls` subcommands make unauthenticated read-only requests to the public GitHub API. They do not write or publish.
- Public API limits or unavailable endpoints are reported as errors; no network data is silently fabricated.

## Explicit non-goals

There is no backend, database, authentication layer, credential vault, autonomous code modification, GitHub write integration, vector database, or LLM dependency in the core CLI.

The optional OmniRoute Workbench integration is a separate local model-routing component and does not grant the core CLI repository write permissions.

## Extension policy

Start external integrations read-only. Preserve external IDs, source URLs, timestamps, and evidence lineage. Require explicit authorization and separate approval before any future external writes. Do not duplicate a canonical issue or create a second task record where an existing issue already serves as the authoritative work item.
