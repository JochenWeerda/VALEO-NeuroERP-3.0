from decimal import Decimal
from unittest.mock import Mock, patch

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


@pytest.mark.parametrize("extra", [
    {"tenant_id": "tenant-b"},
    {"mandanten_id": "tenant-b"},
    {"bediener": "admin"},
    {"approval_granted": True},
])
def test_arguments_cannot_override_identity_or_approval(client, extra):
    http, _, db = client
    result = http.post('/mcp/tools/call', json={"tool_name": "crm.contact.log", "parameters": {**PARAMETERS, **extra}})
    assert result.status_code == 422
    db.execute.assert_not_called()


def test_mandanten_id_claim_is_accepted_as_tenant(client):
    """IdP-Claim mandanten_id ist Alias der Mandanten-ID; Header muss passen."""
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-agent",
        "scopes": ["crm:write"],
        "raw": {"mandanten_id": "tenant-a"},
    }
    result = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.contact.log", "parameters": PARAMETERS},
        headers={"X-Tenant-ID": "tenant-a"},
    )
    assert result.status_code == 200
    assert result.json()["mode"] == "dryRun"
    db.commit.assert_not_called()


def test_mandanten_id_claim_rejects_mismatched_header(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-agent",
        "scopes": ["crm:write"],
        "raw": {"mandanten_id": "tenant-a"},
    }
    result = http.post(
        "/mcp/tools/call",
        json={"tool_name": "crm.contact.log", "parameters": PARAMETERS},
        headers={"X-Tenant-ID": "tenant-b"},
    )
    assert result.status_code == 403
    assert not db.mock_calls


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


ACTIVITY = {"kunden_nr": "TEST", "betreff": "Rueckruf", "typ": "Anruf"}
CUSTOMER_OPEN = {"kunden_nr": "TEST"}
CUSTOMER_ROW = {"id": "cust-uuid-1", "name": "Test GmbH", "kunden_nr": "TEST"}


def _as_crm_read(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["crm:read"],
    }
    return http, db


