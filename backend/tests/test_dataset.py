import pytest
from sqlalchemy import select, func
from app.dataset_import import import_csv
from app.db import Session
from app.models import Incident, ReferenceIncident


def test_import_is_separate_repeatable_and_validated(tmp_path):
    p = tmp_path / "reference.csv"
    p.write_text("Description,Employee\nHistorical injury at loading dock,A person\n,Other\n")
    with pytest.raises(ValueError):
        import_csv(p)
    assert import_csv(p, license_confirmed=True) == {"imported": 1, "skipped": 1}
    assert import_csv(p, license_confirmed=True) == {"imported": 0, "skipped": 2}
    with Session() as db:
        assert db.scalar(select(func.count()).select_from(Incident)) == 0
        assert db.scalar(select(func.count()).select_from(ReferenceIncident)) == 1
    p.write_text("WrongColumn\nMissing description\n")
    with pytest.raises(ValueError):
        import_csv(p, license_confirmed=True)
