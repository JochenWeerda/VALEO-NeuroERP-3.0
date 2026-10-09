"""Batch2 Fortsetzung: Tour anlegen + Bestellung speichern CE/MCP + Isolation."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import einkauf_bestellvorschlag, logistics_tours
from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db as mcp_get_db, router as mcp_router
from app.core.database import get_db
from app.core.dependencies import get_tenant_id as get_tenant_dep
from app.core.tenant import get_tenant_id



def _client_tours():
    app = FastAPI()
    app.include_router(logistics_tours.router, prefix="/api/v1")
    db = Mock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.mappings.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_dep] = lambda: "tenant-a"
    return TestClient(app), db


def _client_po():
    app = FastAPI()
    app.include_router(einkauf_bestellvorschlag.router, prefix="/api/v1")
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


def test_po_ce_cross_tenant_is_not_found():
    http, db = _client_po()
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post(
        "/api/v1/einkauf/bestellungen/PO-X/actions/speichern",
        json={"notiz": "x", "_mode": "dryRun"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert "nicht gefunden" in (body.get("error") or "").lower()
    db.commit.assert_not_called()


def test_po_ce_dry_run_tenant_scoped():
    http, db = _client_po()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "b1",
        "bestellnummer": "PO-1",
        "status": "entwurf",
    }
    with patch(
        "app.services.procurement_service.ProcurementService.update_bestellung"
    ) as upd:
        response = http.post(
            "/api/v1/einkauf/bestellungen/b1/actions/speichern",
            json={"notiz": "Hinweis", "tenant_id": "evil", "_mode": "dryRun"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    upd.assert_not_called()
    sql = str(db.execute.call_args[0][0])
    assert "tenant_id" in sql


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


def test_mcp_po_save_rejects_tenant_override():
    http, db = _mcp(["einkauf:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "einkauf.bestellung.speichern",
            "parameters": {
                "bestellung_id": "b1",
                "notiz": "x",
                "reason": "Korrektur",
                "mandanten_id": "evil",
            },
        },
    )
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_mcp_po_save_cross_tenant_404():
    http, db = _mcp(["einkauf:write"])
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "einkauf.bestellung.speichern",
            "parameters": {
                "bestellung_id": "foreign",
                "notiz": "x",
                "reason": "Korrektur",
            },
        },
    )
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_screen_definitions_tour_and_po_command_endpoints():
    from app.core.screen_definitions import get_screen_definition
    from app.core.screen_definitions_capture import build_logistik_tourenplanung_screen_definition

    tour = build_logistik_tourenplanung_screen_definition()
    anlegen = next(a for a in tour["actions"] if a["key"] == "anlegen")
    assert anlegen["commandEndpoint"].endswith("/tours/actions/anlegen")
    assert "stubReason" not in anlegen

    po = get_screen_definition("einkauf/purchase-order")
    save = next(a for a in po["actions"] if a["key"] == "speichern")
    assert save["commandEndpoint"].endswith("/actions/speichern")
    assert "inputFlow" not in save
    assert not save.get("forbiddenForAgents")
