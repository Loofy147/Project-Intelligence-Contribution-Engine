# Optional AI review gateway contract

This adapter connects existing Project Intelligence task drafts to the existing OmniRoute Workbench. It is opt-in; core indexing, inventory, task drafting and verification remain local and dependency-free.

## Run

1. Start the OmniRoute service and Workbench according to the [Workbench guide](../integrations/omniroute-workbench/README.md).
2. Create one unique Workbench key for the project and export it to PIE_AI_API_KEY in your local shell. Do not put keys in project manifests, source code, GitHub workflow files, or command-line arguments.
3. Generate task drafts with `pie tasks /path/to/checkout`.
4. From the desired project directory, run `pie ai-review --tasks .project-intelligence/tasks.json --output .project-intelligence/ai-review.json`.
5. Review every recommendation and verify the source evidence independently.

The default endpoint is `http://127.0.0.1:20129/v1`. The endpoint can be overridden with `PIE_AI_BASE_URL` or `--base-url`. Non-loopback endpoints are rejected unless `--allow-remote` is explicitly provided. Remote use sends the selected task metadata to that remote service; inspect the payload and endpoint before allowing it.

## Data contract

The adapter transmits project ID/name plus a bounded allowlist of task ID, title, kind, classification, confidence, observed fact, hypothesis, evidence type/path/line/digest/canonical record ID/status, and existing acceptance criteria. It deliberately excludes source excerpts, repository file contents, environment variables, and provider credentials.

The OpenAI-compatible request routes as task class `reasoning`, requests JSON output, uses a single request attempt, and has a 64 KB request ceiling, 1 MB response ceiling, 180-second maximum timeout, and at most 50 tasks. Smaller task batches are the default.

## Response and safety

Every submitted task must receive exactly one recommendation. IDs must match the submitted tasks; priority and decision values are restricted to enumerated values; text and list lengths are bounded. Invalid or partial model output is rejected. Reports are written atomically to a separate output file.

Recommendations may include priority P0–P3, keep/defer/reject advice, rationale, missing evidence, and suggested acceptance criteria. They do not rewrite the underlying task, prove a defect, execute commands, create GitHub issues, merge code, award XP, or create a bounty. The human remains the decision authority.

The adapter is not a durable cost budget. The Workbench's RPM limiter is in-memory; the route currently has no persistent token/cost settlement. Do not use it as a spending guarantee or expose it publicly. Offline tests use a fake upstream and require no live API key.