def test_customer_open_dry_run_returns_route_without_writing(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = CUSTOMER_ROW
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["customer_id"] == "cust-uuid-1"
    assert body["kunden_nr"] == "TEST"
    assert body["name"] == "Test GmbH"
    assert body["route_path"] == "/crm/customers/cust-uuid-1"
    assert body["screen_id"] == "crm/customer-360"
    sql = str(db.execute.call_args[0][0])
    assert "domain_crm.customers" in sql
    assert "tenant_id" in sql
    db.commit.assert_not_called()


def test_customer_open_execute_is_read_only(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = CUSTOMER_ROW
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": CUSTOMER_OPEN,
        "mode": "execute",
        "idempotency_key": "nav-once",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "execute"
    assert body["route_path"] == "/crm/customers/cust-uuid-1"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO domain_crm" not in joined
    db.commit.assert_not_called()


def test_customer_open_requires_crm_read_scope(client):
    http, _, db = client  # default USER has crm:write only
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_customer_open_cross_tenant_is_not_found(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_customer_open_rejects_mandant_parameter(client):
    http, db = _as_crm_read(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": {**CUSTOMER_OPEN, "mandanten_id": "other"},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_customer_open_rejects_propose_mode(client):
    http, db = _as_crm_read(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.open",
        "parameters": CUSTOMER_OPEN,
        "mode": "propose",
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


SEARCH_ROWS = [
    {
        "id": "cust-uuid-1",
        "kunden_nr": "TEST",
        "name": "Test GmbH",
        "address": {"city": "Oldenburg", "postal_code": "26121"},
    },
]


def test_customer_search_dry_run_returns_items_without_writing(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.all.return_value = SEARCH_ROWS
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": "Test", "limit": 10},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["count"] == 1
    assert body["items"][0]["kunden_nr"] == "TEST"
    assert body["items"][0]["name"] == "Test GmbH"
    assert body["items"][0]["ort"] == "Oldenburg"
    assert body["items"][0]["route_path"] == "/crm/customers/cust-uuid-1"
    assert body["items"][0]["customer_id"] == "cust-uuid-1"
    sql = str(db.execute.call_args[0][0])
    assert "domain_crm.customers" in sql
    assert "tenant_id" in sql
    db.commit.assert_not_called()


def test_customer_search_execute_is_read_only_and_allows_empty(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.all.return_value = []
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": "nobody"},
        "mode": "execute",
        "idempotency_key": "search-once",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "execute"
    assert body["items"] == []
    assert body["count"] == 0
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    db.commit.assert_not_called()


def test_customer_search_requires_crm_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": "Test"},
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_customer_search_rejects_mandant_parameter(client):
    http, db = _as_crm_read(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": "Test", "mandanten_id": "other"},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_customer_search_rejects_propose_and_empty_query(client):
    http, db = _as_crm_read(client)
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": "Test"},
        "mode": "propose",
    })
    assert propose.status_code == 422
    empty = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.search",
        "parameters": {"query": ""},
    })
    assert empty.status_code == 422
    db.execute.assert_not_called()


SUMMARY_CUSTOMER = {
    "id": "cust-uuid-1",
    "name": "Test GmbH",
    "kunden_nr": "TEST",
    "business_partner_id": "bp-1",
}


def _summary360_execute(sql, params=None):
    result = Mock()
    sql_s = str(sql)
    if "FROM domain_crm.customers" in sql_s and "FOR SHARE" in sql_s:
        result.mappings.return_value.first.return_value = SUMMARY_CUSTOMER
    elif "sales_orders" in sql_s:
        result.mappings.return_value.first.return_value = {"offene_auftraege": 2}
    elif "offene_posten" in sql_s:
        result.mappings.return_value.first.return_value = {"op_saldo_eur": 150.5}
    elif "FROM domain_crm.activities" in sql_s:
        result.mappings.return_value.all.return_value = [
            {"id": "a1", "kanal": "Anruf", "betreff": "Rueckruf", "erfasst_am": "2026-10-01"},
        ]
    elif "business_partners" in sql_s:
        result.mappings.return_value.first.return_value = {"segment": "A"}
    else:
        result.mappings.return_value.first.return_value = None
        result.mappings.return_value.all.return_value = []
    return result


def test_customer_summary360_dry_run_aggregates_without_writing(client):
    http, db = _as_crm_read(client)
    db.execute.side_effect = _summary360_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["customer_id"] == "cust-uuid-1"
    assert body["kunden_nr"] == "TEST"
    assert body["name"] == "Test GmbH"
    assert body["offene_auftraege"] == 2
    assert body["op_saldo_eur"] == 150.5
    assert body["letzte_kontakte"][0]["id"] == "a1"
    assert body["segment"] == "A"
    assert body["route_path"] == "/crm/customers/cust-uuid-1"
    assert body["screen_id"] == "crm/customer-360"
    db.commit.assert_not_called()


def test_customer_summary360_execute_is_read_only(client):
    http, db = _as_crm_read(client)
    db.execute.side_effect = _summary360_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": CUSTOMER_OPEN,
        "mode": "execute",
        "idempotency_key": "sum-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_customer_summary360_requires_crm_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_customer_summary360_missing_customer_is_404(client):
    http, db = _as_crm_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": CUSTOMER_OPEN,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_customer_summary360_rejects_mandant_and_propose(client):
    http, db = _as_crm_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": {**CUSTOMER_OPEN, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "crm.customer.summary360",
        "parameters": CUSTOMER_OPEN,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


ORDER_STATUS = {"auftrag_nr": "SO-100"}
ORDER_ROW = {"id": "ord-1", "auftrag_nr": "SO-100", "status": "confirmed"}


def _as_sales_read(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["sales:read"],
    }
    return http, db


def _order_status_execute(sql, params=None):
    result = Mock()
    sql_s = str(sql)
    if "FROM domain_crm.sales_orders" in sql_s:
        result.mappings.return_value.first.return_value = ORDER_ROW
    elif "sales_order_items" in sql_s:
        result.mappings.return_value.first.return_value = {"offene_positionen": 3}
    else:
        result.mappings.return_value.first.return_value = None
    return result


def test_order_status_dry_run_returns_lifecycle_without_writing(client):
    http, db = _as_sales_read(client)
    db.execute.side_effect = _order_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": ORDER_STATUS,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["order_id"] == "ord-1"
    assert body["auftrag_nr"] == "SO-100"
    assert body["status"] == "confirmed"
    assert body["offene_positionen"] == 3
    assert body["naechster_schritt"] == "Lieferschein erstellen"
    assert body["route_path"] == "/sales/order-editor/ord-1"
    assert body["screen_id"] == "sales/sales-order"
    db.commit.assert_not_called()


def test_order_status_execute_is_read_only(client):
    http, db = _as_sales_read(client)
    db.execute.side_effect = _order_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": ORDER_STATUS,
        "mode": "execute",
        "idempotency_key": "ord-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_order_status_terminal_has_zero_open_lines(client):
    http, db = _as_sales_read(client)

    def execute(sql, params=None):
        result = Mock()
        result.mappings.return_value.first.return_value = {
            "id": "ord-2", "auftrag_nr": "SO-200", "status": "completed",
        }
        return result

    db.execute.side_effect = execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": {"auftrag_nr": "SO-200"},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["offene_positionen"] == 0
    assert "abgeschlossen" in body["naechster_schritt"]
    assert db.execute.call_count == 1


def test_order_status_requires_sales_read_scope(client):
    http, _, db = client  # crm:write only
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": ORDER_STATUS,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_order_status_missing_is_404(client):
    http, db = _as_sales_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": ORDER_STATUS,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_order_status_rejects_mandant_and_propose(client):
    http, db = _as_sales_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": {**ORDER_STATUS, "mandanten_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "sales.order.status",
        "parameters": ORDER_STATUS,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


OPEN_ITEMS = {"typ": "forderung", "limit": 20}
OPEN_ITEM_ROWS = [
    {
        "beleg_nr": "RE-1",
        "kunden_nr": "K-1",
        "betrag_eur": 99.5,
        "faellig_am": "2026-10-15",
        "mahnstatus": "1",
    },
]


def _as_finance_read(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["finance:read"],
    }
    return http, db


def test_open_items_list_dry_run_returns_items_without_writing(client):
    http, db = _as_finance_read(client)
    db.execute.return_value.mappings.return_value.all.return_value = OPEN_ITEM_ROWS
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": OPEN_ITEMS,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["typ"] == "forderung"
    assert body["count"] == 1
    assert body["items"][0]["beleg_nr"] == "RE-1"
    assert body["items"][0]["betrag_eur"] == 99.5
    assert body["items"][0]["mahnstatus"] == "1"
    sql = str(db.execute.call_args[0][0])
    params = db.execute.call_args[0][1]
    assert "domain_erp.offene_posten" in sql
    assert params["konto_typ"] == "debitoren"
    assert params["tenant"] == "tenant-a"
    db.commit.assert_not_called()


def test_open_items_list_verbindlichkeit_maps_konto_typ(client):
    http, db = _as_finance_read(client)
    db.execute.return_value.mappings.return_value.all.return_value = []
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": {"typ": "verbindlichkeit"},
    })
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert db.execute.call_args[0][1]["konto_typ"] == "kreditoren"


def test_open_items_list_execute_is_read_only(client):
    http, db = _as_finance_read(client)
    db.execute.return_value.mappings.return_value.all.return_value = OPEN_ITEM_ROWS
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": OPEN_ITEMS,
        "mode": "execute",
        "idempotency_key": "op-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_open_items_list_requires_finance_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": OPEN_ITEMS,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_open_items_list_rejects_mandant_and_propose(client):
    http, db = _as_finance_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": {**OPEN_ITEMS, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.open_items.list",
        "parameters": OPEN_ITEMS,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


DUNNING = {"kunden_nr": "TEST"}
DUNNING_CUSTOMER = {
    "id": "cust-uuid-1",
    "name": "Test GmbH",
    "kunden_nr": "TEST",
    "business_partner_id": "bp-1",
}


def _dunning_status_execute(sql, params=None):
    result = Mock()
    sql_s = str(sql)
    if "FROM domain_crm.customers" in sql_s and "FOR SHARE" in sql_s:
        result.mappings.return_value.first.return_value = DUNNING_CUSTOMER
    elif "MAX(COALESCE(mahn_stufe" in sql_s or "MAX(COALESCE(mahn_stufe, 0))" in sql_s:
        result.mappings.return_value.first.return_value = {"mahnstufe": 2}
    elif "gesamt_offen_eur" in sql_s and "offene_posten" in sql_s:
        result.mappings.return_value.first.return_value = {"gesamt_offen_eur": 420.75}
    elif "dunning_notices" in sql_s:
        result.mappings.return_value.all.return_value = [
            {"letzte_mahnung": "2026-09-15", "dunning_level": 3},
        ]
    else:
        result.mappings.return_value.first.return_value = None
        result.mappings.return_value.all.return_value = []
    return result


def test_dunning_status_dry_run_aggregates_without_writing(client):
    http, db = _as_finance_read(client)
    db.execute.side_effect = _dunning_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": DUNNING,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["kunden_nr"] == "TEST"
    assert body["customer_id"] == "cust-uuid-1"
    assert body["mahnstufe"] == 3
    assert body["letzte_mahnung"] == "2026-09-15"
    assert body["gesamt_offen_eur"] == 420.75
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "domain_erp.offene_posten" in joined
    assert "domain_erp.dunning_notices" in joined
    assert all(call.args[1]["tenant"] == "tenant-a" for call in db.execute.call_args_list)
    db.commit.assert_not_called()


def test_dunning_status_execute_is_read_only(client):
    http, db = _as_finance_read(client)
    db.execute.side_effect = _dunning_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": DUNNING,
        "mode": "execute",
        "idempotency_key": "dunn-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_dunning_status_requires_finance_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": DUNNING,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_dunning_status_missing_customer_is_404(client):
    http, db = _as_finance_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": DUNNING,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_dunning_status_rejects_mandant_and_propose(client):
    http, db = _as_finance_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": {**DUNNING, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "fibu.dunning.status",
        "parameters": DUNNING,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


LOT_TRACE = {"lot_id": "LOT-42"}
SILO_LOT_ROW = {
    "id": "lot-uuid-1",
    "virtual_lot_number": "LOT-42",
    "artikel_id": "ART-9",
    "quantity_tons": 1.5,
    "status": "active",
}


def _as_inventory_read(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["inventory:read"],
    }
    return http, db


def _lot_trace_execute(sql, params=None):
    result = Mock()
    sql_s = str(sql)
    if "FROM domain_inventory.silo_lots" in sql_s:
        result.mappings.return_value.first.return_value = SILO_LOT_ROW
    elif "silozelle" in sql_s and "silo_cells" in sql_s:
        result.mappings.return_value.first.return_value = {"silozelle": "ZELLE-A1"}
    elif "qs_status" in sql_s and "silo_cells" in sql_s:
        result.mappings.return_value.first.return_value = {"qs_status": "frei"}
    elif "silo_lot_movements" in sql_s:
        result.mappings.return_value.all.return_value = [
            {"typ": "in", "menge_kg": 1500.0, "notiz": "WE", "zeit": "2026-10-01"},
        ]
    else:
        result.mappings.return_value.first.return_value = None
        result.mappings.return_value.all.return_value = []
    return result


def test_lot_trace_dry_run_returns_silo_lot_without_writing(client):
    http, db = _as_inventory_read(client)
    db.execute.side_effect = _lot_trace_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": LOT_TRACE,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["lot_id"] == "lot-uuid-1"
    assert body["artikel_id"] == "ART-9"
    assert body["menge_kg"] == 1500.0
    assert body["status"] == "active"
    assert body["qs_status"] == "frei"
    assert body["silozelle"] == "ZELLE-A1"
    assert body["bewegungen"][0]["typ"] == "in"
    assert body["route_path"] == "/charge/stamm/lot-uuid-1"
    assert body["screen_id"] == "charge/stamm"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "domain_inventory.silo_lots" in joined
    assert all(call.args[1].get("tenant") == "tenant-a" for call in db.execute.call_args_list)
    db.commit.assert_not_called()


def test_lot_trace_execute_is_read_only(client):
    http, db = _as_inventory_read(client)
    db.execute.side_effect = _lot_trace_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": LOT_TRACE,
        "mode": "execute",
        "idempotency_key": "lot-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_lot_trace_requires_inventory_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": LOT_TRACE,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_lot_trace_missing_lot_is_404(client):
    http, db = _as_inventory_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": LOT_TRACE,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_lot_trace_rejects_mandant_and_propose(client):
    http, db = _as_inventory_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": {**LOT_TRACE, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "wms.lot.trace",
        "parameters": LOT_TRACE,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


CELL_STATUS = {"cell_code": "ZELLE-A1"}
SILO_CELL_ROW = {
    "id": "cell-uuid-1",
    "cell_code": "ZELLE-A1",
    "current_stock_kg": 12500.5,
    "qs_status": "frei",
    "current_material": "ART-WEIZEN",
}


def _cell_status_execute(sql, params=None):
    result = Mock()
    sql_s = str(sql)
    if "FROM domain_inventory.silo_cells" in sql_s:
        result.mappings.return_value.first.return_value = SILO_CELL_ROW
    elif "flush_required" in sql_s and "material_flow_edges" in sql_s:
        result.mappings.return_value.first.return_value = {"flush_required": True}
    else:
        result.mappings.return_value.first.return_value = None
        result.mappings.return_value.all.return_value = []
    return result


def test_cell_status_dry_run_returns_cell_without_writing(client):
    http, db = _as_inventory_read(client)
    db.execute.side_effect = _cell_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": CELL_STATUS,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["cell_code"] == "ZELLE-A1"
    assert body["current_stock_kg"] == 12500.5
    assert body["qs_status"] == "frei"
    assert body["current_material"] == "ART-WEIZEN"
    assert body["flush_required"] is True
    assert body["cell_id"] == "cell-uuid-1"
    assert body["route_path"] == "/lager/silo-zellen/cell-uuid-1"
    assert body["screen_id"] == "lager/silo-cell"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "domain_inventory.silo_cells" in joined
    assert all(call.args[1].get("tenant") == "tenant-a" for call in db.execute.call_args_list)
    db.commit.assert_not_called()


def test_cell_status_execute_is_read_only(client):
    http, db = _as_inventory_read(client)
    db.execute.side_effect = _cell_status_execute
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": CELL_STATUS,
        "mode": "execute",
        "idempotency_key": "cell-once",
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "execute"
    joined = "\n".join(str(call.args[0]) for call in db.execute.call_args_list)
    assert "mcp_tool_executions" not in joined
    assert "INSERT INTO" not in joined
    db.commit.assert_not_called()


def test_cell_status_requires_inventory_read_scope(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": CELL_STATUS,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_cell_status_missing_cell_is_404(client):
    http, db = _as_inventory_read(client)
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": CELL_STATUS,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_cell_status_rejects_mandant_and_propose(client):
    http, db = _as_inventory_read(client)
    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": {**CELL_STATUS, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422
    propose = http.post("/mcp/tools/call", json={
        "tool_name": "wms.cell.status",
        "parameters": CELL_STATUS,
        "mode": "propose",
    })
    assert propose.status_code == 422
    db.execute.assert_not_called()


def _as_scopes(client, scopes):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {**USER, "scopes": list(scopes)}
    return http, db


def _rows_execute(rows):
    def execute(sql, params=None):
        result = Mock()
        result.mappings.return_value.all.return_value = rows
        result.mappings.return_value.first.return_value = rows[0] if rows else None
        return result
    return execute


def test_document_search_happy_and_guards(client):
    http, db = _as_scopes(client, ["nachweisraum:read"])
    db.execute.side_effect = _rows_execute([
        {"dokument_id": "d1", "titel": "LS", "status": "EINGEGANGEN", "erstellt_am": "2026-10-01"},
    ])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "dms.document.search",
        "parameters": {"limit": 10},
    })
    assert ok.status_code == 200
    assert ok.json()["count"] == 1
    assert ok.json()["items"][0]["dokument_id"] == "d1"
    assert ok.json()["items"][0]["route_path"] == "/docflow/nachweisraum/d1"
    assert ok.json()["items"][0]["screen_id"] == "docflow/nachweisraum"
    db.commit.assert_not_called()
    http2, db2 = _as_scopes(client, ["crm:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "dms.document.search", "parameters": {},
    }).status_code == 403
    http3, db3 = _as_scopes(client, ["nachweisraum:read"])
    db3.execute.reset_mock()
    assert http3.post("/mcp/tools/call", json={
        "tool_name": "dms.document.search",
        "parameters": {"tenant_id": "x"},
    }).status_code == 422
    db3.execute.assert_not_called()


def test_document_search_by_dokument_id_returns_route(client):
    http, db = _as_scopes(client, ["nachweisraum:read"])
    db.execute.side_effect = _rows_execute([
        {"dokument_id": "doc-1", "titel": "Rechnung", "status": "EINGEGANGEN", "erstellt_am": "2026-10-01"},
    ])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "dms.document.search",
        "parameters": {"dokument_id": "doc-1", "limit": 1},
    })
    assert ok.status_code == 200
    body = ok.json()
    assert body["items"][0]["dokument_id"] == "doc-1"
    assert body["items"][0]["route_path"] == "/docflow/nachweisraum/doc-1"
    assert body["items"][0]["screen_id"] == "docflow/nachweisraum"
    db.commit.assert_not_called()


