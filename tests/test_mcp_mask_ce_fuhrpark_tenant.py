"""FUHRPARK-TENANT-CE-20261009: CE/MCP Isolation fuer Fuhrpark-Maskenwrites."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import fuhrpark
from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db as mcp_get_db, router as mcp_router
from app.core.database import get_db
from app.core.tenant import get_tenant_id


def _client_fuhrpark():
    app = FastAPI()
    app.include_router(fuhrpark.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[fuhrpark.get_tenant_id] = lambda: "tenant-a"
    db.query.return_value.filter.return_value.first.return_value = None
    return TestClient(app), db


def _mcp(scopes):
    app = FastAPI()
    app.include_router(mcp_router)
    db = Mock()
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "agent",
        "scopes": list(scopes),
        "raw": {"tenant_id": "tenant-a"},
    }
    app.dependency_overrides[mcp_get_db] = lambda: db
    return TestClient(app), db


def test_fahrzeug_ce_dry_run_no_commit():
    http, db = _client_fuhrpark()
    response = http.post(
        "/api/v1/fuhrpark/fahrzeuge/actions/speichern",
        json={"kennzeichen": "AB-CD 1", "typ": "LKW", "_mode": "dryRun"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    assert body["proposedChanges"][0]["tenant_id"] == "tenant-a"
    db.commit.assert_not_called()


def test_fahrzeug_ce_strips_tenant_override():
    http, db = _client_fuhrpark()
    with patch(
        "app.api.v1.endpoints.fuhrpark.upsert_fahrzeug",
        return_value={"id": "F-1", "kennzeichen": "AB-CD 1"},
    ) as upsert, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/fuhrpark/fahrzeuge/actions/speichern",
            json={
                "kennzeichen": "AB-CD 1",
                "typ": "LKW",
                "tenant_id": "evil",
                "_mode": "execute",
            },
        )
    assert response.status_code == 200
    assert response.json()["affectedIds"] == ["F-1"]
    assert upsert.call_args.args[1] == "tenant-a"
    assert "tenant_id" not in upsert.call_args.args[2]


def test_fahrzeug_loeschen_cross_tenant_dry_run_fails():
    http, db = _client_fuhrpark()
    with patch.object(fuhrpark.FahrzeugRepository, "get_by_id", return_value=None):
        response = http.post(
            "/api/v1/fuhrpark/fahrzeuge/foreign/actions/loeschen",
            json={"_mode": "dryRun"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_mcp_fahrzeug_rejects_tenant_override():
    http, db = _mcp(["logistics:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "logistik.fahrzeug.speichern",
            "parameters": {
                "kennzeichen": "AB-CD 1",
                "typ": "LKW",
                "reason": "Erfassung",
                "tenant_id": "evil",
            },
        },
    )
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_mcp_loeschen_cross_tenant_404():
    http, db = _mcp(["logistics:write"])
    with patch(
        "app.domains.operations.repository.FahrzeugRepository.get_by_id",
        return_value=None,
    ):
        response = http.post(
            "/mcp/tools/call",
            json={
                "tool_name": "logistik.fahrzeug.loeschen",
                "parameters": {"fahrzeug_id": "foreign", "reason": "Cleanup"},
                "mode": "dryRun",
            },
        )
    assert response.status_code == 404


def test_screen_definitions_fuhrpark_command_endpoints():
    from app.core.screen_definitions_capture import (
        build_fuhrpark_ausgehende_dokumente_screen_definition,
        build_fuhrpark_fahrzeug_stamm_screen_definition,
        build_fuhrpark_rechnungen_screen_definition,
        build_fuhrpark_terminarten_screen_definition,
    )

    stamm = build_fuhrpark_fahrzeug_stamm_screen_definition()
    save = next(a for a in stamm["actions"] if a["key"] == "speichern")
    delete = next(a for a in stamm["actions"] if a["key"] == "loeschen")
    assert save["commandEndpoint"].endswith("/fahrzeuge/actions/speichern")
    assert "{entity_id}" in delete["commandEndpoint"]
    term = next(
        a
        for a in build_fuhrpark_terminarten_screen_definition()["actions"]
        if a["key"] == "speichern"
    )
    assert term["commandEndpoint"].endswith("/terminarten/actions/speichern")
    rechnung = next(
        a
        for a in build_fuhrpark_rechnungen_screen_definition()["actions"]
        if a["key"] == "speichern"
    )
    assert rechnung["commandEndpoint"].endswith("/rechnungen/actions/speichern")
    dok = next(
        a
        for a in build_fuhrpark_ausgehende_dokumente_screen_definition()["actions"]
        if a["key"] == "speichern"
    )
    assert dok["commandEndpoint"].endswith("/ausgehende-dokumente/actions/speichern")
