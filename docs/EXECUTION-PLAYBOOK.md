# Task Execution Playbook

This is the canonical procedure for turning a request or tracked work item into a tested repository change. Follow it in order. The [Professional Operating Charter](OPERATING-CHARTER.md) defines the required professional coverage; this playbook turns it into the repeatable execution loop. The dependency-gated roadmap and assumptions register are the planning source of truth; do not replace them with dates or a second plan.

## 0. Interpret the outcome and perform professional discovery

Do not interpret a short request as a short checklist of responsibilities. Use the user's stated outcome and existing project context to determine the work necessary to deliver it. When more than one portfolio project is involved, consult [Portfolio Context](PORTFOLIO-CONTEXT.md), then verify each project's live canonical documents and current state; this index does not override their records. Before editing, inspect the actual repo/runtime, canonical records, current CI, and relevant tools/integrations. Identify missing product, business, architecture, data, security, UX, testing, operational, licensing, documentation, and contribution/agent-guidance concerns where material. Research authoritative standards, current vendor/API docs, datasets and maintained open-source alternatives when they could alter the decision. Select only capabilities that improve the outcome; do not add providers or complexity for their own sake. Record unknowns as assumptions or blockers, not facts. Ask only when a consequential decision has no defensible reversible default.

## 1. Choose the task source

Apply these rules in order:

1. **Direct user request:** implement the behavior or change the user actually requested.
2. **Named issue, PR, or work-item ID:** use that exact record. Read its body/criteria and linked implementation; do not substitute a similarly worded item.
3. **Existing repository-native registry:** use it only when the project manifest explicitly declares it and its status is on the allowlist. The registry stays authoritative.
4. **Roadmap continuation with no named task:** read `docs/ROADMAP.md` and `docs/ASSUMPTIONS-REGISTER.md`. Select a gate only when its dependencies are PASSED and required decisions are resolved. Among READY gates, prioritize safety/data integrity, downstream gates unblocked, the smallest decisive end-to-end test, then stable gate ID. Gate IDs are not a schedule.
5. **OPEN assumptions:** inspect the register entry before deciding. Run its falsification method when evidence can answer it; require the named owner's decision for product-policy choices. Do not silently pick a branch. Every OPEN entry must specify owner, falsification method, evidence, and scenario outcomes.
6. **No safe executable task:** do a focused inspection and identify the smallest missing fact or prerequisite. Do not invent tasks or report speculation as a confirmed defect.

Never promote a heuristic draft, a model suggestion, or a roadmap hypothesis above an existing canonical issue/registry record. Do not create duplicate work items just to make the task look actionable.

## 2. Establish the actual baseline

From the repository root, inspect the state before editing:

~~~bash
git status --short
git branch --show-current
git log -1 --oneline
git diff --stat
~~~

If a command cannot run because there is no local checkout or shell, state that limitation accurately. Do not imply that the remote repository was locally tested.

Read the relevant docs and the implementation/tests, not just the README. For roadmap work, read the gate and linked assumptions first; identify which branch the evidence permits. Find:
- the current code path for the behavior;
- its input and output contract;
- nearby tests and error paths;
- relevant workflow configuration;
- the canonical task's acceptance criteria;
- any security/privacy boundary touched by the change.

When a runnable checkout is available, capture baseline results before editing:

~~~bash
python --version
python -m pip install -e ".[dev]"
python -m pytest -q
pie --help
~~~

The supported core runtime is Python 3.11+. Optional Workbench tests are separate; see [the Workbench guide](../integrations/omniroute-workbench/README.md).

## 3. Convert the task into a small implementation contract

Before editing, write down (in the issue/PR description or scratch notes):

- **Observed problem:** cite a path, line, reproduction, failing test, or source record. Label assumptions as assumptions.
- **Expected result:** describe observable behavior, not just the code to write.
- **Acceptance checks:** make each condition independently testable.
- **Scope:** list expected files/modules and explicit non-goals.
- **Risk:** state whether secrets, network access, external writes, data formats, licenses, or migrations are involved.

If the repository already supplies acceptance criteria, preserve them and add clarification rather than replacing them. Use [the work-item template](WORK-ITEM-TEMPLATE.md) for new issue descriptions; never create a second tracker when a canonical record already exists.

## 4. Implement with the smallest correct change

1. Trace the existing data flow and follow the repository map.
2. Add a focused failing test for a behavior defect when practical.
3. Make the minimum change that makes the expected behavior true.
4. Preserve stable IDs, source pointers, digests, and schema/version compatibility unless the task explicitly requires a migration.
5. Fail closed on malformed allowlists, unsafe paths, invalid model output, untrusted identifiers, or unavailable network data. Do not silently fabricate fallback records.
6. Keep model recommendations advisory. They must not set task status or invoke external actions.
7. Update documentation when interfaces, data formats, commands, trust boundaries, or limitations change.
8. Do not add new dependencies, a service, persistence, or an integration just because it is convenient. Demonstrate the requirement first.

## 5. Validate in layers

Run the checks that match the change. Prefer the whole core suite; do not claim checks that were not run.

### Core Python changes

~~~bash
python -m pytest -q
python -m compileall -q src tests
pie --help
~~~

If package metadata or entry points changed, also run:

~~~bash
python -m pip install -e ".[dev]"
~~~

Use the README's safe local smoke path when indexing/CLI behavior changes. Generated output belongs under `.project-intelligence/`, which is Git-ignored:

~~~bash
pie index . --output .project-intelligence/index.json
pie search "authentication callback" --index .project-intelligence/index.json
pie inventory . --output .project-intelligence/inventory.md
pie tasks .
pie verify-tasks .
~~~

These commands inspect this repository. Remember that an index contains copied text; do not commit it or share it without review.

### OmniRoute Workbench changes

Run the documented tests in `integrations/omniroute-workbench/` using Node.js 22 or newer:

~~~bash
npm test
npm run check
~~~

Tests use a fake upstream and should not need live provider keys. Do not use real keys for unit tests. Check that listening ports remain loopback-only and that request/prompt/authorization data are not logged.

### Documentation-only changes

- Check every changed Markdown relative link against the actual repository paths.
- Verify commands and filenames against the README, `pyproject.toml`, implementation, or workflow—not memory.
- Check fenced code blocks and headings for clear, consistent Markdown.
- Run a relevant CI workflow if available; otherwise report exactly what was checked manually.

### Network/evaluation behavior

GitHub snapshot and real-project evaluation workflows can require network access and are separate from unit tests. Run them only when relevant. A target project's successful indexing is not proof that its application is correct. Preserve target repositories as read-only.

### Explicit relationship audit

To audit cross-reference links for a repository, first produce public GitHub issue/PR snapshots. Then run:

~~~bash
pie github-relations \
  --issues .project-intelligence/OWNER--REPO-issues.json \
  --pulls .project-intelligence/OWNER--REPO-pulls.json
~~~

Supply the correct snapshot paths; either input is optional, but at least one is required. Each record in the supplied snapshots becomes a timeline target. The default cap is 50 targets; increase `--max-records` deliberately if needed. The audit uses read-only GitHub timeline GET requests and writes a JSON report plus a Markdown summary.

Only an actual `cross-referenced` event with a grounded source record produces a relationship. An in-repository relation additionally requires repository identity to match. External/unverified sources are kept separate. The record includes direction, source/target IDs and URLs, event actor/time, timeline URL, and `verification_state=explicit_source_event_observed`; completion state stays unknown. Do not mark a linked issue resolved solely from that event. Missing events mean “not observed in the selected timelines,” not “no relationship exists.”

### Read-only source snapshot comparison

To compare two previously captured issue snapshots, optionally including matching pull-request snapshots:

~~~bash
pie compare-snapshots --previous-issues .project-intelligence/issues-before.json --current-issues .project-intelligence/issues-after.json --previous-pulls .project-intelligence/pulls-before.json --current-pulls .project-intelligence/pulls-after.json
~~~

Both PR paths must be supplied together or both omitted. Snapshots must refer to the same repository and supported schema. Use `--state all` for both time points if full-state comparison is needed. Filtered queries can omit records; absence never proves closure, deletion, resolution, or completion. The report compares visible metadata only and never changes source records or automatically links issues to PRs.

## 6. Review the change before declaring success

Inspect the entire final diff and answer every question:

- Does each changed line serve the requested task?
- Did the tests prove the new or corrected behavior?
- Are failure cases and malformed input handled?
- Did the change expose source text, secrets, tokens, absolute paths, or private data?
- Are external records still canonical and unmodified?
- Do docs accurately distinguish observed facts, hypotheses, recommendations, and unverified behavior?
- Are any TODOs, roadmap checkboxes, badges, version claims, or release notes being updated without evidence?
- Did any generated output or environment file enter the diff?

Do not mark a roadmap item complete merely because code exists or CI is green. The item's acceptance criteria must be met and the evidence recorded. Green unit tests do not substitute for required live acceptance or authorization tests.

## 7. Branch, commit, and PR behavior

- Preserve any pre-existing user changes; never reset, overwrite, or clean them away to obtain a tidy diff.
- Prefer a focused branch and pull request for reviewable repository changes when repository access allows it. Do not force-push or rewrite shared history.
- Use descriptive commit and PR titles. Summarize the problem, implementation, tests, limitations, and any migration or security implications.
- Include only evidence actually observed. Link an issue only where the source explicitly identifies the relationship or a maintainer confirms it.
- Do not close canonical issues, merge pull requests, publish a release, deploy, create funded bounties, or change external project state as an incidental side effect.

## 8. Handoff so another model can continue without this conversation

Update the task's canonical record where possible. If an assumption was evaluated, record its outcome, evidence, and scenario in `docs/ASSUMPTIONS-REGISTER.md`; update dependent gate states in `docs/ROADMAP.md` in the same change. For cross-session work, complete [the handoff template](SESSION-HANDOFF-TEMPLATE.md) with:
- repository URL, branch, exact HEAD SHA, and date;
- objective and canonical task source;
- exact files changed and their roles;
- commands executed and observed outcomes;
- current CI URLs or explicit “not checked”;
- decisions made, assumptions, blockers, and known risks;
- one next action that can be executed without re-planning.

Do not include credentials, raw environment files, private task payloads, or full copied project indexes in a handoff.

## Stop and escalate only for these conditions

Pause the consequential part of the task when it would require an unapproved external write, publishing/deployment/spend, irreversible deletion, a credential or privilege change, an unresolved licensing/rights decision, a destructive data migration, or a product decision that materially changes the requested behavior. Continue safe investigation, write tests, document the blocker, and identify the smallest decision needed. Do not use a blocker as an excuse to skip unrelated, reversible work.
