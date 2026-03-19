"""
Wave 73 — Gap 004: Settlement Freigabe-Flow + Gutschrift/Belastung
Zustandsmaschine: ENTWURF → ZUR_FREIGABE → FREIGEGEBEN → VERBUCHT
Human-Gate: KI-Agenten (AGENT) dürfen nie direkt auf VERBUCHT setzen.
Tests: stateless /freigabe/evaluate Endpoint.

Response-Struktur: audit_entry-Felder direkt im Body (gespreadet) +
    allowed_transitions + is_terminal.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agrar_settlements


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(agrar_settlements.router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Hilfsfunktion
# ---------------------------------------------------------------------------

def evaluate(client, current_status, target_status, actor_type="SACHBEARBEITER", actor_id="user1"):
    return client.post(
        "/freigabe/evaluate",
        json={
            "actor_id": actor_id,
            "actor_type": actor_type,
            "target_status": target_status,
            "current_status": current_status,
        },
    )


# ---------------------------------------------------------------------------
# Gültige Übergänge
# ---------------------------------------------------------------------------

def test_sachbearbeiter_kann_entwurf_zu_zur_freigabe(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE", "SACHBEARBEITER")
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is True
    assert body["new_status"] == "ZUR_FREIGABE"


def test_abteilungsleiter_kann_zur_freigabe_freigeben(client: TestClient):
    resp = evaluate(client, "ZUR_FREIGABE", "FREIGEGEBEN", "ABTEILUNGSLEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_prokurist_kann_zur_freigabe_freigeben(client: TestClient):
    resp = evaluate(client, "ZUR_FREIGABE", "FREIGEGEBEN", "PROKURIST")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_sachbearbeiter_kann_freigegeben_verbuchen(client: TestClient):
    resp = evaluate(client, "FREIGEGEBEN", "VERBUCHT", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_ablehnung_aus_zur_freigabe(client: TestClient):
    resp = evaluate(client, "ZUR_FREIGABE", "ABGELEHNT", "ABTEILUNGSLEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_abgelehnt_kann_zu_entwurf_zurueck(client: TestClient):
    resp = evaluate(client, "ABGELEHNT", "ENTWURF", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_rueckzug_zur_freigabe_zu_entwurf(client: TestClient):
    resp = evaluate(client, "ZUR_FREIGABE", "ENTWURF", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_system_darf_verbuchen(client: TestClient):
    resp = evaluate(client, "FREIGEGEBEN", "VERBUCHT", "SYSTEM")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


# ---------------------------------------------------------------------------
# Human-Gate / Rollenschranken: AGENT
# ---------------------------------------------------------------------------

def test_agent_darf_nicht_verbuchen(client: TestClient):
    """AGENT ist nicht in der required-actor-Menge für VERBUCHT."""
    resp = evaluate(client, "FREIGEGEBEN", "VERBUCHT", "AGENT")
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is False


def test_agent_darf_zur_freigabe_einreichen(client: TestClient):
    """Agent darf Entwurf zur Freigabe einreichen — aber nicht final verbuchen."""
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE", "AGENT")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


# ---------------------------------------------------------------------------
# Unzulässige Übergänge (Zustandsmaschine)
# ---------------------------------------------------------------------------

def test_entwurf_kann_nicht_direkt_freigegeben_werden(client: TestClient):
    resp = evaluate(client, "ENTWURF", "FREIGEGEBEN", "ABTEILUNGSLEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


def test_entwurf_kann_nicht_verbucht_werden(client: TestClient):
    resp = evaluate(client, "ENTWURF", "VERBUCHT", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


def test_verbucht_ist_terminal(client: TestClient):
    """Kein Übergang aus VERBUCHT möglich."""
    for target in ["ENTWURF", "ZUR_FREIGABE", "FREIGEGEBEN", "ABGELEHNT"]:
        resp = evaluate(client, "VERBUCHT", target, "PROKURIST")
        assert resp.status_code == 200
        assert resp.json()["allowed"] is False, f"VERBUCHT → {target} sollte verboten sein"


def test_sachbearbeiter_darf_nicht_direkt_freigeben(client: TestClient):
    """Nur ABTEILUNGSLEITER/PROKURIST/SYSTEM dürfen FREIGEGEBEN setzen."""
    resp = evaluate(client, "ZUR_FREIGABE", "FREIGEGEBEN", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


# ---------------------------------------------------------------------------
# Response-Struktur: audit_entry-Felder sind direkt im Body
# ---------------------------------------------------------------------------

def test_response_contains_actor_id(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE", "SACHBEARBEITER", actor_id="user-007")
    body = resp.json()
    assert body["actor_id"] == "user-007"


def test_response_contains_actor_type(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE", "SACHBEARBEITER")
    assert resp.json()["actor_type"] == "SACHBEARBEITER"


def test_response_contains_previous_status(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE")
    assert resp.json()["previous_status"] == "ENTWURF"


def test_response_contains_timestamp(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE")
    assert "decided_at" in resp.json()
    assert len(resp.json()["decided_at"]) > 10  # ISO-Timestamp


def test_response_contains_event_name(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE")
    body = resp.json()
    assert "event" in body
    assert "zur_freigabe" in body["event"].lower() or "ZUR_FREIGABE" in body["event"]


def test_response_contains_allowed_transitions(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE")
    body = resp.json()
    assert "allowed_transitions" in body
    assert isinstance(body["allowed_transitions"], list)


def test_response_is_terminal_false_for_entwurf(client: TestClient):
    resp = evaluate(client, "ENTWURF", "ZUR_FREIGABE")
    assert resp.json()["is_terminal"] is False


# ---------------------------------------------------------------------------
# Validierungsfehler: ungültige Enum-Werte
# ---------------------------------------------------------------------------

def test_unknown_actor_type_returns_422(client: TestClient):
    resp = client.post(
        "/freigabe/evaluate",
        json={"actor_id": "u1", "actor_type": "CHEF", "target_status": "ZUR_FREIGABE"},
    )
    assert resp.status_code == 422


def test_unknown_target_status_returns_422(client: TestClient):
    resp = client.post(
        "/freigabe/evaluate",
        json={"actor_id": "u1", "actor_type": "SACHBEARBEITER", "target_status": "GENEHMIGT"},
    )
    assert resp.status_code == 422


def test_unknown_current_status_returns_422(client: TestClient):
    resp = client.post(
        "/freigabe/evaluate",
        json={
            "actor_id": "u1",
            "actor_type": "SACHBEARBEITER",
            "target_status": "ZUR_FREIGABE",
            "current_status": "OFFEN",
        },
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Teilweise-Freigegeben Pfad
# ---------------------------------------------------------------------------

def test_teilweise_freigegeben_zu_freigegeben(client: TestClient):
    resp = evaluate(client, "TEILWEISE_FREIGEGEBEN", "FREIGEGEBEN", "PROKURIST")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_teilweise_freigegeben_zu_zur_freigabe_neustart(client: TestClient):
    resp = evaluate(client, "TEILWEISE_FREIGEGEBEN", "ZUR_FREIGABE", "SACHBEARBEITER")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


# ---------------------------------------------------------------------------
# Default current_status = ENTWURF wenn nicht angegeben
# ---------------------------------------------------------------------------

def test_default_current_status_is_entwurf(client: TestClient):
    resp = client.post(
        "/freigabe/evaluate",
        json={"actor_id": "u1", "actor_type": "SACHBEARBEITER", "target_status": "ZUR_FREIGABE"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is True
    assert body["previous_status"] == "ENTWURF"
