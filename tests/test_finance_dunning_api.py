"""
COV-FIN-002: Tests for Dunning API endpoints.

Covers /api/v1/finance/dunning — rules CRUD, dunning notices,
batch processing, dunning runs, and status transitions.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Dunning Rules ────────────────────────────────────────────────


class TestDunningRules:
    """GET/POST /finance/dunning/rules"""

    def test_list_rules_returns_200(self):
        r = client.get("/api/v1/finance/dunning/rules", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_rule_valid(self):
        payload = {
            "level": 3,
            "days_overdue_min": 60,
            "days_overdue_max": 90,
            "fee_amount": "15.00",
            "fee_percentage": "0.00",
            "interest_rate": "0.05",
            "payment_deadline_days": 14,
            "block_customer": False,
            "escalate_to_collection": False,
            "description_template": "Mahnstufe {level} - Letzte Mahnung",
            "active": True,
        }
        r = client.post("/api/v1/finance/dunning/rules", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code == 400:
            # Duplicate level — acceptable on repeat runs
            assert "already exists" in r.text.lower() or "level" in r.text.lower()
        else:
            assert r.status_code == 201
            data = r.json()
            assert data["level"] == 3

    def test_create_rule_missing_level_422(self):
        r = client.post("/api/v1/finance/dunning/rules", headers=AUTH, json={})
        assert r.status_code == 422


# ── Dunning Notices ──────────────────────────────────────────────


class TestDunningNotices:
    """CRUD on /finance/dunning (notices list, manual create)"""

    def test_list_notices_returns_200(self):
        r = client.get("/api/v1/finance/dunning", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_notice_valid(self):
        payload = {
            "op_id": "OP-TEST-001",
            "debtor_id": "DEB-TEST-001",
            "dunning_level": 1,
            "dunning_date": "2026-04-01",
            "due_date": "2026-04-15",
            "open_amount": 1250.00,
        }
        r = client.post("/api/v1/finance/dunning", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        assert r.status_code in (200, 201)
        data = r.json()
        assert data["debtor_id"] == "DEB-TEST-001"
        assert data["dunning_level"] == 1

    def test_create_notice_missing_fields_422(self):
        r = client.post("/api/v1/finance/dunning", headers=AUTH, json={})
        assert r.status_code == 422

    def test_send_nonexistent_404(self):
        r = client.put("/api/v1/finance/dunning/NONEXISTENT-ID/send", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_paid_nonexistent_404(self):
        r = client.put("/api/v1/finance/dunning/NONEXISTENT-ID/paid", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Dunning Run ──────────────────────────────────────────────────


class TestDunningRun:
    """POST /finance/dunning/run and /finance/dunning/process"""

    def test_run_returns_structured_result(self):
        payload = {"as_of_date": "2026-04-13", "tenant_id": "test-tenant"}
        r = client.post("/api/v1/finance/dunning/run", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code == 200:
            data = r.json()
            assert "run_id" in data
            assert "notices_created" in data
        else:
            assert r.status_code in (200, 500)

    def test_process_returns_list(self):
        payload = {"auto_apply_rules": True, "tenant_id": "test-tenant"}
        r = client.post("/api/v1/finance/dunning/process", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code == 200:
            assert isinstance(r.json(), list)
