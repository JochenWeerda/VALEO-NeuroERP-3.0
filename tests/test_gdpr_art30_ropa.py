"""
Tests für Slice-008: DSGVO Art. 30 Verarbeitungsverzeichnis (RoPA).

Verifiziert:
- CRUD-Roundtrip (create, list, get, update, delete)
- Pflichtfelder nach Art. 30 Abs. 1 a-h
- JSON-Export-Endpoint
- 404 auf unbekannte ID
- Status-Filter
"""
from __future__ import annotations

import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.api.v1.endpoints import gdpr_art30_ropa
from app.api.v1.endpoints.gdpr_art30_ropa import _store


TENANT = "tenant-art30-test"
TEST_HEADERS = {"X-Tenant-ID": TENANT}

SAMPLE_ACTIVITY = {
    "controller_name": "VALEO Agrar Handel GmbH",
    "controller_contact": "datenschutz@valeo-agrar.de",
    "purpose": "Kundenstammdatenverwaltung für Auftragsabwicklung (Art. 6 Abs. 1 lit. b)",
    "subject_categories": ["Kunden", "Interessenten"],
    "data_categories": ["Name", "Adresse", "E-Mail", "Bankverbindung"],
    "recipients": ["Steuerberater", "Kreditinstitut"],
    "third_country_transfers": [],
    "retention_period": "10 Jahre nach Ende der Geschäftsbeziehung (§ 257 HGB)",
    "toms": "Verschlüsselung, Zugriffskontrolle, Backup-Konzept",
    "legal_basis": "Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)",
    "system_or_tool": "VALEO NeuroERP 3.0",
    "status": "AKTIV",
}


@pytest.fixture(autouse=True)
def clear_store():
    """Leert den In-Memory Store vor jedem Test."""
    prefix = f"{TENANT}::"
    keys_to_del = [k for k in _store if k.startswith(prefix)]
    for k in keys_to_del:
        del _store[k]
    yield
    keys_to_del = [k for k in _store if k.startswith(prefix)]
    for k in keys_to_del:
        del _store[k]


@pytest.fixture
def client():
    app = FastAPI()
    mock_db = MagicMock()
    mock_db.execute.side_effect = Exception("no db")

    def get_db_override():
        return mock_db

    def get_tenant_override():
        return TENANT

    from app.core.database import get_db
    from app.core.tenant import get_tenant_id
    app.dependency_overrides[get_db] = get_db_override
    app.dependency_overrides[get_tenant_id] = get_tenant_override
    app.include_router(gdpr_art30_ropa.router)
    return TestClient(app)


class TestCreateActivity:
    def test_create_returns_201_with_id(self, client):
        r = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        assert r.status_code == 201
        body = r.json()
        assert "id" in body
        assert body["controller_name"] == SAMPLE_ACTIVITY["controller_name"]
        assert body["status"] == "AKTIV"

    def test_create_stores_all_art30_pflichtfelder(self, client):
        r = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        assert r.status_code == 201
        body = r.json()
        for field in ("purpose", "subject_categories", "data_categories", "recipients",
                      "retention_period", "toms", "controller_name", "controller_contact"):
            assert field in body, f"Pflichtfeld {field} fehlt"

    def test_create_third_country_transfers_empty_list(self, client):
        r = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        assert r.json()["third_country_transfers"] == []

    def test_create_with_third_country(self, client):
        data = {**SAMPLE_ACTIVITY, "third_country_transfers": [{"country": "US", "guarantee": "SCCs"}]}
        r = client.post("/gdpr/art30/activities", json=data, headers=TEST_HEADERS)
        assert r.status_code == 201
        assert r.json()["third_country_transfers"] == [{"country": "US", "guarantee": "SCCs"}]


class TestListActivities:
    def test_list_empty(self, client):
        r = client.get("/gdpr/art30/activities", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json() == []

    def test_list_returns_created_activity(self, client):
        client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities", headers=TEST_HEADERS)
        assert len(r.json()) == 1

    def test_list_status_filter(self, client):
        client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        entwurf = {**SAMPLE_ACTIVITY, "status": "ENTWURF"}
        client.post("/gdpr/art30/activities", json=entwurf, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities?status=AKTIV", headers=TEST_HEADERS)
        items = r.json()
        assert all(i["status"] == "AKTIV" for i in items)

    def test_list_multiple_activities(self, client):
        for i in range(3):
            client.post("/gdpr/art30/activities", json={**SAMPLE_ACTIVITY, "purpose": f"Zweck {i}"}, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities", headers=TEST_HEADERS)
        assert len(r.json()) == 3


class TestGetActivity:
    def test_get_returns_activity(self, client):
        created = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS).json()
        r = client.get(f"/gdpr/art30/activities/{created['id']}", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_404_on_unknown_id(self, client):
        r = client.get("/gdpr/art30/activities/does-not-exist", headers=TEST_HEADERS)
        assert r.status_code == 404


class TestUpdateActivity:
    def test_update_changes_purpose(self, client):
        created = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS).json()
        updated = {**SAMPLE_ACTIVITY, "purpose": "Neuer Zweck: Marketinganalyse"}
        r = client.put(f"/gdpr/art30/activities/{created['id']}", json=updated, headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["purpose"] == "Neuer Zweck: Marketinganalyse"

    def test_update_404_on_unknown(self, client):
        r = client.put("/gdpr/art30/activities/ghost", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        assert r.status_code == 404

    def test_update_preserves_created_at(self, client):
        created = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS).json()
        updated_payload = {**SAMPLE_ACTIVITY, "status": "INAKTIV"}
        r = client.put(f"/gdpr/art30/activities/{created['id']}", json=updated_payload, headers=TEST_HEADERS)
        assert r.json()["created_at"] == created["created_at"]


class TestDeleteActivity:
    def test_delete_returns_204(self, client):
        created = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS).json()
        r = client.delete(f"/gdpr/art30/activities/{created['id']}", headers=TEST_HEADERS)
        assert r.status_code == 204

    def test_delete_removes_from_list(self, client):
        created = client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS).json()
        client.delete(f"/gdpr/art30/activities/{created['id']}", headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities", headers=TEST_HEADERS)
        assert r.json() == []

    def test_delete_404_on_unknown(self, client):
        r = client.delete("/gdpr/art30/activities/ghost", headers=TEST_HEADERS)
        assert r.status_code == 404


class TestExportJson:
    def test_export_returns_200_with_art30_key(self, client):
        client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities/export/json", headers=TEST_HEADERS)
        assert r.status_code == 200
        body = r.json()
        assert "art30_verarbeitungsverzeichnis" in body

    def test_export_contains_total_count(self, client):
        for _ in range(2):
            client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities/export/json", headers=TEST_HEADERS)
        assert r.json()["art30_verarbeitungsverzeichnis"]["total_activities"] == 2

    def test_export_contains_all_activities(self, client):
        client.post("/gdpr/art30/activities", json=SAMPLE_ACTIVITY, headers=TEST_HEADERS)
        r = client.get("/gdpr/art30/activities/export/json", headers=TEST_HEADERS)
        activities = r.json()["art30_verarbeitungsverzeichnis"]["activities"]
        assert len(activities) == 1
        assert activities[0]["purpose"] == SAMPLE_ACTIVITY["purpose"]

    def test_export_empty_verzeichnis(self, client):
        r = client.get("/gdpr/art30/activities/export/json", headers=TEST_HEADERS)
        assert r.status_code == 200
        assert r.json()["art30_verarbeitungsverzeichnis"]["total_activities"] == 0
