"""Schemas für Präferenzkalkulationen."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class BomComponent(BaseModel):
    component_id: str
    origin: str
    value: float
    originating: bool


class PreferenceCalculationRequest(BaseModel):
    tenant_id: str
    bill_of_materials_id: str
    agreement_code: str
    components: List[BomComponent]
    ruleset_override: Optional[str] = Field(default=None, description="Optional alternative ruleset")


class PreferenceCalculationResponse(BaseModel):
    qualifies: bool
    originating_value_percent: float
    remarks: Optional[str]
    calculation_details: dict = Field(default_factory=dict)
