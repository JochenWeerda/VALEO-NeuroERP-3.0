"""CommandEndpoint-Vertraege fuer Sanktionspruefung und Frachttabelle."""
from __future__ import annotations

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import logistik_frachttabellen, sanctions_compliance
from app.core.database import get_db
from app.core.dependencies import get_tenant_id as get_tenant_id_deps
from app.core.tenant import get_tenant_id as get_tenant_id_core


def _client_sanctions():
    app = FastAPI()
    app.include_router(sanctions_compliance.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id_core] = lambda: "tenant-a"
    return TestClient(app), db


def _client_fracht():
    app = FastAPI()
    app.include_router(logistik_frachttabellen.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id_deps] = lambda: "tenant-a"
    return TestClient(app), db


def test_sanctions_ce_dry_run_does_not_persist():
    http, db = _client_sanctions()
    with patch(
        "app.api.v1.endpoints.sanctions_compliance.match_sanctions_name",
        return_value=([], "KEIN_TREFFER", "ok"),
    ) as match, patch(
        "app.api.v1.endpoints.sanctions_compliance.persist_sanctions_check"
    ) as persist:
        response = http.post(
            "/api/v1/compliance/sanctions/actions/pruefen/customers",
            json={"name": "Muster", "_mode": "dryRun"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    assert body["proposedChanges"][0]["status"] == "KEIN_TREFFER"
    match.assert_called_once()
    persist.assert_not_called()
    db.commit.assert_not_called()


def test_sanctions_ce_rejects_scope_mismatch():
    http, _db = _client_sanctions()
    response = http.post(
        "/api/v1/compliance/sanctions/actions/pruefen/personal",
        json={"name": "X", "scope": "customers", "_mode": "validate"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert "Scope" in (body.get("error") or "")


def test_sanctions_ce_execute_persists_protocol():
    http, db = _client_sanctions()
    with patch(
        "app.api.v1.endpoints.sanctions_compliance.match_sanctions_name",
        return_value=([], "KEIN_TREFFER", "ok"),
    ), patch(
        "app.api.v1.endpoints.sanctions_compliance.persist_sanctions_check",
        return_value="chk-9",
    ) as persist, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/compliance/sanctions/actions/pruefen/customers",
            json={"name": "Muster", "entity_ref": "K-1"},
            headers={"X-User-ID": "agent-1"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "execute"
    assert body["affectedIds"] == ["chk-9"]
    persist.assert_called_once()
    assert persist.call_args.kwargs["tenant_id"] == "tenant-a"
    assert persist.call_args.kwargs["scope"] == "customers"
    db.commit.assert_called()


def test_fracht_ce_dry_run_no_insert():
    http, db = _client_fracht()
    db.execute.return_value.fetchone.return_value = None
    with patch(
        "app.api.v1.endpoints.logistik_frachttabellen.insert_frachttabelle"
    ) as insert:
        response = http.post(
            "/api/v1/logistik/frachttabellen/actions/anlegen",
            json={"tabelle_nr": "FT-1", "bezeichnung": "Test", "_mode": "dryRun"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    insert.assert_not_called()
    db.commit.assert_not_called()


def test_fracht_ce_execute_inserts():
    http, db = _client_fracht()
    db.execute.return_value.fetchone.return_value = None
    with patch(
        "app.api.v1.endpoints.logistik_frachttabellen.insert_frachttabelle",
        return_value={"id": "id-1", "tabelle_nr": "FT-1"},
    ) as insert, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/logistik/frachttabellen/actions/anlegen",
            json={"tabelle_nr": "FT-1", "bezeichnung": "Test", "einheit": "t"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["affectedIds"] == ["id-1"]
    insert.assert_called_once()
    assert insert.call_args.kwargs["tenant_id"] == "tenant-a"
    assert insert.call_args.kwargs["commit"] is False
    db.commit.assert_called()


def test_screen_definitions_expose_command_endpoints():
    from app.core.screen_definitions import get_screen_definition

    kunden = get_screen_definition("auswertungen/sanktionspruefung-kunden")
    personal = get_screen_definition("auswertungen/sanktionspruefung-personal")
    assert kunden["actions"][0]["commandEndpoint"].endswith("/pruefen/customers")
    assert personal["actions"][0]["commandEndpoint"].endswith("/pruefen/personal")
    assert "inputFlow" not in kunden["actions"][0]
    assert not kunden["actions"][0].get("forbiddenForAgents")

    from app.core.screen_definitions_capture import build_logistik_frachttabellen_screen_definition

    fracht = build_logistik_frachttabellen_screen_definition()
    anlegen = next(a for a in fracht["actions"] if a["key"] == "anlegen")
    assert anlegen["commandEndpoint"] == "/api/v1/logistik/frachttabellen/actions/anlegen"
    assert not anlegen.get("forbiddenForAgents")
