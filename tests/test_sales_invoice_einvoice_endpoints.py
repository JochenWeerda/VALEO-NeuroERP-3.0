"""Sales Invoice E-Rechnung — echte HTTP-Vertraege (SPEC-P0-05).

Erfordert PostgreSQL/`document store` (`require_db`). Unbekannte Rechnungen → 404.
Happy Path speichert ueber den Document-Store (DB oder In-Memory-Fallback).
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.documents.router_helpers import get_repository, save_to_store
from app.main import app
from app.core.database import SessionLocal

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/sales/invoices"

pytestmark = pytest.mark.unit


def _missing() -> str:
    return f"INV-MISSING-{uuid.uuid4().hex[:8]}"


def _seed_invoice() -> str:
    number = f"INV-Q-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "number": number,
        "date": "2026-03-01",
        "dueDate": "2026-03-31",
        "paymentTerms": "net14",
        "customerId": "C-QUALITY-1",
        "subtotalNet": 100,
        "totalTax": 19,
        "totalGross": 119,
        "lines": [{"article": "Weizen", "qty": 2, "price": 50, "vatRate": 19}],
    }
    db = SessionLocal()
    try:
        repo = get_repository(db)
        save_to_store("sales_invoice", number, payload, repo=repo)
    finally:
        db.close()
    return number


def test_generate_xrechnung_unknown_invoice_returns_404(require_db):
    resp = client.post(f"{BASE}/{_missing()}/einvoice/xrechnung", json={}, headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_generate_zugferd_unknown_invoice_returns_404(require_db):
    resp = client.post(f"{BASE}/{_missing()}/einvoice/zugferd", json={}, headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_get_xrechnung_unknown_invoice_returns_404(require_db):
    resp = client.get(f"{BASE}/{_missing()}/einvoice/xrechnung", headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_generate_xrechnung_empty_payload_is_not_422(require_db):
    resp = client.post(f"{BASE}/{_missing()}/einvoice/xrechnung", json={}, headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_generate_xrechnung_for_seeded_invoice(require_db):
    number = _seed_invoice()
    resp = client.post(
        f"{BASE}/{number}/einvoice/xrechnung",
        json={
            "buyer_reference": "LEITWEG-99",
            "supplier": {"name": "VALEO Test", "country_code": "DE", "vat_id": "DE123"},
            "customer": {"name": "Kunde Test", "country_code": "DE"},
        },
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    assert "xml" in resp.headers.get("content-type", "")
    assert b"Invoice" in resp.content or b"CrossIndustryInvoice" in resp.content or len(resp.content) > 100
    assert resp.headers.get("X-EInvoice-Format") == "XRechnung-3.0"


def test_get_xrechnung_for_seeded_invoice(require_db):
    number = _seed_invoice()
    resp = client.get(f"{BASE}/{number}/einvoice/xrechnung", headers=HEADERS)
    assert resp.status_code == 200, resp.text
    assert len(resp.content) > 100


def test_generate_zugferd_for_seeded_invoice(require_db):
    number = _seed_invoice()
    resp = client.post(f"{BASE}/{number}/einvoice/zugferd", json={}, headers=HEADERS)
    # 200 mit PDF oder 503 wenn factur-x/reportlab fehlen — beides ist spezifizierter Vertrag
    assert resp.status_code in (200, 503), resp.text
    if resp.status_code == 200:
        assert resp.headers.get("content-type") == "application/pdf"
        assert resp.content[:4] == b"%PDF"
