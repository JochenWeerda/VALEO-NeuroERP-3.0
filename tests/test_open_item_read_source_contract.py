from datetime import date, datetime
from decimal import Decimal

import pytest
from fastapi import HTTPException


class _Result:
    def __init__(self, *, scalar=None, rows=None, one=None):
        self._scalar = scalar
        self._rows = list(rows or [])
        self._one = one

    def scalar(self):
        return self._scalar

    def fetchall(self):
        return self._rows

    def mappings(self):
        return self

    def first(self):
        return self._one

    def all(self):
        return self._rows


class _ReadDB:
    def __init__(self, *, parent=True):
        self.calls = []
        self.parent = parent
        self.summary_row = {
            "id": "op-1",
            "konto_nr": "10001",
            "konto_name": "Musterkunde",
            "konto_typ": "debitoren",
            "beleg_nr": "RE-2026-17",
            "offener_betrag": Decimal("245.75"),
            "faellig_am": date(2026, 10, 20),
            "status": "teilweise",
        }
        self.settlement_rows = [
            {
                "id": "journal-1",
                "entry_number": "BU-101",
                "entry_date": date(2026, 10, 21),
                "description": "Ausgleich RE-2026-17",
                "total_debit": Decimal("100.25"),
                "created_at": datetime(2026, 10, 21, 12, 30),
                "waehrung": "EUR",
            }
        ]

    def execute(self, statement, params=None):
        sql = str(statement)
        bound = dict(params or {})
        self.calls.append((sql, bound))
        if "FROM pg_class" in sql:
            return _Result(scalar="domain_erp")
        if "FROM information_schema.columns" in sql:
            return _Result(rows=[(name,) for name in {
                "rechnungsnr", "offen", "faelligkeit", "op_status",
            }])
        if "FROM domain_erp.offene_posten" in sql and "SELECT id FROM" in sql:
            parent = {"id": bound["id"]} if self.parent else None
            return _Result(one=parent)
        if "FROM domain_erp.offene_posten" in sql and "beleg_nr" in sql:
            return _Result(one=self.summary_row)
        if "FROM domain_erp.journal_entries" in sql:
            return _Result(rows=self.settlement_rows)
        raise AssertionError(f"Unexpected SQL in mock: {sql}")


def test_settlements_use_exact_audit_entity_link_not_description_matching():
    from app.services.open_item_read_source import read_settlements

    db = _ReadDB()
    rows = read_settlements(db, "op-1", "tenant-a")

    parent_sql, parent_params = next(call for call in db.calls if "SELECT id FROM" in call[0])
    settlement_sql, settlement_params = next(call for call in db.calls if "journal_entries" in call[0])
    assert "tenant_id=:tenant AND id=:id" in parent_sql
    assert parent_params == {"tenant": "tenant-a", "id": "op-1"}
    assert "j.source='op_settlement'" in settlement_sql
    assert "a.entity_id=j.id" in settlement_sql
    assert "a.entity_type='journal_entry'" in settlement_sql
    assert "a.action='create'" in settlement_sql
    assert "a.changes->>'source'='op_settlement'" in settlement_sql
    assert "a.changes->>'op_id'=:op_id" in settlement_sql
    assert "description ILIKE" not in settlement_sql
    assert "description LIKE" not in settlement_sql
    assert settlement_params == {"tenant": "tenant-a", "op_id": "op-1"}
    assert rows == [{
        "id": "journal-1",
        "payment_amount": 100.25,
        "payment_date": "2026-10-21",
        "payment_reference": "BU-101",
        "payment_type": "payment",
        "notes": "Ausgleich RE-2026-17",
        "created_at": "2026-10-21T12:30:00",
        "waehrung": "EUR",
    }]


def test_settlement_read_requires_verified_tenant_and_scoped_parent():
    from app.services.open_item_read_source import read_settlements

    missing_tenant = _ReadDB()
    with pytest.raises(HTTPException) as missing:
        read_settlements(missing_tenant, "op-1", "")
    assert missing.value.status_code == 403
    assert missing_tenant.calls == []

    foreign_parent = _ReadDB(parent=False)
    with pytest.raises(HTTPException) as not_found:
        read_settlements(foreign_parent, "foreign-op", "tenant-a")
    assert not_found.value.status_code == 404
    assert not any("journal_entries" in sql for sql, _ in foreign_parent.calls)
    _, parent_params = next(call for call in foreign_parent.calls if "SELECT id FROM" in call[0])
    assert parent_params == {"tenant": "tenant-a", "id": "foreign-op"}


def test_ar_open_item_summary_is_tenant_scoped_and_projects_canonical_values():
    from app.services.mask_rollout_summary_service import MaskRolloutSummaryService

    db = _ReadDB()
    result = MaskRolloutSummaryService(db, "tenant-a").build_summary(
        "finance/ar-open-item", "op-1"
    )

    sql, params = next(call for call in db.calls if "beleg_nr" in call[0])
    assert "WHERE tenant_id=:tenant_id AND id=:op_id" in sql
    assert params == {"tenant_id": "tenant-a", "op_id": "op-1"}
    assert result["tenant_id"] == "tenant-a"
    assert result["op_id"] == "op-1"
    assert result["title"] == "RE-2026-17"
    assert result["subtitle"] == "Musterkunde"
    assert result["summary"] == {
        "konto_typ": "debitoren",
        "offener_betrag": 245.75,
        "faellig_am": "2026-10-20",
        "status": "teilweise",
    }
    assert result["available_tabs"] == ["kopf", "ausgleich"]


def test_ar_open_item_settlement_tab_uses_shared_source_and_aliases(monkeypatch):
    import app.services.mask_rollout_summary_service as summary_module

    db = _ReadDB()
    captured = {}

    def fake_tab_page(**kwargs):
        captured.update(kwargs)
        return kwargs

    monkeypatch.setattr(summary_module, "build_tab_page", fake_tab_page)
    result = summary_module.MaskRolloutSummaryService(db, "tenant-a").build_tab_data(
        "finance/ar-open-item", "op-1", "ausgleich"
    )

    parent_sql, parent_params = next(call for call in db.calls if "SELECT id FROM" in call[0])
    settlement_sql, settlement_params = next(call for call in db.calls if "journal_entries" in call[0])
    assert "tenant_id=:tenant AND id=:id" in parent_sql
    assert parent_params == {"tenant": "tenant-a", "id": "op-1"}
    assert "a.changes->>'op_id'=:op_id" in settlement_sql
    assert settlement_params == {"tenant": "tenant-a", "op_id": "op-1"}
    assert result["table_key"] == "settlements"
    assert result["items"] == [{
        "id": "journal-1",
        "betrag": 100.25,
        "buchungs_datum": "2026-10-21",
        "referenz": "BU-101",
        "notiz": "Ausgleich RE-2026-17",
        "zahlungsart": "payment",
        "waehrung": "EUR",
        "datum": "2026-10-21",
        "bank_ref": "BU-101",
    }]
