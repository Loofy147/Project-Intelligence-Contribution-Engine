# Project Intelligence & Contribution Engine

A local-first tool for understanding software projects and converting verified gaps into reviewable contribution work.

The Python CLI indexes readable project files, ranks keyword search results, inventories common technology markers, imports explicitly configured work-item registries, snapshots public GitHub issues and pull requests, and creates an issue-first work plan. It does not modify scanned source repositories, change GitHub records, or create funded bounties.

## Start here (including AI coding agents)

- **Professional operating standard:** [Operating charter](docs/OPERATING-CHARTER.md)
- **Mandatory agent instructions:** [`AGENTS.md`](AGENTS.md)
- **Do the task step by step:** [Execution playbook](docs/EXECUTION-PLAYBOOK.md)
- **Choose a gate using dependencies and evidence:** [Dependency-gated roadmap](docs/ROADMAP.md)
- **Resolve open questions by falsification:** [Assumptions register](docs/ASSUMPTIONS-REGISTER.md)
- **Find the correct code/tests/docs:** [Repository map](docs/REPOSITORY-MAP.md)
- **Create well-defined work:** [Work-item template](docs/WORK-ITEM-TEMPLATE.md)
- **Transfer work without losing state:** [Session handoff template](docs/SESSION-HANDOFF-TEMPLATE.md)
- **Review checklist:** [Pull request template](.github/pull_request_template.md)

Agents and contributors should treat the request as an outcome, identify the missing professional work themselves, research relevant approaches, inspect the actual state, implement the smallest complete solution, verify it, and update the canonical project records. Do not wait for the user to enumerate standard concerns. A plan alone is not completion when safe implementation is possible. Use the charter proportionately: it sets the quality floor, not a requirement for unnecessary ceremony.

## Capabilities

- Scan local projects with file-size limits and exclusions for common generated and secret-bearing paths.
- Build a local JSON index with relative paths, SHA-256 digests, and copied UTF-8 text.
- Search indexed files using explainable TF-IDF-style ranking.
- Detect common language extensions, packaging manifests, test paths, and CI markers without executing repository code.
- Produce Markdown/JSON inventory reports and separate observed signals from hypotheses.
- Draft tasks from source TODO/FIXME/XXX/HACK markers.
- Optionally read unchecked Markdown items only from manifest-declared `checklist_paths`; fenced examples and unconfigured documents are ignored.
- Optionally project nonterminal work items from manifest-declared JSON registries, preserving canonical IDs, status, acceptance criteria, dependencies, record digests and source pointers.
- Verify source-line, checklist and registry evidence freshness and report missing acceptance criteria.
- Fetch public GitHub issue and PR metadata via read-only GET requests.
- Build a work plan that keeps canonical issues, PR proposals, repository-registry items, and engine-generated draft findings distinct.
- Compare previous/current GitHub issue and optional paired PR snapshots to expose metadata changes without inferring closure, deletion, issue/PR linkage, or task completion.
- Audit explicit GitHub issue/PR cross-reference events while preserving source IDs, URLs, event evidence, repository scope, and unknown completion state.

## Requirements

- Python 3.11 or newer.
- No runtime third-party dependencies for the core CLI.
- Public GitHub API access is required only for `github-issues` and `github-pulls`.

## Quick start

~~~bash
python -m venv .venv
# Activate the environment for your platform, then:
python -m pip install -e ".[dev]"
python -m pytest
pie index . --output .project-intelligence/index.json
pie search "authentication callback" --index .project-intelligence/index.json
pie inventory . --output .project-intelligence/inventory.md
pie tasks .
pie verify-tasks .
~~~

Generated local index/task output lives in `.project-intelligence/`, which is ignored by Git. The index contains copied source text, so keep it local and review it before sharing.

## Project manifests

An optional `.project-intelligence.json` file registers project identity and can explicitly select planning sources. The engine does not infer that every Markdown checkbox or every JSON array is a task list. See [the manifest reference](docs/PROJECT-MANIFEST.md).

Example for a repository with a canonical typed registry:

~~~json
{
  "schema_version": 1,
  "id": "context-swarm",
  "name": "Context Swarm",
  "repository_url": "https://github.com/Loofy147/Context-swarm",
  "registry_work_item_sources": [
    {
      "path": "swarm/registry.json",
      "collection": "work_items",
      "id_field": "work_item_id",
      "title_field": "title",
      "status_field": "status",
      "active_statuses": ["ready", "in_progress", "blocked", "review"]
    }
  ]
}
~~~

Only records in the named collection whose status is explicitly allowlisted are projected. They remain anchored to the registry; no duplicate issue or external task is created.

## Build a plan from existing GitHub records

The following example snapshots public issues and PRs without changing them, then creates a local work-plan report:

~~~
mkdir -p .project-intelligence

pie github-issues Loofy147/Contribution-bounties-centre- \
  --state open \
  --json-output .project-intelligence/contribquest-issues.json \
  --markdown-output .project-intelligence/contribquest-issues.md

pie github-pulls Loofy147/Contribution-bounties-centre- \
  --state open \
  --json-output .project-intelligence/contribquest-pulls.json \
  --markdown-output .project-intelligence/contribquest-pulls.md

pie tasks /path/to/local/contribquest-checkout \
  --json-output .project-intelligence/contribquest-drafts.json \
  --markdown-output .project-intelligence/contribquest-drafts.md