def test_document_search_missing_dokument_id_is_404(client):
    http, db = _as_scopes(client, ["nachweisraum:read"])
    db.execute.side_effect = _rows_execute([])
    response = http.post("/mcp/tools/call", json={
        "tool_name": "dms.document.search",
        "parameters": {"dokument_id": "missing"},
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_gobd_export_status_happy_and_404(client):
    http, db = _as_scopes(client, ["nachweisraum:read"])
    db.execute.side_effect = _rows_execute([{
        "export_id": "ex1", "status": "OFFEN", "dokument_anzahl": 3, "pruefprotokoll": "p1",
    }])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "dms.gobd.export_status",
        "parameters": {"export_id": "ex1"},
    })
    assert ok.status_code == 200
    assert ok.json()["export_id"] == "ex1"
    assert ok.json()["dokument_anzahl"] == 3
    assert ok.json()["route_path"] == "/docflow/gobd-export/ex1"
    assert ok.json()["screen_id"] == "docflow/gobd-export"
    db.commit.assert_not_called()
    db.execute.side_effect = None
    db.execute.return_value.mappings.return_value.first.return_value = None
    assert http.post("/mcp/tools/call", json={
        "tool_name": "dms.gobd.export_status",
        "parameters": {"export_id": "missing"},
    }).status_code == 404


def test_agrar_contract_and_weighing_happy_and_guards(client):
    http, db = _as_scopes(client, ["agrar:read"])
    db.execute.side_effect = _rows_execute([{
        "kontrakt_id": "c1", "ware": "ART-1", "menge_t": 12.5, "preis_eur": 210.0, "status": "open",
    }])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "agrar.contract.get",
        "parameters": {"kontrakt_id": "K-1"},
    })
    assert ok.status_code == 200
    assert ok.json()["kontrakt_id"] == "c1"
    assert ok.json()["menge_t"] == 12.5
    assert ok.json()["route_path"] == "/agrar/kontrakt/c1"
    assert ok.json()["screen_id"] == "agrar/kontrakte"
    assert http.post("/mcp/tools/call", json={
        "tool_name": "agrar.contract.get",
        "parameters": {"kontrakt_id": "K-1", "tenant_id": "other"},
    }).status_code == 422
    db.execute.side_effect = _rows_execute([{
        "ticket_id": "t1", "partie_id": "p1", "brutto_kg": 1000.0, "netto_kg": 980.0, "erstellt_am": "2026-10-01",
    }])
    tickets = http.post("/mcp/tools/call", json={
        "tool_name": "agrar.weighing_ticket.list",
        "parameters": {},
    })
    assert tickets.status_code == 200
    assert tickets.json()["count"] == 1
    assert tickets.json()["items"][0]["route_path"] == "/waage/wiegeschein/t1"
    assert tickets.json()["items"][0]["screen_id"] == "waage/wiegeschein"
    by_id = http.post("/mcp/tools/call", json={
        "tool_name": "agrar.weighing_ticket.list",
        "parameters": {"ticket_id": "t1", "limit": 1},
    })
    assert by_id.status_code == 200
    assert by_id.json()["items"][0]["ticket_id"] == "t1"
    db.execute.side_effect = _rows_execute([])
    missing = http.post("/mcp/tools/call", json={
        "tool_name": "agrar.weighing_ticket.list",
        "parameters": {"ticket_id": "missing"},
    })
    assert missing.status_code == 404
    db.commit.assert_not_called()
    http2, _ = _as_scopes(client, ["lager:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "agrar.contract.get", "parameters": {"kontrakt_id": "K-1"},
    }).status_code == 403


