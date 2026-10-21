# OmniRoute Workbench

A local-first policy gateway placed in front of the MIT-licensed OmniRoute service. OmniRoute remains the provider adapter and routing engine; this companion adds project-scoped bearer keys, task-class routing, per-project output-token caps, request-rate limits, bounded request bodies, and metadata-only request logs. It does not copy upstream source.

## Boundaries

- Compose publishes both services only on 127.0.0.1.
- Each bearer key maps to a project policy; caller-supplied project headers are ignored.
- X-Task-Class accepts general, coding, reasoning, research, fast, cheap, or offline, subject to project policy.
- The proxy exposes only GET /v1/models, POST /v1/chat/completions, and unauthenticated GET /healthz. It does not proxy dashboard or administration routes.
- Prompts, completions, and authorization headers are not logged.
- The in-memory limiter resets on restart and is not durable billing or budget enforcement.
- This is an early personal-use layer, not a multi-user production boundary. Do not expose it publicly without TLS, durable quota accounting, key rotation/revocation, and operational monitoring.

## Setup

Requirements: Docker Compose v2 and OpenSSL.

1. Copy .env.example to .env.
2. Generate distinct secrets locally:

~~~sh
openssl rand -base64 48  # OmniRoute dashboard JWT secret
openssl rand -hex 32     # OmniRoute API key signing secret
openssl rand -hex 32     # OmniRoute storage encryption key
openssl rand -hex 32     # one unique key per Workbench project
~~~

3. Put generated values in .env, including the project-to-key JSON map. Do not commit .env.
4. Start OmniRoute: docker compose up -d omniroute.
5. Open http://localhost:20128, complete first-run setup, connect only providers you are authorized to use, and create a dedicated API key in the dashboard's Endpoints area. Set it as OMNIROUTE_API_KEY in .env.
6. Start the optional policy gateway: docker compose --profile workbench up -d --build workbench.
7. Check health: curl http://127.0.0.1:20129/healthz.
8. Check models using a Workbench project key: curl http://127.0.0.1:20129/v1/models -H 'Authorization: Bearer YOUR_PROJECT_API_KEY'.

Example coding request:

~~~sh
curl http://127.0.0.1:20129/v1/chat/completions \
  -H 'Authorization: Bearer YOUR_PROJECT_API_KEY' \
  -H 'Content-Type: application/json' \
  -H 'X-Task-Class: coding' \
  -d '{"messages":[{"role":"user","content":"Explain this function"}]}'
~~~

## Routing and tests

Edit config/policies.json to narrow allowed task classes, lower token caps, and reduce requests per minute. The route values are validated against a fixed allowlist so a policy cannot turn this service into an arbitrary-URL proxy or permit arbitrary model strings.

Run checks with Node.js 22 or newer:

~~~sh
npm test
npm run check
~~~

Tests use a fake upstream; no provider credentials or network access are needed.

## License

These companion files are MIT-licensed; see LICENSE. OmniRoute remains a separate dependency under its own license and third-party notices. Review both projects' notices for any combined distribution.
