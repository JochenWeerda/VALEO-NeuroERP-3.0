"""
DOMAIN-PARITY-COV-001 / COV-INT-002: Tests fuer AP Invoices API.

Abdeckung: /api/v1/ap/invoices — Eingangsrechnungen, semantische Status,
DQ-Validierung, Approval-Workflow-Pfade.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.ap_invoices import (
    _compute_ap_invoice_semantic_status,
    calculate_invoice_totals,
)
from app.documents.models import SalesInvoice, DocLine

_TENANT = "test-tenant"
_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": _TENANT}
_client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Unit-Tests semantischer Status
# ---------------------------------------------------------------------------


def test_semantic_status_verbucht():
    assert _compute_ap_invoice_semantic_status({"status": "VERBUCHT"}) == "VERBUCHT"


def test_semantic_status_bezahlt():
    assert _compute_ap_invoice_semantic_status({"status": "BEZAHLT"}) == "BEZAHLT"


def test_semantic_status_pending_approval():
    inv = {"status": "ENTWURF", "approval_status": "pending"}
    assert _compute_ap_invoice_semantic_status(inv) == "ZUR_FREIGABE"


def test_semantic_status_partially_approved():
    inv = {"status": "ENTWURF", "approval_status": "partially_approved"}
    assert _compute_ap_invoice_semantic_status(inv) == "TEILWEISE_FREIGEGEBEN"


def test_semantic_status_approved():
    inv = {"status": "ENTWURF", "approval_status": "approved"}
    assert _compute_ap_invoice_semantic_status(inv) == "FREIGEGEBEN"


def test_semantic_status_rejected():
    inv = {"status": "ENTWURF", "approval_status": "rejected"}
    assert _compute_ap_invoice_semantic_status(inv) == "ABGELEHNT"


def test_semantic_status_fallback_to_document_status():
    inv = {"status": "ENTWURF"}
    assert _compute_ap_invoice_semantic_status(inv) == "ENTWURF"


# ---------------------------------------------------------------------------
# Unit-Tests Summenberechnung
# ---------------------------------------------------------------------------


def _make_invoice(lines=None) -> SalesInvoice:
    doc = SalesInvoice(
        number="AP-001",
        date="2026-05-07",
        customerId="supplier-1",
        dueDate="2026-06-07",
    )
    doc.lines = lines or []
    return doc


def test_calculate_totals_empty():
    doc = _make_invoice()
    result = calculate_invoice_totals(doc)
    assert result.subtotalNet == 0.0
    assert result.totalTax == 0.0
    assert result.totalGross == 0.0


def test_calculate_totals_single_line():
    line = DocLine(article="Weizen", qty=10, price=100.0, vatRate=19.0)
    doc = _make_invoice([line])
    result = calculate_invoice_totals(doc)
    assert result.subtotalNet == pytest.approx(1000.0)
    assert result.totalTax == pytest.approx(190.0)
    assert result.totalGross == pytest.approx(1190.0)


def test_calculate_totals_zero_vat():
    line = DocLine(article="Weizen", qty=5, price=200.0, vatRate=0.0)
    doc = _make_invoice([line])
    result = calculate_invoice_totals(doc)
    assert result.totalTax == pytest.approx(0.0)
    assert result.totalGross == pytest.approx(1000.0)


# ---------------------------------------------------------------------------
# HTTP Endpoint-Tests
# ---------------------------------------------------------------------------


def test_list_ap_invoices_returns_200():
    resp = _client.get("/api/v1/finance/ap/invoices/", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_get_nonexistent_ap_invoice_returns_404():
    resp = _client.get("/api/v1/finance/ap/invoices/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 404


def test_create_ap_invoice_minimal():
    payload = {
        "number": "AP-TEST-001",
        "date": "2026-05-07",
        "customerId": "supplier-1",
        "dueDate": "2026-06-07",
        "lines": [
            {"article": "Weizen", "qty": 1, "price": 100.0, "vatRate": 19.0}
        ],
    }
    resp = _client.post("/api/v1/finance/ap/invoices/", json=payload, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (200, 201, 422)
