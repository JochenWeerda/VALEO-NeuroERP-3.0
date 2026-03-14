"""
Settlement Compatibility Contract - Wave 18 Follow-up

Expliziter Vertrag fuer den Legacy-/Canonical-Split zwischen
`settlement` (Prozess-/Referenzsprache) und `agrar_settlement`
(kanonischer Aggregattyp).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


LEGACY_SETTLEMENT_PROCESS_KEY = "settlement"
LEGACY_SETTLEMENT_ANCHOR = "settlement"
CANONICAL_SETTLEMENT_AGGREGATE = "agrar_settlement"
CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY = "quality_to_settlement"


class SettlementCompatibilityContract(BaseModel):
    legacy_process_key: str = Field(default=LEGACY_SETTLEMENT_PROCESS_KEY, min_length=1)
    legacy_anchor_entity: str = Field(default=LEGACY_SETTLEMENT_ANCHOR, min_length=1)
    canonical_aggregate_type: str = Field(
        default=CANONICAL_SETTLEMENT_AGGREGATE, min_length=1
    )
    canonical_process_definition_key: str = Field(
        default=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY, min_length=1
    )
    schema_version: int = 1


DEFAULT_SETTLEMENT_COMPATIBILITY = SettlementCompatibilityContract()


def get_settlement_compatibility_contract() -> SettlementCompatibilityContract:
    return DEFAULT_SETTLEMENT_COMPATIBILITY.model_copy()


def to_canonical_settlement_aggregate(aggregate_type: str) -> str:
    if aggregate_type == LEGACY_SETTLEMENT_ANCHOR:
        return CANONICAL_SETTLEMENT_AGGREGATE
    return aggregate_type


def is_legacy_settlement_process_key(process_key: str) -> bool:
    return process_key == LEGACY_SETTLEMENT_PROCESS_KEY
