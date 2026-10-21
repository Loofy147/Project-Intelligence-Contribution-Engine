# Project registration manifest

The optional `.project-intelligence.json` file gives a project a stable identity and human-readable metadata. It can also explicitly allowlist planning inputs. This JSON format keeps the MVP dependency-free.

## Basic example

~~~json
{
  "schema_version": 1,
  "id": "contribquest",
  "name": "ContribQuest",
  "description": "A contribution bounty and progress platform.",
  "repository_url": "https://github.com/Loofy147/Contribution-bounties-centre-",
  "tags": ["contributions", "product"]
}
~~~

Fields:

- `schema_version`: currently `1`.
- `id`: stable project key; letters, numbers, dots, underscores, colon, slash and hyphen are permitted.
- `name`: required, non-empty display name.
- `description`: optional plain-text description.
- `repository_url`: optional HTTPS URL; the engine records it but does not connect to it.
- `tags`: optional list of plain-text strings.

## Explicit Markdown checklist paths

Use `checklist_paths` only for planning documents whose unchecked items are intended to represent active work. The parser only reads those files; it skips items inside fenced code examples. Unlisted Markdown files, including acceptance specifications and examples, are not mined for checkboxes.

~~~json
{
  "schema_version": 1,
  "id": "example-project",
  "name": "Example Project",
  "checklist_paths": [
    "plans/current-work.md"
  ]
}
~~~

Each path must be normalized, relative to the project root and end in `.md` or `.markdown`. Parent-directory traversal, absolute paths, backslashes, duplicates, missing files and paths that were not indexed are rejected. A checklist item becomes a review-required draft with its source path/line, section and source digest. It does not mutate the Markdown item.

## Typed JSON registry work-item sources

Use `registry_work_item_sources` when the repository already owns a canonical typed work queue. The configuration requires a relative JSON path, array collection name, identifier/title/status fields and an explicit allowlist of active statuses.

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
      "active_statuses": [
        "ready",
        "in_progress",
        "blocked",
        "conflicted",
        "needs_information",
        "review"
      ]
    }
  ]
}
~~~

Optional mapping fields are available when the source schema uses different names: `acceptance_criteria_field`, `dependencies_field`, `priority_field`, `kind_field`, `required_evidence_field`, and `requested_by_field`. Each defaults to the common field name.

Rules:

- Unknown manifest fields and unknown registry mapping fields are rejected to expose configuration mistakes.
- Registry paths must be normalized project-relative `.json` files and must be present in the index.
- JSON field names must be simple identifier-like names, not expressions or paths.
- Only records whose configured status matches an explicitly allowlisted active status are projected.
- Active records require unique stable IDs and non-empty titles. Acceptance criteria, dependencies and required-evidence fields, when present, must be lists of strings.
- A projected item preserves the canonical source path, collection position/pointer, source ID/status, acceptance criteria and dependencies, plus an individual record digest.
- The source registry remains authoritative. The engine does not mark the item accepted, edit its status, create a second issue, or publish a bounty.
- Verification checks the individual record digest, so an unrelated registry item being added should not invalidate evidence for this item; changes to the item itself do.

Do not store credentials, access tokens, personal data or private notes in the manifest. Registry/list extraction is intentionally opt-in rather than a crawler over every JSON or Markdown file.
