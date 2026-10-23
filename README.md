# CarrySafe

**Temporary risks should not disappear when a shift ends.**

CarrySafe is a workplace coordination application that carries unresolved incidents, temporary measures and accepted responsibilities across shifts. A deterministic integrity engine flags missing reviews, disputed observations, unaccepted ownership and unacknowledged handovers. Closure requires evidence and an independent supervisor decision.

Built for the **Alexa+ track of the Amazon Developer Hackathon 2026**: an Alexa+-ready MCP capability demonstrated through our own web client. It is not installed on Echo and does not use Amazon's private Alexa+ APIs. No measured accident-reduction or production-certification claim is made.

## Current status

- Working FastAPI backend, SQLAlchemy persistence, Alembic migration and React/TypeScript UI.
- **19 actual MCP tools**, official **Python MCP SDK 2.3.0**, **Streamable HTTP**.
- **2025-11-25** protocol negotiation, discovery, reads, writes and denial paths verified over real HTTP.
- Assistant shortcuts execute multiple MCP calls. Form writes also execute through MCP.
- Configurable LLM tool orchestration with persisted conversations and expiring, user-bound confirmation proposals.
- Without a model key, free-form AI is explicitly unavailable; manual reporting, MCP briefings and all workflow screens remain usable.
- 100 clearly labeled synthetic incidents, three shifts and isolated local demo accounts.
- Role checks, tenant isolation, Argon2 passwords, expiring hashed sessions, idempotency receipts, optimistic concurrency and audit history.
- Browser voice input with editable transcript and optional speech output, subject to browser support.

**Release limitations:** live LLM, microphone behavior, browser end-to-end execution and public deployment remain unverified. Browser inspection was blocked by the build environment's security policy. There is no public deployment or published demo video. See [TEST_REPORT.md](TEST_REPORT.md) for exact evidence and [docs/STATUS.md](docs/STATUS.md) for remaining work.

## Fastest local start — Windows

Install **Python 3.12** and **Node.js 22 LTS or newer**. From PowerShell:

```powershell
git clone https://github.com/tharunnaidu87-lab/CarrySafe.git
cd CarrySafe
py -3.12 scripts/setup.py
py -3.12 scripts/start.py
```

Setup installs dependencies, builds the UI, runs migrations and asks you to choose a local demo password of at least 12 characters. It never resets existing records. Open **http://localhost:8000**. Keep the terminal open.

After setup, `START_WINDOWS.bat` starts the same application. The first double-click also offers setup if the environment is absent.

| Account | Role | Demo responsibility |
|---|---|---|
| `alex@demo.carrysafe.test` | Worker | Initial owner / morning shift |
| `sam@demo.carrysafe.test` | Worker | Incoming handover recipient |
| `jordan@demo.carrysafe.test` | Supervisor | Independent review |

Use your chosen password for all three local demo accounts. There is no checked-in default password. These identities are fictional.

## macOS / Linux

```bash
python3.12 scripts/setup.py
python3.12 scripts/start.py
```

For manual setup:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.lock
cd frontend
npm ci
npm run build
cd ../backend
../.venv/bin/python -m alembic upgrade head
# Set a unique local demo password in your shell before this command.
../.venv/bin/python -m app.seed
../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. Native startup reads `backend/.env`; copy the root `.env.example` there if configuration is needed. Never commit a real `.env` file.

For frontend development, run `npm run dev` inside `frontend` while the backend runs on port 8000. Vite serves port 4173 and proxies API calls. A production build is served directly by FastAPI, so only one application process is needed.

## Optional AI setup

Set the following in `backend/.env` and restart:

```dotenv
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
```

Fill these with your provider's actual OpenAI-compatible API base URL, secret key and exact model identifier. The application appends `/chat/completions`. The provider must support function calling. NVIDIA-compatible providers can be used if their chosen endpoint and model implement this interface; no endpoint or model name is assumed. Provider requests time out and the orchestration loop is bounded. The UI clearly distinguishes configured AI from manual MCP mode.

A real provider interaction is a **remaining validation gate**. Mock-provider tests do not satisfy it.

## Verify the MCP implementation

With the local application running, open another terminal from the repository root:

```powershell
.venv\Scripts\python.exe scripts\verify_mcp.py
```

Or:

```bash
.venv/bin/python scripts/verify_mcp.py
```

Enter the local demo password. This script creates a clearly labeled synthetic verification incident and exercises discovery, persistence, worker denial, blocked premature approval, control retirement, independent approval and audit retrieval. It checks protocol `2025-11-25` and prints no session tokens. The fixture record stays in the database for inspection.

MCP endpoint: **http://127.0.0.1:8000/mcp/**. Browser requests use an HttpOnly session cookie; the backend forwards the authenticated user's token to MCP as a bearer token. External MCP clients can use a token from the authenticated local login flow, as shown by the verification script. OAuth discovery/authorization is not implemented in this release.

## Tests

```bash
cd backend
../.venv/bin/python -m pytest -q
../.venv/bin/ruff check .
cd ../frontend
npm test
npm run build
```

Prepared browser test, **not executed in the build environment**:

```bash
# Run the application against an isolated seeded demo first.
# Set DEMO_PASSWORD to the password used during setup.
cd frontend
npx playwright install chromium
npm run test:e2e
```

The browser test skips when `DEMO_PASSWORD` is absent. Do not treat that skip as passing browser coverage.

## Demo and deployment

Start with [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for the click sequence and under-three-minute narration. Reset instructions are included there. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) covers Docker Compose and the optional Render configuration using persistent PostgreSQL. No cloud resources have been created.

Documentation: [Architecture](docs/ARCHITECTURE.md) · [Security](docs/SECURITY.md) · [MCP](docs/MCP.md) · [API](docs/API.md) · [Data sources](docs/DATA_SOURCES.md) · [Submission draft](docs/DEVPOST_SUBMISSION.md) · [Product feedback](docs/PRODUCT_FEEDBACK.md) · [Friction log](docs/FRICTION_LOG.md)

## License

Original CarrySafe code is MIT licensed. Dependency licenses are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Historical datasets are not bundled; their licenses must be checked before import.
