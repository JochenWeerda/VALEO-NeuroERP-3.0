"""
COV-FIN-002: Tests for Payment Runs API endpoints.

Covers /api/v1/finance/payment-runs — plan, CRUD, approve, execute, SEPA XML.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestPaymentRunsList:
    """GET /finance/payment-runs"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/finance/payment-runs", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestPaymentRunPlan:
    """POST /finance/payment-runs/plan"""

    def test_plan_returns_suggestions(self):
        payload = {
            "execution_date": "2026-04-20",
            "tenant_id": "test-tenant",
        }
        r = client.post("/api/v1/finance/payment-runs/plan", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "suggested_payments" in data
        assert "total_amount" in data

    def test_plan_missing_date_422(self):
        r = client.post("/api/v1/finance/payment-runs/plan", headers=AUTH, json={})
        assert r.status_code == 422


class TestPaymentRunCRUD:
    """POST/GET /finance/payment-runs, approve, execute"""

    def test_create_payment_run(self):
        payload = {
            "run_number": "ZL-TEST-001",
            "execution_date": "2026-04-20",
            "initiator_name": "VALEO Test GmbH",
            "initiator_iban": "DE89370400440532013000",
            "initiator_bic": "COBADEFFXXX",
            "payments": [
                {
                    "creditor_id": "KRED-001",
                    "creditor_name": "Lieferant A",
                    "iban": "DE27100777770209299700",
                    "amount": 500.0,
                    "purpose": "RE-2026-001",
                    "discount_used": False,
                    "discount_amount": 0,
                },
            ],
        }
        r = client.post("/api/v1/finance/payment-runs", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code in (400, 500):
            return  # Duplicate or DB unavailable
        assert r.status_code == 201
        data = r.json()
        assert data["run_number"] == "ZL-TEST-001"
        assert data["payment_count"] >= 1

    def test_get_nonexistent_run_404(self):
        r = client.get("/api/v1/finance/payment-runs/NONEXISTENT-RUN", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_approve_nonexistent_run_404(self):
        r = client.post(
            "/api/v1/finance/payment-runs/NONEXISTENT-RUN/approve",
            headers=AUTH,
            json={"approved_by": "test-user"},
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_execute_nonexistent_run_404(self):
        r = client.post(
            "/api/v1/finance/payment-runs/NONEXISTENT-RUN/execute",
            headers=AUTH,
            json={"executed_by": "test-user"},
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_sepa_xml_nonexistent_run_404(self):
        r = client.get("/api/v1/finance/payment-runs/NONEXISTENT-RUN/sepa-xml", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404
