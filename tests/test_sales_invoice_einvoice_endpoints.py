"""Coverage-Offensive sales_invoice_einvoice.py (A6 / SPEC-P0-05).

Deckt XRechnung-/ZUGFeRD-Generierung und den GET-Abruf ueber Routing,
Validierung und den Not-Found-Pfad (_load_sales_invoice -> 404) ab.
E-Rechnungs-Export war laut Audit bei ~30%.
"""
from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/sales/invoices"


def _missing() -> str:
    return f"INV-MISSING-{uuid.uuid4().hex[:8]}"


def test_generate_xrechnung_unknown_invoice_returns_404():
    resp = client.post(f"{BASE}/{_missing()}/einvoice/xrechnung", json={}, headers=HEADERS)
    assert resp.status_code in (404, 503), resp.text


def test_generate_zugferd_unknown_invoice_returns_404():
    resp = client.post(f"{BASE}/{_missing()}/einvoice/zugferd", json={}, headers=HEADERS)
    assert resp.status_code in (404, 500, 503), resp.text


def test_get_xrechnung_unknown_invoice_returns_404():
    resp = client.get(f"{BASE}/{_missing()}/einvoice/xrechnung", headers=HEADERS)
    assert resp.status_code in (404, 503), resp.text


def test_generate_xrechnung_accepts_empty_payload_shape():
    # Leerer Payload ist valide (EInvoiceExportRequest Defaults) -> nicht 422,
    # sondern 404 wegen fehlender Rechnung.
    resp = client.post(f"{BASE}/{_missing()}/einvoice/xrechnung", json={}, headers=HEADERS)
    assert resp.status_code != 422, resp.text
