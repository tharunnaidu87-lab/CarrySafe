import pytest
from sqlalchemy import func, select

from app.config import settings
from app.db import Base, Session, engine
from app.models import Incident, Organization, User
from app.seed import seed
from app.auth import hasher


def configure(monkeypatch):
    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "database_url", "postgresql://test-only")
    monkeypatch.setenv("DEMO_PASSWORD", "Test-hosted-password-42!")


def test_hosted_seed_requires_opt_in_and_postgres(monkeypatch):
    configure(monkeypatch)
    monkeypatch.delenv("BOOTSTRAP_SYNTHETIC_DEMO", raising=False)
    with pytest.raises(RuntimeError, match="explicit opt-in"):
        seed(hosted=True)
    monkeypatch.setenv("BOOTSTRAP_SYNTHETIC_DEMO", "true")
    monkeypatch.setattr(settings, "database_url", "sqlite:///test.db")
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        seed(hosted=True)
    with pytest.raises(RuntimeError, match="local/test"):
        seed()


def test_hosted_seed_preserves_existing_organizations(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setenv("BOOTSTRAP_SYNTHETIC_DEMO", "true")
    seed(hosted=True)
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(Organization)) == 2
        assert db.scalar(select(func.count()).select_from(User)) == 4
        assert db.scalar(select(func.count()).select_from(Incident)) == 0


def test_empty_database_bootstrap_is_repeatable_without_password_reset(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setenv("BOOTSTRAP_SYNTHETIC_DEMO", "true")
    # conftest confines this engine to a disposable test database.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    monkeypatch.setenv("DEMO_PASSWORD", "short")
    with pytest.raises(RuntimeError, match="12 characters"):
        seed(hosted=True)
    monkeypatch.setenv("DEMO_PASSWORD", "Test-hosted-password-42!")
    seed(hosted=True)
    monkeypatch.setenv("DEMO_PASSWORD", "Different-password-42!")
    seed(hosted=True)
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(Incident)) == 100
        assert db.scalar(select(func.count()).select_from(User)) == 3
        assert db.get(Organization, 1).synthetic
        assert hasher.verify(db.get(User, 1).password_hash, "Test-hosted-password-42!")
