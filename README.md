# Project Intelligence & Contribution Engine

A local-first tool for understanding software projects and converting verified gaps into reviewable contribution drafts.

The first release is a dependency-free Python CLI. It indexes readable project files, supports ranked keyword search, inventories languages and project markers, and emits draft contribution tasks with source evidence. It does not modify scanned source files, call an AI service, or require a backend.

## Capabilities

- Scan local projects with file-size limits and exclusions for common generated and secret-bearing paths.
- Build a local JSON index with relative paths, SHA-256 digests, and copied UTF-8 text.
- Search indexed files using explainable TF-IDF-style ranking.
- Detect common language extensions, packaging manifests, test paths, and CI workflow markers without executing project code.
- Generate a Markdown inventory with observed tooling signals and separately classified review hypotheses.
- Draft structured tasks from explicit TODO/FIXME/XXX/HACK markers and low-confidence inventory hypotheses.
- Preserve the difference between an observed fact and an unverified hypothesis. All tasks remain drafts; nothing is published or turned into a bounty.
- Recheck stored draft evidence with `pie verify-tasks .`; stale source evidence and hypotheses that no longer apply are flagged, and missing acceptance criteria are reported.

## Requirements

- Python 3.11 or newer.
- No runtime third-party dependencies.

## Quick start

~~~bash
python -m venv .venv
# Activate the environment for your platform, then:
python -m pip install -e ".[dev]"
pie index . --output .project-intelligence/index.json
pie search "authentication callback" --index .project-intelligence/index.json
pie inventory . --output .project-intelligence/inventory.md
pie tasks .
pie verify-tasks .
~~~

Default generated output lives in `.project-intelligence/`, which is ignored by Git. The task command writes `tasks.json` and a Markdown review report. You can select a JSON inventory with `pie inventory . --format json`.

To register a project, add an optional `.project-intelligence.json` in its root. See [the manifest format](docs/PROJECT-MANIFEST.md).

## Privacy and safety

- Indexing is local-only; no content is sent to a service.
- The scanner is read-only with respect to source files.
- Common secret filenames and key material are excluded, but exclusion rules cannot guarantee that every secret is detected.
- The JSON index contains copied file text. Keep it local and review it before sharing.
- Task excerpts apply basic credential-pattern redaction, but are not a substitute for secret scanning.
- Inventory detections are filename/extension heuristics, not a full semantic code audit.
- Hypothesis tasks are intentionally low-confidence review prompts. Confirm the gap before implementation.
- No task is automatically published, assigned, or converted into a funded bounty. Verification is read-only and does not approve tasks.

## Development

~~~bash
python -m pip install -e ".[dev]"
python -m pytest
pie --help
~~~

See [the architecture](docs/ARCHITECTURE.md), [the roadmap](docs/ROADMAP.md), [the project manifest specification](docs/PROJECT-MANIFEST.md), and [contributing](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
