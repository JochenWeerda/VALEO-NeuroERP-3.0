from app.integrations.services.superglue_connector_registry import (
    build_superglue_connector_binding,
    list_superglue_connector_bindings,
)


def test_superglue_connector_registry_builds_deterministic_bindings(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_connector_registry.resolve_superglue_connector_value",
        lambda tenant_id, connector_key, field_name, fallback=None: {
            ("tenant-a", "document_search", "SYSTEM_URL"): "https://dms.example.test/api",
            ("tenant-a", "document_search", "apiKey"): "doc-key",
        }.get((tenant_id, connector_key, field_name), fallback),
    )

    binding = build_superglue_connector_binding(tenant_id="tenant-a", connector_key="document_search")

    assert binding.tool_id == "tenant-a.sg.document.search"
    assert binding.system.system_id == "tenant-a.document_search.system"
    assert binding.system.url == "https://dms.example.test/api"
    assert binding.run_credentials == {"apiKey": "doc-key"}
    assert binding.metadata["tool_family"] == "sg.document.search"
    assert binding.metadata["credential_fields"] == ["apiKey", "apiSecret", "accessToken"]


def test_superglue_connector_registry_lists_all_default_connectors():
    bindings = list_superglue_connector_bindings("tenant-a")

    assert {binding.connector_key for binding in bindings} >= {
        "document_search",
        "partner_edi",
        "customer_profile",
        "supplier_directory",
        "finance_export",
        "carrier_tracking",
        "agribusiness_market",
        "field_service_tasks",
        "analytics_dataset",
    }
