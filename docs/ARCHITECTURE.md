# Architecture

## Current boundary

The first release is a local Python package with three responsibilities:

- **Indexer**: discovers eligible text files, applies exclusions and size limits, and emits a versioned JSON document index.
- **Search**: tokenizes queries and content, computes a transparent TF-IDF-style score, adds small phrase/path boosts, and returns snippets.
- **CLI**: exposes index and search operations with clear exit codes and local file paths.

The index schema contains a schema version, resolved root path, creation timestamp, counts, and document entries. Each entry has a root-relative path, byte length, SHA-256 digest, and copied UTF-8 text.

## Trust and safety boundaries

- Scanning does not modify source files.
- Symlinks and common secret-bearing paths/file types are skipped.
- Exclusion rules are defense in depth, not a secret-detection guarantee.
- The JSON index may contain proprietary source text. It is ignored by Git, should remain local, and must be reviewed before sharing.
- Search results report files and snippets; they are not proof that a defect exists.
- No network calls or AI provider calls occur.

## Explicit non-goals for the MVP

There is no server, database, authentication layer, credential vault, autonomous code modification, GitHub write integration, embedding store, or LLM dependency.

## Planned extension seam

Future task extraction can consume an evidence record with project identifier, source path, source digest, observation, confidence, acceptance criteria, validation command, and status. A task must distinguish observed fact from hypothesis and must not become a bounty until scope and completion checks are reviewed.
