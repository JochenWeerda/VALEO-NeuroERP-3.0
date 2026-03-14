"""
Wave-16 Contract Tests: Aggregate Ownership Register

AP1: AggregateDefinition — Struktur, schema_version, Pflichtfelder
AP2: Alle 8 Aggregat-Typen registriert mit korrekten Besitzern
AP3: Command-Katalog-Konsistenz — alle 9 Catalog-Commands zeigen auf registrierte Aggregate
AP4: Read-Model-Ownership — get_read_model_owner() für alle bekannten Projektionsschlüssel
AP5: get_aggregates_by_domain() — finance / agrar korrekt getrennt
AP6: validate_command_aggregate_consistency() + get_aggregate_definition() Fehlerfall
"""
from __future__ import annotations

import pytest

from app.core.aggregate_registry import (
    AggregateDefinition,
    get_aggregate_definition,
    get_aggregate_registry,
    get_aggregates_by_domain,
    get_command_owner,
    get_read_model_owner,
    validate_command_aggregate_consistency,
)
from app.core.business_commands import build_core_command_catalog


# ---------------------------------------------------------------------------
# AP1: AggregateDefinition Struktur
# ---------------------------------------------------------------------------

def test_aggregate_definition_schema_version():
    registry = get_aggregate_registry()
    for defn in registry:
        assert defn.schema_version == 1


def test_aggregate_definition_has_required_fields():
    registry = get_aggregate_registry()
    for defn in registry:
        assert defn.aggregate_type
        assert defn.business_domain
        assert defn.description
        assert isinstance(defn.allowed_commands, list)
        assert isinstance(defn.read_model_keys, list)
        assert isinstance(defn.agent_tools, list)


def test_registry_returns_list_of_aggregate_definitions():
    registry = get_aggregate_registry()
    assert all(isinstance(d, AggregateDefinition) for d in registry)


# ---------------------------------------------------------------------------
# AP2: Alle erwarteten Aggregat-Typen vorhanden mit korrekten Besitzern
# ---------------------------------------------------------------------------

def test_ap_invoice_is_registered_under_finance():
    defn = get_aggregate_definition("ap_invoice")
    assert defn.business_domain == "finance"


def test_harvest_acceptance_is_registered_under_agrar():
    defn = get_aggregate_definition("harvest_acceptance")
    assert defn.business_domain == "agrar"


def test_quality_protocol_is_registered_under_agrar():
    defn = get_aggregate_definition("quality_protocol")
    assert defn.business_domain == "agrar"


def test_agrar_settlement_is_registered_under_agrar():
    defn = get_aggregate_definition("agrar_settlement")
    assert defn.business_domain == "agrar"


def test_payment_run_is_registered_under_finance():
    defn = get_aggregate_definition("payment_run")
    assert defn.business_domain == "finance"


def test_direct_debit_run_is_registered_under_finance():
    defn = get_aggregate_definition("direct_debit_run")
    assert defn.business_domain == "finance"


def test_contract_is_registered_under_agrar():
    defn = get_aggregate_definition("contract")
    assert defn.business_domain == "agrar"


def test_journal_entry_is_registered_under_finance():
    defn = get_aggregate_definition("journal_entry")
    assert defn.business_domain == "finance"


def test_registry_has_eight_aggregates():
    assert len(get_aggregate_registry()) == 8


# ---------------------------------------------------------------------------
# AP3: Command-Katalog-Konsistenz
# ---------------------------------------------------------------------------

def test_all_catalog_commands_reference_registered_aggregates():
    catalog = build_core_command_catalog()
    registry = {defn.aggregate_type for defn in get_aggregate_registry()}
    for cmd in catalog:
        assert cmd.aggregate_type in registry, (
            f"Command '{cmd.command_name}' zeigt auf nicht-registriertes "
            f"Aggregat '{cmd.aggregate_type}'"
        )


