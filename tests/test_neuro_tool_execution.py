"""Tests for Neuro Tool Execution Service (NC-A7)."""

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.mcp_tool_contracts import MCPRequestPayloadMode, MCPToolContract, MCPToolKategorie
from app.services.neuro_tool_execution import NeuroToolExecutionService
from test_system_tenant_binding import keys, probe


@pytest.fixture(autouse=True)
def signed_identity(probe):
    global _probe
    _probe = probe


def _token(tenant):
    return _probe.token(tenant)


def _contract(tool_name: str, api_endpoint: str) -> MCPToolContract:
    return MCPToolContract(
        tool_name=tool_name,
        domain="process",
        operation="demo",
        beschreibung="demo",
        kategorie=MCPToolKategorie.LESEN,
        api_endpoint=api_endpoint,
    )


def test_execute_contract_calls_internal_openapi_route():
    app = FastAPI()

    @app.get("/api/v1/demo/{tenant_id}")
    def read_demo(tenant_id: str):
        return {"tenant_id": tenant_id, "status": "ok"}

    service = NeuroToolExecutionService(TestClient(app))
    result = service.execute_contract(
        _contract("valeo_demo_read", "GET /api/v1/demo/{tenant_id}"),
        parameters={},
        tenant_id="tenant-1",
        context={"auth_token": _token("tenant-1")},
    )

    assert result["mode"] == "openapi_internal"
    assert result["http_status"] == 200
    assert result["response"]["tenant_id"] == "tenant-1"


def test_execute_contract_falls_back_when_route_errors():
    app = FastAPI()
    service = NeuroToolExecutionService(TestClient(app, raise_server_exceptions=False))

    result = service.execute_contract(
        _contract("valeo_demo_missing", "GET /api/v1/missing/{tenant_id}"),
        parameters={},
        tenant_id="tenant-1",
        context={"auth_token": _token("tenant-1")},
    )

    assert result["mode"] == "fallback_contract"
    assert result["fallback_reason"] == "http_404"


def test_execute_contract_uses_external_base_url_when_configured():
    captured = {}

    def external_requester(**kwargs):
        captured.update(kwargs)
        return {"status_code": 200, "body": {"status": "external-ok"}}

    service = NeuroToolExecutionService(external_requester=external_requester)
    result = service.execute_contract(
        _contract("valeo_demo_external", "GET /api/v1/demo/{tenant_id}"),
        parameters={},
        tenant_id="tenant-9",
        context={"auth_token": "synthetic-transport-token", "external_base_url": "https://tool-gateway.example", "execution_headers": {"X-Env": "prod"}},
    )

    assert result["mode"] == "execution_rejected"
    assert result["rejection_reason"] == "external_target_not_approved"
    assert captured == {}


def test_execute_contract_external_http_error_falls_back():
    def external_requester(**kwargs):
        return {"status_code": 502, "body": {"detail": "bad gateway"}}

    service = NeuroToolExecutionService(external_requester=external_requester)
    result = service.execute_contract(
        _contract("valeo_demo_external", "GET /api/v1/demo/{tenant_id}"),
        parameters={},
        tenant_id="tenant-9",
        context={"auth_token": "synthetic-transport-token", "external_base_url": "https://tool-gateway.example"},
    )

    assert result["mode"] == "execution_rejected"
    assert result["rejection_reason"] == "external_target_not_approved"


def test_execute_contract_uses_contract_payload_mode_for_policy_context():
    app = FastAPI()

    @app.post("/api/v1/demo/policy")
    def evaluate_policy(payload: dict):
        return payload

    service = NeuroToolExecutionService(TestClient(app))
    result = service.execute_contract(
        MCPToolContract(
            tool_name="valeo_demo_policy_eval",
            domain="demo",
            operation="policy_eval",
            beschreibung="demo",
            kategorie=MCPToolKategorie.BERECHNEN,
            api_endpoint="POST /api/v1/demo/policy",
            request_payload_mode=MCPRequestPayloadMode.POLICY_CONTEXT,
        ),
        parameters={"betrag_eur": 125, "lieferant_typ": "MITGLIED"},
        tenant_id="tenant-7",
        context={"auth_token": _token("tenant-7"), "policy_context": {"rolle": "einkauf"}},
    )

    assert result["mode"] == "openapi_internal"
    assert result["request"]["json"] == {
        "prozess_key": "agrar_settlement",
        "kontext": {
            "betrag_eur": 125,
            "tenant_id": "tenant-7",
            "rolle": "einkauf",
            "lieferant_typ": "MITGLIED",
        },
    }


def test_execute_contract_uses_contract_payload_mode_for_dataset_validation():
    app = FastAPI()

    @app.post("/api/v1/demo/dq")
    def validate_dataset(payload: dict):
        return payload

    service = NeuroToolExecutionService(TestClient(app))
    result = service.execute_contract(
        MCPToolContract(
            tool_name="valeo_demo_dq_validate",
            domain="demo",
            operation="dq_validate",
            beschreibung="demo",
            kategorie=MCPToolKategorie.VALIDIEREN,
            api_endpoint="POST /api/v1/demo/dq",
            request_payload_mode=MCPRequestPayloadMode.DATASET_VALIDATION,
        ),
        parameters={"entity_type": "supplier", "lieferant_nr": "LF-1"},
        tenant_id="tenant-1",
        context={"auth_token": _token("tenant-1"), "comparison_records": [{"lieferant_nr": "LF-1"}]},
    )

    assert result["mode"] == "openapi_internal"
    assert result["request"]["json"] == {
        "entity_typ": "KREDITOR",
        "datensatz": {"entity_type": "supplier", "lieferant_nr": "LF-1"},
        "kontext_datensaetze": [{"lieferant_nr": "LF-1"}],
    }


