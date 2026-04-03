from app.integrations.adapters.superglue.tool_sync import (
    build_superglue_health_status,
    build_superglue_sync_status,
    build_superglue_tool_summary,
    list_superglue_tool_records,
)


def test_superglue_tool_sync_defaults_to_mapped_catalog():
    records = list_superglue_tool_records()

    assert len(records) >= 3
    assert any(item.valeo_contract_id == "superglue.document.search" for item in records)


def test_superglue_sync_status_surfaces_tool_count():
    status = build_superglue_sync_status()

    assert status.provider_key == "superglue"
    assert status.tool_count >= 3


def test_superglue_health_status_reports_missing_config_as_unhealthy(monkeypatch):
    monkeypatch.setattr("app.integrations.adapters.superglue.tool_sync.settings.SUPERGLUE_ENABLED", False)

    health = build_superglue_health_status()

    assert health.healthy is False


def test_superglue_tool_summary_serializes_records():
    summary = build_superglue_tool_summary()

    assert summary["provider_key"] == "superglue"
    assert summary["tool_count"] >= 3
