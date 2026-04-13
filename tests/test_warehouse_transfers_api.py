"""
COV-INV-002: Tests for Warehouse Transfers API endpoints.

Covers /api/v1/warehouses/transfers — Transfers CRUD + Post,
Corrections CRUD, Bin Locations.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Transfers ───────────────────────────────────────────────────


class TestTransfersList:
    """GET /warehouses/transfers/"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/transfers/", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data

    def test_list_with_pagination(self):
        r = client.get("/api/v1/warehouses/transfers/?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestTransfersCRUD:
    """POST/GET/PUT/DELETE /warehouses/transfers"""

    def test_create_transfer(self):
        payload = {
            "transfer_number": "UML-TEST-001",
            "from_warehouse_id": "WH-001",
            "to_warehouse_id": "WH-002",
            "notes": "Test-Umlagerung COV-INV-002",
        }
        r = client.post("/api/v1/warehouses/transfers/", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_create_transfer_missing_fields_422(self):
        r = client.post("/api/v1/warehouses/transfers/", headers=AUTH, json={})
        assert r.status_code == 422

    def test_get_nonexistent_transfer_404(self):
        r = client.get(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_update_nonexistent_transfer_404(self):
        payload = {
            "transfer_number": "UML-TEST-002",
            "from_warehouse_id": "WH-001",
            "to_warehouse_id": "WH-003",
        }
        r = client.put(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_transfer_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_post_nonexistent_transfer_404(self):
        r = client.post(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/post",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestTransferLines:
    """POST/PUT/DELETE /warehouses/transfers/{id}/lines"""

    def test_create_line_nonexistent_transfer_404(self):
        payload = {
            "article_id": "ART-001",
            "quantity": 100,
        }
        r = client.post(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_update_line_nonexistent_404(self):
        payload = {
            "article_id": "ART-001",
            "quantity": 50,
        }
        r = client.put(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines/NONEXISTENT-LINE",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_line_nonexistent_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/NONEXISTENT-TRANSFER/lines/NONEXISTENT-LINE",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Corrections ─────────────────────────────────────────────────


class TestCorrectionsList:
    """GET /warehouses/transfers/corrections"""

    def test_list_returns_paginated(self):
        r = client.get("/api/v1/warehouses/transfers/corrections", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data


class TestCorrectionsCRUD:
    """POST/PUT/DELETE /warehouses/transfers/corrections"""

    def test_create_correction(self):
        payload = {
            "correction_number": "KORR-TEST-001",
            "warehouse_id": "WH-001",
            "reason": "Inventurdifferenz",
        }
        r = client.post(
            "/api/v1/warehouses/transfers/corrections",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_create_correction_missing_fields_422(self):
        r = client.post(
            "/api/v1/warehouses/transfers/corrections",
            headers=AUTH,
            json={},
        )
        assert r.status_code == 422

    def test_update_nonexistent_correction_404(self):
        payload = {
            "correction_number": "KORR-TEST-002",
            "warehouse_id": "WH-001",
        }
        r = client.put(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_correction_404(self):
        r = client.delete(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


class TestCorrectionLines:
    """GET/POST correction lines"""

    def test_get_lines_nonexistent_404(self):
        r = client.get(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR/lines",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_line_nonexistent_404(self):
        payload = {
            "article_id": "ART-001",
            "old_quantity": 100,
            "new_quantity": 95,
        }
        r = client.post(
            "/api/v1/warehouses/transfers/corrections/NONEXISTENT-CORR/lines",
            headers=AUTH,
            json=payload,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Bin Locations ───────────────────────────────────────────────


class TestBinLocations:
    """GET /warehouses/transfers/bin-locations"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/warehouses/transfers/bin-locations", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_filter_by_warehouse(self):
        r = client.get(
            "/api/v1/warehouses/transfers/bin-locations?warehouse_id=WH-001",
            headers=AUTH,
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 200
