from __future__ import annotations

from typing import Any, List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.api.v1.schemas.base import BaseSchema

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

