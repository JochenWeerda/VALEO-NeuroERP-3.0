"""Auto-generated domain schemas for ebilanz elster.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class EbilanzElsterOut(BaseSchema):
    """Response schema for ebilanz elster endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class EBilanzExportRequest(BaseModel):
    wirtschaftsjahr: int
    bilanzart: str  # HGB / IFRS / EStG
    berichtsperiode_von: str  # ISO date
    berichtsperiode_bis: str  # ISO date
    steuernummer: str
    finanzamt_nr: str


class EBilanzValidierungsRequest(BaseModel):
    """Dict of XBRL element names → values submitted for validation."""
    felder: dict[str, Any]


class EricReadinessOut(BaseModel):
    status: str
    repo_contract_ready: bool
    xbrl_taxonomie_version: str
    supported_paths: list[str]
    external_gates: list[str]
    next_action: str


class UStVARequest(BaseModel):
    steuernummer: str = Field(..., description="Steuernummer des Unternehmens")
    finanzamt_nr: str = Field(..., description="Finanzamtsnummer (4-stellig)")
    voranmeldungszeitraum: str = Field(..., description="Monat YYYY-MM oder Quartal YYYY-Q1/Q2/Q3/Q4")
    # Kennzahlen gemäß § 18 UStG Anlage UR
    kz_81_steuerpflichtige_ums_19: float = Field(0.0, description="KZ 81: Steuerpfl. Umsätze 19 %")
    kz_86_steuerpflichtige_ums_7:  float = Field(0.0, description="KZ 86: Steuerpfl. Umsätze 7 %")
    kz_35_innergemeinschaftliche_lieferungen: float = Field(0.0, description="KZ 41/86: Innergem. Lieferungen")
    kz_66_vorsteuer_rechnungen:    float = Field(0.0, description="KZ 66: Vorsteuer aus Rechnungen")
    kz_61_einfuhrvorsteuer:        float = Field(0.0, description="KZ 61: Einfuhrumsatzsteuervorsteuer")
    kz_67_innergemeinschaftlicher_erwerb_vorsteuer: float = Field(0.0, description="KZ 67: Vorsteuer innergem. Erwerb")
    dauerfreistellung: bool = Field(False, description="§ 18 Abs. 2 UStG: Dauerfreist. von Voranmeldung")

