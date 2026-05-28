"""Pydantic schemas for the tax keys domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class TaxKeyCreate(BaseModel):
    """Schema for creating a tax key"""
    code: str = Field(..., max_length=2, description="Tax key code (1-2 digits)")
    bezeichnung: str = Field(..., max_length=100, description="Tax key description")
    steuersatz: Decimal = Field(..., ge=0, le=100, description="Tax rate in percent")
    ustva_position: str = Field(..., max_length=10, description="UStVA position code")
    ustva_bezeichnung: str = Field(..., max_length=200, description="UStVA description")
    intracom: bool = Field(default=False, description="Intracommunity delivery (EU)")
    export: bool = Field(default=False, description="Export outside EU")
    reverse_charge: bool = Field(default=False, description="Reverse charge mechanism")
    gueltig_von: date = Field(..., description="Valid from date")
    gueltig_bis: Optional[date] = Field(None, description="Valid until date")
    notizen: Optional[str] = Field(None, max_length=500, description="Internal notes")
    debit_account: Optional[str] = Field(None, max_length=20, description="Debit account for tax")
    credit_account: Optional[str] = Field(None, max_length=20, description="Credit account for tax")
    country: str = Field(default="DE", max_length=2, description="Country code (ISO 3166-1 alpha-2)")
    region: Optional[str] = Field(None, max_length=50, description="Region/state if applicable")
    active: bool = Field(default=True, description="Active status")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v):
        if not v.isdigit() or len(v) > 2:
            raise ValueError('Code must be 1-2 digits')
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str):
        v = (v or "").strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('country must be ISO 3166-1 alpha-2 (e.g. DE)')
        return v

    @field_validator('gueltig_bis')
    @classmethod
    def validate_valid_until(cls, v, info):
        gueltig_von = info.data.get("gueltig_von")
        if v is not None and gueltig_von is not None and v < gueltig_von:
            raise ValueError('gueltig_bis must be >= gueltig_von')
        return v

    @field_validator('reverse_charge')
    @classmethod
    def validate_reverse_charge_rate(cls, v, info):
        steuersatz = info.data.get("steuersatz")
        if v and steuersatz is not None and Decimal(str(steuersatz)) != Decimal("0"):
            raise ValueError('reverse_charge requires steuersatz = 0')
        return v


class TaxKeyUpdate(BaseModel):
    """Schema for updating a tax key"""
    bezeichnung: Optional[str] = Field(None, max_length=100)
    steuersatz: Optional[Decimal] = Field(None, ge=0, le=100)
    ustva_position: Optional[str] = Field(None, max_length=10)
    ustva_bezeichnung: Optional[str] = Field(None, max_length=200)
    intracom: Optional[bool] = None
    export: Optional[bool] = None
    reverse_charge: Optional[bool] = None
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    notizen: Optional[str] = Field(None, max_length=500)
    debit_account: Optional[str] = Field(None, max_length=20)
    credit_account: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=2)
    region: Optional[str] = Field(None, max_length=50)
    active: Optional[bool] = None

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError('country must be ISO 3166-1 alpha-2 (e.g. DE)')
        return v


class TaxKeyResponse(BaseModel):
    """Response schema for tax key"""
    id: str
    code: str
    bezeichnung: str
    steuersatz: Decimal
    ustva_position: str
    ustva_bezeichnung: str
    intracom: bool
    export: bool
    reverse_charge: bool
    gueltig_von: date
    gueltig_bis: Optional[date]
    notizen: Optional[str]
    debit_account: Optional[str]
    credit_account: Optional[str]
    country: str
    region: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime

