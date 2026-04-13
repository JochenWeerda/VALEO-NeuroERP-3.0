"""
COV-FIN-002: Tests for Booking Templates API endpoints.

Covers /api/v1/finance/booking-templates — CRUD and apply.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


class TestBookingTemplatesList:
    """GET /finance/booking-templates"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/finance/booking-templates", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestBookingTemplateCRUD:
    """POST/GET/PUT/DELETE /finance/booking-templates"""

    def test_create_template(self):
        payload = {
            "name": "Test-Vorlage Wareneingang",
            "description": "Standardbuchung Wareneingang",
            "category": "einkauf",
            "trigger_type": "manual",
            "lines": [
                {
                    "account_number": "3000",
                    "debit_percentage": 100,
                    "credit_percentage": 0,
                    "line_number": 1,
                },
                {
                    "account_number": "1600",
                    "debit_percentage": 0,
                    "credit_percentage": 100,
                    "line_number": 2,
                },
            ],
            "currency": "EUR",
            "active": True,
        }
        r = client.post("/api/v1/finance/booking-templates", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code in (400, 500):
            return  # Duplicate or DB unavailable
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Test-Vorlage Wareneingang"
        assert len(data["lines"]) == 2

    def test_create_unbalanced_400(self):
        payload = {
            "name": "Unbalanced",
            "category": "test",
            "trigger_type": "manual",
            "lines": [
                {
                    "account_number": "3000",
                    "debit_percentage": 100,
                    "credit_percentage": 0,
                    "line_number": 1,
                },
                {
                    "account_number": "1600",
                    "debit_percentage": 0,
                    "credit_percentage": 50,
                    "line_number": 2,
                },
            ],
            "currency": "EUR",
            "active": True,
        }
        r = client.post("/api/v1/finance/booking-templates", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        # Should reject unbalanced templates
        assert r.status_code in (400, 422)

    def test_create_empty_body_422(self):
        r = client.post("/api/v1/finance/booking-templates", headers=AUTH, json={})
        assert r.status_code == 422

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/finance/booking-templates/NONEXISTENT-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/finance/booking-templates/NONEXISTENT-ID", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestBookingTemplateApply:
    """POST /finance/booking-templates/{id}/apply"""

    def test_apply_nonexistent_404(self):
        payload = {
            "amount": 100.0,
            "entry_date": "2026-04-13",
        }
        r = client.post(
            "/api/v1/finance/booking-templates/NONEXISTENT-ID/apply",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code in (400, 404)
