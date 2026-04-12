"""
Tests for AP invoices endpoints (app/api/v1/endpoints/ap_invoices.py).

Covers _compute_ap_invoice_semantic_status helper and endpoint structure tests.
"""

import pytest
from starlette.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def auth_headers():
    return {
        "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
        "X-Tenant-ID": "test-tenant",
    }


# ═══════════════════════════════════════════════════════════════════════════
# _compute_ap_invoice_semantic_status unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestComputeApInvoiceSemanticStatus:
    """
    Status logic:
    - VERBUCHT, BEZAHLT, TEILWEISE_FREIGEGEBEN in document_status -> return as-is
    - approval_status == 'pending'             -> ZUR_FREIGABE
    - approval_status == 'partially_approved'  -> TEILWEISE_FREIGEGEBEN
    - approval_status == 'approved'            -> FREIGEGEBEN
    - approval_status == 'rejected'            -> ABGELEHNT
    - fallback -> document_status
    """

    def _compute(self, invoice_dict):
        from app.api.v1.endpoints.ap_invoices import _compute_ap_invoice_semantic_status
        return _compute_ap_invoice_semantic_status(invoice_dict)

    def test_entwurf_no_approval(self):
        assert self._compute({"status": "ENTWURF"}) == "ENTWURF"

    def test_verbucht_overrides_approval(self):
        assert self._compute({"status": "VERBUCHT", "approval_status": "pending"}) == "VERBUCHT"

    def test_bezahlt_overrides_approval(self):
        assert self._compute({"status": "BEZAHLT", "approval_status": "rejected"}) == "BEZAHLT"

    def test_teilweise_freigegeben_from_document_status(self):
        assert self._compute({"status": "TEILWEISE_FREIGEGEBEN"}) == "TEILWEISE_FREIGEGEBEN"

    def test_pending_approval_maps_to_zur_freigabe(self):
        assert self._compute({"status": "ENTWURF", "approval_status": "pending"}) == "ZUR_FREIGABE"

    def test_partially_approved_maps_to_teilweise_freigegeben(self):
        assert self._compute({"status": "ENTWURF", "approval_status": "partially_approved"}) == "TEILWEISE_FREIGEGEBEN"

    def test_approved_maps_to_freigegeben(self):
        assert self._compute({"status": "ENTWURF", "approval_status": "approved"}) == "FREIGEGEBEN"

    def test_rejected_maps_to_abgelehnt(self):
        assert self._compute({"status": "ENTWURF", "approval_status": "rejected"}) == "ABGELEHNT"

    def test_none_status_defaults_to_entwurf(self):
        assert self._compute({}) == "ENTWURF"

    def test_none_approval_status_returns_document_status(self):
        assert self._compute({"status": "ENTWURF", "approval_status": None}) == "ENTWURF"

    def test_unknown_approval_status_falls_back_to_document_status(self):
        assert self._compute({"status": "ENTWURF", "approval_status": "some_unknown"}) == "ENTWURF"


# ═══════════════════════════════════════════════════════════════════════════
# Endpoint structure tests
# ═══════════════════════════════════════════════════════════════════════════

class TestApInvoiceEndpoints:
    def test_list_ap_invoices(self, client, auth_headers):
        resp = client.get("/api/v1/finance/ap/invoices/", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_ap_invoice_422_on_empty_body(self, client, auth_headers):
        resp = client.post(
            "/api/v1/finance/ap/invoices/",
            headers=auth_headers,
            json={},
        )
        # SalesInvoice model requires fields -> 422
        assert resp.status_code == 422

    def test_get_ap_invoice_404(self, client, auth_headers):
        resp = client.get(
            "/api/v1/finance/ap/invoices/nonexistent-invoice",
            headers=auth_headers,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 404

    def test_delete_ap_invoice_404(self, client, auth_headers):
        resp = client.delete(
            "/api/v1/finance/ap/invoices/nonexistent-invoice",
            headers=auth_headers,
        )
        skip_if_db_unavailable(resp)
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════
# calculate_invoice_totals unit tests
# ═══════════════════════════════════════════════════════════════════════════

class TestCalculateInvoiceTotals:
    def test_calculates_totals_correctly(self):
        from app.api.v1.endpoints.ap_invoices import calculate_invoice_totals
        from app.documents.models import SalesInvoice

        # Build a minimal SalesInvoice with lines (DocLine requires 'article' field)
        inv = SalesInvoice(
            number="TEST-001",
            date="2026-04-10",
            customerId="CUST-001",
            dueDate="2026-05-10",
            lines=[
                {"article": "Item A", "qty": 10, "price": 100.0, "vatRate": 19.0},
                {"article": "Item B", "qty": 5, "price": 50.0, "vatRate": 7.0},
            ],
        )
        result = calculate_invoice_totals(inv)
        # 10*100 = 1000 + 5*50 = 250 -> net = 1250
        assert result.subtotalNet == 1250.0
        # tax: 1000*0.19=190 + 250*0.07=17.5 -> 207.5
        assert result.totalTax == 207.5
        assert result.totalGross == 1457.5

    def test_zero_lines(self):
        from app.api.v1.endpoints.ap_invoices import calculate_invoice_totals
        from app.documents.models import SalesInvoice

        inv = SalesInvoice(
            number="TEST-EMPTY",
            date="2026-04-10",
            customerId="CUST-001",
            dueDate="2026-05-10",
            lines=[],
        )
        result = calculate_invoice_totals(inv)
        assert result.subtotalNet == 0.0
        assert result.totalTax == 0.0
        assert result.totalGross == 0.0
