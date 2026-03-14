from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class TaxKeyCreate(BaseModel):
    code: str = Field(..., max_length=2, description="Tax key code (1-2 digits)")
    bezeichnung: str = Field(..., max_length=100, description="Tax key description")
    steuersatz: Decimal = Field(..., ge=0, le=100, description="Tax rate in percent")
    ustva_position: str = Field(..., max_length=10, description="UStVA position code")
    ustva_bezeichnung: str = Field(..., max_length=200, description="UStVA description")
    intracom: bool = Field(default=False, description="Intracommunity delivery (EU)")
    export: bool = Field(default=False, description="Export outside EU")
    reverse_charge: bool = Field(default=False, description="Reverse charge mechanism")
    gueltig_von: date = Field(..., description="Valid from date")
    gueltig_bis: date | None = Field(None, description="Valid until date")
    notizen: str | None = Field(None, max_length=500, description="Internal notes")
    debit_account: str | None = Field(None, max_length=20, description="Debit account for tax")
    credit_account: str | None = Field(None, max_length=20, description="Credit account for tax")
    country: str = Field(default="DE", max_length=2, description="Country code (ISO 3166-1 alpha-2)")
    region: str | None = Field(None, max_length=50, description="Region/state if applicable")
    active: bool = Field(default=True, description="Active status")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str):
        if not v.isdigit() or len(v) > 2:
            raise ValueError("Code must be 1-2 digits")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str):
        v = (v or "").strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError("country must be ISO 3166-1 alpha-2 (e.g. DE)")
        return v

    @field_validator("gueltig_bis")
    @classmethod
    def validate_valid_until(cls, v, info):
        gueltig_von = info.data.get("gueltig_von")
        if v is not None and gueltig_von is not None and v < gueltig_von:
            raise ValueError("gueltig_bis must be >= gueltig_von")
        return v

    @field_validator("reverse_charge")
    @classmethod
    def validate_reverse_charge_rate(cls, v, info):
        steuersatz = info.data.get("steuersatz")
        if v and steuersatz is not None and Decimal(str(steuersatz)) != Decimal("0"):
            raise ValueError("reverse_charge requires steuersatz = 0")
        return v