def test_lager_bestand_and_inventur_happy_and_guards(client):
    http, db = _as_scopes(client, ["lager:read"])
    db.execute.side_effect = _rows_execute([{
        "artikel_id": "a1", "menge": 40.0, "einheit": "kg", "reserviert": 5.0, "verfuegbar": 35.0,
    }])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "lager.bestand.get",
        "parameters": {"artikel_id": "ART-1"},
    })
    assert ok.status_code == 200
    assert ok.json()["verfuegbar"] == 35.0
    assert ok.json()["artikel_id"] == "a1"
    assert ok.json()["route_path"] == "/lager/artikel/a1"
    assert ok.json()["screen_id"] == "lager/article-stock"
    db.commit.assert_not_called()

    def inventur_execute(sql, params=None):
        result = Mock()
        sql_s = str(sql)
        if "offene_inventuren" in sql_s:
            result.mappings.return_value.first.return_value = {"offene_inventuren": 2}
        elif "differenzen_eur" in sql_s:
            result.mappings.return_value.first.return_value = {"differenzen_eur": 15.5}
        elif "letzter_abschluss" in sql_s:
            result.mappings.return_value.first.return_value = {"letzter_abschluss": "2026-09-01"}
        else:
            result.mappings.return_value.first.return_value = None
        return result

    db.execute.side_effect = inventur_execute
    inv = http.post("/mcp/tools/call", json={
        "tool_name": "lager.inventur.status",
        "parameters": {},
    })
    assert inv.status_code == 200
    assert inv.json()["offene_inventuren"] == 2
    assert inv.json()["differenzen_eur"] == 15.5
    assert http.post("/mcp/tools/call", json={
        "tool_name": "lager.bestand.get",
        "parameters": {"artikel_id": "ART-1", "tenant_id": "x"},
    }).status_code == 422


def test_bestellung_status_dry_run_returns_route(client):
    http, db = _as_scopes(client, ["einkauf:read"])
    db.execute.return_value.mappings.return_value.first.return_value = {
        "bestellung_id": "po-uuid-1",
        "bestellnummer": "BE-100",
        "status": "offen",
        "lieferant": "Mueller",
    }
    response = http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.status",
        "parameters": {"bestellung_id": "BE-100"},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["bestellung_id"] == "po-uuid-1"
    assert body["bestellnummer"] == "BE-100"
    assert body["route_path"] == "/einkauf/bestellung/po-uuid-1"
    assert body["screen_id"] == "einkauf/purchase-order"
    db.commit.assert_not_called()


def test_bestellung_status_missing_is_404(client):
    http, db = _as_scopes(client, ["einkauf:read"])
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.status",
        "parameters": {"bestellung_id": "missing"},
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_bestellung_status_requires_einkauf_read(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.status",
        "parameters": {"bestellung_id": "BE-100"},
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_bestellung_list_happy_and_guards(client):
    http, db = _as_scopes(client, ["einkauf:read"])
    db.execute.side_effect = _rows_execute([{
        "bestellung_id": "b1", "lieferant": "Mueller", "status": "offen",
        "liefertermin": "2026-10-20", "wert_eur": 99.0,
    }])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.list",
        "parameters": {"status": "offen"},
    })
    assert ok.status_code == 200
    assert ok.json()["items"][0]["bestellung_id"] == "b1"
    assert ok.json()["items"][0]["route_path"] == "/einkauf/bestellung/b1"
    assert ok.json()["items"][0]["screen_id"] == "einkauf/purchase-order"
    db.commit.assert_not_called()
    http2, _ = _as_scopes(client, ["crm:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.list", "parameters": {},
    }).status_code == 403


def test_compliance_gate_status_honest_empty_signals(client):
    http, db = _as_scopes(client, ["compliance:read"])
    db.execute.side_effect = _rows_execute([])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "compliance.gate.status",
        "parameters": {"gate_typ": "all"},
    })
    assert ok.status_code == 200
    body = ok.json()
    assert body["count"] == 4
    assert all(item["status"] == "keine_daten" for item in body["items"])
    db.commit.assert_not_called()
    assert http.post("/mcp/tools/call", json={
        "tool_name": "compliance.gate.status",
        "parameters": {"tenant_id": "x"},
    }).status_code == 422


def test_proposal_list_happy_and_guards(client):
    http, db = _as_scopes(client, ["agent:read"])
    db.execute.side_effect = _rows_execute([{
        "proposal_id": "p1", "action_type": "crm.contact.log",
        "approval_status": "pending", "created_at": "2026-10-01",
    }])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "agent.proposal.list",
        "parameters": {"status": "pending"},
    })
    assert ok.status_code == 200
    assert ok.json()["items"][0]["proposal_id"] == "p1"
    db.commit.assert_not_called()
    http2, _ = _as_scopes(client, ["crm:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "agent.proposal.list", "parameters": {},
    }).status_code == 403


LEAD_QUALIFY = {"lead_id": "lead-1", "customer_id": "cust-1"}
PO_SEND = {"bestellung_id": "po-1", "versand_art": "email"}


def test_lead_qualify_dry_run_and_guards(client):
    http, _, db = client  # crm:write
    with patch("app.services.mcp_execution_service.crm_lead_service.qualification_inputs") as qi:
        qi.return_value = ({"id": "lead-1"}, {"id": "cust-1", "company_name": "Test"})
        db.execute.return_value.mappings.return_value.first.return_value = {"id": "cust-1"}
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "crm.lead.qualify",
            "parameters": LEAD_QUALIFY,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["customer_id"] == "cust-1"
    db.commit.assert_not_called()

    missing = http.post("/mcp/tools/call", json={
        "tool_name": "crm.lead.qualify",
        "parameters": {"lead_id": "lead-1"},
    })
    assert missing.status_code == 422

    forbidden = http.post("/mcp/tools/call", json={
        "tool_name": "crm.lead.qualify",
        "parameters": {**LEAD_QUALIFY, "tenant_id": "other"},
    })
    assert forbidden.status_code == 422

    http2, _ = _as_scopes(client, ["crm:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "crm.lead.qualify", "parameters": LEAD_QUALIFY,
    }).status_code == 403


