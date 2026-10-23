# Database selection must happen before importing application modules.
# ruff: noqa: E402
import os
import tempfile
from urllib.parse import urlparse

test_url = os.environ.get("CARRYSAFE_TEST_DATABASE_URL")
if test_url:
    parsed = urlparse(test_url)
    if (
        parsed.scheme not in ("postgresql", "postgresql+psycopg")
        or parsed.hostname not in ("localhost", "127.0.0.1")
        or not parsed.path.startswith("/carrysafe_test")
    ):
        raise RuntimeError("Tests require a disposable local carrysafe_test database.")
os.environ["DATABASE_URL"] = test_url or "sqlite:///" + tempfile.mktemp(suffix=".db")
os.environ["ENVIRONMENT"] = "test"
import pytest
from app.db import Base, engine, Session
from app.models import Organization, User, Location, Shift
from app.auth import hasher


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session.begin() as db:
        db.add_all(
            [
                Organization(id=1, name="Synthetic A", synthetic=True),
                Organization(id=2, name="Synthetic B", synthetic=True),
            ]
        )
        db.flush()
        db.add_all(
            [
                User(
                    id=n,
                    org_id=2 if n == 4 else 1,
                    name=f"User {n}",
                    email=f"u{n}@demo.test",
                    role="supervisor" if n == 3 else "worker",
                    password_hash=hasher.hash("Testing-password-42!"),
                )
                for n in range(1, 5)
            ]
        )
        db.add_all(
            [
                Location(id=1, org_id=1, name="Bay 2"),
                Location(id=2, org_id=2, name="Other site"),
                Shift(id=1, org_id=1, name="A"),
                Shift(id=2, org_id=1, name="B"),
                Shift(id=3, org_id=1, name="C"),
            ]
        )
    yield


@pytest.fixture
def users():
    with Session() as db:
        return [db.get(User, n) for n in range(1, 5)]
