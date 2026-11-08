from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException


class _Result:
    def __init__(self, *, scalar=None, rows=()):
        self._scalar = scalar
        self._rows = list(rows)

    def scalar(self):
        return self._scalar

    def fetchall(self):
        return self._rows


class _Session:
    def __init__(self, schema):
        self.schema = schema
        self.calls = []

    def execute(self, statement, params=None):
        self.calls.append((str(statement), params))
        if len(self.calls) == 1:
            return _Result(scalar=self.schema)
        return _Result(rows=[("id",), ("tenant_id",)])


def _open_item(due_date: date, open_amount: Decimal):
    from app.api.v1.endpoints.open_items import OpenItem

    return OpenItem(
        id="op-1",
        tenant_id="tenant-a",
        rechnungsnr="RE-1",
        rechnungsdatum=date(2031, 2, 1),
        faelligkeit=due_date,
        op_betrag=Decimal("100.00"),
        offen=open_amount,
        created_at=datetime(2031, 2, 1, tzinfo=timezone.utc),
        updated_at=datetime(2031, 2, 1, tzinfo=timezone.utc),
    )


def test_overdue_uses_business_timezone_boundary_and_keeps_due_day_open(monkeypatch):
    import app.core.business_time as business_time

    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    # 23:30 UTC on the last day of February is already the next business day.
    utc_instant = datetime(2031, 2, 28, 23, 30, tzinfo=timezone.utc)
    local_now = utc_instant.astimezone(business_time.business_timezone())
    monkeypatch.setattr(
        business_time,
        "business_now",
        lambda: local_now,
    )
    business_day = business_time.business_today()
    assert business_day == business_time.business_date_at(utc_instant) == date(2031, 3, 1)

    assert _open_item(business_day, Decimal("1.00")).ueberfaellig is False
    assert _open_item(date(2031, 2, 28), Decimal("1.00")).ueberfaellig is True
    assert _open_item(date(2031, 2, 28), Decimal("0.00")).ueberfaellig is False


@pytest.mark.parametrize("schema", ["public", "domain_erp"])
def test_open_item_relation_accepts_only_canonical_schemas(schema):
    from app.services.open_item_read_source import _get_open_items_relation

    db = _Session(schema)
    relation, columns = _get_open_items_relation(db)

    assert relation == f"{schema}.offene_posten"
    assert columns == {"id", "tenant_id"}
    assert db.calls[1][1] == {"table_schema": schema}


def test_open_item_relation_rejects_injected_schema_before_identifier_sql():
    from app.services.open_item_read_source import _get_open_items_relation

    injected_schema = "public; DROP SCHEMA domain_erp CASCADE; --"
    db = _Session(injected_schema)

    with pytest.raises(HTTPException) as exc_info:
        _get_open_items_relation(db)

    assert exc_info.value.status_code == 503
    assert len(db.calls) == 1