def test_lead_qualify_execute_writes_with_idempotency(client):
    http, _, db = client
    db.execute.return_value.mappings.return_value.first.return_value = {"id": "cust-1"}
    with patch("app.services.mcp_execution_service.crm_lead_service.qualification_inputs") as qi, \
         patch("app.services.mcp_execution_service.crm_lead_service.qualify") as qualify, \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-1"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        qi.return_value = ({"id": "lead-1"}, {"id": "cust-1"})
        qualify.return_value = "opp-99"
        response = http.post("/mcp/tools/call", json={
            "tool_name": "crm.lead.qualify",
            "parameters": LEAD_QUALIFY,
            "mode": "execute",
            "idempotency_key": "lead-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "execute"
    assert body["opportunity_id"] == "opp-99"
    assert body["auditEntryId"] == "audit-1"
    qualify.assert_called_once()
    db.commit.assert_called()


def test_bestellung_versenden_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "po-uuid", "bestellnummer": "EK-1", "status": "freigegeben",
    }
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.versenden",
        "parameters": PO_SEND,
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["bestellung_id"] == "po-uuid"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.versenden",
        "parameters": {**PO_SEND, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["einkauf:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "einkauf.bestellung.versenden", "parameters": PO_SEND,
    }).status_code == 403


def test_bestellung_versenden_execute_calls_service(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "po-uuid", "bestellnummer": "EK-1", "status": "freigegeben",
    }
    fake_svc = Mock()
    fake_svc.versende_bestellung_svc.return_value = {
        "bestellung_id": "po-uuid",
        "bestellnummer": "EK-1",
        "versand": {"status": "gesendet", "versand_art": "email"},
    }
    with patch("app.services.mcp_execution_service.ProcurementService", return_value=fake_svc), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-po"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "einkauf.bestellung.versenden",
            "parameters": PO_SEND,
            "mode": "execute",
            "idempotency_key": "po-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["versand_status"] == "gesendet"
    assert body["bestellnummer"] == "EK-1"
    fake_svc.versende_bestellung_svc.assert_called_once()
    db.commit.assert_called()


ANGEBOT_BESTELLEN = {"angebot_id": "ang-1"}
AVIS_WE = {"avis_id": "avis-1", "lager_id": "lager-1", "lieferschein_nr": "LS-99"}
STORNO_MOV = {"movement_id": "mov-1", "begruendung": "Fehlbuchung"}


def test_angebot_bestellen_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    row = Mock()
    row._mapping = {
        "id": "ang-uuid", "angebots_nummer": "A-1", "status": "ANGEBOTEN",
    }
    fake = Mock()
    fake._load_angebot_raw_row.return_value = row
    db.execute.return_value.scalar.return_value = 2
    with patch("app.services.mcp_execution_service.EinkaufCompatService", return_value=fake):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "einkauf.angebot.bestellen",
            "parameters": ANGEBOT_BESTELLEN,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["angebot_id"] == "ang-uuid"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.angebot.bestellen",
        "parameters": {**ANGEBOT_BESTELLEN, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["einkauf:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "einkauf.angebot.bestellen", "parameters": ANGEBOT_BESTELLEN,
    }).status_code == 403


def test_angebot_bestellen_execute(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    row = Mock()
    row._mapping = {"id": "ang-uuid", "angebots_nummer": "A-1", "status": "ANGEBOTEN"}
    fake_load = Mock()
    fake_load._load_angebot_raw_row.return_value = row
    fake_exec = Mock()
    async def _convert(_aid):
        return {"purchaseOrderId": "po-9", "purchaseOrderNumber": "EK-9"}
    fake_exec.convert_angebot_to_order = _convert
    db.execute.return_value.scalar.return_value = 1
    with patch("app.services.mcp_execution_service.EinkaufCompatService", side_effect=[fake_load, fake_exec]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-ang"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "einkauf.angebot.bestellen",
            "parameters": ANGEBOT_BESTELLEN,
            "mode": "execute",
            "idempotency_key": "ang-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["bestellnummer"] == "EK-9"
    assert body["bestellung_id"] == "po-9"
    db.commit.assert_called()


def test_anlieferavis_wareneingang_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    with patch("app.services.mcp_execution_service.pruefe_wareneingang", return_value=[{"id": "p1"}]):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "einkauf.anlieferavis.wareneingang",
            "parameters": AVIS_WE,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["positionen_offen"] == 1
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "einkauf.anlieferavis.wareneingang",
        "parameters": {**AVIS_WE, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["einkauf:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "einkauf.anlieferavis.wareneingang", "parameters": AVIS_WE,
    }).status_code == 403


def test_anlieferavis_wareneingang_execute(client):
    http, db = _as_scopes(client, ["einkauf:write"])
    with patch("app.services.mcp_execution_service.pruefe_wareneingang", return_value=[{"id": "p1"}]), \
         patch("app.services.mcp_execution_service.buche_wareneingang_aus_avis", return_value={
             "avis_id": "avis-1", "bestellung_id": "po-1", "bestellnummer": "EK-1",
             "positionen": 1, "lieferschein_nr": "LS-99",
         }), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-we"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "einkauf.anlieferavis.wareneingang",
            "parameters": AVIS_WE,
            "mode": "execute",
            "idempotency_key": "we-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["bestellnummer"] == "EK-1"
    assert body["positionen"] == 1
    db.commit.assert_called()


def test_stock_movement_stornieren_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["lager:write"])
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "mov-1", "movement_type": "einlagerung", "quantity": 10,
        "source_document_type": "WARENEINGANG", "article_id": "art-1", "warehouse_id": "wh-1",
    }
    with patch("app.services.mcp_execution_service.signed_quantity", return_value=10.0), \
         patch("app.services.mcp_execution_service.current_stock", return_value=50.0):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "lager.stock_movement.stornieren",
            "parameters": STORNO_MOV,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["stock_effect"] == 10.0
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "lager.stock_movement.stornieren",
        "parameters": {**STORNO_MOV, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["lager:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "lager.stock_movement.stornieren", "parameters": STORNO_MOV,
    }).status_code == 403


def test_stock_movement_stornieren_execute(client):
    http, db = _as_scopes(client, ["lager:write"])
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "mov-1", "movement_type": "einlagerung", "quantity": 10,
        "source_document_type": "WARENEINGANG", "article_id": "art-1", "warehouse_id": "wh-1",
    }
    with patch("app.services.mcp_execution_service.signed_quantity", return_value=10.0), \
         patch("app.services.mcp_execution_service.current_stock", return_value=50.0), \
         patch("app.services.mcp_execution_service.storno_korrektur", return_value={
             "id": "storno-1", "movement_type": "ABGANG", "quantity": 10,
         }), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-st"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "lager.stock_movement.stornieren",
            "parameters": STORNO_MOV,
            "mode": "execute",
            "idempotency_key": "storno-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["storno_movement_id"] == "storno-1"
    assert body["movement_type"] == "ABGANG"
    db.commit.assert_called()


RATION_TR = {"ration_id": "rat-1", "action_key": "submit_review"}


def test_ration_transition_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake = Mock()
    fake.get_ration.return_value = {
        "latest_version_id": "ver-1",
        "latest_status": "draft",
        "latest_readiness_blockers": 0,
    }
    with patch("app.services.mcp_execution_service.RationLifecycleService", return_value=fake):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.ration.transition",
            "parameters": RATION_TR,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["to_status"] == "in_review"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "agrar.ration.transition",
        "parameters": {**RATION_TR, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["agrar:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "agrar.ration.transition", "parameters": RATION_TR,
    }).status_code == 403


def test_ration_transition_execute(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake_load = Mock()
    fake_load.get_ration.return_value = {
        "latest_version_id": "ver-1",
        "latest_status": "draft",
        "latest_readiness_blockers": 0,
    }
    fake_exec = Mock()
    fake_exec.transition.return_value = {
        "status": "in_review", "superseded_version_ids": [],
    }
    with patch("app.services.mcp_execution_service.RationLifecycleService", side_effect=[fake_load, fake_exec]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-rat"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.ration.transition",
            "parameters": RATION_TR,
            "mode": "execute",
            "idempotency_key": "rat-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["to_status"] == "in_review"
    assert body["version_id"] == "ver-1"
    fake_exec.transition.assert_called_once()
    db.commit.assert_called()


def test_ration_transition_retire_requires_reason(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake = Mock()
    fake.get_ration.return_value = {
        "latest_version_id": "ver-1",
        "latest_status": "active",
        "latest_readiness_blockers": 0,
    }
    with patch("app.services.mcp_execution_service.RationLifecycleService", return_value=fake):
        missing = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.ration.transition",
            "parameters": {"ration_id": "rat-1", "action_key": "retire"},
        })
    assert missing.status_code == 422


HANDOFF = {
    "plan_version_id": "pv-1", "feed_id": "feed-1",
    "reason": "Unterdeckung fuer naechste 30 Tage melden.",
}
MEASURE = {
    "actual_component_id": "comp-1",
    "title": "Anteil korrigieren",
    "reason": "Abweichung kritisch, Massnahme noetig.",
    "due_date": "2030-01-15",
}


def test_feeding_supply_handoff_dry_run_and_guards(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake = Mock()
    fake.project.return_value = [{
        "plan_version_id": "pv-1", "feed_id": "feed-1", "group_id": "g1",
        "shortage_kg": 100, "suggested_order_kg": 120,
    }]
    with patch("app.services.mcp_execution_service.FeedingSupplyService", return_value=fake):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feeding.supply_handoff", "parameters": HANDOFF,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["shortage_kg"] == 100
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "agrar.feeding.supply_handoff",
        "parameters": {**HANDOFF, "tenant_id": "x"},
    }).status_code == 422

    http2, _ = _as_scopes(client, ["agrar:read"])
    assert http2.post("/mcp/tools/call", json={
        "tool_name": "agrar.feeding.supply_handoff", "parameters": HANDOFF,
    }).status_code == 403


