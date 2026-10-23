# Product feedback — observed during this build

| Tool | Use and observed benefit | Friction / limitation | Use again? |
|---|---|---|---|
| Official Python MCP SDK 2.3.0 | Real typed tool discovery, Streamable HTTP and client calls; legacy 2025-11-25 negotiation verified | v2 requires its actual imports and typed structured return metadata. Expected rule errors need ToolError; a generic ValueError hides the explanation. A session manager cannot be started twice. | Yes, with version pinning and real transport tests. |
| FastAPI / Pydantic | Authenticated API, strict request schemas and interactive docs | MCP lifespan ownership needs explicit integration. Unexpected input fields must be rejected deliberately. | Yes; one backend can serve both the UI and MCP. |
| SQLAlchemy / Alembic | Shared transactional model, persistent receipts and version checks; migration executed on SQLite | Hosted PostgreSQL behavior still requires execution. Schema compatibility is not proof of runtime correctness. | Yes, with database-specific integration tests. |
| React / TypeScript / Vite | Connected screens, centralized API handling and production build | Browser inspection was unavailable after a policy block. Compilation cannot replace visual/end-to-end validation. | Yes; complete browser QA before release. |
| TanStack Query / React Router | Shared query invalidation and linked incident screens | Large list/handovers need further pagination work beyond the bounded demo view. | Yes. |
| Tailwind CSS / Lucide | Consistent visual controls and icons without a heavy animation stack | Visual polish has not been independently verified in a browser. | Yes, after accessibility review. |
| Pytest / Vitest | Negative authorization and lifecycle assertions; tested form conversions | Mock model tests validate control flow, not a real model's comprehension. | Yes; keep coverage tied to real failure modes. |
| Playwright | Prepared reproducible browser journey | Not executed because browser inspection was blocked in this environment. | Planned; not an execution claim. |
| Docker / Render | Deployment files and schema-validated hosting template prepared | Docker engine, PostgreSQL runtime and public deployment were not available/attempted. | Decision deferred until runtime verification. |

Amazon's gated Alexa+ developer tools were not used; the official FAQ permits our own frontend over a self-hosted MCP server. No feedback is invented for private Amazon tools, NVIDIA models or cloud services that were not actually called.
