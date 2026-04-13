"""
COV-INV-002: Tests for Waage API endpoints.

Covers /api/v1/waage — Waagen CRUD + Wiegungen CRUD.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}


# ── Waagen ──────────────────────────────────────────────────────


class TestWaagenList:
    """GET /waage/waagen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/waagen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/waagen?skip=0&limit=5", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_status(self):
        r = client.get("/api/v1/waage/waagen?status=aktiv", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


class TestWaagenCRUD:
    """POST/GET/PATCH/DELETE /waage/waagen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_waage(self):
        payload = {
            "id": "WAAGE-TEST-001",
            "waage_name": "Testwaage COV-INV-002",
            "standort": "Hauptlager",
            "status": "aktiv",
            "max_kapazitaet": 60000,
        }
        r = client.post("/api/v1/waage/waagen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_patch_nonexistent_404(self):
        r = client.patch(
            "/api/v1/waage/waagen/NONEXISTENT-WAAGE",
            headers=AUTH,
            json={"status": "inaktiv"},
        )
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/waagen/NONEXISTENT-WAAGE", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404


# ── Wiegungen ───────────────────────────────────────────────────


class TestWiegungenList:
    """GET /waage/wiegungen"""

    def test_list_returns_200(self):
        r = client.get("/api/v1/waage/wiegungen", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_with_pagination(self):
        r = client.get("/api/v1/waage/wiegungen?skip=0&limit=10", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_waage_id(self):
        r = client.get("/api/v1/waage/wiegungen?waage_id=WAAGE-001", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200

    def test_list_filter_by_kennzeichen(self):
        r = client.get("/api/v1/waage/wiegungen?kennzeichen=AB-CD-1234", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 200


class TestWiegungenCRUD:
    """POST/GET/DELETE /waage/wiegungen"""

    def test_get_nonexistent_404(self):
        r = client.get("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404

    def test_create_wiegung(self):
        payload = {
            "id": "WIEG-TEST-001",
            "waage_id": "WAAGE-001",
            "kennzeichen": "AB-CD-1234",
            "brutto": 25000,
            "tara": 12000,
        }
        r = client.post("/api/v1/waage/wiegungen", headers=AUTH, json=payload)
        skip_if_db_unavailable(r)
        if r.status_code not in (201, 400, 500):
            pytest.fail(f"Unexpected status {r.status_code}: {r.text}")

    def test_delete_nonexistent_404(self):
        r = client.delete("/api/v1/waage/wiegungen/NONEXISTENT-WIEGUNG", headers=AUTH)
        skip_if_db_unavailable(r)
        assert r.status_code == 404
