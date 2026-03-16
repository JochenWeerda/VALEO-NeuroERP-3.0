from __future__ import annotations

from io import BytesIO

import pytest

from app.core.data_quality_enforcement import DQValidationException
from modules.agrar.services.feldbuch_service import import_csv


class FailFeldbuchDB:
    def query(self, *args, **kwargs):
        raise AssertionError("DB lookup should not happen before DQ validation")

    def add(self, *args, **kwargs):
        raise AssertionError("DB write should not happen before DQ validation")

    def flush(self):
        raise AssertionError("flush should not happen before DQ validation")


def test_feldbuch_service_rejects_invalid_row_before_any_db_access():
    csv_content = "Datum;Schlag;Typ;Flaeche\n;Nordfeld;duengung;12,5\n".encode("utf-8")

    with pytest.raises(DQValidationException) as exc:
        import_csv(
            FailFeldbuchDB(),
            file_content=csv_content,
            tenant_id="tenant-1",
            customer_id="cust-1",
        )

    assert exc.value.entity_typ == "FeldbuchMassnahme"
