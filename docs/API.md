# Application API

Interactive API documentation: `/docs`. Authentication is required for operational endpoints.

| Endpoint | Behavior |
|---|---|
| POST /api/login | Email/password -> HttpOnly cookie |
| POST /api/logout | Revoke current session |
| GET /api/me | Authenticated identity, mode and AI availability |
| GET /api/health | Database connectivity |
| GET /api/tools | Typed manual-form schemas |
| GET /api/data/{read_tool} | Shared-service read, scoped to caller |
| POST /api/operations/{tool} | Confirmed manual request -> actual MCP client |
| GET /api/mcp/tools | Actual MCP discovery and negotiated protocol |
| POST /api/assistant/shortcut | Deterministic multi-tool MCP briefing or integrity view |
| POST /api/assistant/chat | Optional model tool orchestration |
| POST /api/assistant/confirm | Execute/cancel saved user-bound proposal |
| GET /api/conversations/{id} | Owner-only persisted conversation |

Cookie-authenticated POST requests require `X-CarrySafe-Intent: interactive`. Bearer requests are also accepted. A manual operation body is `{ "payload": { ... }, "request_id": "unique-request-key", "confirmed": true }`. Never reuse a key for a materially different request. A network failure may leave the write outcome unknown; retry the same request ID to recover its receipt rather than inventing a new operation.

Common rule errors: NOT_FOUND (including tenant isolation), AUTHORIZATION, VALIDATION, CONCURRENT_UPDATE, ACTIVE_CONTROL, INDEPENDENT_REVIEW, MISSING_OWNER, CONFLICTING_INFORMATION and STATE_TRANSITION. Transport failures produce MCP_UNAVAILABLE; they must not be presented as confirmed successful changes.
