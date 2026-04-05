from __future__ import annotations

import pytest

from app.api.v1.endpoints.webhooks import WebhookCreate
from app.core.mcp_tool_contracts import MCPToolContract, MCPToolKategorie
from app.core.outbound_security import OutboundTargetPolicyError, validate_outbound_http_target
from app.services.neuro_tool_execution import NeuroToolExecutionService


def _contract(tool_name: str, api_endpoint: str) -> MCPToolContract:
    return MCPToolContract(
        tool_name=tool_name,
        domain="process",
        operation="demo",
        beschreibung="demo",
        kategorie=MCPToolKategorie.LESEN,
        api_endpoint=api_endpoint,
    )


def test_outbound_policy_rejects_private_ip_targets():
    with pytest.raises(OutboundTargetPolicyError):
        validate_outbound_http_target("http://10.0.0.5/hook")


def test_outbound_policy_rejects_internal_hostname_suffixes():
    with pytest.raises(OutboundTargetPolicyError):
        validate_outbound_http_target("https://billing.internal/hook")


def test_outbound_policy_honors_explicit_allowlists(monkeypatch):
    monkeypatch.setattr(
        "app.core.outbound_security.settings.OUTBOUND_HTTP_ALLOWED_DOMAINS",
        ["example.com"],
        raising=False,
    )
    assert validate_outbound_http_target("https://api.example.com/hook") == "https://api.example.com/hook"

    with pytest.raises(OutboundTargetPolicyError):
        validate_outbound_http_target("https://api.other.example/hook")


def test_outbound_policy_can_allow_loopback_only_when_explicitly_enabled():
    assert (
        validate_outbound_http_target("http://localhost:3011/v1/health", allow_loopback_hosts=True)
        == "http://localhost:3011/v1/health"
    )

    with pytest.raises(OutboundTargetPolicyError):
        validate_outbound_http_target("https://billing.internal/hook", allow_loopback_hosts=True)

    with pytest.raises(OutboundTargetPolicyError):
        validate_outbound_http_target("http://10.0.0.5/hook", allow_loopback_hosts=True)


def test_webhook_create_uses_shared_outbound_policy():
    with pytest.raises(ValueError):
        WebhookCreate(url="http://localhost:8080/hook", event_area="auftrag")


def test_external_tool_execution_rejects_private_base_url():
    service = NeuroToolExecutionService()
    result = service.execute_contract(
        _contract("valeo_demo_external", "GET /api/v1/demo/{tenant_id}"),
        parameters={},
        tenant_id="tenant-9",
        context={"external_base_url": "http://127.0.0.1:9000"},
    )

    assert result["mode"] == "fallback_contract"
    assert result["fallback_reason"].startswith("transport_error:")
    assert "nicht erlaubt" in result["fallback_reason"]
