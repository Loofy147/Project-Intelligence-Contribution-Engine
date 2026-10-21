# Project Intelligence & Contribution Engine

A local-first tool for understanding software projects and converting verified gaps into actionable contributions.

The first release is intentionally small: a dependency-free Python CLI that indexes readable project files, ranks search results with TF-IDF-style scoring, and returns source paths and evidence. It does not modify scanned repositories, call an AI service, or require a backend.

## Why this exists

Project work is spread across repositories, code, issues, and documents. This engine aims to make that work easier to inspect and prioritize, then provide an evidence-backed path from a discovered gap to a contribution task.

## MVP scope

- Scan a project directory using explicit exclusions and file-size limits.
- Exclude common generated directories and likely secret-bearing files.
- Build a local JSON search index with relative paths, SHA-256 digests, and text.
- Rank search results using TF-IDF-style term weights, with path and phrase bonuses.
- Expose indexing and searching through a simple command-line interface.
- Keep task generation, GitHub writes, semantic retrieval, and persistent services out of the first milestone.

## Requirements

- Python 3.11 or newer.
- No runtime third-party dependencies.

## Quick start

From the repository root:

~~~bash
python -m venv .venv
# Activate the environment for your platform, then:
python -m pip install -e .
pie index . --output .project-intelligence/index.json
pie search "authentication callback" --index .project-intelligence/index.json
~~~

You can also run the CLI without installing the package:

~~~bash
PYTHONPATH=src python -m project_intelligence.cli index .
PYTHONPATH=src python -m project_intelligence.cli search "TODO"
~~~

The default index path is `.project-intelligence/index.json`. The generated directory is ignored by Git.

## Privacy and safety

- Indexing is local-only; no content is sent to a service.
- The scanner is read-only with respect to source files.
- Common secret filenames and key material are excluded, but exclusion rules are not a guarantee that every secret will be detected.
- The index contains copied text from indexed files. Treat it as sensitive project data, keep it local, and do not commit it or share it without reviewing the contents.
- Never point this tool at credential stores or directories that you are not authorized to inspect.

## Design principles

1. Evidence before recommendations.
2. Local-first before services and infrastructure.
3. Read-only inspection before write automation.
4. Small interfaces and reproducible outputs.
5. No task becomes a bounty until its scope and acceptance criteria are verifiable.

## Development

~~~bash
python -m pip install -e ".[dev]"
python -m pytest
~~~

See [the architecture](docs/ARCHITECTURE.md), [the roadmap](docs/ROADMAP.md), and [contributing](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
