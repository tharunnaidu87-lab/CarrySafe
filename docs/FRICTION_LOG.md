# Authentic friction log

1. **MCP structured output registration** — Typed tool registration initially failed because a bare `dict` return annotation was not accepted for structured output. Changed it to `dict[str, Any]`. Impact: blocked server import. Suggestion: show a minimal typed-dictionary return example beside v2 tool documentation.
2. **Expected domain errors hidden** — An unauthorized closure returned only a generic tool failure because the domain adapter raised ValueError. Switched intended rule denials to the SDK's ToolError and reran the real client test. Impact: users could not see the missing rule. Suggestion: emphasize safe business-error handling in migration guidance.
3. **Session manager lifecycle** — Starting the same MCP session manager through multiple TestClient contexts raised a one-start-only error. Reused a single test application lifespan and tested fresh process startup separately. Impact: test fixture setup failure. No SDK bypass or error suppression was used.
4. **Local proxy environment** — Loopback HTTP tests inherited a SOCKS proxy without its optional dependency. The internal MCP client and loopback test clients now use `trust_env=False`; external provider requests retain normal environment behavior. Impact: prevented local transport validation.
5. **Managed preview dependencies** — The preview runtime did not contain the Python virtual environment. Dependencies were made available for the preview, which then started. A subsequent browser URL-policy gate blocked inspection. Browser QA remains unverified; no alternate browser-control path was used to evade that denial.
6. **Render YAML scalar** — A YAML parser interpreted unquoted `off` as boolean false. Quoting `autoDeployTrigger: 'off'` fixed current schema validation. No resources were deployed.
7. **Uncertain write retries** — Review found that UI retries could rotate the idempotency key after a timeout. The form now keeps its request ID, and an ambiguous MCP failure keeps the assistant proposal available for retry. A regression test verifies the preserved proposal identifier.

8. **Mixed test runners** — Vitest discovered a Playwright scenario and rejected its test API. A separate Vitest include list now limits unit discovery to source tests. The corrected unit suite and production build pass; Playwright remains unexecuted.
9. **Local origin configuration** — Final startup review found the default allowlist omitted the documented port 8000 application origin. Both localhost variants are now included and checked by HTTP regression assertions.

These entries describe build observations, not reports of flaws in tools that were never used. No bonus eligibility or judging result is claimed.
