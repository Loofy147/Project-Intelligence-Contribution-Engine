# Project registration manifest

The optional `.project-intelligence.json` file gives a project a stable identity and human-readable metadata. It is JSON so the MVP remains dependency-free.

Example:

~~~json
{
  "schema_version": 1,
  "id": "contribquest",
  "name": "ContribQuest",
  "description": "A contribution bounty and progress platform.",
  "repository_url": "https://github.com/Loofy147/contribution-network",
  "tags": ["contributions", "product"]
}
~~~

Fields:

- `schema_version`: currently `1`.
- `id`: stable project key; letters, numbers, dots, underscores, colon, slash, and hyphen are permitted.
- `name`: required, non-empty display name.
- `description`: optional plain-text description.
- `repository_url`: optional HTTPS URL.
- `tags`: optional list of plain-text strings.

Unknown fields are rejected to catch configuration mistakes early. Keep credentials, access tokens, personal data, and private notes out of the manifest. The inventory does not connect to the URL; it only records the declared reference.
