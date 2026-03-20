from __future__ import annotations

from datetime import date, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import reklamation_api


@pytest.fixture(autouse=True)
def _clear_store():
    reklamation_api._store.clear()
    yield
    reklamation_api._store.clear()


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(reklamation_api.router)
    return TestClient(app, raise_server_exceptions=True)


def test_create_reklamation_surfaces_crm_dms_and_sla_state(client: TestClient):
    payload = {
        "tenant_id": "TENANT-REK-1",
        "lieferant_id": "LF-100",
        "typ": "qualitaet",
        "positionen": [
            {
                "artikel_id": "ART-001",
                "beanstandete_menge": 50.0,
                "anerkannte_menge": 0.0,
                "beanstandeter_wert_eur": 250.0,
                "begruendung": "Feuchte zu hoch",
            }
        ],
        "zustaendiger": "Anna Beispiel",
        "frist_datum": (date.today() + timedelta(days=10)).isoformat(),
        "kontrakt_id": "K-4711",
        "crm_referenz": {
            "crm_system": "Salesforce",
            "crm_case_id": "CRM-CASE-1001",
            "crm_ticket_id": "CRM-TICKET-55",
            "crm_status": "open",
            "crm_url": "https://crm.example/cases/CRM-CASE-1001",
        },
        "dms_referenzen": [
            {
                "dokument_id": "DMS-REK-1001",
                "dokument_typ": "reklamation",
                "dateiname": "reklamation.pdf",
                "checksum": "sha256:abc123",
                "source_uri": "dms://documents/DMS-REK-1001",
            }
        ],
        "aktor_id": "crm-user",
    }

    response = client.post("/reklamationen", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["hat_crm_bezug"] is True
    assert body["hat_dms_bezug"] is True
    assert body["crm_referenz"]["crm_case_id"] == "CRM-CASE-1001"
    assert body["dms_referenzen"][0]["dokument_id"] == "DMS-REK-1001"
    assert body["sla_status"] == "in_frist"
    assert body["audit_eintrag_anzahl"] >= 2
    assert body["audit_integritaet_ok"] is True


def test_reklamation_transition_records_audit_and_overdue_state(client: TestClient):
    create = client.post(
        "/reklamationen",
        json={
            "tenant_id": "TENANT-REK-2",
            "lieferant_id": "LF-200",
            "typ": "menge",
            "positionen": [
                {
                    "artikel_id": "ART-002",
                    "beanstandete_menge": 100.0,
                    "anerkannte_menge": 0.0,
                    "beanstandeter_wert_eur": 500.0,
                    "begruendung": "Fehlmenge",
                }
            ],
            "zustaendiger": "Max Muster",
            "frist_datum": (date.today() - timedelta(days=1)).isoformat(),
            "aktor_id": "service-user",
        },
    )
    reklamation_id = create.json()["reklamation_id"]

    overdue = client.get("/reklamationen/ueberfaellige/TENANT-REK-2")
    assert overdue.status_code == 200
    assert any(item["reklamation_id"] == reklamation_id for item in overdue.json())

    transition_1 = client.post(
        f"/reklamationen/{reklamation_id}/transition",
        params={"neuer_status": "abgelehnt", "aktor_id": "reviewer-1", "kommentar": "Teilweise unklar"},
    )
    assert transition_1.status_code == 200
    assert transition_1.json()["status"] == "abgelehnt"

    transition_2 = client.post(
        f"/reklamationen/{reklamation_id}/transition",
        params={"neuer_status": "geschlossen", "aktor_id": "reviewer-2"},
    )
    assert transition_2.status_code == 200
    assert transition_2.json()["status"] == "geschlossen"
    assert transition_2.json()["sla_status"] == "erledigt"
    assert transition_2.json()["ist_ueberfaellig"] is False

    audit = client.get(f"/reklamationen/{reklamation_id}/audit")
    assert audit.status_code == 200
    audit_body = audit.json()
    assert audit_body["count"] == 3
    assert audit_body["audit_integritaet_ok"] is True
    assert audit_body["audit_trail"][-1]["aktion"] == "status_geaendert"


def test_crm_and_dms_reference_endpoints_update_existing_complaint(client: TestClient):
    create = client.post(
        "/reklamationen",
        json={
            "tenant_id": "TENANT-REK-3",
            "lieferant_id": "LF-300",
            "typ": "preis",
            "positionen": [
                {
                    "artikel_id": "ART-003",
                    "beanstandete_menge": 25.0,
                    "anerkannte_menge": 0.0,
                    "beanstandeter_wert_eur": 125.0,
                    "begruendung": "Falscher Preis",
                }
            ],
            "zustaendiger": "Klara Rolle",
            "frist_datum": (date.today() + timedelta(days=5)).isoformat(),
        },
    )
    reklamation_id = create.json()["reklamation_id"]

    crm_update = client.post(
        f"/reklamationen/{reklamation_id}/crm-reference",
        json={
            "aktor_id": "crm-sync",
            "crm_referenz": {
                "crm_system": "Salesforce",
                "crm_case_id": "CRM-CASE-2002",
                "crm_status": "in_progress",
                "crm_url": "https://crm.example/cases/CRM-CASE-2002",
            },
        },
    )
    assert crm_update.status_code == 200
    assert crm_update.json()["crm_referenz"]["crm_case_id"] == "CRM-CASE-2002"

    dms_update = client.post(
        f"/reklamationen/{reklamation_id}/dms-referenzen",
        json={
            "aktor_id": "dms-sync",
            "dms_referenzen": [
                {
                    "dokument_id": "DMS-REK-2002",
                    "dokument_typ": "support_ticket",
                    "dateiname": "ticket.pdf",
                    "source_uri": "dms://documents/DMS-REK-2002",
                }
            ],
        },
    )
    assert dms_update.status_code == 200
    assert dms_update.json()["gobd_beleg_id"] == "DMS-REK-2002"
    assert dms_update.json()["audit_eintrag_anzahl"] >= 3

    crm_lookup = client.get("/reklamationen/crm/CRM-CASE-2002")
    assert crm_lookup.status_code == 200
    assert len(crm_lookup.json()) == 1
    assert crm_lookup.json()[0]["reklamation_id"] == reklamation_id
