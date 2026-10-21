# Architecture

## Current boundary

The first release is a local Python package with five responsibilities:

- **Indexer**: discovers eligible text files, applies exclusions and size limits, and emits a versioned JSON document index.
- **Search**: tokenizes text, computes a transparent TF-IDF-style score, and returns source paths with excerpts.
- **Inventory**: detects language extensions and conventional project/tooling manifests without executing project code. Optional project metadata lives in `.project-intelligence.json`.
- **Task drafts**: turns explicit TODO/FIXME/XXX/HACK source markers into observed-fact drafts and turns inventory signals into separately labeled hypotheses.
- **CLI**: exposes index, search, inventory, and task-draft operations with local file outputs.

## Data flow

1. Read a chosen project directory.
2. Skip common generated directories, symlinks, oversized files, binary files, and likely credential-bearing paths.
3. Produce an in-memory index of readable text and SHA-256 source digests.
4. Derive a portable inventory: languages, recognized technology markers, and convention-based review signals.
5. Generate deterministic draft IDs using project identity and marker location/reason, then verify their source digest and line against future scans.
6. Write JSON/Markdown reports under `.project-intelligence/` by default.

## Task semantics and authority

- `observed` means a source marker was present at a specific file and line in the indexed snapshot; it does not prove the work is still needed.
- `hypothesis` means an inventory heuristic did not find a conventional marker; it does not prove a capability is absent.
- Each draft includes evidence, source digest where available, review steps, and empty acceptance criteria until a human defines them.
- `pie verify-tasks` compares stored source evidence and inventory hypotheses against a fresh scan without mutating the task file. Stale source digests or disappeared hypotheses are flagged.
- Missing acceptance criteria are reported as blockers; freshness alone never implies approval.
- Generated tasks are drafts. There is no automatic issue publishing, assignment, bounty creation, XP award, or source-code editing.

## Trust and safety boundaries

- Scanning does not modify source files.
- Symlinks and common secret-bearing paths/file types are skipped; the rules are defense in depth, not a guarantee.
- The JSON index contains copied project source text. Keep it local, ignore it in Git, and review before sharing.
- Task excerpt output applies basic credential-pattern redaction; do not treat that as a complete secret scanner.
- Markdown and JSON reports avoid printing the absolute machine path by default.
- Inventory results are filename/extension heuristics, not a semantic audit.
- No network calls or AI provider calls occur.

## Explicit non-goals

There is no server, database, authentication layer, credential vault, autonomous code modification, GitHub write integration, vector database, or LLM dependency.

## Planned extension seam

Future integrations can map reviewed tasks to existing issue/PR records. Any integration should begin read-only, preserve external identifiers and evidence lineage, and require explicit authorization before external writes. Do not duplicate task records where an existing issue already serves as the canonical work item.
