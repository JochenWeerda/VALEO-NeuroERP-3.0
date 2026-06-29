"""Tests for the AgentMaskContract generation endpoint and helper."""

import pytest

from app.api.v1.endpoints.mask_screen_definition import _generate_agent_contract


MINIMAL_SCREEN = {
    "schemaVersion": 1,
    "id": "crm/customer-360",
    "domain": "crm",
    "mode": "detail",
    "title": "Kundenstamm",
}

FULL_SCREEN = {
    "schemaVersion": 1,
    "id": "crm/customer-360",
    "domain": "crm",
    "mode": "detail",
    "title": "Kundenstamm",
    "fields": [
        {"key": "name", "label": "Name", "type": "text", "required": True},
        {"key": "iban", "label": "IBAN", "type": "text"},
        {"key": "email", "label": "E-Mail", "type": "text", "readOnly": True},
    ],
    "tabs": [
        {
            "key": "kontakt",
            "label": "Kontakt",
            "fields": [{"key": "phone", "label": "Telefon", "type": "text"}],
        }
    ],
    "actions": [
        {"key": "freigeben", "label": "Freigeben", "humanApprovalRequired": True, "auditReasonRequired": True},
        {"key": "loeschen", "label": "Loeschen", "dangerLevel": "destructive", "requiresConfirmation": True},
    ],
}


@pytest.mark.unit
def test_minimal_screen_generates_contract():
    contract = _generate_agent_contract(MINIMAL_SCREEN)
    assert contract["screenId"] == "crm/customer-360"
    assert contract["domain"] == "crm"
    assert contract["contractVersion"] == 1
    assert isinstance(contract["readableFields"], list)
    assert isinstance(contract["availableActions"], list)


@pytest.mark.unit
def test_readable_fields_includes_root_and_tab_fields():
    contract = _generate_agent_contract(FULL_SCREEN)
    assert "name" in contract["readableFields"]
    assert "iban" in contract["readableFields"]
    assert "phone" in contract["readableFields"]


@pytest.mark.unit
def test_readonly_fields_excluded_from_editable():
    contract = _generate_agent_contract(FULL_SCREEN)
    assert "name" in contract["editableFields"]
    assert "email" not in contract["editableFields"]


@pytest.mark.unit
def test_sensitive_field_detection():
    contract = _generate_agent_contract(FULL_SCREEN)
    assert "iban" in contract["sensitiveFields"]
    assert "name" not in contract["sensitiveFields"]


@pytest.mark.unit
def test_validation_rules_for_required_fields():
    contract = _generate_agent_contract(FULL_SCREEN)
    rules = {r["fieldKey"]: r for r in contract["validationRules"]}
    assert "name" in rules
    assert rules["name"]["severity"] == "blocking"
    assert "email" not in rules


@pytest.mark.unit
def test_actions_mapped_correctly():
    contract = _generate_agent_contract(FULL_SCREEN)
    actions = {a["key"]: a for a in contract["availableActions"]}
    assert actions["freigeben"]["requiresHumanApproval"] is True
    assert actions["loeschen"]["dangerLevel"] == "destructive"
    assert actions["loeschen"]["requiresConfirmation"] is True


@pytest.mark.unit
def test_audit_requirements_generated():
    contract = _generate_agent_contract(FULL_SCREEN)
    audit = {a["actionKey"]: a for a in contract["auditRequirements"]}
    assert "freigeben" in audit
    assert audit["freigeben"]["requiresReason"] is True
    assert "loeschen" not in audit


@pytest.mark.unit
def test_test_selectors_generated():
    contract = _generate_agent_contract(FULL_SCREEN)
    assert contract["testSelectors"]["screenRoot"] == '[data-testid="screen-crm/customer-360"]'
    assert contract["testSelectors"]["submitButton"] == '[data-testid="form-submit-btn"]'


@pytest.mark.unit
def test_explicit_agent_contract_overrides_generated():
    screen = {
        **FULL_SCREEN,
        "agentContract": {
            "businessPurpose": "Explizit gesetzt",
            "forbiddenAgentTasks": ["Kunden loeschen"],
            "examplePrompts": ["Zeige alle Kunden aus Bayern"],
        },
    }
    contract = _generate_agent_contract(screen)
    assert contract["businessPurpose"] == "Explizit gesetzt"
    assert "Kunden loeschen" in contract["forbiddenAgentTasks"]
    assert "Zeige alle Kunden aus Bayern" in contract["examplePrompts"]


@pytest.mark.unit
def test_primary_entity_derived_from_screen_id():
    contract = _generate_agent_contract(MINIMAL_SCREEN)
    assert contract["primaryEntity"] == "customer-360"


# ─── Readiness gate tests ────────────────────────────────────────────────────

from app.api.v1.endpoints.mask_screen_definition import _check_readiness  # noqa: E402

