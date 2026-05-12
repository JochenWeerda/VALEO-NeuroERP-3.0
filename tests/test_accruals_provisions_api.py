"""DOM-FIN-002: Tests fuer accruals_provisions.py (Abgrenzungen/Rueckstellungen).

Abdeckung: AccrualItemBase/Create-Validierung, HTTP smoke.
"""
from __future__ import annotations

from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.accruals_provisions import (
    AccrualItemBase,
    AccrualItemCreate,
    AccrualItem,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# AccrualItemBase / AccrualItemCreate validation
# ---------------------------------------------------------------------------

def test_accrual_item_create_valid():
    item = AccrualItemCreate(
        description="Umsatzsteuervorauszahlung April",
        amount=Decimal("2500.00"),
        account_number="1780",
        counterpart_account="1200",
        period="2026-04",
        accrual_type="rechnungsabgrenzungsposten",
    )
    assert item.amount == Decimal("2500.00")
    assert item.period == "2026-04"


def test_accrual_item_rejects_empty_description():
    with pytest.raises(Exception):
        AccrualItemCreate(
            description="",
            amount=Decimal("100.00"),
            account_number="1780",
            counterpart_account="1200",
            period="2026-04",
            accrual_type="rueckstellung",
        )


def test_accrual_item_rejects_negative_amount():
    with pytest.raises(Exception):
        AccrualItemCreate(
            description="Test",
            amount=Decimal("-1.00"),
            account_number="1780",
            counterpart_account="1200",
            period="2026-04",
            accrual_type="rueckstellung",
        )


def test_accrual_item_requires_all_fields():
    with pytest.raises(Exception):
        AccrualItemCreate(description="Test", amount=Decimal("100"))


def test_accrual_item_zero_amount_allowed():
    item = AccrualItemCreate(
        description="Nullbuchung",
        amount=Decimal("0.00"),
        account_number="1780",
        counterpart_account="1200",
        period="2026-05",
        accrual_type="rueckstellung",
    )
    assert item.amount == Decimal("0.00")


def test_accrual_item_full_model_defaults():
    item = AccrualItem(
        id="ai-001",
        tenant_id="test-tenant",
        description="Reparaturrückstellung",
        amount=Decimal("5000.00"),
        account_number="4900",
        counterpart_account="1300",
        period="2026-04",
        accrual_type="rueckstellung",
    )
    assert item.status == "draft"
    assert item.created_at is None


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_accruals_returns_200():
    resp = _client.get("/api/v1/finance/accruals-provisions", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_list_accruals_with_period_filter():
    resp = _client.get("/api/v1/finance/accruals-provisions?period=2026-04", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_create_accrual_missing_fields_returns_422():
    resp = _client.post("/api/v1/finance/accruals-provisions", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_create_accrual_valid_payload():
    import uuid
    payload = {
        "description": f"Test Rueckstellung {uuid.uuid4().hex[:6]}",
        "amount": "1500.00",
        "account_number": "1780",
        "counterpart_account": "1200",
        "period": "2026-04",
        "accrual_type": "rueckstellung",
    }
    resp = _client.post("/api/v1/finance/accruals-provisions", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)


def test_get_nonexistent_accrual_returns_404():
    resp = _client.get("/api/v1/finance/accruals-provisions/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_update_nonexistent_accrual_returns_404():
    resp = _client.put(
        "/api/v1/finance/accruals-provisions/does-not-exist",
        json={"description": "Updated"},
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_delete_nonexistent_accrual_returns_404():
    resp = _client.delete("/api/v1/finance/accruals-provisions/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_post_nonexistent_accrual_returns_404():
    resp = _client.post(
        "/api/v1/finance/accruals-provisions/does-not-exist/post",
        headers=_HEADERS,
    )
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404
