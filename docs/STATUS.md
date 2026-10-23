# Release status

## Implemented and verified

Persistent incidents, temporary controls, ownership acceptance, three-shift handover snapshots and recipient acknowledgment; deterministic continuity flags; closure requests with evidence, independent supervisor review and blocked premature closure; tenant-scoped roles, sessions, audit history, idempotency and optimistic version checks.

The official MCP server exposes 19 typed tools over Streamable HTTP. An actual client negotiated protocol 2025-11-25 and completed writes, reads and rejection paths. Manual form writes and assistant shortcuts use MCP. The React/TypeScript application compiles and provides assistant, operations, incident, handover, integrity and review screens. The database contains 100 synthetic seed records when freshly initialized.

Verification results: 29 backend tests pass locally, including three new hosted-bootstrap checks. GitHub Actions run 39928359754 passed for this change, including backend, frontend, PostgreSQL and Docker jobs. See [exact verification](../TEST_REPORT.md).

## Implemented with remaining verification

Free-form assistant orchestration supports an OpenAI-compatible provider, persisted conversations and explicit write proposals, but was tested with mocked providers only. NVIDIA has been selected, and the current endpoint/model configuration is documented in [NVIDIA setup](NVIDIA_SETUP.md). The user entered provider configuration in Render; live model behavior is not yet verified. Without configuration, manual MCP mode is explicit.

Browser speech input/output and responsive UI are implemented, but full browser workflow inspection remains pending. The hosted login page has been inspected; earlier local browser inspection was blocked. Playwright coverage is prepared, not executed. Docker image build, PostgreSQL migrations and tests, real container MCP workflow and restart persistence passed in GitHub Actions. A schema-validated Render Blueprint is supplied; the direct-created Render service is now live and its database health check passes. Native startup scripts are supplied; Windows execution remains unverified.

## Missing before a credible complete submission

1. Verify the configured NVIDIA provider with a multi-tool conversational task and confirmed write.
2. Run the browser workflow, inspect desktop/mobile layouts, microphone support and keyboard interactions; fix discovered failures.
3. Complete authenticated workflow checks on the hosted demo. The public login page and database health check already pass.
4. Record the authentic under-three-minute demo, replace the team/video placeholders and submit the final project through Devpost. Nothing has been submitted automatically.

Additional production work includes staff lifecycle provisioning, account recovery/SSO, stronger distributed rate limiting, PostgreSQL contention testing, operational backups and tamper-evident audit retention. The initial operator CLI provisions only an empty organization and its first supervisor. OAuth-based external MCP distribution is not implemented. The interface and fixtures currently target the India-timezone demonstration.

## Delivery map

- Setup and configuration: [README](../README.md)
- Local demo accounts, reset command and 2:55 narration: [demo guide](DEMO_GUIDE.md)
- SDK, protocol, endpoint and all tools: [MCP](MCP.md)
- API and architecture: [API](API.md), [architecture](ARCHITECTURE.md)
- Deployment options and remaining steps: [deployment](DEPLOYMENT.md)
- Submission text and manual checklist: [submission draft](DEVPOST_SUBMISSION.md)
- Dataset boundaries and license inventory: [data sources](DATA_SOURCES.md), [third-party notices](../THIRD_PARTY_NOTICES.md)
- Actual observations: [product feedback](PRODUCT_FEEDBACK.md), [friction log](FRICTION_LOG.md)

## Hosting progress

The free Docker service is live at https://carrysafe.onrender.com in Render Singapore, backed by PostgreSQL 17. Deploy `dep-dbdi6mt9fdbs73b7lo40` serves source commit `3e51f5d4d78b50c81e3c106e0801bd3abdfed212`. On 23 October 2026, `/api/health` returned HTTP 200 with `status=ok` and `database=connected`. Startup logs confirm creation of 100 synthetic incidents, three accounts and two pending handovers. The public login page loaded in Chrome. Authenticated browser and live NVIDIA checks await user sign-in. The database remains blocked to external connections; the read-only connector cannot query it, and its allowlist was not widened. The free database expires 22 November 2026.
