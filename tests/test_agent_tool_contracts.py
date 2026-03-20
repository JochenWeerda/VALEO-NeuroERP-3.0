from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import agent_tool_contracts


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(agent_tool_contracts.router)
    return TestClient(app)


def test_agent_tool_contract_manifest_exposes_multiple_external_tools():
    client = _client()

    response = client.get("/agent/tool-contracts")

    assert response.status_code == 200
    body = response.json()
    assert body["manifest_kind"] == "MCP_OPENAPI_TOOL_CONTRACT"
    assert body["tool_count"] >= 20
    assert set(["agrar", "finance", "workflow", "compliance", "process", "inventory"]).issubset(
        set(body["domains"])
    )
    assert body["command_manifest"]["command_count"] >= 10
    tool_names = {tool["tool_name"] for tool in body["tools"]}
    assert "valeo_process_action_execute" in tool_names
    assert "valeo_finance_payment_run_create" in tool_names
    assert "valeo_agrar_settlement_list" in tool_names


def test_agent_tool_contract_manifest_domain_filter_returns_only_requested_domain():
    client = _client()

    response = client.get("/agent/tool-contracts", params={"domain": "finance"})

    assert response.status_code == 200
    body = response.json()
    assert body["domains"] == ["finance"]
    assert body["tool_count"] >= 5
    assert all(tool["domain"] == "finance" for tool in body["tools"])
    assert all(tool["openapi_ref"]["openapi_url"] == "/api/v1/openapi.json" for tool in body["tools"])


def test_agent_tool_contract_endpoints_surface_mcp_and_openapi_views():
    client = _client()

    mcp_response = client.get("/agent/tool-contracts/mcp", params={"tool_name": "valeo_process_action_execute"})
    assert mcp_response.status_code == 200
    mcp_body = mcp_response.json()
    assert mcp_body["tool_count"] == 1
    assert mcp_body["tools"][0]["name"] == "valeo_process_action_execute"
    assert "inputSchema" in mcp_body["tools"][0]

    openapi_response = client.get("/agent/tool-contracts/openapi", params={"domain": "process"})
    assert openapi_response.status_code == 200
    openapi_body = openapi_response.json()
    assert openapi_body["tool_count"] >= 3
    assert any(tool["tool_name"] == "valeo_process_action_execute" for tool in openapi_body["tools"])
    assert all(tool["openapi_url"] == "/api/v1/openapi.json" for tool in openapi_body["tools"])


def test_single_tool_contract_lookup_returns_404_for_unknown_tool():
    client = _client()

    response = client.get("/agent/tool-contracts/valeo_unknown_tool")

    assert response.status_code == 404
