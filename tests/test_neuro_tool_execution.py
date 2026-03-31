"""Tests for Neuro Tool Execution Service (NC-A7)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.mcp_tool_contracts import MCPRequestPayloadMode, MCPToolContract, MCPToolKategorie
from app.services.neuro_tool_execution import NeuroToolExecutionService


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
        context={"external_base_url": "https://tool-gateway.example", "execution_headers": {"X-Env": "prod"}},
    )

    assert result["mode"] == "openapi_external"
    assert result["request"]["url"] == "https://tool-gateway.example/api/v1/demo/tenant-9"
    assert captured["headers"]["X-Env"] == "prod"


def test_execute_contract_external_http_error_falls_back():
    def external_requester(**kwargs):
        return {"status_code": 502, "body": {"detail": "bad gateway"}}

    service = NeuroToolExecutionService(external_requester=external_requester)
    result = service.execute_contract(
        _contract("valeo_demo_external", "GET /api/v1/demo/{tenant_id}"),
        parameters={},
        tenant_id="tenant-9",
        context={"external_base_url": "https://tool-gateway.example"},
    )

    assert result["mode"] == "fallback_contract"
    assert result["fallback_reason"] == "http_502"


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
        context={"policy_context": {"rolle": "einkauf"}},
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
        context={"comparison_records": [{"lieferant_nr": "LF-1"}]},
    )

    assert result["mode"] == "openapi_internal"
    assert result["request"]["json"] == {
        "entity_typ": "KREDITOR",
        "datensatz": {"entity_type": "supplier", "lieferant_nr": "LF-1"},
        "kontext_datensaetze": [{"lieferant_nr": "LF-1"}],
    }
