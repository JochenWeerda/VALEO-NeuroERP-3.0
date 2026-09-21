"""AI-service MCP must not claim ERP persistence for disconnected adapters."""
import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative, monkeypatch):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def server_module(monkeypatch):
    return load_module("ai_mcp_test_server", "services/ai/app/mcp/server.py", monkeypatch)


@pytest.mark.parametrize("name", ["query_database", "search_documents", "create_procurement_order"])
def test_disconnected_tools_are_advertised_as_unavailable(server_module, name):
    tool = next(t for t in server_module.mcp_server.list_tools() if t["name"] == name)
    assert tool["available"] is False
    with pytest.raises(NotImplementedError):
        asyncio.run(server_module.mcp_server.call_tool(name, article="TEST", quantity=1))


def test_even_direct_procurement_handler_cannot_fabricate_success(server_module):
    with pytest.raises(NotImplementedError, match="no order was created"):
        asyncio.run(server_module.mcp_server._handle_create_order(article="TEST", quantity=1))


@pytest.fixture
def client(server_module, monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    monkeypatch.setitem(sys.modules, "app.mcp", ModuleType("app.mcp"))
    monkeypatch.setitem(sys.modules, "app.mcp.server", server_module)
    endpoint = load_module("ai_mcp_test_endpoint", "services/ai/app/api/v1/endpoints/mcp.py", monkeypatch)
    app = FastAPI()
    app.include_router(endpoint.router)
    with TestClient(app) as http:
        yield http


@pytest.mark.parametrize("name", ["query_database", "search_documents", "create_procurement_order"])
def test_http_call_cannot_return_success_for_unimplemented_tools(client, name):
    response = client.post("/tools/call", json={"tool_name": name, "parameters": {}})
    assert response.status_code == 501
    assert "result" not in response.json()
    assert "status" not in response.json()


def test_unknown_tool_is_not_found(client):
    response = client.post("/tools/call", json={"tool_name": "missing", "parameters": {}})
    assert response.status_code == 404


def test_real_registered_handler_still_returns_its_result(client, server_module):
    async def connected():
        return {"validated": True}

    server_module.mcp_server.tools.append(server_module.MCPTool("connected", "Test", {}, connected))
    response = client.post("/tools/call", json={"tool_name": "connected", "parameters": {}})
    assert response.status_code == 200
    assert response.json() == {"result": {"validated": True}, "status": "success"}
