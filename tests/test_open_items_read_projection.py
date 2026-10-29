from datetime import date, datetime
from decimal import Decimal
from inspect import signature

import pytest
from typing import Annotated
from pydantic import TypeAdapter, ValidationError


class _MappingResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _CountResult:
    def __init__(self, count):
        self._count = count

    def scalar_one(self):
        return self._count

    def scalar(self):
        return self._count

    def fetchall(self):
        return self._count


class _DB:
    def __init__(self, total, rows, columns=None):
        self.total = total
        self.rows = rows
        self.calls = []
        self.columns = columns or {
            "konto_nr", "konto_name", "konto_typ", "op_status", "rechnungsnr",
            "rechnungsdatum", "datum", "faelligkeit", "op_betrag", "betrag",
            "offen", "mahn_stufe", "kunde_name",
        }

    def execute(self, statement, params=None):
        sql = str(statement)
        self.calls.append((sql, dict(params or {})))
        if "FROM pg_class" in sql:
            return _CountResult("domain_erp")
        if "FROM information_schema.columns" in sql:
            return _CountResult([(name,) for name in self.columns])
        if sql.lstrip().upper().startswith("SELECT COUNT(*)"):
            return _CountResult(self.total)
        return _MappingResult(self.rows)


def _row(**overrides):
    row = {
        "id": "op-1",
        "tenant_id": "tenant-a",
        "konto_nr": "10001",
        "konto_name": "Kunde A",
        "konto_typ": "debitoren",
        "op_status": "offen",
        "rechnungsnr": "RE-1",
        "rechnungsdatum": date(2026, 10, 1),
        "datum": date(2026, 10, 1),
        "faelligkeit": date(2026, 10, 10),
        "valuta": None,
        "op_betrag": Decimal("125.50"),
        "betrag": Decimal("125.50"),
        "saldo": Decimal("0"),
        "offen": Decimal("25.50"),
        "op_text": None,
        "waehrung": "EUR",
        "kunde_id": "customer-1",
        "kunde_name": "Kunde A GmbH",
        "lieferant_id": None,
        "lieferant_name": None,
        "skonto_prozent": None,
        "skonto_bis": None,
        "mahn_stufe": 2,
        "zahlbar": True,
        "letzte_bewegung_am": None,
        "kredit_limit": None,
        "kv_limit": None,
        "sperre_grund": None,
        "created_at": datetime(2026, 10, 1),
        "updated_at": datetime(2026, 10, 1),
    }
    row.update(overrides)
    return row


def _call_sync_endpoint(coroutine):
    """Run this synchronous-body async route without a Windows event loop."""
    try:
        coroutine.send(None)
    except StopIteration as completed:
        return completed.value
    raise AssertionError("list endpoint unexpectedly suspended on an await")


def test_list_applies_shared_filters_count_offset_and_stable_order():
    from app.api.v1.endpoints.open_items import list_open_items

    db = _DB(total=17, rows=[_row()])
    response = _call_sync_endpoint(list_open_items(
        tenant_id="tenant-a",
        konto_typ="debitoren",
        op_status=None,
        konto_nr=None,
        search="Kunde",
        limit=2,
        offset=4,
        only_open=True,
        db=db,
    ))

    assert response.total == 17
    assert response.summary["count"] == 1  # summary retains limited-page semantics
    assert len(db.calls) == 4
    count_sql, count_params = db.calls[2]
    page_sql, page_params = db.calls[3]
    assert "tenant_id = :tenant_id" in count_sql
    assert "konto_typ = :konto_typ" in count_sql
    assert "rechnungsnr ILIKE :search" in count_sql
    assert "offen > 0" in count_sql
    assert "op_status IN (:only_open_status, :partially_open_status)" in count_sql
    assert count_params == {
        "tenant_id": "tenant-a",
        "konto_typ": "debitoren",
        "search": "%Kunde%",
        "only_open_status": "offen",
        "partially_open_status": "teilweise",
    }
    assert "ORDER BY faelligkeit ASC, rechnungsnr ASC, id ASC" in page_sql
    assert "LIMIT :limit" in page_sql and "OFFSET :offset" in page_sql
    assert page_params["offset"] == 4
    assert page_params["limit"] == 2


def test_only_open_uses_only_open_amount_when_status_column_is_unavailable():
    from app.api.v1.endpoints.open_items import list_open_items

    db = _DB(total=0, rows=[], columns={"offen"})
    _call_sync_endpoint(list_open_items(
        tenant_id="tenant-a",
        konto_typ=None,
        op_status=None,
        konto_nr=None,
        search=None,
        limit=500,
        offset=0,
        only_open=True,
        db=db,
    ))
    sql, params = db.calls[2]
    assert "offen > 0" in sql
    assert "op_status IN" not in sql
    assert "only_open_status" not in params


def test_open_item_projection_exposes_overdue_as_computed_field():
    from app.api.v1.endpoints.open_items import OpenItem

    data = _row(faelligkeit=date.today(), offen=Decimal("10"))
    item = OpenItem(**data)
    serialized = item.model_dump()
    assert serialized["ueberfaellig"] is False  # due today is not overdue
    assert serialized["op_betrag"] == Decimal("125.50")
    assert serialized["mahn_stufe"] == 2

    overdue = OpenItem(**_row(faelligkeit=date.fromordinal(date.today().toordinal() - 1)))
    assert overdue.ueberfaellig is True
    settled = OpenItem(**_row(offen=Decimal("0"), faelligkeit=date.fromordinal(date.today().toordinal() - 1)))
    assert settled.ueberfaellig is False


def test_list_route_retains_read_role_guard_and_canonical_projection_fields():
    from app.api.v1.endpoints.open_items import OpenItem, open_items_read, router

    route = next(route for route in router.routes if getattr(route, "endpoint", None).__name__ == "list_open_items")
    assert any(dependency.dependency is open_items_read for dependency in route.dependencies)
    fields = OpenItem.model_fields
    assert {"id", "konto_nr", "kunde_name", "rechnungsdatum", "faelligkeit", "op_betrag", "offen", "mahn_stufe"}.issubset(fields)
    assert "ueberfaellig" in OpenItem.model_computed_fields


@pytest.mark.parametrize("field,value", [("limit", 0), ("limit", 5001), ("offset", -1), ("offset", 1_000_001)])
def test_list_query_constraints_reject_out_of_range_values(field, value):
    from app.api.v1.endpoints.open_items import list_open_items

    parameter = signature(list_open_items).parameters[field]
    query = parameter.default
    with pytest.raises(ValidationError):
        TypeAdapter(Annotated[parameter.annotation, *query.metadata]).validate_python(value)
