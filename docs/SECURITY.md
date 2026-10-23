# Security model and limits

Implemented protections:

- Argon2id password hashing; a chosen local password, no shipped administrator secret.
- Random 256-bit session tokens; only hashes stored server-side; 8-hour expiry and logout revocation.
- HttpOnly, SameSite=Strict browser session cookie; Secure enabled in production.
- Origin allowlist, trusted Host allowlist, custom header for cookie-authenticated writes, restricted CORS, CSP and frame denial.
- Bearer authentication on every MCP request; request-local verified identity.
- Organization scoping before read or mutation; directory IDs checked against the caller's organization.
- Worker/supervisor checks, independent reviewer requirement and deterministic evidence gates.
- Typed inputs reject extra role/organization properties.
- Persistent idempotency receipts and incident version checks; rejected domain writes are audited.
- Agent writes become user-bound, expiring proposals; confirming executes the saved payload, not new model arguments.
- Tool output is treated as untrusted data by the agent prompt; text is rendered through React escaping, without HTML injection.
- The application exposes no shell or arbitrary SQL tool.
- Per-process request limits, provider timeouts, an orchestration loop limit and request-level assistant timeout.

Limitations requiring further review:

- Prompt instructions are defense in depth, not proof of resistance to every prompt injection. Authorization, confirmation and closure rules are enforced outside the model. Adversarial real-provider testing is still required.
- No OAuth authorization server/discovery, SSO, MFA, recovery UI, staff-management UI or fine-grained location permissions.
- Session cleanup, durable shared rate limiting, security monitoring, backups and restore drills require operational setup. The in-process rate limit is not a distributed abuse control.
- Audit records are append-only through application workflows, but database administrators can alter them. There is no cryptographic tamper-proof audit store.
- Evidence is text/reference metadata; no file uploads or physical inspection verification.
- Free-form historical descriptions may contain identifiers even after basic email/number cleanup. Human data review is required before importing real records.
- API/body limits should also be enforced at the public reverse proxy. This build has not undergone a penetration test or certification.
- Provisioning currently requires a server operator. Use `python -m app.manage --organization "..." --email "..." --name "..."` on an empty migrated database. Further staff and location configuration requires an approved administration process.

Use production mode only behind HTTPS with persistent PostgreSQL and exact host/origin values. Never expose the local demo seed credentials as production access. Report security issues privately to the repository owner rather than including secrets or live worker records in public issues.
