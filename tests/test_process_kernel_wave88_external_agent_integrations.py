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
    external_agent_integrations.provision_superglue_pilot_tools = lambda: {
        "provider_key": "superglue",
        "tool_count": 3,
        "tool_ids": [
            "sg.document.search",
            "sg.partner.adapter.preview",
            "sg.customer.profile.preview",
        ],
    }
    external_agent_integrations.run_superglue_pilot_smoke = lambda: {
        "provider_key": "superglue",
        "tool_id": "sg.document.search",
        "run_id": "sg-run-smoke",
        "status": "success",
    }
    external_agent_integrations.provision_superglue_tenant_connectors = lambda tenant_id: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "connector_count": 3,
        "tool_ids": [
            f"{tenant_id}.sg.document.search",
            f"{tenant_id}.sg.partner.adapter.preview",
            f"{tenant_id}.sg.customer.profile.preview",
        ],
    }
    external_agent_integrations.build_superglue_tool_lifecycle_summary = lambda tenant_id: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "connector_count": 3,
        "connectors": [
            {"connector_key": "document_search", "tool_id": f"{tenant_id}.sg.document.search"},
        ],
    }
    external_agent_integrations.build_superglue_tenant_tool_summary = lambda tenant_id: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "tool_count": 3,
        "tools": [
            {"connector_key": "document_search", "tool_id": f"{tenant_id}.sg.document.search"},
        ],
    }
    external_agent_integrations.build_superglue_admin_overview = lambda tenant_id: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "connector_count": 9,
    }
    external_agent_integrations.build_superglue_monitoring_summary = lambda tenant_id=None: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "run_count": 4,
    }
    external_agent_integrations.build_superglue_domain_rollout_summary = lambda tenant_id: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_count": 6,
        "domains": [{"domain_key": "finance", "connector_count": 1, "connectors": []}],
    }
    external_agent_integrations.preview_superglue_domain_rollout = lambda tenant_id, domain_key, parameters=None: {
        "provider_key": "superglue",
        "tenant_id": tenant_id,
        "domain_key": domain_key,
        "preview_count": 1,
        "previews": [],
    }
    external_agent_integrations.retry_quarantine_entry = lambda entry_id, retried_by, note=None, dead_letter=False: {
        "entry_id": entry_id,
        "status": "open" if not dead_letter else "dead_letter",
        "retry_count": 1,
    }
    client = _client()

    provider = client.get("/agent/integrations/providers/superglue")
    sync = client.get("/agent/integrations/providers/superglue/sync-status")
    tools = client.get("/agent/integrations/providers/superglue/tools")
    tenant_tools = client.get("/agent/integrations/providers/superglue/tenants/tenant-a/tools")
    health = client.get("/agent/integrations/providers/superglue/health")
    config = client.get("/agent/integrations/providers/superglue/config-summary")
    history = client.get("/agent/integrations/providers/superglue/sync-history")
    quarantine = client.get("/agent/integrations/providers/superglue/quarantine")
    journal = client.get("/agent/integrations/providers/superglue/execution-journal")
    admin_overview = client.get("/agent/integrations/providers/superglue/admin-overview?tenant_id=tenant-a")
    monitoring = client.get("/agent/integrations/providers/superglue/monitoring?tenant_id=tenant-a")
    refresh = client.post("/agent/integrations/providers/superglue/sync-status/refresh")
    provision = client.post("/agent/integrations/providers/superglue/pilot-tools/provision")
    smoke = client.post("/agent/integrations/providers/superglue/pilot-tools/smoke-run")
    bootstrap = client.post("/agent/integrations/providers/superglue/tenants/tenant-a/bootstrap")
    lifecycle = client.get("/agent/integrations/providers/superglue/tenants/tenant-a/tool-lifecycle")
    domain_rollouts = client.get("/agent/integrations/providers/superglue/domain-rollouts?tenant_id=tenant-a")
    domain_preview = client.post("/agent/integrations/providers/superglue/domain-rollouts/finance/preview?tenant_id=tenant-a", json={})
    quarantine_retry = client.post("/agent/integrations/providers/superglue/quarantine/sgq-1/retry?retried_by=tester")

    assert provider.status_code == 200
    assert provider.json()["provider_key"] == "superglue"
    assert sync.status_code == 200
    assert sync.json()["provider_key"] == "superglue"
    assert tools.status_code == 200
    assert tools.json()["provider_key"] == "superglue"
    assert tools.json()["tool_count"] >= 1
    assert tenant_tools.status_code == 200
    assert tenant_tools.json()["tenant_id"] == "tenant-a"
    assert health.status_code == 200
    assert health.json()["provider_key"] == "superglue"
    assert config.status_code == 200
    assert config.json()["provider_key"] == "superglue"
    assert history.status_code == 200
    assert history.json()["provider_key"] == "superglue"
    assert quarantine.status_code == 200
    assert "entry_count" in quarantine.json()
    assert journal.status_code == 200
    assert "entry_count" in journal.json()
    assert admin_overview.status_code == 200
    assert admin_overview.json()["tenant_id"] == "tenant-a"
    assert monitoring.status_code == 200
    assert monitoring.json()["provider_key"] == "superglue"
    assert refresh.status_code == 200
    assert refresh.json()["provider_key"] == "superglue"
    assert provision.status_code == 200
    assert provision.json()["provider_key"] == "superglue"
    assert smoke.status_code == 200
    assert smoke.json()["provider_key"] == "superglue"
    assert bootstrap.status_code == 200
    assert bootstrap.json()["tenant_id"] == "tenant-a"
    assert lifecycle.status_code == 200
    assert lifecycle.json()["tenant_id"] == "tenant-a"
    assert domain_rollouts.status_code == 200
    assert domain_rollouts.json()["domain_count"] == 6
    assert domain_preview.status_code == 200
    assert domain_preview.json()["domain_key"] == "finance"
    assert quarantine_retry.status_code == 200
    assert quarantine_retry.json()["retry_count"] == 1


def test_external_agent_unknown_use_case_returns_404():
    client = _client()

    response = client.get("/agent/integrations/use-cases/does-not-exist")

    assert response.status_code == 404
