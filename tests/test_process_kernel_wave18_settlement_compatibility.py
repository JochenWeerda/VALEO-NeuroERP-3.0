"""
Wave-18 Follow-up Contract Tests: Settlement Compatibility

Expliziter Vertrag fuer `settlement` (legacy) vs. `agrar_settlement` (canonical).
"""

from __future__ import annotations

from app.core.agrar_process_references import build_agrar_settlement_reference_context
from app.core.e2e_chain import E2EProcessChain
from app.core.settlement_compatibility import (
    CANONICAL_SETTLEMENT_AGGREGATE,
    CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
    LEGACY_SETTLEMENT_ANCHOR,
    LEGACY_SETTLEMENT_PROCESS_KEY,
    get_settlement_compatibility_contract,
    is_legacy_settlement_process_key,
    to_canonical_settlement_aggregate,
)


def test_settlement_compatibility_contract_exposes_legacy_and_canonical_names():
    contract = get_settlement_compatibility_contract()
    assert contract.legacy_process_key == LEGACY_SETTLEMENT_PROCESS_KEY
    assert contract.legacy_anchor_entity == LEGACY_SETTLEMENT_ANCHOR
    assert contract.canonical_aggregate_type == CANONICAL_SETTLEMENT_AGGREGATE
    assert (
        contract.canonical_process_definition_key
        == CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY
    )


def test_to_canonical_settlement_aggregate_maps_legacy_name():
    assert to_canonical_settlement_aggregate("settlement") == "agrar_settlement"
    assert to_canonical_settlement_aggregate("ap_invoice") == "ap_invoice"


def test_agrar_settlement_reference_context_keeps_legacy_surface_and_sets_canonical_metadata():
    ctx = build_agrar_settlement_reference_context(
        settlement_id="SET-1",
        contract_id="KON-1",
    )
    assert ctx.process_key == "settlement"
    assert ctx.anchor_entity == "settlement"
    assert ctx.canonical_process_definition_key == "quality_to_settlement"
    assert ctx.canonical_anchor_entity == "agrar_settlement"


def test_e2e_chain_settlement_link_carries_canonical_aggregate_type():
    chain = E2EProcessChain(
        tenant_id="t1",
        settlement_id="SET-1",
    )
    settlement_link = next(link for link in chain.links() if link.aggregate_type == "settlement")
    assert settlement_link.canonical_aggregate_type == "agrar_settlement"
    assert settlement_link.present is True


def test_is_legacy_settlement_process_key_true_only_for_legacy_name():
    assert is_legacy_settlement_process_key("settlement") is True
    assert is_legacy_settlement_process_key("agrar_settlement") is False
