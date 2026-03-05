"""
Regressionstests für Einkauf-Bestellungen-API (E4: Bestellung(en) importieren im Lieferschein).
- GET /api/v1/einkauf/bestellungen (optional lieferant_id)
- GET /api/v1/einkauf/bestellungen/{id} (Bestellung mit Positionen)
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}
TENANT_HEADER = {"X-Tenant-ID": "default"}


@pytest.mark.integration
class TestEinkaufBestellungenAPI:
    """E4: Bestellungen-API für Lieferschein-Import."""

    def test_list_bestellungen_returns_200_and_list(self):
        r = client.get(
            "/api/v1/einkauf/bestellungen",
            params={"limit": 10},
            headers={**AUTH_HEADERS, **TENANT_HEADER},
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_list_bestellungen_with_lieferant_id_returns_200(self):
        r = client.get(
            "/api/v1/einkauf/bestellungen",
            params={"lieferant_id": "00000000-0000-0000-0000-000000000001"},
            headers={**AUTH_HEADERS, **TENANT_HEADER},
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_bestellung_returns_404_for_unknown_id(self):
        r = client.get(
            "/api/v1/einkauf/bestellungen/00000000-0000-0000-0000-000000000099",
            headers={**AUTH_HEADERS, **TENANT_HEADER},
        )
        assert r.status_code == 404

    def test_get_bestellung_returns_object_with_positionen_when_found(self):
        list_r = client.get(
            "/api/v1/einkauf/bestellungen",
            params={"limit": 1},
            headers={**AUTH_HEADERS, **TENANT_HEADER},
        )
        if list_r.status_code != 200 or not list_r.json():
            pytest.skip("Keine Bestellungen in DB")
        first_id = list_r.json()[0]["id"]
        r = client.get(
            f"/api/v1/einkauf/bestellungen/{first_id}",
            headers={**AUTH_HEADERS, **TENANT_HEADER},
        )
        assert r.status_code == 200
        data = r.json()
        assert "id" in data
        assert "bestellnummer" in data
        assert "positionen" in data
        assert isinstance(data["positionen"], list)
