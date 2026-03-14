"""
Cross-domain process reference models for contract -> acceptance -> quality -> settlement.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProcessReferenceChain(BaseModel):
    contract_id: str | None = None
    harvest_acceptance_id: str | None = None
    weighing_ticket_id: str | None = None
    quality_protocol_id: str | None = None
    settlement_id: str | None = None
    charge_id: str | None = None
    supplier_id: str | None = None
    article_id: str | None = None


class ProcessReferenceContext(BaseModel):
    process_key: str = Field(min_length=1)
    chain: ProcessReferenceChain
    anchor_entity: str = Field(min_length=1)
    anchor_id: str = Field(min_length=1)
    canonical_process_definition_key: str | None = None
    canonical_anchor_entity: str | None = None


def build_process_reference_context(
    *,
    process_key: str,
    anchor_entity: str,
    anchor_id: str,
    contract_id: str | None = None,
    harvest_acceptance_id: str | None = None,
    weighing_ticket_id: str | None = None,
    quality_protocol_id: str | None = None,
    settlement_id: str | None = None,
    charge_id: str | None = None,
    supplier_id: str | None = None,
    article_id: str | None = None,
    canonical_process_definition_key: str | None = None,
    canonical_anchor_entity: str | None = None,
) -> ProcessReferenceContext:
    return ProcessReferenceContext(
        process_key=process_key,
        anchor_entity=anchor_entity,
        anchor_id=anchor_id,
        canonical_process_definition_key=canonical_process_definition_key,
        canonical_anchor_entity=canonical_anchor_entity,
        chain=ProcessReferenceChain(
            contract_id=contract_id,
            harvest_acceptance_id=harvest_acceptance_id,
            weighing_ticket_id=weighing_ticket_id,
            quality_protocol_id=quality_protocol_id,
            settlement_id=settlement_id,
            charge_id=charge_id,
            supplier_id=supplier_id,
            article_id=article_id,
        ),
    )
