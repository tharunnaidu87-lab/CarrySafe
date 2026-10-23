"""Explicit local CSV import. No network download and no active-incident writes."""

import csv
import hashlib
import re
from .db import Session
from .models import ReferenceIncident

SOURCE = "https://www.kaggle.com/datasets/ihmstefanini/industrial-safety-and-health-analytics-database"


def import_csv(path, description_column="Description", license_confirmed=False):
    if not license_confirmed:
        raise ValueError("Review the source license and confirm permission before importing.")
    imported = skipped = 0
    with open(path, encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or description_column not in reader.fieldnames:
            raise ValueError("Description column missing. Available columns: " + str(reader.fieldnames))
        with Session.begin() as db:
            for record in reader:
                description = " ".join((record.get(description_column) or "").split())
                if len(description) < 10 or len(description) > 4000:
                    skipped += 1
                    continue
                description = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[email removed]", description)
                description = re.sub(r"\b(?:\+?\d[\d ()-]{8,}\d)\b", "[number removed]", description)
                id = hashlib.sha256((SOURCE + description).encode()).hexdigest()
                if db.get(ReferenceIncident, id):
                    skipped += 1
                    continue
                db.add(
                    ReferenceIncident(
                        id=id,
                        source=SOURCE,
                        description=description,
                        metadata_json={
                            "source_type": "historical_reference",
                            "license": "user-confirmed",
                            "notice": "Not an active CarrySafe incident. Review narrative for residual identifiers.",
                        },
                    )
                )
                imported += 1
    return {"imported": imported, "skipped": skipped}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--description-column", default="Description")
    parser.add_argument("--confirm-license", action="store_true")
    args = parser.parse_args()
    print(import_csv(args.csv, args.description_column, args.confirm_license))
