import httpx

from app.integrations.adapters.superglue.tool_sync import (
    build_superglue_health_status,
    build_superglue_sync_status,
    build_superglue_tenant_tool_summary,
    build_superglue_tool_summary,
    list_superglue_tool_records,
)
from app.integrations.adapters.superglue.client import SuperglueClient


def test_superglue_tool_sync_defaults_to_mapped_catalog():
    records = list_superglue_tool_records()

    assert len(records) >= 1
    assert any(item.valeo_contract_id == "superglue.document.search" for item in records)


def test_superglue_sync_status_surfaces_tool_count():
    status = build_superglue_sync_status()

    assert status.provider_key == "superglue"
    assert status.tool_count >= 1


def test_superglue_health_status_reports_missing_config_as_unhealthy(monkeypatch):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_ENABLED", False)

    health = build_superglue_health_status()

    assert health.healthy is False


def test_superglue_tool_summary_serializes_records():
    summary = build_superglue_tool_summary()

    assert summary["provider_key"] == "superglue"
    assert summary["tool_count"] >= 1


def test_superglue_tool_sync_maps_tenant_specific_tool_ids(monkeypatch):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_ENABLED", True)
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_SYNC_ENABLED", True)
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "tenant-a.sg.document.search",
                            "name": "Tenant Document Search",
                        }
                    ]
                },
            )
        ),
    )

    records = list_superglue_tool_records(client)

    assert records[0].valeo_contract_id == "superglue.document.search"
    assert records[0].target_kind == "document"
    assert "connector" in records[0].tags


def test_superglue_tenant_tool_summary_surfaces_registry_bindings():
    summary = build_superglue_tenant_tool_summary("tenant-a")

    assert summary["tenant_id"] == "tenant-a"
    assert summary["tool_count"] >= 9
    assert any(item["tool_id"] == "tenant-a.sg.document.search" for item in summary["tools"])
