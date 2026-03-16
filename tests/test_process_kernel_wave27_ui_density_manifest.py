from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.command_catalog import router as command_catalog_router
from app.core.ui_density_manifest import build_ui_density_manifest, get_ui_density_entry


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(command_catalog_router, prefix="/api/v1")
    return TestClient(app)


def test_ui_density_manifest_derives_finance_domains_from_command_catalog() -> None:
    manifest = build_ui_density_manifest()

    finance_entry = next(entry for entry in manifest.entries if entry.page_domain == "finance-approval")

    assert finance_entry.requires_human_confirmation is True
    assert finance_entry.requires_explainability is True
    assert finance_entry.recommended_density == "dense"
    assert "ApproveAPInvoice" in finance_entry.command_names
    assert finance_entry.policy_rule_ids == ["ap.approval.rule"]
    assert finance_entry.approval_roles == ["approver", "manager"]
    assert finance_entry.explainability_statuses == ["approval-required"]
    assert finance_entry.source_contracts == ["ap_approval_status", "explainability", "policy_decisions"]


def test_get_ui_density_entry_returns_agrar_settlement_hint() -> None:
    entry = get_ui_density_entry("agrar-settlement")

    assert entry is not None
    assert entry.page_domain == "agrar-settlement"
    assert "CreateAgrarSettlement" in entry.command_names
    assert "ENTWURF" in entry.approval_statuses
    assert "VERBUCHT" in entry.approval_statuses
    assert "abteilungsleiter" in entry.approval_actor_types
    assert "settlement_approval" in entry.source_contracts


def test_get_ui_density_entry_returns_finance_policy_domains() -> None:
    closing_entry = get_ui_density_entry("finance-closing")
    vat_entry = get_ui_density_entry("finance-vat")

    assert closing_entry is not None
    assert closing_entry.policy_rule_ids == ["finance.closing.period"]
    assert closing_entry.requires_explainability is True
    assert "controller" in closing_entry.approval_roles

    assert vat_entry is not None
    assert vat_entry.policy_rule_ids == ["finance.vat_return.submission"]
    assert "submitted" in vat_entry.approval_statuses


def test_ui_density_manifest_endpoint_returns_schema() -> None:
    client = _build_client()

    response = client.get("/api/v1/commands/ui-density-manifest")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == 1
    finance_entry = next(entry for entry in payload["entries"] if entry["page_domain"] == "finance-approval")

    assert finance_entry["requires_explainability"] is True
    assert finance_entry["policy_rule_ids"] == ["ap.approval.rule"]
