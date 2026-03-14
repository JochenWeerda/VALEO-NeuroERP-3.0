"""
Quality-Lot-Price Binding Models — Wave 3 AP5
Verbindet Qualitaetsprotokoll mit Charge (Partie), Preis und Freigabe.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class LotQualityProfile(BaseModel):
    lot_id: str
    acceptance_id: str | None = None
    contract_id: str | None = None
    protocol_id: str | None = None
    tenant_id: str
    moisture_pct: float | None = None
    impurities_pct: float | None = None
    protein_pct: float | None = None
    hl_weight: float | None = None
    overall_grade: Literal["A", "B", "C", "rejected"] | None = None
    price_deduction_pct: float = 0.0
    approval_status: Literal["pending", "approved", "rejected"] = "pending"
    schema_version: int = 1


class QualityPriceDeductionRule(BaseModel):
    rule_id: str
    parameter: str  # e.g. "moisture_pct"
    threshold: float
    deduction_pct_per_unit: float
    max_deduction_pct: float
    applies_to: list[str] = []  # article IDs, empty = all


class QualityReleaseDecision(BaseModel):
    lot_id: str
    protocol_id: str
    decision: Literal["approve", "reject", "hold"]
    decided_by: str
    decided_at: str
    reason: str | None = None
    price_deduction_applied_pct: float = 0.0
    schema_version: int = 1


def compute_price_deduction(
    profile: LotQualityProfile,
    rules: list[QualityPriceDeductionRule],
) -> float:
    """Compute total price deduction % based on quality profile values and rules."""
    total_deduction = 0.0

    for rule in rules:
        value = getattr(profile, rule.parameter, None)
        if value is None:
            continue
        if value > rule.threshold:
            excess = value - rule.threshold
            raw_deduction = excess * rule.deduction_pct_per_unit
            capped_deduction = min(raw_deduction, rule.max_deduction_pct)
            total_deduction += capped_deduction

    return total_deduction