def test_feeding_supply_handoff_execute(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake_load = Mock()
    fake_load.project.return_value = [{
        "plan_version_id": "pv-1", "feed_id": "feed-1", "group_id": "g1",
        "shortage_kg": 100, "suggested_order_kg": 120,
    }]
    fake_exec = Mock()
    fake_exec.create_handoff.return_value = {"id": "ho-1"}
    with patch("app.services.mcp_execution_service.FeedingSupplyService", side_effect=[fake_load, fake_exec]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-ho"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feeding.supply_handoff",
            "parameters": HANDOFF,
            "mode": "execute",
            "idempotency_key": "ho-once",
        })
    assert response.status_code == 200
    assert response.json()["handoff_id"] == "ho-1"
    fake_exec.create_handoff.assert_called_once()
    db.commit.assert_called()


def test_feeding_actual_measure_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["agrar:write"])
    db.execute.return_value.mappings.return_value.all.return_value = [{"id": "g1"}]
    fake = Mock()
    fake.findings.return_value = [{
        "actual_component_id": "comp-1", "severity": "critical", "group_id": "g1",
    }]
    with patch("app.services.mcp_execution_service.FeedingActualMeasureService", return_value=fake):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feeding.actual_measure", "parameters": MEASURE,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["severity"] == "critical"
    db.commit.assert_not_called()

    fake_exec = Mock()
    fake_exec.create_measure.return_value = {"id": "m-1"}
    fake_load = Mock()
    fake_load.findings.return_value = [{
        "actual_component_id": "comp-1", "severity": "critical", "group_id": "g1",
    }]
    with patch("app.services.mcp_execution_service.FeedingActualMeasureService", side_effect=[fake_load, fake_exec]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-m"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feeding.actual_measure",
            "parameters": MEASURE,
            "mode": "execute",
            "idempotency_key": "m-once",
        })
    assert response.status_code == 200
    assert response.json()["measure_id"] == "m-1"
    db.commit.assert_called()


THRESHOLD = {
    "feed_class": "forage", "warning_pct": 5, "critical_pct": 15,
    "valid_from": "2030-01-01", "reason": "Schwellen fuer Heu saisonal anpassen.",
}
ANALYSIS_TR = {
    "analysis_id": "an-1", "action_key": "reject",
    "reason": "Plausibilitaet nicht gegeben.",
}
REKLAMATION = {"reklamation_id": "rek-1", "kommentar": "Abgeschlossen nach Pruefung."}


def test_feeding_configure_threshold_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["agrar:write"])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "agrar.feeding.configure_threshold", "parameters": THRESHOLD,
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "agrar.feeding.configure_threshold",
        "parameters": {**THRESHOLD, "tenant_id": "x"},
    }).status_code == 422

    fake = Mock()
    fake.create_policy.return_value = {"id": "pol-1", "version": 2}
    with patch("app.services.mcp_execution_service.FeedingActualMeasureService", return_value=fake), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-th"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feeding.configure_threshold",
            "parameters": THRESHOLD,
            "mode": "execute",
            "idempotency_key": "th-once",
        })
    assert response.status_code == 200
    assert response.json()["policy_id"] == "pol-1"
    assert response.json()["version"] == 2
    db.commit.assert_called()


def test_feed_analysis_transition_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["agrar:write"])
    fake = Mock()
    fake.get_analysis.return_value = {
        "status": "draft", "revision": 1, "findings": [],
    }
    with patch("app.services.mcp_execution_service.FeedingFeedAnalysisService", return_value=fake):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feed_analysis.transition", "parameters": ANALYSIS_TR,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["to_status"] == "rejected"
    db.commit.assert_not_called()

    fake_load = Mock()
    fake_load.get_analysis.return_value = {
        "status": "draft", "revision": 1, "findings": [],
    }
    fake_exec = Mock()
    fake_exec.transition.return_value = {"status": "rejected", "revision": 2}
    with patch("app.services.mcp_execution_service.FeedingFeedAnalysisService", side_effect=[fake_load, fake_exec]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-an"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "agrar.feed_analysis.transition",
            "parameters": ANALYSIS_TR,
            "mode": "execute",
            "idempotency_key": "an-once",
        })
    assert response.status_code == 200
    assert response.json()["to_status"] == "rejected"
    fake_exec.transition.assert_called_once()
    db.commit.assert_called()


def test_reklamation_abschliessen_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["quality:write"])
    zeile = Mock()
    zeile.status = "anerkannt"
    with patch("app.services.mcp_execution_service._query_reklamation", return_value=zeile), \
         patch("app.services.mcp_execution_service.ReklamationZustandsmaschine.pruefe_statuswechsel"):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "qualitaet.reklamation.abschliessen", "parameters": REKLAMATION,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["to_status"] == "geschlossen"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "qualitaet.reklamation.abschliessen",
        "parameters": {**REKLAMATION, "tenant_id": "x"},
    }).status_code == 422

    with patch("app.services.mcp_execution_service._query_reklamation", return_value=zeile), \
         patch("app.services.mcp_execution_service.ReklamationZustandsmaschine.pruefe_statuswechsel"), \
         patch("app.services.mcp_execution_service.transition_status"), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-rek"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "qualitaet.reklamation.abschliessen",
            "parameters": REKLAMATION,
            "mode": "execute",
            "idempotency_key": "rek-once",
        })
    assert response.status_code == 200
    assert response.json()["status"] == "geschlossen"
    db.commit.assert_called()


SYNC = {"reason": "Leitstand nach Produktionslauf synchronisieren."}


def test_produktion_control_sync_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["ops:write"])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "produktion.control.sync", "parameters": SYNC,
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "produktion.control.sync",
        "parameters": {**SYNC, "tenant_id": "x"},
    }).status_code == 422

    fake = Mock()
    fake.sync_production_orders.return_value = {"synchronized": 3}
    with patch("app.services.mcp_execution_service.ProductionControlService", return_value=fake), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-sync"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "produktion.control.sync",
            "parameters": SYNC,
            "mode": "execute",
            "idempotency_key": "sync-once",
        })
    assert response.status_code == 200
    assert response.json()["synchronized"] == 3
    fake.sync_production_orders.assert_called_once()
    db.commit.assert_called()


def test_planung_calendar_reproject_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["planung:write"])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "planung.calendar.reproject", "parameters": {},
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["horizon_days"] == 120
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "planung.calendar.reproject",
        "parameters": {"horizon_days": 30, "tenant_id": "x"},
    }).status_code == 422

    fake = Mock()
    fake.reproject.return_value = {"projected": 12, "sources": {"orders": 12}}
    with patch("app.services.mcp_execution_service.CalendarProjectionService", return_value=fake), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-cal"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "planung.calendar.reproject",
            "parameters": {"horizon_days": 30},
            "mode": "execute",
            "idempotency_key": "cal-once",
        })
    assert response.status_code == 200
    assert response.json()["projected"] == 12
    assert response.json()["horizon_days"] == 30
    fake.reproject.assert_called_once()
    db.commit.assert_called()


def test_mobile_sync_process_pending_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["mobile:write"])
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "mobile.sync.process_pending", "parameters": {},
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["proposedChanges"]["limit"] == 50
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "mobile.sync.process_pending",
        "parameters": {"limit": 10, "tenant_id": "x"},
    }).status_code == 422

    fake = Mock()
    fake.process_pending.return_value = {
        "processed": 4, "failed": 1, "skipped": 0, "total": 5,
    }
    with patch("app.services.mcp_execution_service.MobileSyncService", return_value=fake), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-mde"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "mobile.sync.process_pending",
            "parameters": {"limit": 10, "reason": "MDE-Batch nach Schichtende."},
            "mode": "execute",
            "idempotency_key": "mde-once",
        })
    assert response.status_code == 200
    assert response.json()["processed"] == 4
    assert response.json()["failed"] == 1
    fake.process_pending.assert_called_once()
    db.commit.assert_called()


def test_activity_dry_run_is_tenant_scoped_and_non_mutating(client):
    http, _, db = client
    db.execute.return_value.mappings.return_value.first.return_value = {
        "id": "c1", "name": "Test GmbH", "kunden_nr": "TEST",
    }
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.activity.create",
        "parameters": ACTIVITY,
    })
    assert response.status_code == 200
    assert response.json()["mode"] == "dryRun"
    sql = str(db.execute.call_args[0][0])
    assert "domain_crm.customers" in sql
    assert "tenant_id" in sql
    db.commit.assert_not_called()


