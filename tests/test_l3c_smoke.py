"""
Smoke-Tests for L3-Connect gap-closure endpoints.
Validates that every new router is reachable and returns a valid HTTP status.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Helper ───────────────────────────────────────────────────────

def _ok(resp, expected_status: int = 200):
    """Assert response status and that body is valid JSON."""
    assert resp.status_code == expected_status, (
        f"Expected {expected_status}, got {resp.status_code}: {resp.text[:200]}"
    )
    return resp.json()


# ── Inventory Counts ─────────────────────────────────────────────

class TestInventoryCounts:
    def test_list(self):
        data = _ok(client.get("/api/v1/inventory/counts/"))
        assert "items" in data
        assert "total" in data

    def test_get_lines(self):
        resp = client.get("/api/v1/inventory/counts/nonexistent/lines")
        assert resp.status_code == 200
        assert resp.json() == []


# ── Weighing Tickets ─────────────────────────────────────────────

class TestWeighingTickets:
    def test_list(self):
        data = _ok(client.get("/api/v1/weighing-tickets/"))
        assert "items" in data

    def test_create(self):
        data = _ok(
            client.post("/api/v1/weighing-tickets/", json={
                "ticket_number": "WT-SMOKE-001",
                "direction": "in",
            }),
            expected_status=201,
        )
        assert data["ticket_number"] == "WT-SMOKE-001"


# ── Warehouse Transfers ──────────────────────────────────────────

class TestWarehouseTransfers:
    def test_list(self):
        data = _ok(client.get("/api/v1/warehouses/transfers/"))
        assert "items" in data

    def test_corrections_list(self):
        data = _ok(client.get("/api/v1/warehouses/transfers/corrections"))
        assert "items" in data

    def test_bin_locations(self):
        resp = client.get("/api/v1/warehouses/transfers/bin-locations")
        assert resp.status_code == 200


# ── Preparation Lists ───────────────────────────────────────────

class TestPreparationLists:
    def test_list(self):
        data = _ok(client.get("/api/v1/preparation-lists/"))
        assert "items" in data


# ── Pick Lists ───────────────────────────────────────────────────

class TestPickLists:
    def test_list(self):
        data = _ok(client.get("/api/v1/pick-lists/"))
        assert "items" in data


# ── GS1 Parser ──────────────────────────────────────────────────

class TestGS1Parser:
    def test_parse_simple(self):
        data = _ok(
            client.post("/api/v1/gs1/parse", json={
                "barcode": "0104012345678901101234561712312110ABC123",
            })
        )
        assert "elements" in data
        assert data["raw"] != ""

    def test_parse_empty(self):
        data = _ok(
            client.post("/api/v1/gs1/parse", json={"barcode": ""})
        )
        assert data["elements"] == {}


# ── NVE / SSCC ───────────────────────────────────────────────────

class TestNVE:
    def test_list(self):
        data = _ok(client.get("/api/v1/nve/"))
        assert "items" in data


# ── Webhooks ─────────────────────────────────────────────────────

class TestWebhooks:
    def test_list(self):
        data = _ok(client.get("/api/v1/webhooks/"))
        assert "items" in data

    def test_areas(self):
        data = _ok(client.get("/api/v1/webhooks/areas"))
        assert len(data) > 0
        assert data[0]["name"] != ""


# ── Article Extensions ───────────────────────────────────────────

class TestArticleExtensions:
    def test_batches(self):
        data = _ok(client.get("/api/v1/articles/batches"))
        assert "items" in data

    def test_selections(self):
        resp = client.get("/api/v1/articles/selections")
        assert resp.status_code == 200


# ── Customer Extensions ──────────────────────────────────────────

class TestCustomerExtensions:
    def test_geo_search(self):
        data = _ok(
            client.post("/api/v1/crm/customers/geo-search", json={
                "latitude": 51.0,
                "longitude": 9.0,
                "radius_km": 100,
            })
        )
        assert isinstance(data, list)


# ── Messages ─────────────────────────────────────────────────────

class TestMessages:
    def test_list(self):
        data = _ok(client.get("/api/v1/messages/"))
        assert "items" in data

    def test_health(self):
        data = _ok(client.get("/api/v1/messages/health"))
        assert data["status"] == "ok"


# ── DMS Images ───────────────────────────────────────────────────

class TestDMSImages:
    def test_documents(self):
        resp = client.get("/api/v1/dms/documents")
        assert resp.status_code == 200

    def test_images(self):
        resp = client.get("/api/v1/dms/images")
        assert resp.status_code == 200


# ── Master Data ──────────────────────────────────────────────────

class TestMasterData:
    def test_list(self):
        data = _ok(client.get("/api/v1/master-data/"))
        assert "items" in data

    def test_branches(self):
        resp = client.get("/api/v1/master-data/branches")
        assert resp.status_code == 200

    def test_countries(self):
        resp = client.get("/api/v1/master-data/countries")
        assert resp.status_code == 200

    def test_dispatchers(self):
        resp = client.get("/api/v1/master-data/dispatchers")
        assert resp.status_code == 200

    def test_units(self):
        resp = client.get("/api/v1/master-data/units")
        assert resp.status_code == 200


# ── OData Adapter (unit test) ────────────────────────────────────

class TestODataAdapter:
    def test_import(self):
        """Verify the OData adapter module imports without side effects."""
        from app.middleware.odata_adapter import apply_odata
        assert callable(apply_odata)


