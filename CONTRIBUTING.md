# Contributing

## Start here

Before changing code, apply the [professional operating charter](docs/OPERATING-CHARTER.md), then follow the repository's mandatory [agent instructions](AGENTS.md) and [task execution playbook](docs/EXECUTION-PLAYBOOK.md). Use the [repository map](docs/REPOSITORY-MAP.md) to find the implementation and tests. Choose work from the dependency-gated [roadmap](docs/ROADMAP.md); resolve relevant open assumptions using the [assumptions register](docs/ASSUMPTIONS-REGISTER.md). These instructions apply to human contributors and AI coding agents.

## Ground rules

- Keep the first release local-first and dependency-light.
- Link recommendations to repository evidence; do not describe guesses as confirmed defects.
- Never commit generated search indexes or credentials.
- Prefer small functions, clear error messages, and tests for observable behavior.
- Avoid adding a service, database, model provider, or background worker without a demonstrated requirement.
- Research suitable existing standards, APIs, MCPs, datasets, tools, and open-source implementations when they may materially help; assess rights, costs, security, maintenance and fit before adoption.
- Do not make users enumerate routine professional concerns. Identify necessary architecture, testing, security, UX, operational, business, documentation, and contribution/agent-guidance work from the outcome.
- Preserve canonical issue and registry records; do not create duplicate backlogs.
- Keep scanned repositories and GitHub records read-only unless a separately authorized feature with the required controls is implemented.

## Local setup

~~~bash
python -m pip install -e ".[dev]"
python -m pytest
pie --help
~~~

## Change workflow

1. Identify the canonical task and write testable acceptance criteria. Use [the work-item template](docs/WORK-ITEM-TEMPLATE.md) only when a new work item is genuinely needed.
2. Inspect the current code path, related tests, schemas, and trust boundary before editing.
3. Add or update focused tests for the observable behavior.
4. Implement the smallest correct change; avoid unrelated refactoring.
5. Run the full test suite and applicable CLI/integration checks. Record checks that could not run.
6. Update the README or architecture notes when interfaces, data formats, commands, or trust boundaries change.
7. Review the full diff for secrets, generated files, accidental side effects, broken documentation links, and unsupported claims.
8. If this change affects a gate or assumption, update the roadmap and assumptions register together and record the selected scenario. Every OPEN item needs an owner and a falsification method.
9. If a change adds issue/PR relationships, preserve canonical source IDs, URLs, relation evidence and verification state. Never infer relationships from text similarity or treat a reference as proof of completed work.
10. Summarize concrete evidence, exact validation results, limitations, and one next action in the PR. Do not claim that a test or deployment passed unless you observed the result.

For cross-session work, complete [the session handoff template](docs/SESSION-HANDOFF-TEMPLATE.md) and re-check repository HEAD before continuing.
