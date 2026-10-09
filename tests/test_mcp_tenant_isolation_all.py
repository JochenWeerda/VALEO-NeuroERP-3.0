"""MCP-Tools: Mandantenisolation fuer Reads, Writes und CRUD.

Regeln:
- Mandant nur aus Token (tenant_id / mandanten_id Claim)
- Parameter-Override → 422
- Queries/Lookups immer Token-tenant; fremde IDs → 404, kein Write
"""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints.mcp_tool_registry import get_current_user, get_db, router
from app.services.mask_action_runtime_service import parse_action_body
from app.services.mcp_execution_service import (
    ToolExecutionRequest,
    _reject_identity_parameters,
    execute_mcp_tool,
)

USER = {"sub": "test-agent", "scopes": ["crm:write"], "raw": {"tenant_id": "tenant-a"}}
CONTACT = {"kunden_nr": "TEST", "kanal": "telefon", "ergebnis": "Synthetic test"}
ACTIVITY = {"kunden_nr": "TEST", "betreff": "Follow-up", "typ": "Anruf"}
SEARCH = {"query": "Muster", "limit": 10}
OPEN = {"kunden_nr": "TEST"}
ORDER_STATUS = {"auftrag_nr": "SO-FOREIGN"}
SANCTIONS = {"name": "Muster GmbH", "scope": "customers"}
FRACHT = {"tabelle_nr": "FT-ISO", "bezeichnung": "Iso Test"}
BONUS = {
    "report_id": "bonus-by-customer",
    "from_date": "2026-01-01",
    "to_date": "2026-01-31",
    "rate_pct": "2.5",
    "reason": "Iso Test",
}
QUERY_IMP = {
    "bundle": {
        "schema_version": 1,
        "definition": {"name": "OP", "tenant_id": "evil"},
        "signature": "x",
    },
    "reason": "Iso Testlauf",
}


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    db = Mock()
    db.execute.return_value.first.return_value = (1,)
    db.execute.return_value.mappings.return_value.first.return_value = None
    db.execute.return_value.mappings.return_value.all.return_value = []
    db.execute.return_value.fetchone.return_value = None
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as http:
        yield http, app, db


def _as_scopes(client, scopes):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": list(scopes),
    }
    return http, db


@pytest.mark.parametrize(
    "key,value",
    [
        ("tenant_id", "tenant-b"),
        ("mandanten_id", "tenant-b"),
    ],
)
def test_central_guard_rejects_identity_parameters(key, value):
    with pytest.raises(HTTPException) as err:
        _reject_identity_parameters({**CONTACT, key: value})
    assert err.value.status_code == 422


def test_mask_action_body_strips_tenant_fields():
    mode, _reason, _key, payload = parse_action_body(
        {
            "name": "X",
            "tenant_id": "evil",
            "mandanten_id": "evil2",
            "_mode": "dryRun",
        }
    )
    assert mode == "dryRun"
    assert "tenant_id" not in payload
    assert "mandanten_id" not in payload


@pytest.mark.parametrize(
    "tool,params,scopes",
    [
        # Reads
        ("crm.customer.search", SEARCH, ["crm:read"]),
        ("crm.customer.open", OPEN, ["crm:read"]),
        ("sales.order.status", ORDER_STATUS, ["sales:read"]),
        # Writes
        ("crm.contact.log", CONTACT, ["crm:write"]),
        ("crm.activity.create", ACTIVITY, ["crm:write"]),
        ("compliance.sanctions.check", SANCTIONS, ["compliance:write"]),
        ("logistik.frachttabelle.anlegen", FRACHT, ["logistics:write"]),
        ("reporting.bonus.calculate", BONUS, ["reporting:write"]),
        ("reporting.query.import_signed", QUERY_IMP, ["reporting:write"]),
    ],
)
@pytest.mark.parametrize(
    "poison",
    [
        {"tenant_id": "tenant-b"},
        {"mandanten_id": "tenant-b"},
    ],
)
def test_all_tools_reject_tenant_override_parameters(client, tool, params, scopes, poison):
    http, db = _as_scopes(client, scopes)
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": tool, "parameters": {**params, **poison}},
    )
    assert response.status_code == 422
    db.execute.assert_not_called()
    db.commit.assert_not_called()


def test_customer_search_sql_is_token_tenant_scoped(client):
    http, db = _as_scopes(client, ["crm:read"])
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.customer.search", "parameters": SEARCH},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []
    sql = str(db.execute.call_args[0][0])
    params = db.execute.call_args[0][1]
    assert "tenant_id" in sql
    assert params["tenant"] == "tenant-a"
    db.commit.assert_not_called()


