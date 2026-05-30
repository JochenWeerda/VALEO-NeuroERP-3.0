"""Pydantic schemas for the Finance domain.

Covers closing, credit limits, collaterals, payment suggestions, buchungsuebergabe,
close-readiness, journal entries, financial reports.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Period Closing ────────────────────────────────────────────────────────────

class ClosingCalculateOut(BaseModel):
    """Result of a period closing calculation run."""
    model_config = {"extra": "allow"}


class ClosingApproveOut(BaseModel):
    """Result of closing approval action."""
    model_config = {"extra": "allow"}


# ── Credit Limits ─────────────────────────────────────────────────────────────

class CreditLimitOut(BaseModel):
    id: Optional[str] = None
    partner_name: Optional[str] = None
    credit_limit: Optional[float] = None
    used_credit: Optional[float] = None
    currency: Optional[str] = None


# ── Collaterals ───────────────────────────────────────────────────────────────

class CollateralOut(BaseModel):
    """Security / collateral item (Pfandrecht, Bürgschaft)."""
    model_config = {"extra": "allow"}


# ── Payment Suggestions ───────────────────────────────────────────────────────

class PaymentSuggestionOut(BaseModel):
    """Open creditor item due within N days."""
    model_config = {"extra": "allow"}


# ── Buchungsübergabe Export ───────────────────────────────────────────────────

class BuchungsuebergabeExportOut(BaseModel):
    success: bool = True
    dateiname: str
    von: str
    bis: str
    anzahl_buchungen: int
    summe_soll: float
    summe_haben: float
    message: str


# ── Close Readiness ───────────────────────────────────────────────────────────

class CloseReadinessOut(BaseModel):
    status: str
    current_period: str
    checklist_completion_pct: int
    open_reconciliation_items: int
    open_accruals: int
    sign_off_status: str
    blocking_items: list[str] = Field(default_factory=list)
    last_updated: str


# ── Journal Entries ───────────────────────────────────────────────────────────

class JournalEntryLineOut(BaseModel):
    id: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    debit: Optional[float] = None
    credit: Optional[float] = None
    description: Optional[str] = None
    cost_center: Optional[str] = None


class JournalEntryOut(BaseModel):
    id: str
    tenant_id: Optional[str] = None
    entry_number: Optional[str] = None
    entry_date: Optional[str] = None
    description: Optional[str] = None
    document_number: Optional[str] = None
    status: Optional[str] = None
    total_debit: Optional[float] = None
    total_credit: Optional[float] = None
    lines: list[JournalEntryLineOut] = Field(default_factory=list)
    created_at: Optional[str] = None


# ── Financial Reports ─────────────────────────────────────────────────────────

class FinancialReportLineOut(BaseModel):
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    amount: Optional[float] = None
    prior_year_amount: Optional[float] = None
    change_pct: Optional[float] = None


class FinancialReportOut(BaseModel):
    report_type: str
    period: Optional[str] = None
    tenant_id: Optional[str] = None
    lines: list[FinancialReportLineOut] = Field(default_factory=list)
    total: Optional[float] = None
    generated_at: Optional[str] = None