@pytest.mark.parametrize("context", [{}, {"auth_token": ""}, {"auth_token": "\r\ninjected"}])
def test_missing_credentials_never_reach_transport(context):
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own", context=context)
    assert result["http_status"] == 401
    client.request.assert_not_called()


@pytest.mark.parametrize("name", ["Authorization", "authorization", "X-Tenant-ID", "x-tenant-id", "Cookie", "X-User-ID"])
def test_execution_headers_cannot_change_identity(name):
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own",
        context={"auth_token": "synthetic-transport-token", "execution_headers": {name: "foreign"}})
    assert result["rejection_reason"] == "execution_headers_not_allowed"
    client.request.assert_not_called()


@pytest.mark.parametrize("category", [MCPToolKategorie.SCHREIBEN, MCPToolKategorie.ESKALIEREN])
def test_legacy_write_contract_stays_disabled(category):
    from unittest.mock import Mock
    client = Mock()
    contract = _contract("write", "POST /demo")
    contract.kategorie = category
    result = NeuroToolExecutionService(client).execute_contract(
        contract, parameters={}, tenant_id="own",
        context={"auth_token": "synthetic-transport-token", "enabled": True, "approval_status": "approved"})
    assert result["rejection_reason"] == "write_capability_not_approved"
    client.request.assert_not_called()


def test_transport_token_is_sent_but_not_returned_in_trace():
    from unittest.mock import Mock
    client = Mock()
    client.request.return_value.status_code = 200
    client.request.return_value.json.return_value = {"ok": True}
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own",
        context={"auth_token": _token("own"), "execution_headers": {"X-Correlation-ID": "c1"}})
    assert client.request.call_args.kwargs["headers"]["Authorization"].startswith("Bearer ey")
    assert result["request"]["headers"]["Authorization"] == "[REDACTED]"


@pytest.mark.parametrize("changes", [{"aud": "foreign-api"}, {"iss": "https://foreign.invalid"}, {"exp": 1}])
def test_wrong_audience_issuer_or_expiry_stops_before_transport(changes):
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own",
        context={"auth_token": _probe.token("own", changes=changes)})
    assert result["http_status"] == 401
    client.request.assert_not_called()


@pytest.mark.parametrize("parameters,tenant", [({}, "foreign"), ({"tenant_id": "foreign"}, "own"), ({"child": {"tenant_id": "foreign"}}, "own")])
def test_signed_identity_cannot_select_foreign_tenant(parameters,tenant):
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters=parameters, tenant_id=tenant,
        context={"auth_token": _token("own")})
    assert result["http_status"] == 403
    client.request.assert_not_called()


@pytest.mark.parametrize("credential", ["dev-token", "neuro-tool-broker", "opaque-own-dev-token"])
def test_legacy_tokens_are_not_verified_identity(credential):
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own",
        context={"auth_token": credential})
    assert result["http_status"] == 401
    client.request.assert_not_called()


def test_forged_signature_stops_before_transport():
    from unittest.mock import Mock
    client = Mock()
    result = NeuroToolExecutionService(client).execute_contract(
        _contract("read", "GET /demo"), parameters={}, tenant_id="own",
        context={"auth_token": _probe.token("own", key=1)})
    assert result["http_status"] == 401
    client.request.assert_not_called()


@pytest.mark.parametrize("roles,expected", [(["FINANCE_BEARBEITEN"],200), ([],403)])
def test_internal_adapter_keeps_endpoint_authorization(roles,expected):
    result = NeuroToolExecutionService(_probe.client).execute_contract(
        _contract("read", "GET /api/probe"), parameters={}, tenant_id="own",
        context={"auth_token": _probe.token("own", changes={"roles":roles})})
    assert result["http_status"] == expected
    assert len(_probe.calls) == (1 if expected == 200 else 0)



def test_pipeline_uses_verified_bearer_not_context_token(monkeypatch):
    from app.api.v1.endpoints import neuro_pipeline
    from app.core.database import get_db
    from unittest.mock import Mock
    pipeline = Mock(return_value={"status":"checked"})
    monkeypatch.setattr(neuro_pipeline,"run_pipeline",pipeline)
    app = FastAPI()
    app.include_router(neuro_pipeline.router,prefix="/api/v1")
    app.dependency_overrides[get_db] = lambda: None
    token = _token("own")
    response = TestClient(app).post("/api/v1/neuro/execute",
        headers={"Authorization":"Bearer "+token},
        json={"user_input":"Lagerbestand", "context":{"auth_token":"foreign", "channel":"api"}})
    assert response.status_code == 200
    assert pipeline.call_args.kwargs["auth_token"] == token
    assert "auth_token" not in pipeline.call_args.kwargs["context"]
    assert pipeline.call_args.kwargs["tenant_id"] == "own"
    assert token not in response.text



def test_pipeline_credentials_never_enter_classifier_or_planner(monkeypatch):
    from app.agents import neuro_pipeline
    from unittest.mock import Mock
    original_classify, original_plan = neuro_pipeline.classify, neuro_pipeline.generate_plan
    classify, planner = Mock(wraps=original_classify), Mock(wraps=original_plan)
    monkeypatch.setattr(neuro_pipeline,"classify",classify)
    monkeypatch.setattr(neuro_pipeline,"generate_plan",planner)
    result = neuro_pipeline.run_pipeline("Lagerbestand abfragen",
        context={"auth_token":"untrusted-body-token"}, auth_token="transport-only-token", dry_run=True)
    assert result["status"] == "dry_run"
    assert "auth_token" not in classify.call_args.args[1]
    assert "auth_token" not in planner.call_args.args[1]
    assert "transport-only-token" not in str(result)
