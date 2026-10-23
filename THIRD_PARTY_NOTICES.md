# Third-party notices

CarrySafe original code is MIT licensed. Dependencies retain their own licenses; the CarrySafe license does not replace them. Versions below are from the locked packages installed during verification. This inventory is not legal advice or a complete redistribution compliance determination.

## Python dependencies

License identifiers/text labels below are taken from installed package metadata. Full upstream license and copyright files remain in the installed distributions; retain them when distributing an environment or container.

| Package | Version | Declared license |
|---|---|---|
| alembic | 1.20.1 | MIT |
| annotated-doc | 0.0.5 | MIT |
| annotated-types | 0.8.0 | MIT |
| anyio | 4.15.1 | MIT |
| argon2-cffi | 25.1.0 | MIT |
| argon2-cffi-bindings | 26.1.0 | MIT |
| attrs | 26.1.0 | MIT |
| certifi | 2026.10.19 | MPL-2.0 |
| cffi | 2.1.1 | MIT-0 |
| click | 8.5.0 | BSD-3-Clause |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause |
| fastapi | 0.160.0 | MIT |
| h11 | 0.16.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpcore2 | 2.16.0 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| httpx2 | 2.16.0 | BSD-3-Clause |
| idna | 3.20 | BSD-3-Clause |
| iniconfig | 2.3.1 | MIT |
| jsonschema | 4.26.0 | MIT |
| jsonschema-specifications | 2025.9.1 | MIT |
| Mako | 1.4.3 | MIT |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| mcp | 2.3.0 | MIT |
| mcp-types | 2.3.0 | MIT |
| opentelemetry-api | 1.45.1 | Apache-2.0 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.7.0 | MIT |
| psycopg | 3.3.6 | LGPL-3.0-only |
| psycopg-binary | 3.3.6 | LGPL-3.0-only |
| pycparser | 3.12 | BSD-3-Clause |
| pydantic | 2.14.1 | MIT |
| pydantic-settings | 2.16.1 | MIT |
| pydantic_core | 2.50.1 | MIT |
| Pygments | 2.21.0 | BSD-2-Clause |
| PyJWT | 2.15.1 | MIT |
| pytest | 9.1.1 | MIT |
| pytest-asyncio | 1.4.0 | Apache-2.0 |
| python-dotenv | 1.2.4 | BSD-3-Clause |
| python-multipart | 0.0.32 | Apache-2.0 |
| referencing | 0.37.0 | MIT |
| rpds-py | 2026.9.1 | MIT |
| ruff | 0.17.1 | MIT |
| SQLAlchemy | 2.1.6 | MIT |
| sse-starlette | 3.5.0 | BSD-3-Clause |
| starlette | 1.9.0 | BSD-3-Clause |
| truststore | 0.10.5 | MIT |
| typing-inspection | 0.4.4 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| uvicorn | 0.54.0 | BSD-3-Clause |

## Direct frontend and development dependencies

The npm lockfile also records transitive packages and their declared licenses. Upstream license files are retained by npm under each installed package.

| Package | Version | Declared license |
|---|---|---|
| @playwright/test | 1.56.1 | Apache-2.0 |
| @tailwindcss/vite | 4.1.16 | MIT |
| @tanstack/react-query | 5.90.5 | MIT |
| @types/react | 19.2.2 | MIT |
| @types/react-dom | 19.2.2 | MIT |
| @vitejs/plugin-react | 5.0.4 | MIT |
| lucide-react | 0.548.0 | ISC |
| react | 19.2.0 | MIT |
| react-dom | 19.2.0 | MIT |
| react-router-dom | 7.9.4 | MIT |
| tailwindcss | 4.1.16 | MIT |
| typescript | 5.9.3 | Apache-2.0 |
| vite | 7.1.12 | MIT |
| vitest | 3.2.4 | MIT |

## Distribution considerations

Psycopg and psycopg-binary declare LGPL-3.0-only. Review their upstream license and the licenses of bundled native libraries before redistributing binaries. Container base images, Python, Node.js, PostgreSQL and their system libraries have separate licensing terms.

No external incident dataset is included. All bundled demonstration incidents are synthetic. See [data sources](docs/DATA_SOURCES.md) before importing third-party records.
