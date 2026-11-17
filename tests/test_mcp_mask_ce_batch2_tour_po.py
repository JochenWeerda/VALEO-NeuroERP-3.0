"""Batch2 Fortsetzung: Tour anlegen + Bestellung speichern CE/MCP + Isolation."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import einkauf_bestellvorschlag, logistics_tours
from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db as mcp_get_db, router as mcp_router
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from testgrenze import ALLE_FACHROLLEN, ersetze_nutzer, setze_identitaet



def _client_tours():
    app = FastAPI()
    app.include_router(logistics_tours.router, prefix="/api/v1")
    ersetze_nutzer(app, *ALLE_FACHROLLEN)  # Schreibwege pruefen die Bereichsrolle (19.10.2026)
    setze_identitaet(app, "disp")
    db = Mock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.mappings.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: db
    # Die Tourenwege nehmen den Mandanten seit 28.10.2026 aus dem Token (app.core.tenant).
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app), db


def _client_po():
    app = FastAPI()
    app.include_router(einkauf_bestellvorschlag.router, prefix="/api/v1")
    ersetze_nutzer(app, "EINKAUF_BEARBEITEN")  # Bestellvorschlag ist Einkaufsarbeit
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app), db

def _mcp(scopes):
    app = FastAPI()
    app.include_router(mcp_router)
    db = Mock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    db.execute.return_value.fetchone.return_value = None
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "agent",
        "scopes": list(scopes),
        "raw": {"tenant_id": "tenant-a"},
    }
    app.dependency_overrides[mcp_get_db] = lambda: db
    return TestClient(app), db


def test_tour_ce_dry_run_no_insert():
    http, db = _client_tours()
    with patch("app.api.v1.endpoints.logistics_tours.insert_tour") as insert:
        response = http.post(
            "/api/v1/logistik/tours/actions/anlegen",
            json={"date": "2026-10-09T08:00:00", "notes": "Dispo", "_mode": "dryRun"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    insert.assert_not_called()
    db.commit.assert_not_called()


def test_tour_ce_strips_tenant_override():
    http, db = _client_tours()
    with patch(
        "app.api.v1.endpoints.logistics_tours.insert_tour",
        return_value={"id": "t1", "stops": []},
    ) as insert, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/logistik/tours/actions/anlegen",
            json={
                "notes": "Dispo",
                "tenant_id": "evil",
                "mandanten_id": "evil",
                "_mode": "execute",
            },
            headers={"X-User-ID": "disp"},
        )
    assert response.status_code == 200
    assert response.json()["affectedIds"] == ["t1"]
    assert insert.call_args.kwargs["tenant_id"] == "tenant-a"


def test_mcp_tour_rejects_tenant_override():
    http, db = _mcp(["logistics:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "logistik.tour.anlegen",
            "parameters": {"reason": "Dispo Test", "tenant_id": "evil"},
        },
    )
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_screen_definitions_tour_and_po_command_endpoints():
    from app.core.screen_definitions import get_screen_definition
    from app.core.screen_definitions_capture import build_logistik_tourenplanung_screen_definition

    tour = build_logistik_tourenplanung_screen_definition()
    anlegen = next(a for a in tour["actions"] if a["key"] == "anlegen")
    assert anlegen["commandEndpoint"].endswith("/tours/actions/anlegen")
    assert "stubReason" not in anlegen

    # Die Bestellmaske einkauf/purchase-order ist entfernt (BELEG-052 Phase 3b); die Bestellung ist Belegmaske.
    assert get_screen_definition("einkauf/purchase-order") is None
