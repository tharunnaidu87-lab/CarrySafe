# MCP runtime

Official SDK: **mcp==2.3.0** (and mcp-types==2.3.0), pinned in `backend/requirements.lock`. Uses v2 `MCPServer`, `ClientSession` and Streamable HTTP APIs. No v1 FastMCP imports are mixed in.

Endpoint: `/mcp/`. Transport: Streamable HTTP, stateless server mode, JSON responses. Authentication: verified opaque bearer session. The real client sends the legacy initialize handshake, and the executed test negotiates **2025-11-25**. Newer SDK protocol modes are not claimed as tested.

## Tools

| Tool | Purpose |
|---|---|
| create_incident | Persist confirmed report |
| get_incident | Current facts and version |
| list_open_incidents | Search unresolved work |
| get_directory | Resolve known people, shifts and locations |
| get_dashboard | Real counts and recent events |
| get_integrity_flags | Explain deterministic warnings |
| list_overdue_controls | Retrieve overdue reviews |
| add_temporary_control | Record safeguard and deadline |
| record_control_review | Preserve observation, renew or retire control |
| assign_incident | Supervisor assigns responsibility |
| accept_ownership | Assigned owner accepts |
| record_incident_progress | Preserve updates and flag structured contradictions |
| create_handover | Snapshot unresolved cases into incoming shift |
| get_shift_handover | Retrieve snapshots and current states |
| acknowledge_handover | Designated recipient acknowledges |
| request_incident_closure | Submit evidence for review |
| review_closure_request | Independent supervisor decision |
| get_incident_history | Read audit history |
| search_reference_incidents | Separate historical reference corpus |

Each tool exposes a typed `payload` object and optional `request_id`. Writes require a request ID; versioned writes require `expected_version`. Caller identity is not a tool argument. Errors for intended rule denials use SDK `ToolError` so clients receive the rule explanation; unexpected errors remain masked by the SDK.

Run `scripts/verify_mcp.py` with the local seeded backend running. It exercises genuine discovery, read/write persistence, denial and final state. `backend/tests/test_http_mcp.py` additionally verifies unauthenticated and cross-organization calls and the UI backend's multi-call briefing and MCP-routed form submission.

This is an authenticated local/application MCP integration, not a completed OAuth-enabled marketplace distribution. No claim is made that Amazon's gated tools or Echo runtime were used.
