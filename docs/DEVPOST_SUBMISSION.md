# CarrySafe — AI-Powered Temporary Risk & Shift Handover Guardian

**Draft for team review; not submitted.**

## Inspiration

A temporary containment tray, warning barrier or unfinished repair may remain after the worker who recorded it leaves. The next shift needs more than a checklist: it needs to know what remains unresolved, who has accepted responsibility and which follow-up is missing.

## What it does

CarrySafe carries incidents and temporary measures across shift handovers. Its integrity engine explains missing ownership, overdue reviews, disputed updates and unacknowledged responsibilities. It keeps acknowledgment separate from resolution and requires evidence, retired temporary measures and an independent supervisor decision before final closure.

## How we built it

React and TypeScript provide the assistant and operational screens. FastAPI and SQLAlchemy implement one shared domain service. The official Python MCP SDK exposes 19 authenticated tools over Streamable HTTP. The backend uses a real MCP client for assistant requests and UI mutations. The tested handshake negotiates MCP 2025-11-25.

An optional OpenAI-compatible model can interpret requests, choose tools and propose changes. Human confirmation and backend authorization sit outside the model. Without a configured model, explicit manual workflows and real multi-tool MCP briefings remain available. The UI labels this mode accurately.

## What makes the approach specific

Temporary controls remain traceable across shifts. Each integrity flag has an explainable reason. Closure follows independent review instead of a conversational claim of completion. Audit records preserve both successful changes and rejected actions.

## Testing and limitations

See TEST_REPORT.md for exact executed checks. Real HTTP MCP discovery, writes, tenant isolation, worker denial and closure rules have been tested. Agent tests use a simulated provider. Live model behavior, browser end-to-end execution, microphone behavior, Docker and PostgreSQL runtime remain validation gates. The product coordinates records and does not certify physical safety.

## Data and licensing

The demonstration uses 100 clearly labeled fictional records. An optional historical CSV importer is included, but no Kaggle or OSHA data has been imported. Original code is MIT licensed; dependency notices are included.

## Track and links

- Primary track: Alexa+ — self-hosted MCP server, demonstrated through our web client.
- Repository: https://github.com/tharunnaidu87-lab/CarrySafe
- Setup: root README.md
- Runtime evidence: docs/MCP_VERIFICATION.txt and backend/tests/test_http_mcp.py
- Demo video: **TEAM MUST RECORD AND ADD PUBLIC YOUTUBE/VIMEO LINK**
- Public deployment: **Not available**
- Team members: **TEAM MUST FILL IN ACCURATE NAMES**

No Echo installation, private Alexa+ API integration, AWS service use, measured accident reduction or production certification is claimed. Do not select the AWS mini challenge without actual qualifying usage. A public primary repository alone does not establish the additional Open Source mini-challenge requirement.

## Submission gates

1. Verify a real model interaction if demonstrating AI language understanding.
2. Run browser tests and rehearse the full UI workflow locally.
3. Record a working English demonstration shorter than three minutes; upload publicly to YouTube or Vimeo.
4. Fill team details and actual product feedback; review third-party licenses.
5. Submit the accurate repository/video links before **24 October 2026, 12:30 AM IST**, subject to the official page.

Official sources checked during the build:
- https://amazonappdev2026.devpost.com/rules
- https://amazonappdev2026.devpost.com/details/faqs
