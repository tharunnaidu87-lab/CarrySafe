# Release status

## Implemented and verified

Persistent incidents, temporary controls, ownership acceptance, three-shift handover snapshots and recipient acknowledgment; deterministic continuity flags; closure requests with evidence, independent supervisor review and blocked premature closure; tenant-scoped roles, sessions, audit history, idempotency and optimistic version checks.

The official MCP server exposes 19 typed tools over Streamable HTTP. An actual client negotiated protocol 2025-11-25 and completed writes, reads and rejection paths. Manual form writes and assistant shortcuts use MCP. The React/TypeScript application compiles and provides assistant, operations, incident, handover, integrity and review screens. The database contains 100 synthetic seed records when freshly initialized.

Verification results: 29 backend tests pass locally, including three new hosted-bootstrap checks. The previous 26-test backend suite and five frontend unit tests passed in GitHub Actions, including PostgreSQL. CI for the bootstrap change is pending. See [exact verification](../TEST_REPORT.md).

## Implemented with remaining verification

Free-form assistant orchestration supports an OpenAI-compatible provider, persisted conversations and explicit write proposals, but was tested with mocked providers only. NVIDIA has been selected, and the current endpoint/model configuration is documented in [NVIDIA setup](NVIDIA_SETUP.md). No provider credentials were supplied. Without configuration, manual MCP mode is explicit.

Browser speech input/output and responsive UI are implemented, but browser inspection was blocked. Playwright coverage is prepared, not executed. Docker image build, PostgreSQL migrations and tests, real container MCP workflow and restart persistence passed in GitHub Actions. A schema-validated Render Blueprint is supplied; public hosting remains outstanding. Native startup scripts are supplied; Windows execution remains unverified.

## Missing before a credible complete submission

1. Configure a real function-calling provider and demonstrate a multi-tool conversational task and confirmed write.
2. Run the browser workflow, inspect desktop/mobile layouts, microphone support and keyboard interactions; fix discovered failures.
3. If using a hosted demo, supply a persistent database and host/origin settings, deploy and verify the public URL. Local demonstration is otherwise documented.
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

A free PostgreSQL 17 database and free Docker web service are created in Render Singapore. The service URL is https://carrysafe.onrender.com, not yet live or verified. Dashboard sign-in is complete. Database connection, NVIDIA API key and a unique demo password must be entered in service Environment settings before deploying. The initial build was canceled while these secrets are pending. Hosted demo initialization now requires explicit opt-in and PostgreSQL, seeds only an empty database, and preserves existing accounts. No live model result has been verified yet.