READY_SCREEN = {
    "schemaVersion": 1,
    "id": "crm/customer-360",
    "domain": "crm",
    "mode": "detail",
    "title": "Kundenstamm",
    "noWorkflowReason": "Verwaltungsmaske ohne eigenen Workflow.",
    "dataSources": [{"key": "entity", "endpoint": "/api/v1/crm/customers/{entity_id}"}],
    "tabs": [
        {
            "key": "auftraege",
            "label": "Auftraege",
            "tables": [
                {
                    "key": "recent_orders",
                    "label": "Auftraege",
                    "serverPagination": True,
                    "dataSourceKey": "entity",
                    "columns": [
                        {"key": "order_nr", "label": "Auftrag", "sortable": True},
                        {"key": "status", "label": "Status", "filterable": True},
                    ],
                }
            ],
        }
    ],
    "actions": [{"key": "edit", "label": "Bearbeiten", "dangerLevel": "safe", "permission": "crm.customer.update"}],
    "agentContract": {
        "businessPurpose": "CRM 360 Kundenstamm",
        "testSelectors": {"screenRoot": "[data-testid='crm-customer-360']"},
    },
}


@pytest.mark.unit
def test_readiness_all_gates_green():
    report = _check_readiness(READY_SCREEN)
    assert report["generatorReady"] is True
    assert report["errors"] == []
    assert report["warnings"] == []


@pytest.mark.unit
def test_readiness_fails_non_temporary():
    screen = {**READY_SCREEN, "adapter": {"type": "maskConfig", "temporary": True}}
    report = _check_readiness(screen)
    assert report["generatorReady"] is False
    assert any("non_temporary" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_fails_missing_datasources():
    screen = {k: v for k, v in READY_SCREEN.items() if k != "dataSources"}
    report = _check_readiness(screen)
    assert report["generatorReady"] is False
    assert any("data_sources" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_fails_unbound_server_table():
    screen = {
        **READY_SCREEN,
        "dataSources": [{"key": "other", "endpoint": "/api/v1/other"}],
    }
    report = _check_readiness(screen)
    assert report["generatorReady"] is False
    assert any("table_data_source_bound" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_fails_thin_table_columns():
    screen = {
        **READY_SCREEN,
        "tabs": [
            {
                "key": "auftraege",
                "label": "Auftraege",
                "tables": [
                    {
                        "key": "recent_orders",
                        "label": "Auftraege",
                        "serverPagination": True,
                        "dataSourceKey": "entity",
                        "columns": [
                            {"key": "id", "label": "ID"},
                            {"key": "name", "label": "Name"},
                        ],
                    }
                ],
            }
        ],
    }
    report = _check_readiness(screen)
    assert report["generatorReady"] is False
    assert any("table_columns_complete" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_fails_unclassified_action():
    screen = {**READY_SCREEN, "actions": [{"key": "delete", "label": "Loeschen"}]}
    report = _check_readiness(screen)
    assert report["generatorReady"] is False
    assert any("actions_classified" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_allows_explicit_stub_action():
    screen = {
        **READY_SCREEN,
        "actions": [{"key": "edit", "label": "Bearbeiten", "dangerLevel": "safe", "stubReason": "permission pending"}],
    }
    report = _check_readiness(screen)
    assert report["generatorReady"] is True
    assert not any("actions_classified" in e for e in report["errors"])


@pytest.mark.unit
def test_readiness_reports_advisory_warnings_without_blocking():
    screen = {
        **READY_SCREEN,
        "noWorkflowReason": "",
        "agentContract": {},
        "tabs": [
            {
                "key": "auftraege",
                "label": "Auftraege",
                "tables": [
                    {
                        "key": "recent_orders",
                        "label": "Auftraege",
                        "serverPagination": True,
                        "dataSourceKey": "entity",
                        "columns": [
                            {"key": "col1", "label": "Auftrag", "sortable": True},
                            {"key": "status", "label": "Status"},
                        ],
                    }
                ],
            }
        ],
    }
    report = _check_readiness(screen)
    assert report["generatorReady"] is True
    assert report["errors"] == []
    assert any("agent_contract" in w for w in report["warnings"])
    assert any("workflow_declared" in w for w in report["warnings"])
    assert any("stable_test_selectors" in w for w in report["warnings"])
    assert any("table_query_contract" in w for w in report["warnings"])


@pytest.mark.unit
def test_readiness_skips_table_gates_when_no_tables():
    screen = {k: v for k, v in READY_SCREEN.items() if k not in ("dataSources", "tabs")}
    report = _check_readiness(screen)
    sort_gate = next(g for g in report["gates"] if g["gate"] == "sort_whitelist")
    filter_gate = next(g for g in report["gates"] if g["gate"] == "filter_columns")
    assert sort_gate["passed"] is True
    assert filter_gate["passed"] is True
