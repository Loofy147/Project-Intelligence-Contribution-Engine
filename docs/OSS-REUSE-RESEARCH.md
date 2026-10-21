# Open-source reuse research and integration decisions

**Research snapshot:** 2026-10-21  
**Target:** Project Intelligence & Contribution Engine + the existing OmniRoute Workbench  
**Policy:** permissive licenses only for copied source; every source-level reuse must identify its exact upstream path, license, copyright notice, and local modifications.

This is a curated engineering review of projects that materially overlap our current needs; it is not a claim to enumerate every project on GitHub. We checked upstream project pages, license files, architecture/feature documentation, and current security or maintenance signals. A repository's top-level license is not assumed to apply to every subdirectory, bundled asset, model, or dependency.

## Decisions

| Project | License checked | Useful part | Decision |
|---|---|---|---|
| [OmniRoute](https://github.com/diegosouzapw/OmniRoute) | MIT | Multi-provider routing, task/model aliases, fallbacks, provider adapters, guardrails and MCP/A2A integration | **Selected runtime.** Keep upstream separate and use its compatible API. Pin a published image; re-check releases before upgrading. |
| [Bifrost](https://github.com/boelabs/bifrost) | MIT | Virtual keys, per-key model scopes, rate limits, explicit fallback chains, budgets, cost accounting, OpenTelemetry | **Design reference.** Do not run a second gateway alongside OmniRoute. Port missing budget/accounting patterns into one gateway boundary only after tests and a durable store are designed. |
| [Helicone AI Gateway](https://github.com/Helicone/ai-gateway) | Apache-2.0 in the upstream Cargo workspace | Routing strategies, rate/budget controls, observability and OpenTelemetry | **Alternative/reference, not another runtime.** Avoid a redundant gateway hop. Revisit only if a measured benchmark shows OmniRoute is not meeting a concrete need. |
| [Aider](https://github.com/Aider-AI/aider) | Apache-2.0 in LICENSE.txt | Repository map, concise symbol-aware context, Git/diff workflow, run lint/tests after edits | **Patterns adopted.** Add targeted context and reproducible validation to project-review workflows; do not import its full editor/LLM application. |
| [SWE-agent](https://github.com/SWE-agent/SWE-agent) | MIT | Agent-Computer Interface (ACI), bounded file/search tools, syntax checks on edits, clear output states | **Patterns adopted.** Keep tools narrow and observable. Do not let task text or model output trigger shell/GitHub actions. |
| [OpenHands](https://github.com/OpenHands/OpenHands) | MIT in the root LICENSE | Isolated runtime boundary for code execution and approval-oriented workflows | **Reference only for future execution.** Current engine remains a read-only scanner and review-draft generator; never execute repository code inside the indexing process. |
| [Pydantic AI](https://github.com/pydantic/pydantic-ai) | MIT | Structured outputs, typed dependency boundaries, evaluation datasets and separation of retry layers | **Patterns adopted without adding the package.** The optional adapter has an explicit JSON contract, strict local validation, one network attempt, and fake-upstream tests. |
| [DSPy](https://github.com/stanfordnlp/dspy) | MIT | Program/prompt evaluation against examples rather than subjective prompt iteration | **Evaluation reference.** Build a labelled task-quality benchmark before enabling prompt optimisation or model-generated task creation. |
| [Continue](https://github.com/continuedev/continue) | Apache-2.0 | Content-addressed indexing and local codebase context | **Technique reference only.** The repository page states it is read-only/archived; do not add it as a runtime dependency. |
| [LiteLLM](https://github.com/BerriAI/litellm) | MIT outside its enterprise directory; that directory has a separate license | Provider adapter coverage, budgets and fallbacks | **Hold; no code or runtime dependency added.** The repository has a license-scope exception, and October 2026 reporting describes critical gateway authorization/SSRF issues with a reported fix version. Validate the official advisories and patched release independently before reconsidering. |

## What was actually combined

1. **Project Intelligence remains the source of evidence.** It scans local repositories read-only, preserves source digests and canonical IDs, and distinguishes observations from hypotheses. This adopts the evidence-first principle rather than letting a model invent missing work.
2. **OmniRoute remains the only model/provider router.** The Workbench is a thin policy boundary around the separately licensed upstream service; no OmniRoute application source is vendored here.
3. **The optional pie ai-review adapter connects those systems.** It submits bounded task metadata only—not indexed source text, source excerpts, repository credentials, or environment variables—through a project-scoped Workbench key. Remote endpoints require explicit opt-in.
4. **Model output is treated as untrusted advice.** The adapter validates response shape, exact task IDs, enums, and lengths; writes a separate review report atomically; and cannot approve or edit any source task, create an issue, award XP, or create a bounty.
5. **Tests and evaluation precede autonomy.** Fake-upstream tests are deterministic and need no provider credentials. Any later write-enabled workflow must add preview, explicit approval, idempotency, audit trails, and tested rollback.

## Adopted practices to keep

- One API contract and one gateway hop; no gateway-on-gateway stack.
- Explicit project-to-key mapping, least privilege, per-project task allowlists, request/token limits, and bounded request bodies.
- Content/source evidence stays distinct from confidence or priority claims.
- Narrow tools, no implicit shell execution, and no model-authored write action.
- Strict structured response validation, bounded time and payload sizes, and no automatic retry multiplication.
- Request metadata may be logged; prompts, model responses, and authorization values should not be logged by the gateway.
- Build a labelled offline benchmark and measure false positives before embeddings or agent loops.
- Keep the default CLI standard-library-only. Add optional features as isolated adapters rather than imposing an AI runtime on all users.

## Open gaps

The Workbench's current requests-per-minute counter is in-memory and resets on restart. It is **not** durable cost accounting or a guaranteed spending budget. Usage telemetry, durable quota reservation/settlement, key rotation/revocation, streaming semantics, and end-to-end Docker/provider testing remain explicit follow-up work. Do not expose the gateway publicly until those controls and TLS are in place.

## Source links

- OmniRoute [README](https://github.com/diegosouzapw/OmniRoute), [MIT license](https://github.com/diegosouzapw/OmniRoute/blob/release/v3.8.52/LICENSE), [security policy](https://github.com/diegosouzapw/OmniRoute/blob/release/v3.8.52/SECURITY.md), and [Docker readiness guidance](https://github.com/diegosouzapw/OmniRoute/blob/release/v3.8.52/docs/guides/DOCKER_GUIDE.md).
- Bifrost [README and capability summary](https://github.com/boelabs/bifrost) and [MIT license](https://github.com/boelabs/bifrost/blob/main/LICENSE).
- Helicone [gateway features](https://github.com/Helicone/ai-gateway) and [Cargo license declaration](https://github.com/Helicone/ai-gateway/blob/main/Cargo.toml).
- Aider [repository map](https://github.com/Aider-AI/aider/blob/main/aider/website/docs/repomap.md) and [Apache-2.0 LICENSE.txt](https://github.com/Aider-AI/aider/blob/main/LICENSE.txt).
- SWE-agent [ACI design](https://github.com/SWE-agent/SWE-agent/blob/main/docs/background/aci.md) and [MIT license](https://github.com/SWE-agent/SWE-agent/blob/main/LICENSE).
- OpenHands [MIT license](https://github.com/OpenHands/OpenHands/blob/main/LICENSE).
- Pydantic AI [structured outputs](https://github.com/pydantic/pydantic-ai/blob/main/docs/output.md), [evaluation datasets](https://github.com/pydantic/pydantic-ai/blob/main/docs/evals.md), and [MIT license](https://github.com/pydantic/pydantic-ai/blob/main/LICENSE).
- DSPy [repository](https://github.com/stanfordnlp/dspy) and [MIT license](https://github.com/stanfordnlp/dspy/blob/main/LICENSE).
- Continue [license](https://github.com/continuedev/continue/blob/main/LICENSE) and [indexing design](https://github.com/continuedev/continue/blob/main/core/indexing/README.md); its current repository README says it is no longer actively maintained.
- LiteLLM [license scope](https://github.com/BerriAI/litellm/blob/main/LICENSE), [user/rate-limit docs](https://docs.litellm.ai/docs/proxy/users), and contemporaneous [ITPro](https://www.itpro.com/security/cyber-attacks/litellm-flaws-allow-full-admin-control-and-api-key-theft) / [TechRadar](https://www.techradar.com/pro/security/security-flaws-found-in-top-open-source-ai-gateway-litellm-vulnerabilties-could-affect-millions) reporting. The reporting is a reason to hold, not a substitute for the upstream advisory.

## Reproducibility and maintenance

- Research date is recorded above; re-check each upstream license, security advisory, release, and maintenance status before copying code or updating a pinned component.
- Exact license text must be retained when source code is copied. Apache-2.0 reuse also requires its applicable notice/patent terms and prominent modification notices; MIT reuse retains the copyright and permission notice.
- This change does not copy source code from Aider, Bifrost, Helicone, OpenHands, SWE-agent, Pydantic AI, DSPy, Continue, or LiteLLM. It integrates the separately licensed OmniRoute service and implements selected patterns in a small adapter. This avoids importing large dependency trees, mixed-license directories, or unrelated execution engines.
