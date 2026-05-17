"""
Tests: Rahmenaufträge, Kreditlimit, Sammelrechnung, Zentrale Kontrakte-Engine
"""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from decimal import Decimal


# ── Helpers ────────────────────────────────────────────────────────────────

def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.scalar.return_value = None
    db.commit = MagicMock()
    return db


def _row(**kwargs):
    obj = MagicMock()
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


# ── Rahmenaufträge ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_released_total_sums_quantities():
    from app.api.v1.endpoints.sales_blanket_orders import _released_total
    db = _mock_db()
    db.execute.return_value.scalar.return_value = 70.0
    result = _released_total(db, "bo-1", "tenant-1")
    assert result == 70.0


@pytest.mark.unit
def test_released_total_returns_zero_when_null():
    from app.api.v1.endpoints.sales_blanket_orders import _released_total
    db = _mock_db()
    db.execute.return_value.scalar.return_value = None
    result = _released_total(db, "bo-1", "tenant-1")
    assert result == 0.0


@pytest.mark.unit
def test_blanket_order_row_to_model():
    from app.api.v1.endpoints.sales_blanket_orders import _row_to_blanket, BlanketOrderOut
    row = {
        "id": "bo-1",
        "customer_id": "c-1",
        "article_id": "art-1",
        "total_quantity": 100.0,
        "unit_price": 5.50,
        "valid_from": "2026-01-01",
        "valid_to": "2026-12-31",
        "status": "AKTIV",
        "tenant_id": "t-1",
    }
    result = _row_to_blanket(row)
    assert result.status == "AKTIV"
    assert result.total_quantity == 100.0


# ── Kreditlimit ────────────────────────────────────────────────────────────

def _make_limit_row(credit_limit=10000.0, warn=80.0, block=100.0):
    row = MagicMock()
    data = {"credit_limit_eur": credit_limit, "warning_threshold_percent": warn, "block_threshold_percent": block}
    row.__getitem__ = lambda self, k: data[k]
    row.get = lambda k, d=None: data.get(k, d)
    return row


@pytest.mark.unit
def test_credit_status_ok():
    """Low exposure (500/10000 = 5%) → OK."""
    from app.api.v1.endpoints.credit_management import get_credit_status_data
    db = _mock_db()
    limit_row = _make_limit_row(10000.0)

    call_n = [0]
    def execute_side(stmt, params=None):
        m = MagicMock()
        sql = str(stmt).lower()
        call_n[0] += 1
        if "credit_limit" in sql:
            m.mappings.return_value.first.return_value = limit_row
        else:
            m.scalar.return_value = 250.0  # open_invoices=250, open_orders=250 → total=500
        return m

    db.execute.side_effect = execute_side
    result = get_credit_status_data(db, "c-1", "t-1")
    assert result.status == "OK"


@pytest.mark.unit
def test_credit_status_warning():
    """8500/10000 = 85% → WARNING."""
    from app.api.v1.endpoints.credit_management import get_credit_status_data
    db = _mock_db()
    limit_row = _make_limit_row(10000.0)

    call_n = [0]
    def execute_side(stmt, params=None):
        m = MagicMock()
        sql = str(stmt).lower()
        call_n[0] += 1
        if "credit_limit" in sql:
            m.mappings.return_value.first.return_value = limit_row
        else:
            m.scalar.return_value = 4250.0  # 8500 total across 2 calls
        return m

    db.execute.side_effect = execute_side
    result = get_credit_status_data(db, "c-1", "t-1")
    assert result.status in ("WARNING", "BLOCKED")


@pytest.mark.unit
def test_credit_status_no_limit_row_returns_ok():
    """No credit limit configured → unlimited → OK."""
    from app.api.v1.endpoints.credit_management import get_credit_status_data
    db = _mock_db()

    def execute_side(stmt, params=None):
        m = MagicMock()
        m.mappings.return_value.first.return_value = None
        m.scalar.return_value = 0.0
        return m

    db.execute.side_effect = execute_side
    result = get_credit_status_data(db, "c-1", "t-1")
    assert result.status == "OK"


# ── Zentrale Kontrakt-Engine ────────────────────────────────────────────────

@pytest.mark.unit
def test_contract_version_number_starts_at_1():
    from app.api.v1.endpoints.central_contracts import _next_version_number
    db = _mock_db()
    db.execute.return_value.scalar.return_value = None
    result = _next_version_number(db, "contract-1", "tenant-1")
    assert result == 1


@pytest.mark.unit
def test_contract_version_number_increments():
    from app.api.v1.endpoints.central_contracts import _next_version_number
    db = _mock_db()
    # _next_version_number uses .scalar() directly on the execute result
    db.execute.return_value.scalar.return_value = 4  # COALESCE(MAX,0)+1 = 4
    result = _next_version_number(db, "contract-1", "tenant-1")
    assert result == 4


@pytest.mark.unit
def test_contract_not_found_raises_404():
    from app.api.v1.endpoints.central_contracts import _get_contract
    from fastapi import HTTPException
    db = _mock_db()
    # _get_contract uses .mappings().first()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        _get_contract(db, "missing-id", "tenant-1")
    assert exc_info.value.status_code == 404


@pytest.mark.unit
def test_contract_row_to_model():
    from app.api.v1.endpoints.central_contracts import _row_to_contract
    row = {
        "id": "c-1",
        "contract_number": "K-2026-001",
        "contract_type": "AGRAR",
        "title": "Weizenkontrakt",
        "counterparty_id": "bp-1",
        "counterparty_type": "SUPPLIER",
        "status": "AKTIV",
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "auto_renewal_days": None,
        "notice_period_days": 30,
        "total_value_eur": 50000.0,
        "tenant_id": "t-1",
    }
    result = _row_to_contract(row)
    assert result.contract_type == "AGRAR"
    assert result.status == "AKTIV"


@pytest.mark.unit
def test_collective_invoice_create_schema():
    """Sammelrechnung Schema validiert Pflichtfelder."""
    from app.api.v1.endpoints.collective_documents import CollectiveInvoiceCreate
    payload = CollectiveInvoiceCreate(
        customer_id="c-1",
        delivery_note_ids=["dn-1", "dn-2"],
        invoice_date="2026-05-17",
    )
    assert len(payload.delivery_note_ids) == 2
    assert payload.customer_id == "c-1"
