"""Tests for Neuro Tool Execution Service (NC-A7)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.mcp_tool_contracts import MCPToolContract, MCPToolKategorie
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