def test_customer_open_cross_tenant_id_is_404(client):
    http, db = _as_scopes(client, ["crm:read"])
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.customer.open", "parameters": OPEN},
    )
    assert response.status_code == 404
    sql = str(db.execute.call_args[0][0])
    assert "tenant_id" in sql
    assert "FOR SHARE" in sql
    db.commit.assert_not_called()


def test_order_status_cross_tenant_id_is_404(client):
    http, db = _as_scopes(client, ["sales:read"])
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "sales.order.status", "parameters": ORDER_STATUS},
    )
    assert response.status_code == 404
    sql = str(db.execute.call_args[0][0])
    params = db.execute.call_args[0][1]
    assert "tenant_id" in sql
    assert params["tenant"] == "tenant-a"
    db.commit.assert_not_called()


def test_contact_write_lookup_is_token_tenant_scoped(client):
    http, db = _as_scopes(client, ["crm:write"])
    db.execute.return_value.first.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.contact.log", "parameters": CONTACT},
    )
    assert response.status_code == 404
    sql = str(db.execute.call_args[0][0])
    assert "tenant_id" in sql
    assert "FOR SHARE" in sql
    db.commit.assert_not_called()


def test_activity_write_lookup_is_token_tenant_scoped(client):
    http, db = _as_scopes(client, ["crm:write"])
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.activity.create", "parameters": ACTIVITY},
    )
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_fracht_dry_run_duplicate_check_uses_token_tenant(client):
    http, db = _as_scopes(client, ["logistics:write"])
    db.execute.return_value.fetchone.return_value = None
    response = http.post(
        "/mcp/tools/call",
        json={"tool_name": "logistik.frachttabelle.anlegen", "parameters": FRACHT},
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    sql = str(db.execute.call_args[0][0])
    params = db.execute.call_args[0][1]
    assert "tenant_id" in sql
    assert params["tid"] == "tenant-a"
    db.commit.assert_not_called()


def test_sanctions_execute_persists_only_token_tenant(client):
    http, db = _as_scopes(client, ["compliance:write"])
    with patch(
        "app.api.v1.endpoints.sanctions_compliance.match_sanctions_name",
        return_value=([], "KEIN_TREFFER", "ok"),
    ), patch(
        "app.api.v1.endpoints.sanctions_compliance.persist_sanctions_check",
        return_value="chk-t",
    ) as persist, patch(
        "app.services.mcp_execution_service._write_audit", return_value="a"
    ), patch("app.services.mcp_execution_service._store_execution"), patch(
        "app.services.mcp_execution_service._advisory_lock"
    ), patch(
        "app.services.mcp_execution_service._replay_or_none", return_value=None
    ):
        response = http.post(
            "/mcp/tools/call",
            json={
                "tool_name": "compliance.sanctions.check",
                "parameters": SANCTIONS,
                "mode": "execute",
                "idempotency_key": "iso-san-1",
            },
        )
    assert response.status_code == 200
    assert persist.call_args.kwargs["tenant_id"] == "tenant-a"


def test_query_import_strips_foreign_tenant_from_bundle_definition():
    from app.services.query_center_service import QueryCenterService

    db = Mock()
    svc = QueryCenterService(db, "tenant-a", signing_key="secret")
    with patch.object(
        svc,
        "preview_import_signed",
        return_value={
            "name": "OP (Import)",
            "data_product_id": "x",
            "selected_fields": [],
            "would_import": True,
        },
    ), patch.object(
        svc, "save", return_value={"id": "d1", "name": "OP (Import)"}
    ) as save:
        svc.import_signed(
            {
                "schema_version": 1,
                "definition": {
                    "name": "OP",
                    "id": "foreign-id",
                    "tenant_id": "evil-tenant",
                    "mandanten_id": "evil-tenant",
                    "owner_id": "other-user",
                    "data_product_id": "ar",
                    "selected_fields": ["id"],
                },
                "signature": "x",
            },
            actor="agent",
            reason="Import Test",
        )
    saved_payload = save.call_args.args[0]
    assert "tenant_id" not in saved_payload
    assert "mandanten_id" not in saved_payload
    assert "owner_id" not in saved_payload
    assert "id" not in saved_payload


def test_execute_mcp_tool_never_uses_parameter_tenant(client):
    http, app, db = client
    with pytest.raises(HTTPException) as err:
        execute_mcp_tool(
            db,
            ToolExecutionRequest(
                tool_name="crm.customer.search",
                parameters={**SEARCH, "tenant_id": "tenant-b"},
            ),
            {**USER, "scopes": ["crm:read"]},
            None,
        )
    assert err.value.status_code == 422
