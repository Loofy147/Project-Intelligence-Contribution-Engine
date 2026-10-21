# Repository Task Handoff

> Replace every bracketed placeholder with an observed value. Delete sections only when they truly do not apply. Never include secrets or copied source indexes.

## Repository state

- **Repository:** https://github.com/Loofy147/Project-Intelligence-Contribution-Engine
- **Date/time and timezone:** [ISO 8601]
- **Branch:** [exact branch]
- **HEAD SHA:** [full SHA]
- **Working tree:** [clean / changed; identify uncommitted files]
- **Default branch baseline:** [SHA, if inspected]
- **Canonical task:** [issue/PR/registry item URL and ID, or “direct user request”]

## Objective

[One or two sentences stating the requested result.]

## Operating coverage

- **User/business outcome addressed:** [outcome and success signal]
- **Professional areas assessed:** [product/business, architecture, data, security/privacy, UX, testing, operations, licensing, integrations, research, contribution/agent guidance]
- **Tools/APIs/MCPs/datasets evaluated:** [what was relevant, what was used or rejected, and why]
- **Research references:** [sources/version/freshness; note if none materially changed the decision]
- **Canonical roadmap gate and assumptions:** [gate IDs; OPEN assumptions and selected scenario]

## Existing context recovered

- **Notion operating records searched/fetched:** [page names and URLs; note access limits]
- **Project baselines/handoffs and canonical work items:** [source IDs/URLs and which was authoritative]
- **Relevant account/integration/provider records inspected:** [metadata and current permission evidence; never include secret values]
- **Prior research/decisions reused:** [links and freshness check]
- **Conflicts/unavailable sources:** [exact uncertainty; do not ask the user to repaste data until available sources were checked]

## Evidence inspected

- [File/function/test/source record and what it proved.]
- [Relevant CI/workflow evidence with URL and date.]
- **Not inspected / stale evidence:** [be explicit.]

## Changes made

| Path | Change | Why |
|---|---|---|
| `[path]` | [what changed] | [acceptance criterion] |

## Validation evidence

| Command/check | Result | Evidence / limitation |
|---|---|---|
| `[exact command]` | [PASS / FAIL / NOT RUN] | [observed output or reason] |

Do not call a check “passed” if it was only planned or inferred. Distinguish local tests, CI, static inspection, and live acceptance.

## Decisions and constraints

- **Decisions:** [decision + reason + source]
- **Assumptions:** [assumption and how it could be disproved]
- **Security/privacy/license risks:** [risk and control]
- **External state changed:** [normally “none”; enumerate exact authorized writes if any]
- **Outstanding blockers:** [exact missing fact or permission]

## Acceptance criteria status

- [x] [criterion met — cite evidence]
- [ ] [criterion not met — explain why]

## Exact next action

[One imperative task that can be started immediately, naming the file/test/issue/command. Avoid “continue improving” or “review everything.”]

## Startup instruction for the next session

Read `AGENTS.md`, `docs/OPERATING-CHARTER.md`, `docs/EXECUTION-PLAYBOOK.md`, and `docs/REPOSITORY-MAP.md`. For cross-project work, also read `docs/PORTFOLIO-CONTEXT.md` and verify each relevant repository independently. Recheck the current repository HEAD and working tree before trusting this handoff. Then execute the exact next action above, validate it, and update the canonical handoff/task record.
