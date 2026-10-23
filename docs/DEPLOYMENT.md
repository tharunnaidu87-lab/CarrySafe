# Deployment

## Verified local target

Python 3.12 backend, SQLite file, built React UI served by FastAPI. Use the root README. A server restart preserves the local database. SQLite is rejected when `ENVIRONMENT=production`.

## Docker Compose (verified in GitHub Actions)

Docker was unavailable in the local build environment. The multi-stage image and Compose stack were subsequently built and run in GitHub Actions: migrations, synthetic seed, actual MCP verification and restart persistence all passed. This verifies the isolated container workflow, not a public deployment.

Create a ROOT `.env` with a unique alphanumeric database password (to avoid URL escaping issues) and a separate demo password of at least 12 characters:

```dotenv
POSTGRES_PASSWORD=YOUR_UNIQUE_DATABASE_PASSWORD
DEMO_PASSWORD=YOUR_UNIQUE_LOCAL_DEMO_PASSWORD
```

Then:

```bash
docker compose up --build -d
docker compose exec app python -m app.seed
```

Open http://localhost:8000. Compose binds only to local loopback. Data lives in a named PostgreSQL volume. `docker compose down` retains it. Do not use `down -v` unless you intend to remove that database.

The container starts with Alembic migration and one Uvicorn process. Concurrent replicas should use a controlled migration job rather than racing startup migrations. Seed is permitted only in local/test mode and does nothing when the database already contains an organization.

## Render (database provisioned; web deployment pending)

`render.yaml` defines a Docker web service on the free plan, with automatic deploys off. It references no paid database and creates nothing until someone explicitly applies it. Supply an already provisioned persistent PostgreSQL connection string. The template was validated against Render's current JSON Schema; this is structural validation, not a successful deployment.

Required values:

- `DATABASE_URL`: actual persistent PostgreSQL connection string. `postgres://`, `postgresql://` and `postgresql+psycopg://` are normalized to the installed psycopg driver.
- `ALLOWED_HOSTS`: exact public hostname plus `localhost,127.0.0.1` for internal MCP and health checks. Do not use `*`.
- `ALLOWED_ORIGINS`: exact HTTPS application origin, without a trailing slash.
- `ENVIRONMENT=production`: secure cookies and PostgreSQL requirement.
- Optional `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`: supply verified provider values through Render secrets/settings.

The Docker entrypoint uses Render's `PORT`, sets the matching internal MCP URL, runs migrations and starts the app. The frontend and backend share one origin. `/api/health` checks database connectivity.

The production seed is intentionally disabled. Provision an empty migrated organization through the operator CLI; see SECURITY.md. Before any public rollout, validate staff provisioning, records, TLS, session behavior, cross-tenant restrictions, backup/restore and PostgreSQL concurrency. Configure an external rate limit if using more than one process.

A free CarrySafe PostgreSQL 17 database was created in Singapore on 23 October 2026 and is available. Its trial expires on 22 November 2026. No paid resource was created. No verified public application URL is available yet. The Render connector does not expose its connection credentials; dashboard sign-in is needed to finish wiring the web service. Do not place the connection URL in source control.

The checked-in Blueprint remains an optional template; resources created directly through the connector are managed through the Dashboard/API unless explicitly imported into a Blueprint. See [NVIDIA setup](NVIDIA_SETUP.md) for the selected model configuration.
