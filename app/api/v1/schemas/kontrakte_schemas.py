"""Pydantic schemas for the Kontrakte (contract) domain."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ConfigDict as _ConfigDict

from app.api.v1.schemas.base import BaseSchema

# ── Type aliases ──────────────────────────────────────────────────────────────

ContractType = Literal["EINKAUF", "ZUKAUF", "VERKAUF"]
StatusType = Literal["OFFEN", "ERLEDIGT", "STORNIERT", "GELOESCHT"]
QuantityType = Literal["GESAMTKONTRAKT", "EINZELMENGEN"]


class KontraktOut(BaseSchema):
    """Typed response schema for KontraktOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class KonContractLineIn(BaseModel):
    line_id: Optional[str] = None
    position_no: int = Field(..., ge=1)
    article_id: str
    description1: Optional[str] = None
    description2: Optional[str] = None
    qty_contract: float = Field(..., ge=0)
    price_unit: Optional[str] = None
    unit_price: Optional[float] = None
    discount_pct: Optional[float] = None
    surcharge: Optional[float] = None
    rebate_type: Optional[str] = None
    is_bio: bool = False
    is_matif: bool = False


class KonContractIn(BaseModel):
    contract_no: Optional[str] = None
    contract_type: ContractType
    branch_id: Optional[str] = None
    clerk_id: Optional[str] = None
    party_id: str
    debitor_kto: Optional[str] = None
    kreditor_kto: Optional[str] = None
    contract_date: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    quantity_type: QuantityType = "GESAMTKONTRAKT"
    total_quantity: float = Field(default=0, ge=0)
    unit: str = "kg"
    allow_overdelivery: bool = False
    status: StatusType = "OFFEN"
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    conditions_json: Optional[dict[str, Any]] = None
    pricing_model: Optional[str] = None
    min_price: Optional[float] = None
    premium_type: Optional[str] = None
    premium_value: Optional[float] = None
    basis_reference: Optional[str] = None
    pricing_window_from: Optional[datetime] = None
    pricing_window_to: Optional[datetime] = None
    lines: list[KonContractLineIn] = Field(default_factory=list)


class KonContractMovementOut(BaseModel):
    movement_id: str
    contract_id: str
    line_id: Optional[str] = None
    order_no: Optional[str] = None
    delivery_note_no: Optional[str] = None
    invoice_no: Optional[str] = None
    movement_date: Optional[datetime] = None
    quantity: float
    unit_price: Optional[float] = None
    route_no: Optional[str] = None
    is_invoiced: bool
    is_archived: bool


class KonContractMovementIn(BaseModel):
    line_id: str
    order_no: Optional[str] = None
    delivery_note_no: Optional[str] = None
    invoice_no: Optional[str] = None
    movement_date: Optional[datetime] = None
    quantity: float = Field(..., gt=0)
    unit_price: Optional[float] = None
    route_no: Optional[str] = None
    is_invoiced: bool = False
    is_archived: bool = False


class AmendmentCreate(BaseModel):
    type: str
    reason: str
    changes: dict = {}
    created_by: str = "system"


class AmendmentResponse(BaseModel):
    id: str
    contract_id: str
    type: str
    reason: str
    status: str
    changes: dict
    tenant_id: str
    created_by: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AmendmentTemplateResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    body_markdown: Optional[str]
    sections_schema: Optional[dict]
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AmendmentStatusUpdate(BaseModel):
    status: Literal["approved", "rejected"]


class DispositionCreate(BaseModel):
    kontrakt_nr: str
    kontrakt_pos_nr: int = 1
    geplantes_lieferdatum: Optional[str] = None
    lieferdatum: Optional[str] = None
    menge: float
    freigabe: bool = False
    wiegeschein_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class DispositionOut(DispositionCreate):
    id: str
    disposition_nr: int
    status: str  # OFFEN / FREIGEGEBEN / GELIEFERT / STORNIERT

