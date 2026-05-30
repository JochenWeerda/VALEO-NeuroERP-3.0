"""Pydantic schemas for the docflow domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


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
    tax_rate: float
    line_total_net: float
    line_total_tax: float
    line_total_gross: float


class DocflowHeaderOut(BaseModel):
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


class DocflowCreateRequest(BaseModel):
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
    expected_version: Optional[int] = Field(default=None, ge=1)
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

