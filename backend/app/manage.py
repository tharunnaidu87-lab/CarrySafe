"""Server-operator CLI for initial organization provisioning; no default credentials."""

import argparse
import getpass
from sqlalchemy import select
from .db import Session
from .models import Organization, User, Location, Shift
from .auth import hasher


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("New supervisor password (12+ characters): ")
    if len(password) < 12:
        raise SystemExit("Password too short")
    with Session.begin() as db:
        if db.scalar(select(Organization.id)):
            raise SystemExit("Database already provisioned. Use your approved administration process.")
        org = Organization(name=args.organization, synthetic=False)
        db.add(org)
        db.flush()
        db.add(
            User(
                org_id=org.id,
                email=args.email.lower(),
                name=args.name,
                role="supervisor",
                password_hash=hasher.hash(password),
            )
        )
        db.add(Location(org_id=org.id, name="Unconfigured location — rename before operational use"))
        for name in ["Morning", "Evening", "Night"]:
            db.add(Shift(org_id=org.id, name=name))
    print(
        "Initial organization created. Further staff/location provisioning requires a server operator; no public signup is exposed."
    )


if __name__ == "__main__":
    main()
