from app.integrations.services.superglue_live_readiness import build_superglue_live_readiness


def test_superglue_live_readiness_surfaces_missing_credentials_and_placeholder_urls(monkeypatch):
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.APP_ENV", "staging")
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_EXECUTION_ENABLED", False)
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_REQUIRE_TENANT_SECRETS", True)
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_ALERT_ERROR_RATE_PCT", 7.5)
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_ALERT_OPEN_QUARANTINE_COUNT", 3)
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_RUN_RETENTION_DAYS", 45)
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_ARTIFACT_RETENTION_DAYS", 12)
    monkeypatch.setattr(
        "app.integrations.services.superglue_live_readiness.build_superglue_monitoring_summary",
        lambda tenant_id=None: {
            "run_count": 2,
            "average_latency_ms": 91,
            "total_cost_cents": 40,
            "quarantine": {"open_count": 1},
        },
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_live_readiness.list_superglue_connector_bindings",
        lambda tenant_id: [
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="document_search"),
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="finance_export"),
        ],
    )

    summary = build_superglue_live_readiness("tenant-a")

    assert summary["tenant_id"] == "tenant-a"
    assert summary["environment"] == "staging"
    assert summary["connector_count"] == 2
    assert summary["ready_connector_count"] == 0
    assert summary["blocked_connector_count"] == 2
    assert summary["policy"]["alert_error_rate_pct"] == 7.5
    assert summary["policy"]["run_retention_days"] == 45
    blocked = {item["connector_key"]: item for item in summary["connectors"]}
    assert blocked["document_search"]["uses_placeholder_url"] is True
    assert "missing_credentials" in blocked["document_search"]["blockers"]
    assert "apiKey" in blocked["document_search"]["missing_credential_fields"]
    assert "execute_mode_disabled" in blocked["finance_export"]["blockers"]
    assert summary["recommended_actions"]


def test_superglue_live_readiness_marks_connector_ready_when_credentials_and_url_are_real(monkeypatch):
    monkeypatch.setattr("app.integrations.services.superglue_live_readiness.settings.SUPERGLUE_EXECUTION_ENABLED", True)
    monkeypatch.setattr(
        "app.integrations.services.superglue_live_readiness.build_superglue_monitoring_summary",
        lambda tenant_id=None: {
            "run_count": 0,
            "average_latency_ms": 0,
            "total_cost_cents": 0,
            "quarantine": {"open_count": 0},
        },
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_live_readiness.list_superglue_connector_bindings",
        lambda tenant_id: [
            __import__("app.integrations.services.superglue_connector_registry", fromlist=["build_superglue_connector_binding"])
            .build_superglue_connector_binding(tenant_id=tenant_id, connector_key="finance_export"),
        ],
    )
    monkeypatch.setattr(
        "app.integrations.services.superglue_connector_registry.resolve_superglue_connector_value",
        lambda tenant_id, connector_key, field_name, fallback=None: {
            ("tenant-a", "finance_export", "SYSTEM_URL"): "https://finance.partner.example.com/api",
            ("tenant-a", "finance_export", "apiKey"): "live-key",
            ("tenant-a", "finance_export", "accessToken"): "live-token",
        }.get((tenant_id, connector_key, field_name), fallback),
    )

    summary = build_superglue_live_readiness("tenant-a")

    assert summary["ready_connector_count"] == 1
    assert summary["blocked_connector_count"] == 0
    assert summary["execute_ready_count"] == 1
    connector = summary["connectors"][0]
    assert connector["ready"] is True
    assert connector["blockers"] == []
