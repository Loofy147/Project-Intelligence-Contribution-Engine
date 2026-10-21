# Project Intelligence & Contribution Engine

A local-first tool for understanding software projects and converting verified gaps into reviewable contribution work.

The Python CLI indexes readable project files, ranks keyword search results, inventories common technology markers, drafts evidence-backed review tasks, snapshots public GitHub issues and pull requests, and creates an issue-first work plan. It does not modify scanned source repositories, change GitHub records, or create funded bounties.

## Capabilities

- Scan local projects with file-size limits and exclusions for common generated and secret-bearing paths.
- Build a local JSON index with relative paths, SHA-256 digests, and copied UTF-8 text.
- Search indexed files using explainable TF-IDF-style ranking.
- Detect common language extensions, packaging manifests, test paths, and CI markers without executing repository code.
- Produce Markdown/JSON inventory reports and separate observed signals from hypotheses.
- Draft tasks from explicit TODO/FIXME/XXX/HACK source markers and review hypotheses.
- Verify task evidence freshness and report missing acceptance criteria.
- Fetch public GitHub issues and PR metadata via read-only GET requests.
- Build a work plan that keeps canonical issues, proposed PRs, and engine-generated draft findings distinct.

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

## Build a plan from existing GitHub records

The following example snapshots public issues and PRs without changing them, then creates a local work-plan report:

~~~bash
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

## Project manifest

An optional `.project-intelligence.json` file gives a project a stable ID and metadata. See [the manifest format](docs/PROJECT-MANIFEST.md).

## Privacy and authority boundaries

- Source scanning does not modify the project being scanned.
- Common secret filenames and key material are excluded, but exclusion rules cannot guarantee detection of all secrets.
- Task excerpts apply basic credential-pattern redaction; this is not a secret scanner.
- Inventory results are filename/extension heuristics, not a semantic code audit.
- `observed` markers and `hypothesis` review candidates are different evidence classes. Both require review.
- GitHub issue records remain canonical work records; PRs are proposals, not proof of accepted work.
- No task is automatically published, assigned, merged, or converted into a funded bounty.
- The GitHub snapshot commands read titles, labels, states, timestamps, refs, and canonical URLs. They deliberately omit issue/PR bodies.
- Verification is read-only; a fresh source digest does not approve a task or complete a project.

## Optional AI routing integration

The core Project Intelligence CLI does not require an AI service. For optional project-scoped model access, see the [OmniRoute Workbench integration](integrations/omniroute-workbench/README.md). It uses a separate [OmniRoute service](https://github.com/diegosouzapw/OmniRoute); review the integration guide's security limits before using it.

## Development

~~~bash
python -m pip install -e ".[dev]"
python -m pytest
pie --help
~~~

See [the architecture](docs/ARCHITECTURE.md), [the roadmap](docs/ROADMAP.md), [the manifest specification](docs/PROJECT-MANIFEST.md), and [contributing](CONTRIBUTING.md).

To evaluate public project snapshots, run the **Evaluate real projects** GitHub Actions workflow. It checks out targets without persisting target-repository write credentials and uploads per-project inventory, issue/PR snapshots, task drafts, and work-plan reports as 14-day artifacts.

## License

MIT. See [LICENSE](LICENSE).
