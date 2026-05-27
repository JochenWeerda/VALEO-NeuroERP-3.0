"""
Tests für Slice-009: DSGVO Art. 33 Datenpannen-Meldeprozess.

Verifiziert:
- CRUD-Roundtrip (create, list, get, update)
- Pflichtfelder Art. 33 Abs. 3 a-d
- 72h-Deadline-Berechnung und Ampelfarben
- Notify-Endpoint (Status → GEMELDET, Doppelmeldung → 409)
- Status-Filter
- Validierung ungültiger breach_type / status
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import gdpr_art33_breach
from app.api.v1.endpoints.gdpr_art33_breach import _store

TENANT = "tenant-art33-test"
TEST_HEADERS = {"X-Tenant-ID": TENANT}

SAMPLE_BREACH = {
    "breach_type": "VERTRAULICHKEIT",
    "description": "Unbefugter Zugriff auf Kundendatenbank durch externen Angreifer",
    "data_categories": ["Name", "E-Mail", "Bankverbindung"],
    "persons_count_approx": 500,
    "records_count_approx": 1500,
    "dpo_name": "Max Mustermann",
    "dpo_contact": "dsb@test.de",
    "likely_consequences": "Identitätsdiebstahl, finanzielle Schäden für Betroffene",
    "measures_taken": "Zugangsdaten zurückgesetzt, Sicherheitslücke geschlossen, Forensik beauftragt",
    "status": "ENTDECKT",
    "internal_reference": "INC-2026-001",
}


@pytest.fixture(autouse=True)
def clear_store():
    prefix = f"{TENANT}::"
    for k in [k for k in _store if k.startswith(prefix)]:
        del _store[k]
    yield
    for k in [k for k in _store if k.startswith(prefix)]:
        del _store[k]


@pytest.fixture
def client():
    app = FastAPI()
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("no db")

    from app.core.database import get_db
    from app.core.tenant import get_tenant_id

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_tenant_id] = lambda: TENANT
    app.include_router(gdpr_art33_breach.router)
    return TestClient(app)


class TestCreateBreach:
    def test_create_returns_201_with_id(self, client):
        r = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["breach_type"] == "VERTRAULICHKEIT"

    def test_create_stores_all_art33_pflichtfelder(self, client):
        r = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        body = r.json()
        for field in ("description", "data_categories", "persons_count_approx",
                      "dpo_contact", "likely_consequences", "measures_taken"):
            assert field in body, f"Pflichtfeld {field} fehlt"

    def test_create_invalid_breach_type(self, client):
        bad = {**SAMPLE_BREACH, "breach_type": "UNBEKANNT"}
        r = client.post("/gdpr/art33/breaches", json=bad, headers=TEST_HEADERS)
        assert r.status_code == 400

    def test_create_invalid_status(self, client):
        bad = {**SAMPLE_BREACH, "status": "INVALID"}
        r = client.post("/gdpr/art33/breaches", json=bad, headers=TEST_HEADERS)
        assert r.status_code == 400

    def test_create_sets_default_status_entdeckt(self, client):
        payload = {k: v for k, v in SAMPLE_BREACH.items() if k != "status"}
        r = client.post("/gdpr/art33/breaches", json=payload, headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["status"] == "ENTDECKT"

    def test_create_notified_fields_null_on_creation(self, client):
        r = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        body = r.json()
        assert body["notified_at"] is None
        assert body["notified_by"] is None


class TestListBreaches:
    def test_list_empty(self, client):
        r = client.get("/gdpr/art33/breaches", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created(self, client):
        client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        r = client.get("/gdpr/art33/breaches", headers=TEST_HEADERS)
        assert len(r.json()) == 1

    def test_list_status_filter(self, client):
        client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        in_bearbeitung = {**SAMPLE_BREACH, "status": "IN_BEARBEITUNG"}
        client.post("/gdpr/art33/breaches", json=in_bearbeitung, headers=TEST_HEADERS)
        r = client.get("/gdpr/art33/breaches?status=ENTDECKT", headers=TEST_HEADERS)
        items = r.json()
        assert all(i["status"] == "ENTDECKT" for i in items)

    def test_list_multiple(self, client):
        for i in range(3):
            client.post("/gdpr/art33/breaches", json={**SAMPLE_BREACH, "description": f"Breach {i}"}, headers=TEST_HEADERS)
        r = client.get("/gdpr/art33/breaches", headers=TEST_HEADERS)
        assert len(r.json()) == 3


class TestGetBreach:
    def test_get_returns_breach(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art33/breaches/{created['id']}", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_404(self, client):
        r = client.get("/gdpr/art33/breaches/ghost", headers=TEST_HEADERS)
        assert r.status_code == 404


class TestUpdateBreach:
    def test_update_changes_measures(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        updated = {**SAMPLE_BREACH, "measures_taken": "Systemabschaltung, Strafanzeige erstattet"}
        r = client.put(f"/gdpr/art33/breaches/{created['id']}", json=updated, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert "Strafanzeige" in r.json()["measures_taken"]

    def test_update_404(self, client):
        r = client.put("/gdpr/art33/breaches/ghost", json=SAMPLE_BREACH, headers=TEST_HEADERS)
        assert r.status_code == 404


class TestDeadline:
    def test_deadline_fresh_breach_has_full_hours(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art33/breaches/{created['id']}/deadline", headers=TEST_HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert body["hours_remaining"] > 71  # frisch erstellt → nahe 72h
        assert body["is_overdue"] is False

    def test_deadline_old_breach_is_overdue(self, client):
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=80)).isoformat()
        payload = {**SAMPLE_BREACH, "discovered_at": old_ts}
        created = client.post("/gdpr/art33/breaches", json=payload, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art33/breaches/{created['id']}/deadline", headers=TEST_HEADERS)
        body = r.json()
        assert body["is_overdue"] is True
        assert body["hours_remaining"] == 0.0
        assert body["traffic_light"] == "RED"

    def test_deadline_within_24h_is_red(self, client):
        ts = (datetime.now(timezone.utc) - timedelta(hours=50)).isoformat()
        payload = {**SAMPLE_BREACH, "discovered_at": ts}
        created = client.post("/gdpr/art33/breaches", json=payload, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art33/breaches/{created['id']}/deadline", headers=TEST_HEADERS)
        body = r.json()
        assert body["traffic_light"] == "RED"
        assert body["hours_remaining"] < 24

    def test_deadline_fresh_is_orange(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art33/breaches/{created['id']}/deadline", headers=TEST_HEADERS)
        assert r.json()["traffic_light"] == "ORANGE"

    def test_deadline_notified_is_green(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        client.post(
            f"/gdpr/art33/breaches/{created['id']}/notify",
            json={"notified_by": "Max Mustermann", "authority_reference": "BayLDA-2026-001"},
            headers=TEST_HEADERS,
        )
        r = client.get(f"/gdpr/art33/breaches/{created['id']}/deadline", headers=TEST_HEADERS)
        assert r.json()["traffic_light"] == "GREEN"
        assert r.json()["is_notified"] is True

    def test_deadline_404(self, client):
        r = client.get("/gdpr/art33/breaches/ghost/deadline", headers=TEST_HEADERS)
        assert r.status_code == 404


class TestNotify:
    def test_notify_sets_status_gemeldet(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        r = client.post(
            f"/gdpr/art33/breaches/{created['id']}/notify",
            json={"notified_by": "Hans Müller"},
            headers=TEST_HEADERS,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "GEMELDET"
        assert body["notified_by"] == "Hans Müller"
        assert body["notified_at"] is not None

    def test_notify_duplicate_returns_409(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        client.post(
            f"/gdpr/art33/breaches/{created['id']}/notify",
            json={"notified_by": "Erster"},
            headers=TEST_HEADERS,
        )
        r2 = client.post(
            f"/gdpr/art33/breaches/{created['id']}/notify",
            json={"notified_by": "Zweiter"},
            headers=TEST_HEADERS,
        )
        assert r2.status_code == 409

    def test_notify_404(self, client):
        r = client.post(
            "/gdpr/art33/breaches/ghost/notify",
            json={"notified_by": "X"},
            headers=TEST_HEADERS,
        )
        assert r.status_code == 404

    def test_notify_stores_authority_reference(self, client):
        created = client.post("/gdpr/art33/breaches", json=SAMPLE_BREACH, headers=TEST_HEADERS).json()
        r = client.post(
            f"/gdpr/art33/breaches/{created['id']}/notify",
            json={"notified_by": "Müller", "authority_reference": "BayLDA-9999"},
            headers=TEST_HEADERS,
        )
        assert r.json()["authority_reference"] == "BayLDA-9999"