def test_activity_rejects_foreign_mandant_parameter(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.activity.create",
        "parameters": {**ACTIVITY, "mandanten_id": "other"},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_activity_cross_tenant_customer_is_not_found(client):
    http, _, db = client
    db.execute.return_value.mappings.return_value.first.return_value = None
    response = http.post("/mcp/tools/call", json={
        "tool_name": "crm.activity.create",
        "parameters": ACTIVITY,
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_invoice_post_requires_approved_proposal(client):
    http, db = _as_sales(client)
    db.execute.return_value.mappings.return_value.first.return_value = {
        "proposal_id": "p1",
        "action_type": "rechnung_vorschlag",
        "approval_status": "pending",
        "risk_level": "high",
        "context_snapshot": {"lieferschein_nr": "LS-1", "rechnungsdatum": "2026-09-29"},
        "execution_result": None,
    }
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.post",
        "parameters": {"proposal_id": "p1"},
    })
    assert response.status_code == 409
    db.commit.assert_not_called()


def test_invoice_post_dry_run_reads_approved_proposal_without_writing(client):
    http, db = _as_sales(client)
    db.execute.return_value.mappings.return_value.first.return_value = {
        "proposal_id": "p1",
        "action_type": "rechnung_vorschlag",
        "approval_status": "approved",
        "risk_level": "high",
        "context_snapshot": {
            "lieferschein_nr": "LS-1",
            "rechnungsdatum": "2026-09-29",
            "betrag_netto": 10.5,
            "mwst": 2.0,
            "positionen": 1,
        },
        "execution_result": None,
    }
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.post",
        "parameters": {"proposal_id": "p1"},
    })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["posted"] is False
    assert body["lieferschein_nr"] == "LS-1"
    db.commit.assert_not_called()


def test_invoice_post_rejects_client_approval_flag(client):
    http, db = _as_sales(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "sales.invoice.post",
        "parameters": {"proposal_id": "p1", "approval_granted": True},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


AP_INVOICE = {"invoice_id": "AP-100"}
AP_INVOICE_ROW = {
    "number": "AP-100",
    "status": "ZUR_FREIGABE",
    "totalGross": 120.5,
    "tenantId": "tenant-a",
}


def _as_finance_write(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["finance:write"],
    }
    return http, db


def test_ap_propose_scope_is_required(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "finance.ap_invoice.propose",
        "parameters": AP_INVOICE,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_ap_propose_execute_is_not_wired(client):
    http, db = _as_finance_write(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "finance.ap_invoice.propose",
        "parameters": AP_INVOICE,
        "mode": "execute",
    })
    assert response.status_code == 501
    db.commit.assert_not_called()


def test_ap_propose_rejects_client_approval_flag(client):
    http, db = _as_finance_write(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "finance.ap_invoice.propose",
        "parameters": {**AP_INVOICE, "approval_granted": True},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_ap_propose_dry_run_reads_invoice_without_writing(client):
    http, db = _as_finance_write(client)
    with patch("app.services.mcp_execution_service._load_ap_invoice", return_value=AP_INVOICE_ROW):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "finance.ap_invoice.propose",
            "parameters": AP_INVOICE,
        })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["approved"] is False
    assert body["invoice_id"] == "AP-100"
    assert body["brutto_eur"] == 120.5
    assert body["route_path"] == "/finance/ap-invoice/AP-100"
    assert body["screen_id"] == "finance/ap-invoice"
    assert "entwurf_id" not in body
    db.commit.assert_not_called()


def test_ap_propose_stores_pending_proposal_and_does_not_freigeben(client):
    http, db = _as_finance_write(client)
    statements: list[str] = []

    def execute(sql, params=None):
        statements.append(str(sql))
        result = Mock()
        result.mappings.return_value.first.return_value = None
        return result

    db.execute.side_effect = execute
    with patch("app.services.mcp_execution_service._load_ap_invoice", return_value=AP_INVOICE_ROW), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-ap"):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "finance.ap_invoice.propose",
            "parameters": AP_INVOICE,
            "mode": "propose",
            "idempotency_key": "ap-once",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is False
    assert body["approval_status"] == "pending"
    assert body["entwurf_id"]
    joined = "\n".join(statements)
    assert "agent_proposals" in joined
    assert "ap_invoice_freigabe" in joined
    assert "'pending'" in joined
    db.commit.assert_called_once()


def test_ap_freigeben_requires_approved_proposal(client):
    http, db = _as_finance_write(client)
    db.execute.return_value.mappings.return_value.first.return_value = {
        "proposal_id": "p-ap",
        "action_type": "ap_invoice_freigabe",
        "approval_status": "pending",
        "risk_level": "high",
        "context_snapshot": {"invoice_id": "AP-100"},
        "execution_result": None,
    }
    response = http.post("/mcp/tools/call", json={
        "tool_name": "finance.ap_invoice.freigeben",
        "parameters": {"proposal_id": "p-ap"},
    })
    assert response.status_code == 409
    db.commit.assert_not_called()


def test_ap_freigeben_dry_run_reads_approved_proposal_without_writing(client):
    http, db = _as_finance_write(client)
    db.execute.return_value.mappings.return_value.first.return_value = {
        "proposal_id": "p-ap",
        "action_type": "ap_invoice_freigabe",
        "approval_status": "approved",
        "risk_level": "high",
        "context_snapshot": {"invoice_id": "AP-100"},
        "execution_result": None,
    }
    with patch("app.services.mcp_execution_service._load_ap_invoice", return_value=AP_INVOICE_ROW):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "finance.ap_invoice.freigeben",
            "parameters": {"proposal_id": "p-ap"},
        })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["approved"] is False
    assert body["invoice_id"] == "AP-100"
    assert body["route_path"] == "/finance/ap-invoice/AP-100"
    db.commit.assert_not_called()


def test_ap_freigeben_execute_calls_real_endpoint_after_approval(client):
    http, db = _as_finance_write(client)
    db.execute.return_value.mappings.return_value.first.return_value = {
        "proposal_id": "p-ap",
        "action_type": "ap_invoice_freigabe",
        "approval_status": "approved",
        "risk_level": "high",
        "context_snapshot": {"invoice_id": "AP-100"},
        "execution_result": None,
    }
    approved_row = {**AP_INVOICE_ROW, "status": "FREIGEGEBEN"}

    async def fake_approve(invoice_id, approved_by=None, db=None, tenant_id=None, user=None):
        assert invoice_id == "AP-100"
        assert tenant_id == "tenant-a"
        assert user["sub"] == USER["sub"]
        return {"status": "ok"}

    with patch("app.services.mcp_execution_service._load_ap_invoice", side_effect=[AP_INVOICE_ROW, approved_row]), \
         patch("app.services.mcp_execution_service.Session"), \
         patch("app.api.v1.endpoints.ap_invoices.approve_ap_invoice", side_effect=fake_approve), \
         patch("app.services.mcp_execution_service._write_audit", return_value="audit-ap-f"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "finance.ap_invoice.freigeben",
            "parameters": {"proposal_id": "p-ap"},
            "mode": "execute",
            "idempotency_key": "ap-freigabe-1",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["approved"] is True
    assert body["fibu_journal"] is False
    assert body["status"] == "FREIGEGEBEN"
    assert body["auditEntryId"] == "audit-ap-f"
    db.commit.assert_called_once()


def test_ap_freigeben_rejects_client_approval_flag(client):
    http, db = _as_finance_write(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "finance.ap_invoice.freigeben",
        "parameters": {"proposal_id": "p-ap", "approval_granted": True},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


INVENTUR_OPENING = {"count_id": "inv-count-1"}
INVENTUR_OPENING_PREVIEW = {
    "count_id": "inv-count-1",
    "warehouse_id": "wh-1",
    "status": "in_progress",
    "line_count": 3,
    "difference_count": 1,
    "preliminary_value": 450.0,
    "batch_type": "opening_balance",
    "route_path": "/lager/inventur-nebenlaeufe",
    "screen_id": "lager/inventur-nebenlaeufe",
    "source_route": "/lager/inventur?count=inv-count-1",
}


def _as_lager_write(client):
    http, app, db = client
    app.dependency_overrides[get_current_user] = lambda: {
        **USER,
        "scopes": ["lager:write"],
    }
    return http, db


def test_inventur_propose_opening_scope_is_required(client):
    http, _, db = client
    response = http.post("/mcp/tools/call", json={
        "tool_name": "lager.inventur.propose_opening",
        "parameters": INVENTUR_OPENING,
    })
    assert response.status_code == 403
    db.execute.assert_not_called()


def test_inventur_propose_opening_execute_is_not_wired(client):
    http, db = _as_lager_write(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "lager.inventur.propose_opening",
        "parameters": INVENTUR_OPENING,
        "mode": "execute",
    })
    assert response.status_code == 501
    db.commit.assert_not_called()


def test_inventur_propose_opening_rejects_client_approval_flag(client):
    http, db = _as_lager_write(client)
    response = http.post("/mcp/tools/call", json={
        "tool_name": "lager.inventur.propose_opening",
        "parameters": {**INVENTUR_OPENING, "approval_granted": True},
    })
    assert response.status_code == 422
    db.execute.assert_not_called()


def test_inventur_propose_opening_dry_run_reads_without_booking(client):
    http, db = _as_lager_write(client)
    with patch(
        "app.services.mcp_execution_service._inventur_opening_preview",
        return_value=INVENTUR_OPENING_PREVIEW,
    ):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "lager.inventur.propose_opening",
            "parameters": INVENTUR_OPENING,
        })
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "dryRun"
    assert body["booked"] is False
    assert body["count_id"] == "inv-count-1"
    assert body["line_count"] == 3
    assert body["preliminary_value"] == 450.0
    assert body["route_path"] == "/lager/inventur-nebenlaeufe"
    assert "entwurf_id" not in body
    db.commit.assert_not_called()


