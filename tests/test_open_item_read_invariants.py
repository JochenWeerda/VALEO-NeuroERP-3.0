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
    def __init__(self, columns=(("id",), ("tenant_id",))):
        self.columns = list(columns)
        self.calls = []

    def execute(self, statement, params=None):
        self.calls.append((str(statement), params))
        return _Result(rows=self.columns)


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


def test_open_item_relation_is_the_subsidiary_ledger_not_the_search_path():
    """Der Suchpfad traf den verwaisten Speicher public.offene_posten; gelesen wird das Nebenbuch domain_erp."""
    from app.services.open_item_read_source import _get_open_items_relation

    db = _Session()
    relation, columns = _get_open_items_relation(db)

    assert relation == "domain_erp.offene_posten"
    assert columns == {"id", "tenant_id"}
    assert db.calls == [(db.calls[0][0], {"table_schema": "domain_erp"})]
    assert "to_regclass" not in db.calls[0][0]


def test_open_item_relation_without_table_is_unavailable_not_empty():
    from app.services.open_item_read_source import _get_open_items_relation

    with pytest.raises(HTTPException) as exc_info:
        _get_open_items_relation(_Session(columns=()))

    assert exc_info.value.status_code == 503
