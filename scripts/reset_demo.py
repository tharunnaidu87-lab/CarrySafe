"""Archive an isolated local SQLite demo, then create a fresh one. No PostgreSQL reset."""

import sys
from pathlib import Path
import os
import getpass
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT / "backend")
sys.path.insert(0, str(ROOT / "backend"))
from app.config import settings
from app.db import engine, Session
from app.models import Organization
from sqlalchemy import select
from alembic.config import Config
from alembic import command
from app.seed import seed

if settings.environment != "local" or not settings.database_url.startswith(
    "sqlite:///"
):
    raise SystemExit("Reset is restricted to a local SQLite demo.")
with Session() as db:
    orgs = list(db.scalars(select(Organization)))
    if len(orgs) != 1 or not orgs[0].synthetic:
        raise SystemExit("Refusing: this is not an isolated synthetic organization.")
print(
    "Stop the running server first. The existing demo database will be archived, not deleted."
)
if input("Type RESET SYNTHETIC DEMO: ") != "RESET SYNTHETIC DEMO":
    raise SystemExit("Cancelled")
password = getpass.getpass("New demo password (12+ characters): ")
if len(password) < 12:
    raise SystemExit("Password too short")
with engine.connect() as conn:
    conn.exec_driver_sql("PRAGMA wal_checkpoint(TRUNCATE)")
engine.dispose()
path = Path(engine.url.database)
backup = path.with_name(
    "demo-backup-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + ".db"
)
path.rename(backup)
command.upgrade(Config("alembic.ini"), "head")
os.environ["DEMO_PASSWORD"] = password
seed()
print("Reset complete. Previous records archived locally. Restart the server.")
