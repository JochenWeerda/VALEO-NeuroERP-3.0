"""Batch3: Bewerbung, Einwilligung, Postfach CE/MCP + Isolation."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import mailkonto, personal_bewerbungen
from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db as mcp_get_db, router as mcp_router
from app.core.database import get_db
from app.core.tenant import get_tenant_id


def _client_hr():
    app = FastAPI()
    app.include_router(personal_bewerbungen.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[personal_bewerbungen.personal_write] = lambda: {
        "sub": "hr", "roles": ["PERSONAL_BEARBEITEN"]
    }
    app.dependency_overrides[personal_bewerbungen.personal_admin] = lambda: {
        "sub": "hr-admin", "roles": ["PERSONAL_ADMIN"]
    }
    return TestClient(app), db


def _client_mail():
    app = FastAPI()
    app.include_router(mailkonto.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    app.dependency_overrides[mailkonto.verwaltung] = lambda: {
        "sub": "admin", "roles": ["admin"]
    }
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


def test_bewerbung_ce_dry_run():
    http, db = _client_hr()
    with patch("app.services.bewerbung_service.anlegen") as anlegen:
        response = http.post(
            "/api/v1/personal/applications/actions/speichern",
            json={
                "applicant_name": "Max Muster",
                "applicant_email": "max@example.com",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    anlegen.assert_not_called()
    db.commit.assert_not_called()


def test_bewerbung_ce_strips_tenant_override():
    http, db = _client_hr()
    with patch(
        "app.services.bewerbung_service.anlegen",
        return_value={"id": "app-1", "applicant_name": "Max"},
    ) as anlegen, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/personal/applications/actions/speichern",
            json={
                "applicant_name": "Max Muster",
                "applicant_email": "max@example.com",
                "tenant_id": "evil",
                "_mode": "execute",
            },
        )
    assert response.status_code == 200
    assert response.json()["affectedIds"] == ["app-1"]
    assert anlegen.call_args.args[1] == "tenant-a"


def test_einwilligung_ce_dry_run():
    http, db = _client_hr()
    with patch("app.services.bewerbung_einwilligung_service.erklaerung_anlegen") as create:
        response = http.post(
            "/api/v1/personal/applications/einwilligungserklaerungen/actions/anlegen",
            json={"wortlaut": "Ich willige ein.", "_mode": "dryRun"},
        )
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    create.assert_not_called()


def test_postfach_ce_cross_tenant_404():
    http, db = _client_mail()
    with patch(
        "app.services.mailkonto_service.lesen",
        side_effect=__import__("app.services.mailkonto_service", fromlist=["MailkontoFehler"]).MailkontoFehler(
            "Postfach nicht gefunden."
        ),
    ):
        response = http.post(
            "/api/v1/admin/postfaecher/actions/speichern",
            json={
                "kennung": "info",
                "absender_email": "info@example.com",
                "anbieter": "smtp",
                "postfach_id": "foreign",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_mcp_bewerbung_rejects_tenant_override():
    http, db = _mcp(["hr:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "hr.bewerbung.speichern",
            "parameters": {
                "applicant_name": "Max",
                "applicant_email": "m@x.de",
                "reason": "Erfassung",
                "tenant_id": "evil",
            },
        },
    )
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_mcp_postfach_rejects_tenant_override():
    http, db = _mcp(["admin:write"])
    response = http.post(
        "/mcp/tools/call",
        json={
            "tool_name": "admin.postfach.speichern",
            "parameters": {
                "kennung": "info",
                "absender_email": "info@example.com",
                "reason": "Einrichten",
                "mandanten_id": "evil",
            },
        },
    )
    assert response.status_code == 422


def test_mcp_postfach_cross_tenant_404():
    http, db = _mcp(["admin:write"])
    with patch(
        "app.services.mailkonto_service.lesen",
        side_effect=__import__(
            "app.services.mailkonto_service", fromlist=["MailkontoFehler"]
        ).MailkontoFehler("Postfach nicht gefunden."),
    ):
        response = http.post(
            "/mcp/tools/call",
            json={
                "tool_name": "admin.postfach.speichern",
                "parameters": {
                    "kennung": "info",
                    "absender_email": "info@example.com",
                    "anbieter": "smtp",
                    "postfach_id": "foreign",
                    "reason": "Update",
                },
                "mode": "dryRun",
            },
        )
    assert response.status_code == 404


def test_screen_definitions_batch3_command_endpoints():
    from app.core.screen_definitions_capture import (
        build_admin_postfaecher_screen_definition,
        build_personal_bewerbungen_screen_definition,
        build_personal_einwilligungserklaerungen_screen_definition,
    )

    bew = next(
        a for a in build_personal_bewerbungen_screen_definition()["actions"] if a["key"] == "speichern"
    )
    assert bew["commandEndpoint"].endswith("/applications/actions/speichern")
    erk = next(
        a
        for a in build_personal_einwilligungserklaerungen_screen_definition()["actions"]
        if a["key"] == "anlegen"
    )
    assert "einwilligungserklaerungen/actions/anlegen" in erk["commandEndpoint"]
    pf = next(a for a in build_admin_postfaecher_screen_definition()["actions"] if a["key"] == "speichern")
    assert pf["commandEndpoint"].endswith("/postfaecher/actions/speichern")
