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
    assert body["provider_count"] >= 7
    assert body["use_case_count"] >= 12
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
    assert any(provider["provider_key"] == "superglue" for provider in body["providers"])


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


def test_superglue_provider_routes_surface_sync_and_health():
    client = _client()

    provider = client.get("/agent/integrations/providers/superglue")
    sync = client.get("/agent/integrations/providers/superglue/sync-status")
    tools = client.get("/agent/integrations/providers/superglue/tools")
    health = client.get("/agent/integrations/providers/superglue/health")
    config = client.get("/agent/integrations/providers/superglue/config-summary")
    quarantine = client.get("/agent/integrations/providers/superglue/quarantine")
    refresh = client.post("/agent/integrations/providers/superglue/sync-status/refresh")

    assert provider.status_code == 200
    assert provider.json()["provider_key"] == "superglue"
    assert sync.status_code == 200
    assert sync.json()["provider_key"] == "superglue"
    assert tools.status_code == 200
    assert tools.json()["tool_count"] >= 3
    assert health.status_code == 200
    assert health.json()["provider_key"] == "superglue"
    assert config.status_code == 200
    assert config.json()["provider_key"] == "superglue"
    assert quarantine.status_code == 200
    assert "entry_count" in quarantine.json()
    assert refresh.status_code == 200
    assert refresh.json()["provider_key"] == "superglue"


def test_external_agent_unknown_use_case_returns_404():
    client = _client()

    response = client.get("/agent/integrations/use-cases/does-not-exist")

    assert response.status_code == 404
