# Executed verification

Build-environment results from 23 October 2026. Local checks and GitHub Actions results are identified separately below. No public cloud deployment is claimed.

| Check | Result |
|---|---|
| `cd backend && ../.venv/bin/python -m pytest -q` | 26 passed, 0 failed, 0 skipped; final run 11.79 s |
| `cd backend && ../.venv/bin/ruff check .` | Passed |
| `cd frontend && npm test` | 5 passed, 0 failed, 0 skipped |
| `cd frontend && npm run build` | TypeScript and production Vite build passed |
| `cd backend && ../.venv/bin/python -m alembic check` | No new upgrade operations detected |
| Fresh temporary SQLite migration, seed and `scripts/reset_demo.py` | Passed; archived prior database and restored 100 synthetic incidents |
| `scripts/verify_mcp.py` against a real local Uvicorn process | Passed; [captured output](docs/MCP_VERIFICATION.txt) |
| Render Blueprint against current Render JSON Schema | Passed structural validation; not deployed |

## GitHub Actions follow-up

[Run 39901870549](https://github.com/tharunnaidu87-lab/CarrySafe/actions/runs/39901870549), source commit `6da84d7bd502ce7e91265828faba59cdd204980e`:

| Job | Executed result |
|---|---|
| backend | Lint and 26 SQLite-backed tests passed |
| frontend | Dependency installation, TypeScript/Vite build and five unit tests passed |
| postgres | PostgreSQL 17 migration upgrade/check and all 26 backend tests passed (10.13 s) |
| docker | Image build, Compose startup, seed, real HTTP MCP workflow and restart persistence passed |

The Docker persistence assertion found exactly 101 incidents after restarting the application: 100 fixtures plus the MCP-created record. The failure-only log step was skipped because the job succeeded; this is not a skipped test. The PostgreSQL run repeats the same 26 tests against another database, rather than adding 26 unique test cases.

To rerun PostgreSQL tests, create a disposable local database named `carrysafe_test`, set `CARRYSAFE_TEST_DATABASE_URL` to its PostgreSQL connection URL and run `pytest -q` from `backend`. **The test fixture drops and recreates application tables.** It refuses non-loopback PostgreSQL hosts and database names that do not start with `carrysafe_test`. With the variable absent, tests use a separate temporary SQLite file. The CI workflow provisions and removes isolated databases automatically.

## Coverage and evidence

The backend tests cover domain transitions, owner acceptance, handover acknowledgment, control review, closure evidence and independent approval, disputes, stale versions, idempotency, tenant boundaries, authentication, browser-origin restrictions, logout and dataset-import validation. One integration test starts an actual HTTP server and uses the official MCP client to negotiate 2025-11-25, discover 19 tools, read/write persistent records and check negative paths. It also checks MCP-routed form submission and the three-call briefing.

Agent tests use explicitly mocked provider responses. They check tool selection, bounded orchestration, malformed arguments, missing fields, persisted context, saved confirmation payloads, cancellation, identity binding, provider failure and retry behavior after an ambiguous MCP failure. They do not prove compatibility with a live model provider.

The independent MCP script exercised report creation, a temporary control, closure request, rejected worker approval, rejected approval while a control remained active, supervisor retirement and approval, and persisted closed state with seven audit events. Its synthetic record remains in the local demo database. Tokens and passwords are absent from the captured output.

Frontend unit tests check request/error handling and form value conversion. They do not measure visual layout or accessibility. Vitest explicitly includes `src/**/*.test.ts(x)`; Playwright is run separately with `npm run test:e2e`.

## Failures resolved during verification

- MCP structured output annotation, expected domain-error reporting and test lifespan setup were corrected before the passing runs.
- Loopback proxy interference was resolved for internal MCP HTTP requests.
- Uncertain write retries now retain the request/proposal identifier.
- Vitest initially collected the Playwright suite and failed; separate test configuration fixed that failure. The final five unit tests passed.
- Local startup initially omitted port 8000 from its default origin allowlist. Added both documented localhost origins and regression assertions; the final backend run passed.
- A verifier launched in a separate isolated execution session could not reach the server. Running the server and client in the same execution environment completed the real HTTP verification.

## Not executed / not established

Browser end-to-end and visual checks were blocked by the environment's browser URL security policy. The prepared Playwright scenario was **not run**; it is not counted as a passed or skipped test above. Voice input, speech output, mobile layout and keyboard accessibility still require browser validation.

Live LLM calls require real provider credentials and a verified model identifier. PostgreSQL load/contention behavior, cloud deployment, load testing, backup recovery under failure and Windows/macOS execution were not verified. There is no public deployment URL, video or completed Devpost submission. Automated tests passing does not certify workplace safety or production readiness.
