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


def test_registry_has_45_tools(svc: McpToolRegistryService) -> None:
    assert len(svc.list_tools()) == 51


def test_bonus_and_query_import_writes_are_catalogued(svc: McpToolRegistryService) -> None:
    bonus = svc.get_tool("reporting.bonus.calculate")
    assert bonus["scope"] == "reporting:write"
    assert bonus["audit"] == "write"
    qimp = svc.get_tool("reporting.query.import_signed")
    assert qimp["scope"] == "reporting:write"
    assert qimp["audit"] == "write"


def test_tour_and_po_save_writes_are_catalogued(svc: McpToolRegistryService) -> None:
    tour = svc.get_tool("logistik.tour.anlegen")
    assert tour["scope"] == "logistics:write"
    assert tour["audit"] == "write"
    po = svc.get_tool("einkauf.bestellung.speichern")
    assert po["scope"] == "einkauf:write"
    assert po["audit"] == "write"


def test_ap_freigabe_tools_are_catalogued(svc: McpToolRegistryService) -> None:
    propose = svc.get_tool("finance.ap_invoice.propose")
    assert propose["scope"] == "finance:write"
    assert propose["risk_class"] == "high"
    assert propose["human_approval_required"] is True
    freigeben = svc.get_tool("finance.ap_invoice.freigeben")
    assert freigeben["scope"] == "finance:write"
    assert freigeben["risk_class"] == "high"
    assert freigeben["human_approval_required"] is True
    assert freigeben["idempotent"] is True


def test_sanctions_and_fracht_writes_are_catalogued(svc: McpToolRegistryService) -> None:
    sanctions = svc.get_tool("compliance.sanctions.check")
    assert sanctions["scope"] == "compliance:write"
    assert sanctions["audit"] == "write"
    fracht = svc.get_tool("logistik.frachttabelle.anlegen")
    assert fracht["scope"] == "logistics:write"
    assert fracht["audit"] == "write"


def test_inventur_propose_opening_is_catalogued(svc: McpToolRegistryService) -> None:
    tool = svc.get_tool("lager.inventur.propose_opening")
    assert tool["scope"] == "lager:write"
    assert tool["risk_class"] == "high"
    assert tool["human_approval_required"] is True
    assert tool["idempotent"] is False
    assert tool["audit"] == "write"


def test_lead_qualify_and_po_send_are_catalogued(svc: McpToolRegistryService) -> None:
    lead = svc.get_tool("crm.lead.qualify")
    assert lead["scope"] == "crm:write"
    assert lead["audit"] == "write"
    assert lead["risk_class"] == "medium"
    po = svc.get_tool("einkauf.bestellung.versenden")
    assert po["scope"] == "einkauf:write"
    assert po["audit"] == "write"
    assert po["risk_class"] == "medium"


def test_customer_open_is_catalogued(svc: McpToolRegistryService) -> None:
    tool = svc.get_tool("crm.customer.open")
    assert tool["scope"] == "crm:read"
    assert tool["risk_class"] == "low"
    assert tool["idempotent"] is True
    assert tool["audit"] == "read"


def test_remaining_ops_writes_are_catalogued(svc: McpToolRegistryService) -> None:
    sync = svc.get_tool("produktion.control.sync")
    assert sync["scope"] == "ops:write"
    assert sync["audit"] == "write"
    assert sync["risk_class"] == "medium"
    cal = svc.get_tool("planung.calendar.reproject")
    assert cal["scope"] == "planung:write"
    assert cal["audit"] == "write"
    mde = svc.get_tool("mobile.sync.process_pending")
    assert mde["scope"] == "mobile:write"
    assert mde["audit"] == "write"


def test_all_tools_have_data_classification(svc: McpToolRegistryService) -> None:
    valid = {"PUBLIC", "EU_ONLY", "LOCAL_ONLY", "SYNTHETIC_ALLOWED", "NEVER"}
    for tool in svc.list_tools():
        dc = tool.get("data_classification")
        assert dc in valid, f"{tool['tool_id']}: invalid data_classification {dc!r}"


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