def test_inventur_propose_opening_stores_pending_and_does_not_book(client):
    http, db = _as_lager_write(client)
    statements: list[str] = []

    def execute(sql, params=None):
        statements.append(str(sql))
        result = Mock()
        result.mappings.return_value.first.return_value = None
        return result

    db.execute.side_effect = execute
    with patch(
        "app.services.mcp_execution_service._inventur_opening_preview",
        return_value=INVENTUR_OPENING_PREVIEW,
    ), patch("app.services.mcp_execution_service._write_audit", return_value="audit-inv"):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "lager.inventur.propose_opening",
            "parameters": INVENTUR_OPENING,
            "mode": "propose",
            "idempotency_key": "inv-open-1",
        })
    assert response.status_code == 200
    body = response.json()
    assert body["booked"] is False
    assert body["approval_status"] == "pending"
    assert body["entwurf_id"]
    joined = "\n".join(statements)
    assert "agent_proposals" in joined
    assert "inventur_opening" in joined
    assert "'pending'" in joined
    assert "inventory_stock_movements" not in joined
    assert "opening_balance" not in joined or "batch_type" in body
    db.commit.assert_called_once()


SANCTIONS = {"name": "Muster GmbH", "scope": "customers", "entity_ref": "K-100"}
FRACHT = {"tabelle_nr": "FT-99", "bezeichnung": "Staffel Test", "einheit": "t", "waehrung": "EUR"}


def test_sanctions_check_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["compliance:write"])
    with patch(
        "app.api.v1.endpoints.sanctions_compliance.match_sanctions_name",
        return_value=([], "KEIN_TREFFER", "Kein Sanktionstreffer — Freigabe unter Vorbehalt periodischer Neuprüfung."),
    ):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "compliance.sanctions.check", "parameters": SANCTIONS,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    assert ok.json()["status"] == "KEIN_TREFFER"
    db.commit.assert_not_called()

    assert http.post("/mcp/tools/call", json={
        "tool_name": "compliance.sanctions.check",
        "parameters": {**SANCTIONS, "tenant_id": "x"},
    }).status_code == 422

    with patch(
        "app.api.v1.endpoints.sanctions_compliance.match_sanctions_name",
        return_value=([], "KEIN_TREFFER", "ok"),
    ), patch(
        "app.api.v1.endpoints.sanctions_compliance.persist_sanctions_check",
        return_value="chk-1",
    ), patch("app.services.mcp_execution_service._write_audit", return_value="audit-s"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "compliance.sanctions.check",
            "parameters": SANCTIONS,
            "mode": "execute",
            "idempotency_key": "san-once",
        })
    assert response.status_code == 200
    assert response.json()["check_id"] == "chk-1"
    db.commit.assert_called()


def test_frachttabelle_anlegen_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["logistics:write"])
    db.execute.return_value.fetchone.return_value = None
    ok = http.post("/mcp/tools/call", json={
        "tool_name": "logistik.frachttabelle.anlegen", "parameters": FRACHT,
    })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    db.commit.assert_not_called()

    with patch(
        "app.api.v1.endpoints.logistik_frachttabellen.insert_frachttabelle",
        return_value={"id": "ft-1", "tabelle_nr": "FT-99"},
    ), patch("app.services.mcp_execution_service._write_audit", return_value="audit-f"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "logistik.frachttabelle.anlegen",
            "parameters": FRACHT,
            "mode": "execute",
            "idempotency_key": "ft-once",
        })
    assert response.status_code == 200
    assert response.json()["id"] == "ft-1"
    assert response.json()["tabelle_nr"] == "FT-99"
    db.commit.assert_called()


BONUS = {
    "report_id": "bonus-by-customer",
    "from_date": "2026-01-01",
    "to_date": "2026-01-31",
    "rate_pct": "2.5",
    "reason": "Monatsbonus Test",
}
QUERY_IMP = {
    "bundle": {"schema_version": 1, "definition": {"name": "OP"}, "signature": "deadbeef"},
    "reason": "Import Testlauf",
}


def test_bonus_calculate_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["reporting:write"])
    with patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.validate_bonus_run_params"
    ):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "reporting.bonus.calculate", "parameters": BONUS,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    db.commit.assert_not_called()

    with patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.validate_bonus_run_params"
    ), patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.create_bonus_run",
        return_value={"id": "run-9", "lines": 2, "total_bonus": Decimal("5.00")},
    ), patch("app.services.mcp_execution_service._write_audit", return_value="audit-b"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "reporting.bonus.calculate",
            "parameters": BONUS,
            "mode": "execute",
            "idempotency_key": "bonus-once",
        })
    assert response.status_code == 200
    assert response.json()["run_id"] == "run-9"
    db.commit.assert_called()


def test_query_import_signed_dry_run_and_execute(client):
    http, db = _as_scopes(client, ["reporting:write"])
    with patch("app.services.mcp_execution_service.QueryCenterService") as Svc:
        inst = Mock()
        inst.preview_import_signed.return_value = {
            "name": "OP (Import)", "data_product_id": "x", "selected_fields": [], "would_import": True,
        }
        Svc.return_value = inst
        # patch where it's imported inside the function
        pass
    with patch(
        "app.services.query_center_service.QueryCenterService.preview_import_signed",
        return_value={
            "name": "OP (Import)", "data_product_id": "x", "selected_fields": [], "would_import": True,
        },
    ):
        ok = http.post("/mcp/tools/call", json={
            "tool_name": "reporting.query.import_signed", "parameters": QUERY_IMP,
        })
    assert ok.status_code == 200
    assert ok.json()["mode"] == "dryRun"
    db.commit.assert_not_called()

    with patch(
        "app.services.query_center_service.QueryCenterService.preview_import_signed",
        return_value={
            "name": "OP (Import)", "data_product_id": "x", "selected_fields": [], "would_import": True,
        },
    ), patch(
        "app.services.query_center_service.QueryCenterService.import_signed",
        return_value={"id": "def-1", "name": "OP (Import)"},
    ), patch("app.services.mcp_execution_service._write_audit", return_value="audit-q"), \
         patch("app.services.mcp_execution_service._store_execution"), \
         patch("app.services.mcp_execution_service._advisory_lock"), \
         patch("app.services.mcp_execution_service._replay_or_none", return_value=None):
        response = http.post("/mcp/tools/call", json={
            "tool_name": "reporting.query.import_signed",
            "parameters": QUERY_IMP,
            "mode": "execute",
            "idempotency_key": "qimp-once",
        })
    assert response.status_code == 200
    assert response.json()["definition_id"] == "def-1"
    db.commit.assert_called()
