"""Tests fuer MCP-ERP-TOOLS-001 Tool-Registry."""

import pytest
from pathlib import Path

from app.services.mcp_tool_registry_service import McpToolRegistryService, McpToolValidationError


@pytest.fixture()
def svc() -> McpToolRegistryService:
    return McpToolRegistryService()


def test_list_tools_returns_all(svc: McpToolRegistryService) -> None:
    tools = svc.list_tools()
    assert len(tools) >= 1
    for tool in tools:
        assert "tool_id" in tool
        assert "domain" in tool
        assert "scope" in tool


def test_list_tools_filter_domain(svc: McpToolRegistryService) -> None:
    crm_tools = svc.list_tools(domain="crm")
    assert all(t["domain"] == "crm" for t in crm_tools)
    assert len(crm_tools) >= 1


def test_list_tools_filter_risk_class(svc: McpToolRegistryService) -> None:
    low_tools = svc.list_tools(risk_class="low")
    assert all(t["risk_class"] == "low" for t in low_tools)


def test_get_tool_found(svc: McpToolRegistryService) -> None:
    tool = svc.get_tool("crm.customer.search")
    assert tool["tool_id"] == "crm.customer.search"
    assert tool["scope"] == "crm:read"
    assert tool["idempotent"] is True


def test_get_tool_not_found(svc: McpToolRegistryService) -> None:
    with pytest.raises(KeyError):
        svc.get_tool("does.not.exist")


def test_validate_all_no_errors(svc: McpToolRegistryService) -> None:
    errors = svc.validate_all()
    assert errors == [], f"Validation errors: {errors}"


def test_summary_structure(svc: McpToolRegistryService) -> None:
    summary = svc.summary()
    assert "total_tools" in summary
    assert "by_domain" in summary
    assert "by_risk_class" in summary
    assert summary["total_tools"] >= 1
    assert summary["validation_errors"] == []


def test_human_approval_tools_are_high_risk(svc: McpToolRegistryService) -> None:
    for tool in svc.list_tools():
        if tool.get("human_approval_required"):
            assert tool["risk_class"] in ("high", "critical"), (
                f"Tool {tool['tool_id']} requires human approval but is {tool['risk_class']}"
            )


def test_invalid_tool_raises_validation_error() -> None:
    import tempfile, yaml
    from pathlib import Path

    bad_registry = {
        "registry_id": "TEST",
        "tools": [
            {"tool_id": "bad.tool", "domain": "test", "name": "Bad", "scope": "test:read",
             "idempotent": True, "risk_class": "invalid_class", "audit": "read"}
        ]
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.dump(bad_registry, f)
        tmp_path = Path(f.name)
    try:
        svc = McpToolRegistryService(registry_path=tmp_path)
        errors = svc.validate_all()
        assert any("invalid_class" in e for e in errors)
    finally:
        tmp_path.unlink(missing_ok=True)
