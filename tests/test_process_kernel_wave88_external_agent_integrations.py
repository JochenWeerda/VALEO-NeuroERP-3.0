from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import external_agent_integrations


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(external_agent_integrations.router)
    return TestClient(app)


def test_external_agent_catalog_exposes_openapi_and_mcp_surfaces():
    client = _client()

    response = client.get("/agent/integrations")

    assert response.status_code == 200
    body = response.json()
    assert body["manifest_kind"] == "EXTERNAL_AGENT_INTEGRATION_CATALOG"
    assert body["provider_count"] >= 6
    assert body["use_case_count"] >= 10
    assert set(use_case["domain"] for use_case in body["use_cases"]) >= {
        "process",
        "workflow",
        "finance",
        "docflow",
        "supply_chain",
        "crm",
        "analytics",
    }
    assert body["sources"]
    assert any(source["rel"] == "openapi" for source in body["sources"])
    assert any(source["rel"] == "mcp-tool-contracts" for source in body["sources"])


def test_external_agent_provider_catalog_filters_by_provider_key():
    client = _client()

    response = client.get("/agent/integrations/providers", params={"provider_key": "openapi_client"})

    assert response.status_code == 200
    body = response.json()
    assert body["provider_count"] == 1
    assert body["providers"][0]["provider_key"] == "openapi_client"
    assert body["providers"][0]["supports_openapi"] is True


def test_external_agent_use_cases_surface_install_pack_and_domain_filter():
    client = _client()

    response = client.get("/agent/integrations/use-cases", params={"domain": "process"})

    assert response.status_code == 200
    body = response.json()
    assert body["domain_count"] == 1
    assert body["domains"] == ["process"]
    assert body["use_case_count"] >= 3
    assert all(use_case["domain"] == "process" for use_case in body["use_cases"])

    install_pack = client.get("/agent/integrations/use-cases/knowledge_lookup/install-pack")
    assert install_pack.status_code == 200
    pack = install_pack.json()
    assert pack["use_case_id"] == "knowledge_lookup"
    assert "/api/v1/process/knowledge/retrieve" in pack["entrypoints"]
    assert pack["tool_contracts"]
    assert pack["command_manifest_url"] == "/api/v1/commands/agent-manifest"


def test_external_agent_unknown_use_case_returns_404():
    client = _client()

    response = client.get("/agent/integrations/use-cases/does-not-exist")

    assert response.status_code == 404
