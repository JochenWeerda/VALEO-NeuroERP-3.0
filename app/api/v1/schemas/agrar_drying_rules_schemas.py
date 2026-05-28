"""Auto-generated domain schemas for agrar drying rules.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AgrarDryingRulesOut(BaseSchema):
    """Response schema for agrar drying rules endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class DryingRuleSetCreate(BaseModel):
    crop_code: str = Field(..., min_length=1, max_length=40)
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"] = Field(...)
    base_moisture_pct: float = Field(..., ge=0, le=100)
    rounding_mode: Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"] = Field(default="ROUND_NEAREST")
    clamp_mode: Literal["CLAMP_TO_MAX", "HARD_ERROR"] = Field(default="HARD_ERROR")
    min_moisture_pct: float = Field(default=0, ge=0, le=100)
    max_moisture_pct: float = Field(default=60, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Literal["INVOICE_WEIGHT", "NET_WEIGHT"] = Field(default="INVOICE_WEIGHT")
    contract_id: Optional[str] = Field(None, description="Verknüpfung zu Ankaufskontrakt (optional)")
    customer_id: Optional[str] = Field(None, description="Kunde für Sonderregelung (optional)")
    is_customer_specific: bool = Field(default=False)
    justification: Optional[str] = Field(None, description="Begründung für kundenspezifische Sonderregelungen (erforderlich wenn is_customer_specific=True)")
    document_id: Optional[str] = Field(None, max_length=64, description="DMS-Referenz für Tabelle/Formel-Dokument")

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetUpdate(BaseModel):
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Optional[Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"]] = None
    base_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    rounding_mode: Optional[Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"]] = None
    clamp_mode: Optional[Literal["CLAMP_TO_MAX", "HARD_ERROR"]] = None
    min_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    max_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Optional[Literal["INVOICE_WEIGHT", "NET_WEIGHT"]] = None
    contract_id: Optional[str] = None
    customer_id: Optional[str] = None
    is_customer_specific: Optional[bool] = None
    justification: Optional[str] = None
    document_id: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific is True and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific is True and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetOut(BaseModel):
    id: str
    crop_code: str
    site_id: Optional[str]
    valid_from: Optional[str]
    valid_to: Optional[str]
    version: int
    is_active: bool
    method: str
    base_moisture_pct: float
    rounding_mode: str
    clamp_mode: str
    min_moisture_pct: float
    max_moisture_pct: float
    start_threshold_moisture_pct: Optional[float]
    fee_basis: str
    created_at: str
    created_by: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]
    contract_id: Optional[str]
    customer_id: Optional[str]
    is_customer_specific: bool
    justification: Optional[str]
    document_id: Optional[str]


class DryingLookupRowCreate(BaseModel):
    rule_set_id: str
    moisture_pct: float = Field(..., ge=0, le=100, description="Feuchte in % (0.1-Schritte)")
    entzug_pct_points: float = Field(..., ge=0, description="Entzug in %-Punkten")
    loss_pct: float = Field(..., ge=0, le=100, description="Schwund in %")
    fee_value: Optional[float] = Field(None, ge=0, description="Trocknungskosten (optional)")
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = Field(None, description="Einheit der Trocknungskosten")


class DryingLookupRowUpdate(BaseModel):
    moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    entzug_pct_points: Optional[float] = Field(None, ge=0)
    loss_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_value: Optional[float] = Field(None, ge=0)
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = None


class DryingLookupRowOut(BaseModel):
    id: str
    rule_set_id: str
    moisture_pct: float
    entzug_pct_points: float
    loss_pct: float
    fee_value: Optional[float]
    fee_unit: Optional[str]
    created_at: str


class DryingFactorRangeCreate(BaseModel):
    rule_set_id: str
    from_moisture_incl: float = Field(..., ge=0, le=100, description="Von Feuchte in % (inklusive, 0.1-Schritte)")
    to_moisture_incl: float = Field(..., ge=0, le=100, description="Bis Feuchte in % (inklusive, 0.1-Schritte)")
    factor: float = Field(..., gt=0, description="Faktor für Schwundberechnung")

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl > self.to_moisture_incl:
            raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeUpdate(BaseModel):
    from_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    to_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    factor: Optional[float] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl is not None and self.to_moisture_incl is not None:
            if self.from_moisture_incl > self.to_moisture_incl:
                raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeOut(BaseModel):
    id: str
    rule_set_id: str
    from_moisture_incl: float
    to_moisture_incl: float
    factor: float
    created_at: str

