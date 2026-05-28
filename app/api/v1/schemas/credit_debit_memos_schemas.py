"""Auto-generated domain schemas for credit debit memos.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class CreditDebitMemosOut(BaseSchema):
    """Response schema for credit debit memos endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class CreditMemoCreate(BaseModel):
    """Request-Modell für Credit Memo Erstellung"""
    supplierId: str = Field(..., description="Lieferanten-ID")
    invoiceId: Optional[str] = Field(None, description="Referenz-Rechnung (optional)")
    settlementId: Optional[str] = Field(None, description="Referenz-Settlement fuer Korrekturen (optional)")
    correctionMode: Optional[str] = Field(None, description="Korrekturmodus, z.B. CREDIT_NOTE")
    memoDate: str = Field(..., description="Gutschriftsdatum (YYYY-MM-DD)")
    reason: str = Field(..., min_length=10, description="Grund für Gutschrift (min. 10 Zeichen)")
    notes: Optional[str] = None
    items: List[MemoItem] = Field(..., min_length=1, description="Gutschrifts-Positionen")


class DebitMemoCreate(BaseModel):
    """Request-Modell für Debit Memo Erstellung"""
    supplierId: str = Field(..., description="Lieferanten-ID")
    invoiceId: Optional[str] = Field(None, description="Referenz-Rechnung (optional)")
    settlementId: Optional[str] = Field(None, description="Referenz-Settlement fuer Korrekturen (optional)")
    correctionMode: Optional[str] = Field(None, description="Korrekturmodus, z.B. DEBIT_MEMO")
    memoDate: str = Field(..., description="Belastungsdatum (YYYY-MM-DD)")
    reason: str = Field(..., min_length=10, description="Grund für Belastung (min. 10 Zeichen)")
    notes: Optional[str] = None
    items: List[MemoItem] = Field(..., min_length=1, description="Belastungs-Positionen")


class SettlementRequest(BaseModel):
    """Request-Modell für Verrechnung"""
    invoiceIds: List[str] = Field(..., min_length=1, description="Rechnungs-IDs zur Verrechnung")


class CreditMemoResponse(BaseModel):
    """Response-Modell für Credit Memo"""
    id: str
    number: str
    supplierId: str
    supplierName: str
    invoiceId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    settlementId: Optional[str] = None
    correctionMode: Optional[str] = None
    memoDate: str
    netAmount: float
    taxAmount: float
    grossAmount: float
    status: str
    reason: str
    notes: Optional[str] = None
    settled: bool = False
    settledInvoiceIds: Optional[List[str]] = None
    booked: bool = False
    journalRef: Optional[str] = None
    # Gap 004: Freigabe vor Buchung bei settlement-verknüpften Memos
    approvalStatus: Optional[str] = None
    approvedAt: Optional[str] = None
    approvedBy: Optional[str] = None


class DebitMemoResponse(BaseModel):
    """Response-Modell für Debit Memo"""
    id: str
    number: str
    supplierId: str
    supplierName: str
    invoiceId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    settlementId: Optional[str] = None
    correctionMode: Optional[str] = None
    memoDate: str
    netAmount: float
    taxAmount: float
    grossAmount: float
    status: str
    reason: str
    notes: Optional[str] = None
    settled: bool = False
    settledInvoiceIds: Optional[List[str]] = None
    booked: bool = False
    journalRef: Optional[str] = None
    approvalStatus: Optional[str] = None
    approvedAt: Optional[str] = None
    approvedBy: Optional[str] = None

