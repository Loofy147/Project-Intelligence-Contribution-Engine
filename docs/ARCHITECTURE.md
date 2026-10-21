# Architecture

## Current components

- **Indexer**: discovers eligible text files, applies exclusions and size limits, and emits a versioned local JSON index.
- **Search**: tokenizes content, computes an explainable TF-IDF-style score, and returns paths and snippets.
- **Inventory**: detects language extensions and conventional project/tooling manifests without executing project code. Optional project metadata and explicit source allowlists live in `.project-intelligence.json`.
- **Task drafts**: creates observed-marker tasks for TODO/FIXME/XXX/HACK source lines; optionally reads unchecked checklists from explicitly declared Markdown paths; optionally projects active records from explicitly declared JSON registry collections; and keeps heuristic inventory hypotheses separate.
- **Task verification**: checks source-line, checklist and registry-record evidence against a fresh scan, then reports stale/unverified evidence and missing acceptance criteria.
- **GitHub issue/PR readers**: fetch public list endpoints via HTTP GET and capture titles, labels, states, timestamps, branch references and canonical source URLs. Bodies are not mirrored.
- **Work-plan projection**: sorts existing issues by an explicit leading `[P0]`–`[P3]` title prefix, and keeps issues, proposed PRs, canonical registry items and engine-generated draft findings separate.
- **CLI**: exposes index, search, inventory, GitHub snapshot, work-plan, task-draft and evidence-verification operations.

## Data flow

1. Scan the explicitly selected local project.
2. Skip common generated directories, symlinks, oversized files, binary files and likely credential-bearing paths.
3. Produce root-relative file metadata, content digests and a local text index.
4. Derive inventory signals using file names and conventional directory patterns.
5. Generate source-marker drafts; inspect only manifest-declared checklist paths and registry collections.
6. Preserve registry record identifiers/status/criteria/dependencies and a canonical per-record digest; do not replace their source status.
7. Verify saved evidence against the current source snapshot.
8. When explicitly requested, fetch public GitHub issue/PR metadata and preserve original external identifiers and URLs.
9. Build a read-only work-plan view without creating or changing external records.

## Manifest allowlists

- `checklist_paths` is an explicit list of project-relative Markdown files. Only unchecked Markdown checklist items in those files can become task drafts; fenced code examples and other Markdown files are ignored.
- `registry_work_item_sources` explicitly names a JSON file, collection, ID/title/status fields and the allowlisted active statuses. No general-purpose JSON traversal occurs.
- Manifest paths must be normalized project-relative paths and must be present in the index. Configured registry fields are validated as simple field names. Missing or malformed configured sources fail closed.
- A registry-backed record remains a projection of the canonical registry item. It is not a new issue, task in another service, or accepted state transition.

## Task semantics and authority

- `observed` means a marker/checklist is present in an indexed snapshot, or that a declared registry record has an allowlisted status. It does not independently prove that the work remains actionable.
- `hypothesis` means an inventory heuristic did not find a conventional marker; it does not prove the capability is absent.
- Drafts carry evidence, source digests, review steps and dependencies where available. Criteria from a registry are copied as source evidence; generated marker/checklist drafts retain empty criteria until reviewed.
- `pie verify-tasks` flags stale source digests, removed/changed checklist items, changed registry records and inventory hypotheses that are no longer detected.
- Missing acceptance criteria are blockers; freshness alone never implies approval. No record is execution-eligible until its explicit approval contract is met.
- Existing GitHub issues remain canonical work records. Pull requests remain proposed changes. The engine does not infer that a PR resolves an issue merely because titles look similar.
- Generated drafts cannot publish issues, assign work, create bounties, award XP, merge PRs, or edit scanned source code.

## Trust and safety boundaries

- Source scanning is read-only.
- Common secret-bearing paths and types are excluded, but rules are defense in depth, not a guarantee.
- A local JSON index contains copied project source text. Keep it local, ignore it in Git and review before sharing.
- Task excerpt output applies basic credential-pattern redaction; do not treat it as complete secret scanning.
- Report output avoids absolute local paths by default.
- Inventory is a filename/extension heuristic, not a semantic audit.
- Indexing and search remain local-only. The explicit `pie github-issues` and `pie github-pulls` subcommands make unauthenticated read-only requests to the public GitHub API. They do not write or publish.
- Public API limits or unavailable endpoints are reported as errors; no network data is silently fabricated.

## Explicit non-goals

There is no backend, database, authentication layer, credential vault, autonomous code modification, GitHub write integration, vector database or LLM dependency in the core CLI.

The optional OmniRoute Workbench integration is a separate local model-routing component and does not grant the core CLI repository write permissions.

## Extension policy

Start external integrations read-only. Preserve external IDs, source URLs, timestamps and evidence lineage. Require explicit authorization and separate approval before any future external writes. Do not duplicate a canonical issue or create a second task record where an existing issue or registry already serves as the authoritative work record.
