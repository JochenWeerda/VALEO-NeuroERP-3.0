"""
Wave-18 Contract Tests: Canonical Process Definitions

AP1: Maschinenlesbares Register fuer Kernprozesspfade
"""

from __future__ import annotations

import pytest

from app.core.canonical_process_definitions import (
    CanonicalProcessDefinition,
    get_canonical_process_definition,
    get_canonical_process_definitions,
    get_canonical_processes_by_domain,
    get_canonical_processes_by_workflow_key,
    get_canonical_processes_for_aggregate,
    validate_canonical_process_registry,
)


def test_registry_returns_canonical_process_definitions():
    registry = get_canonical_process_definitions()
    assert registry
    assert all(isinstance(defn, CanonicalProcessDefinition) for defn in registry)


def test_all_canonical_process_definitions_have_schema_version_1():
    for definition in get_canonical_process_definitions():
        assert definition.schema_version == 1


def test_wave18_register_contains_expected_process_keys():
    keys = {
        definition.process_definition_key
        for definition in get_canonical_process_definitions()
    }
    assert keys == {
        "contract_to_intake",
        "intake_to_quality",
        "quality_to_settlement",
        "settlement_to_finance",
    }


def test_contract_to_intake_definition_uses_contract_and_harvest_acceptance():
    definition = get_canonical_process_definition("contract_to_intake")
    assert definition.aggregate_sequence == ["contract", "harvest_acceptance"]
    assert definition.primary_aggregate_type == "harvest_acceptance"
    assert "contract.allocate" in definition.process_command_ids
    assert "FinalizeHarvestAcceptance" in definition.action_command_names


def test_quality_to_settlement_uses_agrar_settlement_without_shadow_alias():
    definition = get_canonical_process_definition("quality_to_settlement")
    assert definition.aggregate_sequence == ["quality_protocol", "agrar_settlement"]
    assert definition.primary_aggregate_type == "agrar_settlement"
    assert "settlement.create" in definition.process_command_ids
    assert "FinalizeAgrarSettlement" in definition.action_command_names


def test_settlement_to_finance_connects_finance_approval_path():
    definition = get_canonical_process_definition("settlement_to_finance")
    assert definition.aggregate_sequence == [
        "agrar_settlement",
        "ap_invoice",
        "journal_entry",
    ]
    assert definition.primary_aggregate_type == "ap_invoice"
    assert definition.workflow_process_keys == ["ap_invoice_approval"]
    assert definition.default_sla_policy_ids == ["sla-ap-approval"]


def test_get_canonical_processes_by_domain_separates_agrar_and_finance():
    agrar_keys = {
        definition.process_definition_key
        for definition in get_canonical_processes_by_domain("agrar")
    }
    finance_keys = {
        definition.process_definition_key
        for definition in get_canonical_processes_by_domain("finance")
    }
    assert agrar_keys == {
        "contract_to_intake",
        "intake_to_quality",
        "quality_to_settlement",
    }
    assert finance_keys == {"settlement_to_finance"}


def test_get_canonical_processes_for_aggregate_returns_all_touching_processes():
    process_keys = {
        definition.process_definition_key
        for definition in get_canonical_processes_for_aggregate("agrar_settlement")
    }
    assert process_keys == {"quality_to_settlement", "settlement_to_finance"}


def test_get_canonical_processes_by_workflow_key_maps_existing_workflow_keys():
    annahme = {
        definition.process_definition_key
        for definition in get_canonical_processes_by_workflow_key("annahme")
    }
    approval = {
        definition.process_definition_key
        for definition in get_canonical_processes_by_workflow_key("ap_invoice_approval")
    }
    assert annahme == {"contract_to_intake", "intake_to_quality"}
    assert approval == {"settlement_to_finance"}


def test_validate_canonical_process_registry_returns_no_reference_errors():
    assert validate_canonical_process_registry() == []


def test_get_canonical_process_definition_raises_for_unknown_key():
    with pytest.raises(KeyError, match="nicht im Register"):
        get_canonical_process_definition("mock_process")
