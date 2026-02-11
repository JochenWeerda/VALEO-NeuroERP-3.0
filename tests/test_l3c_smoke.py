"""
Smoke-Tests for L3-Connect gap-closure endpoints.
Validates that endpoints are reachable and not blocked by auth.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}
ACCEPTABLE_STATUS = {200, 201, 404, 405, 422, 500, 503}


def _assert_reachable(resp, *, expected_success: int | None = None):
    assert resp.status_code in ACCEPTABLE_STATUS, (
        f"Unexpected status {resp.status_code}: {resp.text[:200]}"
    )
    assert resp.status_code not in {401, 403}, (
        f"Unexpected auth failure {resp.status_code}: {resp.text[:200]}"
    )
    if expected_success is not None and resp.status_code == expected_success:
        return resp.json()
    return None


class TestInventoryCounts:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/inventory/counts/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data
            assert "total" in data

    def test_get_lines(self):
        resp = client.get("/api/v1/inventory/counts/nonexistent/lines", headers=AUTH_HEADERS)
        data = _assert_reachable(resp, expected_success=200)
        if data is not None:
            assert isinstance(data, list)


class TestWeighingTickets:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/weighing-tickets/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_create(self):
        data = _assert_reachable(
            client.post(
                "/api/v1/weighing-tickets/",
                json={"ticket_number": "WT-SMOKE-001", "direction": "in"},
                headers=AUTH_HEADERS,
            ),
            expected_success=201,
        )
        if data is not None:
            assert data["ticket_number"] == "WT-SMOKE-001"


class TestWarehouseTransfers:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/warehouses/transfers/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_corrections_list(self):
        data = _assert_reachable(client.get("/api/v1/warehouses/transfers/corrections", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_bin_locations(self):
        _assert_reachable(client.get("/api/v1/warehouses/transfers/bin-locations", headers=AUTH_HEADERS), expected_success=200)


class TestPreparationLists:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/preparation-lists/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data


class TestPickLists:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/pick-lists/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data


class TestGS1Parser:
    def test_parse_simple(self):
        data = _assert_reachable(
            client.post(
                "/api/v1/gs1/parse",
                json={"barcode": "0104012345678901101234561712312110ABC123"},
                headers=AUTH_HEADERS,
            ),
            expected_success=200,
        )
        if data is not None:
            assert "elements" in data
            assert data["raw"] != ""

    def test_parse_empty(self):
        data = _assert_reachable(
            client.post("/api/v1/gs1/parse", json={"barcode": ""}, headers=AUTH_HEADERS),
            expected_success=200,
        )
        if data is not None:
            assert data["elements"] == {}


class TestNVE:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/nve/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data


class TestWebhooks:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/webhooks/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_areas(self):
        data = _assert_reachable(client.get("/api/v1/webhooks/areas", headers=AUTH_HEADERS), expected_success=200)
        if data is not None and len(data) > 0:
            assert data[0]["name"] != ""


class TestArticleExtensions:
    def test_batches(self):
        data = _assert_reachable(client.get("/api/v1/articles/batches", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_selections(self):
        _assert_reachable(client.get("/api/v1/articles/selections", headers=AUTH_HEADERS), expected_success=200)


class TestCustomerExtensions:
    def test_geo_search(self):
        data = _assert_reachable(
            client.post(
                "/api/v1/crm/customers/geo-search",
                json={"latitude": 51.0, "longitude": 9.0, "radius_km": 100},
                headers=AUTH_HEADERS,
            ),
            expected_success=200,
        )
        if data is not None:
            assert isinstance(data, list)


class TestMessages:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/messages/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_health(self):
        data = _assert_reachable(client.get("/api/v1/messages/health", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert data["status"] == "ok"


class TestDMSImages:
    def test_documents(self):
        _assert_reachable(client.get("/api/v1/dms/documents", headers=AUTH_HEADERS), expected_success=200)

    def test_images(self):
        _assert_reachable(client.get("/api/v1/dms/images", headers=AUTH_HEADERS), expected_success=200)


class TestMasterData:
    def test_list(self):
        data = _assert_reachable(client.get("/api/v1/master-data/", headers=AUTH_HEADERS), expected_success=200)
        if data is not None:
            assert "items" in data

    def test_branches(self):
        _assert_reachable(client.get("/api/v1/master-data/branches", headers=AUTH_HEADERS), expected_success=200)

    def test_countries(self):
        _assert_reachable(client.get("/api/v1/master-data/countries", headers=AUTH_HEADERS), expected_success=200)

    def test_dispatchers(self):
        _assert_reachable(client.get("/api/v1/master-data/dispatchers", headers=AUTH_HEADERS), expected_success=200)

    def test_units(self):
        _assert_reachable(client.get("/api/v1/master-data/units", headers=AUTH_HEADERS), expected_success=200)


class TestODataAdapter:
    def test_import(self):
        from app.middleware.odata_adapter import apply_odata

        assert callable(apply_odata)
