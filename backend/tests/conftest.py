import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + tempfile.mktemp(suffix=".db")
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
