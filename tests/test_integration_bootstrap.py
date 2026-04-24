from __future__ import annotations

from types import SimpleNamespace

from app.services import integration_bootstrap


def test_build_integration_bootstrap_summary_marks_required_oidc_blocker(monkeypatch):
    fake_settings = SimpleNamespace(
        OIDC_CLIENT_ID=None,
        KEYCLOAK_CLIENT_ID="",
        OIDC_ISSUER_URL=None,
        KEYCLOAK_URL="",
        EVENT_BUS_ENABLED=False,
        EVENT_BUS_PROVIDER="memory",
        EVENT_BUS_NATS_URL="nats://localhost:4222",
        SUPERGLUE_ENABLED=False,
        SUPERGLUE_BASE_URL=None,
        SUPERGLUE_REST_URL=None,
        SUPERGLUE_AUTH_TOKEN=None,
        CRM_CORE_BASE_URL="http://localhost:5600",
        CRM_SALES_BASE_URL="http://localhost:5700",
        CRM_SERVICE_BASE_URL="http://localhost:5800",
    )
    monkeypatch.setattr(integration_bootstrap, "settings", fake_settings)
    monkeypatch.setattr(integration_bootstrap, "get_secret", lambda *args, **kwargs: None)

    summary = integration_bootstrap.build_integration_bootstrap_summary()

    assert "oidc" in summary["required_blockers"]
    probe_plan = {item["integration_key"]: item for item in summary["probe_plan"]}
    assert probe_plan["oidc"]["status"] == "blocked"
    assert "OIDC_CLIENT_ID or KEYCLOAK_CLIENT_ID" in probe_plan["oidc"]["blocked_by"]


def test_build_integration_bootstrap_summary_marks_superglue_ready(monkeypatch):
    fake_settings = SimpleNamespace(
        OIDC_CLIENT_ID="frontend",
        KEYCLOAK_CLIENT_ID="backend",
        OIDC_ISSUER_URL="http://keycloak/realms/dev",
        KEYCLOAK_URL="http://keycloak:8080",
        EVENT_BUS_ENABLED=True,
        EVENT_BUS_PROVIDER="nats",
        EVENT_BUS_NATS_URL="nats://nats:4222",
        SUPERGLUE_ENABLED=True,
        SUPERGLUE_BASE_URL="http://superglue:3011",
        SUPERGLUE_REST_URL=None,
        SUPERGLUE_AUTH_TOKEN=None,
        CRM_CORE_BASE_URL="http://localhost:5600",
        CRM_SALES_BASE_URL="http://localhost:5700",
        CRM_SERVICE_BASE_URL="http://localhost:5800",
    )

    def fake_secret(key: str, accessor: str = "system"):
        if key == "SUPERGLUE_AUTH_TOKEN":
            return "token"
        if key in {"OPENAI_API_KEY", "VOICE_OPENAI_API_KEY"}:
            return "voice"
        return None

    monkeypatch.setattr(integration_bootstrap, "settings", fake_settings)
    monkeypatch.setattr(integration_bootstrap, "get_secret", fake_secret)

    summary = integration_bootstrap.build_integration_bootstrap_summary()
    integrations = {item["integration_key"]: item for item in summary["integrations"]}

    assert integrations["superglue"]["status"] == "ready"
    assert integrations["event_bus_nats"]["status"] == "ready"
    probe_plan = {item["integration_key"]: item for item in summary["probe_plan"]}
    assert probe_plan["superglue"]["status"] == "ready"
    assert probe_plan["superglue"]["probe_kind"] == "http_get_authenticated"
    assert probe_plan["superglue"]["target"] == "http://superglue:3011/health"
    assert probe_plan["event_bus_nats"]["command_hint"] == "nats server check --server nats://nats:4222"


def test_build_integration_probe_plan_distinguishes_disabled_and_ready(monkeypatch):
    fake_settings = SimpleNamespace(
        OIDC_CLIENT_ID="frontend",
        KEYCLOAK_CLIENT_ID="backend",
        OIDC_ISSUER_URL="http://keycloak/realms/dev",
        KEYCLOAK_URL="http://keycloak:8080",
        EVENT_BUS_ENABLED=False,
        EVENT_BUS_PROVIDER="memory",
        EVENT_BUS_NATS_URL="nats://localhost:4222",
        SUPERGLUE_ENABLED=False,
        SUPERGLUE_BASE_URL=None,
        SUPERGLUE_REST_URL=None,
        SUPERGLUE_AUTH_TOKEN=None,
        CRM_CORE_BASE_URL="http://crm-core:5600",
        CRM_SALES_BASE_URL="http://crm-sales:5700",
        CRM_SERVICE_BASE_URL="http://crm-service:5800",
    )

    def fake_secret(key: str, accessor: str = "system"):
        if key in {"OPENAI_API_KEY", "VOICE_OPENAI_API_KEY"}:
            return "voice"
        return None

    monkeypatch.setattr(integration_bootstrap, "settings", fake_settings)
    monkeypatch.setattr(integration_bootstrap, "get_secret", fake_secret)

    summary = integration_bootstrap.build_integration_bootstrap_summary()
    probe_plan = {item["integration_key"]: item for item in summary["probe_plan"]}

    assert probe_plan["oidc"]["status"] == "ready"
    assert probe_plan["oidc"]["target"] == "http://keycloak/realms/dev/.well-known/openid-configuration"
    assert probe_plan["event_bus_nats"]["status"] == "disabled"
    assert probe_plan["superglue"]["status"] == "disabled"
    assert probe_plan["voice"]["status"] == "ready"
    assert probe_plan["crm_downstream"]["status"] == "ready"
    assert "curl -fsS http://crm-core:5600/health" in probe_plan["crm_downstream"]["command_hint"]