pie workplan \
  --issues .project-intelligence/contribquest-issues.json \
  --pulls .project-intelligence/contribquest-pulls.json \
  --tasks .project-intelligence/contribquest-drafts.json \
  --json-output .project-intelligence/contribquest-workplan.json \
  --markdown-output .project-intelligence/contribquest-workplan.md
~~~

Replace `/path/to/local/contribquest-checkout` with a local checkout before running the task generator. GitHub commands use public API GET requests and can be affected by rate limits. No authentication is requested and no issue or PR is modified. The work plan reads explicit leading `[P0]`–`[P3]` prefixes from issue titles; it does not infer issue/PR relationships based on similar wording.

## Compare source snapshots

Capture snapshots at two points, using the same repository. For a complete state comparison, request `--state all` at both points. Then compare them:

~~~bash
pie github-issues OWNER/REPO --state all --json-output .project-intelligence/issues-after.json
pie compare-snapshots --previous-issues .project-intelligence/issues-before.json --current-issues .project-intelligence/issues-after.json
~~~

For pull requests, pass both `--previous-pulls` and `--current-pulls`. The command is read-only. Missing records are described as absent from the current snapshot, not closed or deleted; metadata differences do not prove the work is complete.

## Audit explicit GitHub relationships

Use the snapshots as the defined target set. The command reads each selected record's GitHub timeline and keeps only actual `cross-referenced` events.

~~~bash
pie github-issues OWNER/REPO --state open
pie github-pulls OWNER/REPO --state open
pie github-relations \
  --issues .project-intelligence/OWNER--REPO-issues.json \
  --pulls .project-intelligence/OWNER--REPO-pulls.json
~~~

Replace `OWNER/REPO` and the generated filenames with the actual repository and files. The audit defaults to a maximum of 50 target records; raise `--max-records` explicitly when needed (maximum 500). It writes JSON and Markdown reports under `.project-intelligence/`.

An internal relationship is emitted only when the GitHub timeline event identifies the source record and its repository matches the audited repository. External or unverified references are reported separately. A reference is not proof that a PR fixes, closes, or completes an issue. The audit is limited to the supplied snapshots; absence of an event does not prove that no relationship exists.

## Privacy and authority boundaries

- Source scanning does not modify the project being scanned.
- Common secret filenames and key material are excluded, but exclusion rules cannot guarantee detection of all secrets.
- Task excerpts apply basic credential-pattern redaction; this is not a secret scanner.
- Inventory results are filename/extension heuristics, not a semantic code audit.
- `observed` source markers/checklist items and `hypothesis` review candidates are distinct evidence classes. All require review.
- Registry-backed items preserve an existing source record; they are not independently accepted by the engine.
- GitHub issue records remain canonical work records; PRs are proposals, not proof of accepted work.
- No task is automatically published, assigned, merged, or converted into a funded bounty.
- GitHub snapshot commands read titles, labels, states, timestamps, refs, and canonical URLs. They deliberately omit issue/PR bodies.
- Verification is read-only; a fresh source digest does not approve a task or complete a project.

## Optional AI routing integration

The core Project Intelligence CLI does not require an AI service. For optional project-scoped model access, see the [OmniRoute Workbench integration](integrations/omniroute-workbench/README.md). It uses a separate [OmniRoute service](https://github.com/diegosouzapw/OmniRoute); review the integration guide's security limits before using it.

### Optional structured AI task review

The optional **pie ai-review** command sends a bounded allowlist of task metadata to the [OmniRoute Workbench](integrations/omniroute-workbench/README.md); it deliberately excludes source excerpts and file contents. It requires a project-scoped Workbench key in the **PIE_AI_API_KEY** environment variable. The default endpoint is loopback at http://127.0.0.1:20129/v1; remote gateways require the explicit **--allow-remote** flag. The result is a separate advisory report and never changes task state.

~~~
export PIE_AI_API_KEY='YOUR_PROJECT_WORKBENCH_KEY'
pie ai-review --tasks .project-intelligence/tasks.json --output .project-intelligence/ai-review.json
unset PIE_AI_API_KEY
~~~

See the [AI review gateway contract](docs/AI-REVIEW-GATEWAY.md) and [open-source reuse research](docs/OSS-REUSE-RESEARCH.md). Model output is untrusted; verify every recommendation before acting.

## Planning contract tests

The core test suite also validates the structure of `docs/ASSUMPTIONS-REGISTER.md` and `docs/ROADMAP.md`. It checks status vocabularies, owner/falsification/evidence/scenario requirements, and that gate dependencies and linked assumption IDs refer to declared records. These tests protect document structure; they do not decide whether the underlying evidence or owner decisions are substantively correct.

## Development

~~~
python -m pip install -e ".[dev]"
python -m pytest
pie --help
~~~

See the [architecture](docs/ARCHITECTURE.md), the [roadmap](docs/ROADMAP.md), the [manifest specification](docs/PROJECT-MANIFEST.md), and [contributing](CONTRIBUTING.md).

To evaluate public project snapshots, run the **Evaluate real projects** GitHub Actions workflow. It checks out targets without persisting target-repository write credentials and uploads per-project inventory, issue/PR snapshots, tasks, verification and work-plan reports as 14-day artifacts.

## License

MIT. See [LICENSE](LICENSE).
