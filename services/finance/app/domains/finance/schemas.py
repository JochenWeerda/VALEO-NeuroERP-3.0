"""Pydantic schemas for Finance domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_number: str
    name: str
    category: str | None = None
    currency: str = "EUR"


class JournalEntryBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    account_id: str
    description: str
    amount: Decimal
    currency: str = "EUR"
    period: str = Field(pattern=r"^\d{4}-\d{2}$")
    document_id: str | None = None
    user_id: str = Field(alias="userId")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    description: str
    amount: Decimal
    currency: str
    period: str
    document_id: str | None
    posted_at: datetime
    created_by: str


class OpenItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_number: str
    customer_id: str
    customer_name: str
    amount: Decimal
    currency: str
    due_date: date
    status: str


class JournalEntryResponse(BaseModel):
    entry: JournalEntryRead
    audit_hash: str


class AccountsResponse(BaseModel):
    items: List[AccountRead]


class JournalEntriesResponse(BaseModel):
    items: List[JournalEntryRead]


class OpenItemsResponse(BaseModel):
    items: List[OpenItemRead]


# GoBD Compliance Schemas
class DocumentNumberGap(BaseModel):
    """A gap in the document number sequence."""
    expected_number: str
    actual_next: str | None = None
    gap_size: int
    document_type: str


class GoBDComplianceResult(BaseModel):
    """Result of GoBD compliance check."""
    is_compliant: bool
    document_type: str
    total_documents: int
    first_number: str | None = None
    last_number: str | None = None
    gaps: List[DocumentNumberGap]
    gap_count: int
    checked_at: datetime
    notes: str = ""


class GoBDComplianceResponse(BaseModel):
    """Response for GoBD compliance check across all document types."""
    overall_compliant: bool
    checks: List[GoBDComplianceResult]
    audit_hash_chain_valid: bool
    total_gaps: int
    recommendation: str


class PeriodCompleteness(BaseModel):
    """Completeness check for a single accounting period."""
    period: str  # e.g. "2026-01"
    journal_entry_count: int
    open_items_count: int
    has_gaps: bool
    gap_count: int
    is_closed: bool
    balance_check: str  # "balanced" or "imbalanced"
    notes: str = ""


class GoBDMonthlyReport(BaseModel):
    """Monthly GoBD compliance report."""
    report_id: str
    tenant_id: str
    report_period: str  # e.g. "2026-01"
    generated_at: datetime
    compliance_status: str  # "compliant", "warning", "violation"

    # Document completeness
    periods: List[PeriodCompleteness]

    # Number sequences
    document_gaps: List[DocumentNumberGap]
    total_gap_count: int

    # Audit trail
    audit_hash_chain_valid: bool
    audit_entry_count: int

    # Cancellations / Reversals
    cancellation_count: int
    cancellations_with_reversal: int
    cancellations_missing_reversal: int

    # Summary
    overall_score: float  # 0-100
    recommendations: List[str]
    signature: str  # Hash of the report for integrity


# ── Storno / Reversal Schemas ─────────────────────────────────────────────

class StornoRequest(BaseModel):
    """Request to cancel (stornieren) a journal entry with automatic reversal booking."""
    journal_entry_id: str = Field(description="ID of the journal entry to cancel")
    reason: str = Field(min_length=5, description="Mandatory cancellation reason (GoBD)")
    user_id: str = Field(description="User performing the cancellation")


class StornoResult(BaseModel):
    """Result of a Storno operation with the reversal (Gegenbuchung)."""
    original_entry_id: str
    original_description: str
    original_amount: Decimal
    reversal_entry_id: str
    reversal_description: str
    reversal_amount: Decimal
    reversal_audit_hash: str
    reason: str
    cancelled_by: str
    cancelled_at: datetime
    is_gobd_compliant: bool = True
    note: str = "Storno mit automatischer Gegenbuchung gemäß GoBD §146 AO"