def test_all_catalog_commands_appear_in_registry_allowed_commands():
    catalog = build_core_command_catalog()
    for cmd in catalog:
        owner = get_command_owner(cmd.command_name)
        assert owner is not None, (
            f"Command '{cmd.command_name}' hat keinen Aggregat-Besitzer im Register"
        )
        assert owner.aggregate_type == cmd.aggregate_type


def test_approve_ap_invoice_owner_is_ap_invoice():
    owner = get_command_owner("ApproveAPInvoice")
    assert owner is not None
    assert owner.aggregate_type == "ap_invoice"


def test_execute_payment_run_owner_is_payment_run():
    owner = get_command_owner("ExecutePaymentRun")
    assert owner is not None
    assert owner.aggregate_type == "payment_run"
    assert owner.agent_tools == []  # blockiert


def test_unknown_command_owner_returns_none():
    assert get_command_owner("DeleteEverything") is None


# ---------------------------------------------------------------------------
# AP4: Read-Model-Ownership
# ---------------------------------------------------------------------------

def test_ap_invoice_cockpit_owned_by_ap_invoice():
    owner = get_read_model_owner("ap-invoice-cockpit")
    assert owner is not None
    assert owner.aggregate_type == "ap_invoice"


def test_payment_run_cockpit_owned_by_payment_run():
    owner = get_read_model_owner("payment-run-cockpit")
    assert owner is not None
    assert owner.aggregate_type == "payment_run"


def test_unknown_read_model_returns_none():
    assert get_read_model_owner("nonexistent-cockpit") is None


def test_ap_invoice_has_read_model_key():
    defn = get_aggregate_definition("ap_invoice")
    assert "ap-invoice-cockpit" in defn.read_model_keys


# ---------------------------------------------------------------------------
# AP5: get_aggregates_by_domain
# ---------------------------------------------------------------------------

def test_finance_domain_has_four_aggregates():
    finance = get_aggregates_by_domain("finance")
    types = {d.aggregate_type for d in finance}
    assert "ap_invoice" in types
    assert "payment_run" in types
    assert "direct_debit_run" in types
    assert "journal_entry" in types
    assert len(finance) == 4


def test_agrar_domain_has_four_aggregates():
    agrar = get_aggregates_by_domain("agrar")
    types = {d.aggregate_type for d in agrar}
    assert "harvest_acceptance" in types
    assert "quality_protocol" in types
    assert "agrar_settlement" in types
    assert "contract" in types
    assert len(agrar) == 4


def test_unknown_domain_returns_empty_list():
    assert get_aggregates_by_domain("sales") == []


# ---------------------------------------------------------------------------
# AP6: validate_command_aggregate_consistency + KeyError bei unbekanntem Aggregat
# ---------------------------------------------------------------------------

def test_validate_command_aggregate_consistency_correct():
    assert validate_command_aggregate_consistency("ApproveAPInvoice", "ap_invoice") is True


def test_validate_command_aggregate_consistency_wrong_aggregate():
    assert validate_command_aggregate_consistency("ApproveAPInvoice", "payment_run") is False


def test_validate_command_aggregate_consistency_unknown_command():
    assert validate_command_aggregate_consistency("UnknownCommand", "ap_invoice") is False


def test_get_aggregate_definition_raises_key_error_for_unknown():
    with pytest.raises(KeyError, match="nicht im Register"):
        get_aggregate_definition("shadow_model")


def test_e2e_chain_positions_are_ordered_correctly():
    """Aggregat-Positionen in der E2E-Kette müssen konsistent 1–6 sein."""
    registry = get_aggregate_registry()
    positioned = [d for d in registry if d.e2e_chain_position is not None]
    positions = sorted(d.e2e_chain_position for d in positioned)
    assert positions == list(range(1, len(positions) + 1))


def test_payment_run_has_no_agent_tools_blocked():
    defn = get_aggregate_definition("payment_run")
    assert defn.agent_tools == []


def test_direct_debit_run_has_no_agent_tools_blocked():
    defn = get_aggregate_definition("direct_debit_run")
    assert defn.agent_tools == []
