"""
Helpers to build process reference contexts for the agrar kernel path.
"""

from __future__ import annotations

from app.core.process_references import ProcessReferenceContext, build_process_reference_context
from app.core.settlement_compatibility import (
    CANONICAL_SETTLEMENT_AGGREGATE,
    CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
)


def build_agrar_settlement_reference_context(
    *,
    settlement_id: str,
    contract_id: str | None = None,
    harvest_acceptance_id: str | None = None,
    weighing_ticket_id: str | None = None,
    quality_protocol_id: str | None = None,
    charge_id: str | None = None,
    supplier_id: str | None = None,
    article_id: str | None = None,
) -> ProcessReferenceContext:
    return build_process_reference_context(
        process_key="settlement",
        anchor_entity="settlement",
        anchor_id=settlement_id,
        canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
        canonical_anchor_entity=CANONICAL_SETTLEMENT_AGGREGATE,
        settlement_id=settlement_id,
        contract_id=contract_id,
        harvest_acceptance_id=harvest_acceptance_id,
        weighing_ticket_id=weighing_ticket_id,
        quality_protocol_id=quality_protocol_id,
        charge_id=charge_id,
        supplier_id=supplier_id,
        article_id=article_id,
    )
