from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints.mcp_tool_registry import router, get_current_user, get_db
from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool


PARAMETERS = {"kunden_nr": "TEST", "kanal": "telefon", "ergebnis": "Synthetic test"}
USER = {"sub": "test-agent", "scopes": ["crm:write"], "raw": {"tenant_id": "tenant-a"}}


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    db = Mock()
    db.execute.return_value.first.return_value = (1,)
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as http:
        yield http, app, db


@pytest.mark.parametrize("user,header", [
    ({"sub": "agent", "scopes": [], "raw": {"tenant_id": "tenant-a"}}, None),
    ({"sub": "agent", "scopes": ["crm:write"], "raw": {}}, None),
    ({"scopes": ["crm:write"], "raw": {"tenant_id": "tenant-a"}}, None),
    (USER, "tenant-b"),
])
def test_unauthorized_identity_never_reaches_database(user, header):
    from fastapi import HTTPException
    db = Mock()
    with pytest.raises(HTTPException) as error:
        execute_mcp_tool(db, ToolExecutionRequest(tool_name="crm.contact.log", parameters=PARAMETERS), user, header)
    assert error.value.status_code == 403
    assert not db.mock_calls


def test_default_is_non_mutating_preview(client):
    http, _, db = client
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS})
    assert result.status_code == 200
    assert result.json()["mode"] == "dryRun"
    db.commit.assert_not_called()


def test_execute_requires_replay_key(client):
    http, _, db = client
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS, "mode": "execute"})
    assert result.status_code == 422
    db.execute.assert_not_called()


@pytest.mark.parametrize("extra", [{"tenant_id": "tenant-b"}, {"bediener": "admin"}, {"approval_granted": True}])
def test_arguments_cannot_override_identity_or_approval(client, extra):
    http, _, db = client
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": {**PARAMETERS, **extra}})
    assert result.status_code == 422
    db.execute.assert_not_called()


def test_cross_tenant_customer_does_not_validate(client):
    http, _, db = client
    db.execute.return_value.first.return_value = None
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS})
    assert result.status_code == 404
    db.commit.assert_not_called()


def test_missing_bearer_cannot_call_tool(client):
    http, app, db = client
    app.dependency_overrides.pop(get_current_user)
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS})
    assert result.status_code in (401, 403)
    db.execute.assert_not_called()


def test_replay_returns_saved_result_without_contact_write(client):
    import hashlib
    import json
    from app.services.mcp_execution_service import ContactLogInput
    http, _, db = client
    canonical = ContactLogInput.model_validate(PARAMETERS).model_dump(mode="json")
    fingerprint = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": USER["sub"], "payload_hash": fingerprint,
        "result": {"success": True, "kontakt_id": "saved-contact", "mode": "execute"},
    }
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS,
                                             "mode": "execute", "idempotency_key": "once"})
    assert result.status_code == 200
    assert result.json()["replayed"] is True
    assert result.json()["kontakt_id"] == "saved-contact"
    assert db.execute.call_count == 2
    db.commit.assert_not_called()


@pytest.mark.parametrize("actor,hash_value", [("another-agent", "different"), ("test-agent", "different")])
def test_replay_key_cannot_be_reused_for_different_actor_or_payload(client, actor, hash_value):
    http, _, db = client
    db.execute.return_value.mappings.return_value.first.return_value = {
        "actor_id": actor, "payload_hash": hash_value, "result": {},
    }
    response = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": PARAMETERS,
                                                "mode": "execute", "idempotency_key": "once"})
    assert response.status_code == 409
    db.commit.assert_not_called()


INVOICE = {"lieferschein_nr": "LS-1", "rechnungsdatum": "2026-09-29"}
NOTE = {"id": "ls-1", "status": "posted", "totals": {"netto": 10.5, "mwst": 2.0}, "positionen": 1}


def _as_sales(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {**USER, "scopes": ["sales:write"]}
    return http, db


def test_client_approval_flag_does_not_enable_invoice_posting(client):
    http, db = _as_sales(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": {**INVOICE, "approval_granted": True},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_invoice_execute_never_posts(client):
    http, db = _as_sales(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": INVOICE,
        "mode": "execute",
    })
    assert response.status_code == 501
    db.execute.assert_not_called()
    db.commit.assert_not_called()


def test_invoice_scope_is_required(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": INVOICE,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_invoice_dry_run_reads_totals_without_writing(client):
    http, db = _as_sales(client)
    db.execute.return_value.mappings.return_value.first.return_value = NOTE
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": INVOICE,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["posted"] is False
    assert body["betrag_netto"] == 10.5
    assert body["mwst"] == 2.0
    assert body["positionen"] == 1
    assert "entwurf_id" not in body
    db.commit.assert_not_called()


def test_unready_delivery_note_is_not_proposed(client):
    http, db = _as_sales(client)
    db.execute.return_value.mappings.return_value.first.return_value = {**NOTE, "status": "draft"}
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": INVOICE,
    })
    assert response.status_code == 409
    db.commit.assert_not_called()


def test_invoice_propose_stores_pending_proposal_and_does_not_post(client):
    http, db = _as_sales(client)
    statements: list[str] = []

    def execute(sql, params=None):
        statements.append(str(sql))
        result = Mock()
        if "delivery_notes" in str(sql):
            result.mappings.return_value.first.return_value = NOTE
        else:
            result.mappings.return_value.first.return_value = None
        return result

    db.execute.side_effect = execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.propose",
        "parameters": INVOICE,
        "mode": "propose",
        "idempotency_key": "once",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["posted"] is False
    assert body["approval_status"] == "pending"
    assert body["entwurf_id"]
    assert body["replayed"] is False
    joined = "\n".join(statements)
    assert "agent_proposals" in joined
    assert "rechnung_vorschlag" in joined
    assert "'pending'" in joined
    assert "domain_erp" not in joined
    assert "sales_invoices" not in joined
    db.commit.assert_called_once()
