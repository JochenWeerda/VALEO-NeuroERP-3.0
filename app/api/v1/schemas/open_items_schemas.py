"""Auto-generated domain schemas for open items.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class OpenItemsOut(BaseSchema):
    """Response schema for open items endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class BatchSettleRequest(BaseModel):
    """Request for batch settlement (Sammelausgleich)"""
    items: List[OpenItemSettlement]


class BatchSettleResponse(BaseModel):
    """Result of batch settlement"""
    results: List[SettlementResult]
    success_count: int
    error_count: int
    errors: List[BatchSettleError]


class OpenItemCreate(OpenItemBase):
    pass


class OpenItemUpdate(BaseModel):
    konto_nr: Optional[str] = None
    konto_name: Optional[str] = None
    konto_typ: Optional[str] = None
    op_status: Optional[str] = None
    rechnungsnr: Optional[str] = None
    rechnungsdatum: Optional[date] = None
    faelligkeit: Optional[date] = None
    valuta: Optional[date] = None
    op_betrag: Optional[Decimal] = None
    saldo: Optional[Decimal] = None
    offen: Optional[Decimal] = None
    op_text: Optional[str] = None
    waehrung: Optional[str] = None
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    skonto_prozent: Optional[Decimal] = None
    skonto_bis: Optional[date] = None
    mahn_stufe: Optional[int] = None
    zahlbar: Optional[bool] = None
    letzte_bewegung_am: Optional[date] = None
    kredit_limit: Optional[Decimal] = None
    kv_limit: Optional[Decimal] = None
    sperre_grund: Optional[str] = None


class OpenItemListResponse(BaseModel):
    items: List[OpenItem]
    summary: dict

