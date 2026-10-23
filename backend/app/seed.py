"""Explicit synthetic fixture initialization; never erases existing data."""

import os
import random
from datetime import timedelta
from sqlalchemy import select
from .db import Session, now
from .models import Organization, User, Location, Shift, Incident, TemporaryControl, Handover, AuditEvent
from .auth import hasher
from .config import settings


def seed(*, hosted=False):
    if hosted:
        if (
            os.environ.get("BOOTSTRAP_SYNTHETIC_DEMO") != "true"
            or settings.environment != "production"
            or not settings.database_url.startswith(("postgresql", "postgres://"))
        ):
            raise RuntimeError("Hosted demo bootstrap requires explicit opt-in and production PostgreSQL.")
    elif settings.environment not in ("local", "test"):
        raise RuntimeError("Synthetic seed is restricted to local/test environments.")
    password = os.environ.get("DEMO_PASSWORD", "")
    if len(password) < 12:
        raise RuntimeError("Set DEMO_PASSWORD to a unique password of at least 12 characters.")
    rng = random.Random(1042)
    with Session.begin() as db:
        if db.scalar(select(Organization.id)):
            print("Database is not empty; nothing changed.")
            return
        db.add(Organization(id=1, name="Northpoint Logistics — Demo Facility", synthetic=True))
        db.flush()
        for id, name, role in [
            (1, "Alex Morgan", "worker"),
            (2, "Sam Rivera", "worker"),
            (3, "Jordan Lee", "supervisor"),
        ]:
            db.add(
                User(
                    id=id,
                    org_id=1,
                    name=name,
                    email=["alex", "sam", "jordan"][id - 1] + "@demo.carrysafe.test",
                    role=role,
                    password_hash=hasher.hash(password),
                )
            )
        for n, name in enumerate(
            ["Loading Bay 2", "Packing Hall", "Service Corridor", "Cold Storage", "Dispatch Gate"], 1
        ):
            db.add(Location(id=n, org_id=1, name=name))
        for n, name in enumerate(["Shift A — Morning", "Shift B — Evening", "Shift C — Night"], 1):
            db.add(Shift(id=n, org_id=1, name=name))
        db.flush()
        descriptions = [
            "Leaking pipe; permanent repair pending",
            "Damaged door awaiting maintenance",
            "Spill cleanup awaiting inspection",
            "Electrical enclosure reported damaged; qualified inspection requested",
            "Temporary barrier awaiting review",
            "Packing station maintenance incomplete",
        ]
        for n in range(100):
            id = f"CS-{1042 + n}"
            closed = n >= 84
            i = Incident(
                id=id,
                org_id=1,
                reporter_id=1,
                location_id=1 if n == 0 else rng.randint(1, 5),
                shift_id=rng.randint(1, 3),
                description="SYNTHETIC: " + descriptions[n % len(descriptions)],
                owner_id=1 if n % 7 else None,
                owner_accepted=n % 7 != 0,
                state="closed" if closed else "open",
                disputed=n in (8, 19),
                created_at=now() - timedelta(hours=4 + n),
                updated_at=now() - timedelta(hours=n % 35),
            )
            if n == 0:
                i.owner_id = 1
                i.owner_accepted = True
            db.add(i)
            db.flush()
            db.add(
                AuditEvent(
                    org_id=1,
                    user_id=1,
                    action="synthetic_fixture",
                    entity_id=id,
                    before={},
                    after={"source": "SYNTHETIC", "state": i.state},
                )
            )
            if n % 3 == 0 and not closed:
                db.add(
                    TemporaryControl(
                        incident_id=id,
                        description="SYNTHETIC: Temporary containment with warning markers",
                        responsible_id=1,
                        review_due=now() + timedelta(hours=-2 if n % 2 == 0 else 6),
                    )
                )
        db.flush()
        ids = list(db.scalars(select(Incident.id).where(Incident.state != "closed").order_by(Incident.id)))
        db.add_all(
            [
                Handover(org_id=1, outgoing_id=1, incoming_id=2, recipient_id=2, incident_ids=ids),
                Handover(org_id=1, outgoing_id=2, incoming_id=3, recipient_id=1, incident_ids=ids),
            ]
        )
    print(
        "Created 100 synthetic incidents, three shifts, three accounts and two pending handovers. No real workplace data."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hosted", action="store_true")
    seed(hosted=parser.parse_args().hosted)
