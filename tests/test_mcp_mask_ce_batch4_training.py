"""Batch4: Personal Training CE/MCP + Fuhrpark blocked_missing_tenant."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import training
from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db as mcp_get_db, router as mcp_router
from app.core.database import get_db
from app.core.tenant import get_tenant_id


def _client_training():
    app = FastAPI()
    app.include_router(training.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
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


def test_onboarding_ce_dry_run():
    http, db = _client_training()
    with patch("app.api.v1.endpoints.training._require_tenant_row"):
        response = http.post(
            "/api/v1/training/onboarding/runs/actions/speichern",
            json={
                "employee_ref": "E-1",
                "checklist_id": "cl-1",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    assert response.json()["success"] is True
    db.commit.assert_not_called()


def test_onboarding_ce_foreign_checklist_fails():
    http, db = _client_training()
    with patch(
        "app.api.v1.endpoints.training._require_tenant_row",
        side_effect=HTTPException(status_code=404, detail="Checklist not found"),
    ):
        response = http.post(
            "/api/v1/training/onboarding/runs/actions/speichern",
            json={
                "employee_ref": "E-1",
                "checklist_id": "foreign",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_qualifikation_ce_strips_tenant_override():
    http, db = _client_training()
    with patch(
        "app.api.v1.endpoints.training.insert_qualification",
        return_value={"id": "q-1", "employee_ref": "E-1", "role_code": "R1"},
    ) as insert, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/training/qualifications/actions/speichern",
            json={
                "employee_ref": "E-1",
                "role_code": "R1",
                "tenant_id": "evil",
                "_mode": "execute",
            },
        )
    assert response.status_code == 200
    assert response.json()["affectedIds"] == ["q-1"]
    assert insert.call_args.args[1] == "tenant-a"


def test_schulung_ce_dry_run():
    http, db = _client_training()
    with patch("app.api.v1.endpoints.training._require_tenant_row"):
        response = http.post(
            "/api/v1/training/assignments/actions/speichern",
            json={
                "employee_ref": "E-1",
                "course_id": "c-1",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    db.commit.assert_not_called()


def test_mcp_onboarding_rejects_tenant_override():
    http, db = _mcp(["hr:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "hr.onboarding.speichern",
            "parameters": {
                "employee_ref": "E-1",
                "checklist_id": "cl-1",
                "reason": "Erfassung",
                "tenant_id": "evil",
            },
        },
    )
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_mcp_schulung_cross_tenant_course_404():
    http, db = _mcp(["hr:write"])
    with patch(
        "app.api.v1.endpoints.training._require_tenant_row",
        side_effect=HTTPException(status_code=404, detail="Course not found"),
    ):
        response = http.post(
            "/mcp/tools/call",
            json={
                "tool_name": "hr.schulung.speichern",
                "parameters": {
                    "employee_ref": "E-1",
                    "course_id": "foreign",
                    "reason": "Zuweisung",
                },
                "mode": "dryRun",
            },
        )
    assert response.status_code == 404


def test_screen_definitions_batch4_command_endpoints():
    from app.core.screen_definitions_capture import (
        build_personal_onboarding_screen_definition,
        build_personal_qualifikationen_screen_definition,
        build_personal_schulungen_screen_definition,
    )

    onb = next(
        a for a in build_personal_onboarding_screen_definition()["actions"] if a["key"] == "speichern"
    )
    assert onb["commandEndpoint"].endswith("/onboarding/runs/actions/speichern")
    qual = next(
        a
        for a in build_personal_qualifikationen_screen_definition()["actions"]
        if a["key"] == "speichern"
    )
    assert qual["commandEndpoint"].endswith("/qualifications/actions/speichern")
    sch = next(
        a for a in build_personal_schulungen_screen_definition()["actions"] if a["key"] == "speichern"
    )
    assert sch["commandEndpoint"].endswith("/assignments/actions/speichern")


def test_fuhrpark_now_mapped_after_tenant_ce():
    """Historischer Batch4-Gap geschlossen durch FUHRPARK-TENANT-CE-20261009."""
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "mask_map_batch4", root / "scripts/generate_mcp_mask_action_map.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.build_map()
    by_id = {m["mask_action_id"]: m for m in data["mappings"]}
    for mid in (
        "mask:fuhrpark/ausgehende-dokumente:speichern",
        "mask:fuhrpark/fahrzeug-stamm:loeschen",
        "mask:fuhrpark/fahrzeug-stamm:speichern",
        "mask:fuhrpark/rechnungen:speichern",
        "mask:fuhrpark/terminarten:speichern",
    ):
        assert by_id[mid]["coverage"] == "mapped"
        assert by_id[mid]["mcp_tool_id"]
    assert data["stats"]["by_coverage"].get("blocked_missing_tenant", 0) == 0
    assert data["stats"]["by_coverage"].get("blocked_no_endpoint", 0) == 0
