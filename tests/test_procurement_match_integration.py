"""Real procurement matching; isolated provider transport and rollback-only data."""

from __future__ import annotations

from uuid import uuid4
from procurement_identity_fixture import keys, probe, procurement_context, seed_match_cases

import pytest
from fastapi.testclient import TestClient

from main import app

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

PO_OK = ''
PO_OVER = ''
AUTH_HEADERS = {}

client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


@pytest.fixture(autouse=True)
def _procurement_match_fixture(procurement_context, monkeypatch):
    first, second = seed_match_cases(procurement_context, monkeypatch)
    monkeypatch.setitem(globals(), 'PO_OK', first)
    monkeypatch.setitem(globals(), 'PO_OVER', second)
    monkeypatch.setitem(globals(), 'AUTH_HEADERS', procurement_context.headers)


class TestProcurementMatchIntegration:
    def test_three_way_demo_po_001_abgeglichen(self):
        r = client.get(
            "/api/v1/procurement/match/three-way",
            params={"bestellung": PO_OK},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["found"] is True
        assert data["summary"]["drei_wege_abgeglichen"] is True
        assert data["three_way"]["geliefert_wert"] == 27700.0
        assert data["three_way"]["fakturiert_netto"] == 27700.0

    def test_three_way_demo_po_002_ers_preview_960(self):
        r = client.get(
            "/api/v1/procurement/match/three-way",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["found"] is True
        assert data["summary"]["hat_abweichung"] is True
        preview = data["ers_preview"]
        assert preview["berechtigt"] is True
        assert preview["betrag_netto"] == 960.0

    def test_follow_up_append_only_and_eskalation_stufe(self):
        r1 = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "eskalation",
                "grund": "IT-Eskalation Stufe 1",
            },
            headers=AUTH_HEADERS,
        )
        assert r1.status_code == 201
        assert r1.json()["eskalationsstufe"] == 1

        r2 = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "eskalation",
                "grund": "IT-Eskalation Stufe 2",
            },
            headers=AUTH_HEADERS,
        )
        assert r2.status_code == 201
        assert r2.json()["eskalationsstufe"] == 2
        assert r2.json()["id"] != r1.json()["id"]
        assert r2.json()["grund"] == "IT-Eskalation Stufe 2"
        # PostgreSQL NOW() is constant in the outer transaction: reproduce the tie.
        assert r2.json()["created_at"] == r1.json()["created_at"]

        listed = client.get(
            "/api/v1/procurement/match/follow-up",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert listed.status_code == 200
        items = listed.json()["items"]
        assert len(items) == 2
        assert items[0]["id"] == r2.json()["id"]
        assert items[1]["id"] == r1.json()["id"]
        assert items[0]["eskalationsstufe"] >= items[1]["eskalationsstufe"]

    def test_ers_credit_create_and_list(self):
        preview = client.get(
            "/api/v1/procurement/match/ers/preview",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert preview.status_code == 200
        assert preview.json()["ers_preview"]["betrag_netto"] == 960.0

        created = client.post(
            "/api/v1/procurement/match/ers",
            json={"bestellnummer": PO_OVER, "grund": "IT-ERS Überlieferung"},
            headers=AUTH_HEADERS,
        )
        assert created.status_code == 201
        body = created.json()
        assert body["betrag_netto"] == 960.0
        assert body["status"] == "entwurf"
        assert body["gutschrift_nummer"].startswith(f"ERS-{PO_OVER}-")

        listed = client.get(
            "/api/v1/procurement/match/ers",
            params={"bestellung": PO_OVER},
            headers=AUTH_HEADERS,
        )
        assert listed.status_code == 200
        assert any(x["id"] == body["id"] for x in listed.json()["items"])

    def test_follow_up_invalid_action_422(self):
        r = client.post(
            "/api/v1/procurement/match/follow-up",
            json={
                "bestellnummer": PO_OVER,
                "action_type": "storno",
                "grund": "IT-invalid",
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 422

    def test_ers_not_eligible_422(self):
        r = client.post(
            "/api/v1/procurement/match/ers",
            json={"bestellnummer": PO_OK, "grund": "IT-sollte scheitern"},
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 422


@pytest.mark.parametrize('credential', [None, 'dev-token'])
def test_match_rejects_missing_or_legacy_identity(credential):
    headers = {'X-Tenant-ID': AUTH_HEADERS['X-Tenant-ID']}
    if credential:
        headers['Authorization'] = 'Bearer '+credential
    response = client.get('/api/v1/procurement/match/three-way', params={'bestellung': PO_OK}, headers=headers)
    assert response.status_code == 401


def test_match_rejects_foreign_tenant_selector():
    response = client.get('/api/v1/procurement/match/three-way', params={'bestellung': PO_OK},
                          headers={**AUTH_HEADERS, 'X-Tenant-ID': str(uuid4())})
    assert response.status_code == 403
