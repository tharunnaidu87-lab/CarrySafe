# Data sources

## Included: synthetic operational fixtures

`backend/app/seed.py` creates 100 fictional incidents with fixed random seed 1042. IDs begin at CS-1042. Locations, users, shifts, temporary controls, missing ownership, disputes, old updates, historical closed fixtures and pending handovers are linked. Timestamps are relative to seeding time so overdue examples work without changing the system clock. Thus relationships/content are deterministic; absolute timestamps intentionally change on reseeding.

Northpoint Logistics — Demo Facility, Alex Morgan, Sam Rivera and Jordan Lee are invented. Every generated report is marked SYNTHETIC. Historical closed fixture cases are explicitly audited as synthetic fixtures, not fabricated completed inspections.

## Optional: Kaggle historical reference corpus

Source: https://www.kaggle.com/datasets/ihmstefanini/industrial-safety-and-health-analytics-database

The build brief described its license as CC0. The source page was opened, but machine-readable content and the actual CSV were unavailable during this build. **No Kaggle data is bundled or represented as imported. License and real source schema are not claimed as verified.**

The optional importer inspects the supplied CSV header, checks the chosen description column, rejects malformed/empty rows, applies basic email/number redaction, hashes descriptions for repeatable deduplication and stores them only in `reference_incidents` with source metadata. It discards other columns. Review descriptions for names and remaining identifiers yourself.

After checking your downloaded file's license and actual column names:

```bash
cd backend
../.venv/bin/python -m app.dataset_import path/to/download.csv --description-column Description --confirm-license
```

If the column differs, use the actual name. A missing column is an error rather than a guessed mapping. Import tests use a small synthetic CSV, not the real Kaggle file. Download failure cannot break normal operation because the importer is opt-in.

No OSHA corpus was added. No accident classifier was trained. Historical severities do not determine current incident safety, closure or review decisions.
