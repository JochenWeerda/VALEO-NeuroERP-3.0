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
