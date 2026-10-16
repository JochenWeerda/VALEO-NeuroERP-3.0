"""Canonical DocFlow request/response models shared by every adapter."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict as _ConfigDict
from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.docflow_screen_context import DocflowScreenContextIn, DocflowScreenContextOut


class DocflowOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


class DocflowItemOut(BaseModel):
    id: str
    line_number: int
    source_line_id: Optional[str] = None
    article_number: str
    description: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    discount_percent: float
    tax_code: Optional[str] = None
    expense_account: Optional[str] = None
    tax_rate: float
    line_total_net: float
    line_total_tax: float
    line_total_gross: float


class DocflowHeaderOut(BaseModel):
    screen_context: Optional[DocflowScreenContextOut] = None
    id: str
    tenant_id: str
    doc_type: str
    doc_number: str
    status: str
    source_system: str
    source_ref: Optional[str] = None
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str
    total_net: float
    total_tax: float
    total_gross: float
    document_date: datetime
    posting_date: Optional[date] = None
    version: int
    created_at: datetime
    updated_at: datetime
    items: list[DocflowItemOut] = Field(default_factory=list)
    pos_compliance: Optional[dict[str, Any]] = None
    printed_at: Optional[datetime] = None
    printed_by: Optional[str] = None
    print_count: int = 0
    exported_at: Optional[datetime] = None
    exported_by: Optional[str] = None


class DocflowConvertRequest(BaseModel):
    target_doc_type: str = Field(..., min_length=3, max_length=40)
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    quantities_by_source_item_id: dict[str, float] = Field(default_factory=dict)
    expected_version: Optional[int] = Field(default=None, ge=1)
    created_by: Optional[str] = Field(default=None, max_length=100)
    dry_run: bool = False


class DocflowPostRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    expected_version: Optional[int] = Field(default=None, ge=1)
    posting_date: Optional[date] = None
    posted_by: Optional[str] = Field(default=None, max_length=100)


class DocflowReleaseRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    expected_version: Optional[int] = Field(default=None, ge=1)
    released_by: Optional[str] = Field(default=None, max_length=100)


class DocflowReverseRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    reason: str = Field(..., min_length=3, max_length=300)
    expected_version: Optional[int] = Field(default=None, ge=1)
    reversed_by: Optional[str] = Field(default=None, max_length=100)


class DocflowRecordPrintRequest(BaseModel):
    printed_by: Optional[str] = Field(default=None, max_length=100)


class DocflowRecordExportRequest(BaseModel):
    exported_by: Optional[str] = Field(default=None, max_length=100)


class DocflowCommandResult(BaseModel):
    command: str
    idempotent_hit: bool = False
    source_doc_id: Optional[str] = None
    target_doc_id: Optional[str] = None
    posting_id: Optional[str] = None
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DocflowLineInput(BaseModel):
    article_number: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = None
    quantity: float = Field(default=0, ge=0)
    unit: Optional[str] = Field(default=None, max_length=20)
    unit_price: float = Field(default=0, ge=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    # Steuerschluessel des Mandanten (tax_keys.code). Mit ihm kommt der Satz vom Server; ein abweichend
    # mitgeschickter Satz wird abgelehnt. Ohne ihn gilt der Satz der Anfrage — gebucht wird so nicht.
    tax_code: Optional[str] = Field(default=None, max_length=2)
    tax_rate: Optional[float] = Field(default=None, ge=0, le=100)
    # Nur Einkaufsbelege: Aufwandskonto der Position; leer = das des Steuerschluessels.
    expense_account: Optional[str] = Field(default=None, max_length=20)
    batch_id: Optional[str] = Field(default=None, max_length=64)
    charge: Optional[str] = Field(default=None, max_length=64)


class PosComplianceInput(BaseModel):
    terminal_id: str = Field(..., min_length=1, max_length=60)
    cash_register_id: Optional[str] = Field(default=None, max_length=60)
    transaction_type: str = Field(default="sale", min_length=4, max_length=20)
    payment_breakdown: Optional[dict[str, Any]] = None
    tse_transaction_id: str = Field(..., min_length=1, max_length=120)
    tse_signature: str = Field(..., min_length=1)
    tse_signature_counter: Optional[int] = None
    transaction_started_at: datetime
    transaction_ended_at: datetime
    receipt_issued_at: datetime
    dsfinvk_export_batch_id: Optional[str] = Field(default=None, max_length=120)
    correction_type: Optional[str] = Field(default=None, max_length=20)
    original_header_id: Optional[str] = Field(default=None, max_length=36)


class DocflowCreateRequest(BaseModel):
    screen_context: Optional[DocflowScreenContextIn] = None
    doc_type: str = Field(..., min_length=3, max_length=40)
    doc_number: str = Field(..., min_length=1, max_length=80)
    status: str = Field(default="draft", min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    created_by: Optional[str] = Field(default=None, max_length=100)
    items: list[DocflowLineInput] = Field(default_factory=list)
    pos_compliance: Optional[PosComplianceInput] = None
    idempotency_key: Optional[str] = Field(default=None, min_length=8, max_length=120)


class DocflowUpdateRequest(BaseModel):
    expected_version: int = Field(..., ge=1, strict=True)
    idempotency_key: str = Field(..., min_length=8, max_length=120)
    status: Optional[str] = Field(default=None, min_length=3, max_length=20)
    source_system: Optional[str] = Field(default=None, max_length=40)
    source_ref: Optional[str] = Field(default=None, max_length=80)
    customer_id: Optional[str] = None
    supplier_id: Optional[str] = None
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    document_date: Optional[datetime] = None
    posting_date: Optional[date] = None
    updated_by: Optional[str] = Field(default=None, max_length=100)
    items: Optional[list[DocflowLineInput]] = None
    pos_compliance: Optional[PosComplianceInput] = None


class DocflowApprovalRequest(BaseModel):
    action: str = Field(..., pattern="^(post|reverse)$")
    reason: Optional[str] = Field(default=None, max_length=300)


class DocflowApprovalDecision(BaseModel):
    granted: bool
    note: Optional[str] = Field(default=None, max_length=300)
