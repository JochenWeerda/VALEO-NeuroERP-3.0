"""Pydantic schemas for Finance Read-Models (stable versioned contracts).

These are the server-side pre-aggregated cockpit KPI schemas.
schema_version fields are part of the stable API contract — never change
without a Wave decision.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class FinanceReadModelsOut(BaseSchema):
    """Generic open schema for settlement-cockpit and position-exposure endpoints."""
    model_config = ConfigDict(extra="allow")


# ── AP-Invoice Cockpit ────────────────────────────────────────────────────────

class APInvoiceBucket(BaseModel):
    status: str
    count: int
    total_amount: float = 0.0


class APInvoiceCockpitReadModel(BaseModel):
    tenant_id: str
    buckets: list[APInvoiceBucket]
    total_count: int
    pending_approval_count: int
    ready_to_post_count: int
    overdue_count: int
    schema_version: int = 1


# ── Payment-Run Cockpit ───────────────────────────────────────────────────────

class PaymentRunCockpitReadModel(BaseModel):
    tenant_id: str
    draft_count: int
    approved_count: int
    executed_count: int
    total_pending_amount: float = 0.0
    schema_version: int = 1


# ── Process Observation ───────────────────────────────────────────────────────

class WorkflowInstanceSummary(BaseModel):
    process_key: str
    running_count: int
    waiting_count: int
    completed_today: int = 0
    failed_count: int = 0


class WorkflowStepSlaSummary(BaseModel):
    step_key: str
    timeout_hours: int | None = None
    escalation_roles: list[str] = Field(default_factory=list)


class WorkflowSlaProfile(BaseModel):
    process_key: str
    escalatable_steps: int = 0
    step_sla: list[WorkflowStepSlaSummary] = Field(default_factory=list)


class ProcessObservationReadModel(BaseModel):
    tenant_id: str
    workflow_instances: list[WorkflowInstanceSummary]
    sla_profiles: list[WorkflowSlaProfile] = Field(default_factory=list)
    total_running: int
    total_waiting: int
    overdue_instances: int = 0
    schema_version: int = 1


# ── Cash Closing ─────────────────────────────────────────────────────────────

class CashClosingTotals(BaseModel):
    cash_expected: float = 0.0
    cash_counted: float = 0.0
    cash_difference: float = 0.0
    card_expected: float = 0.0
    card_counted: float = 0.0
    card_difference: float = 0.0
    paypal_expected: float = 0.0
    paypal_counted: float = 0.0
    paypal_difference: float = 0.0
    b2b_expected: float = 0.0
    gross_total: float = 0.0


class CashClosingPosting(BaseModel):
    journal_entry_id: str | None = None
    journal_entry_number: str | None = None
    posted_at: str | None = None
    posting_status: str | None = None


class CashClosingImportContext(BaseModel):
    import_batch_id: str | None = None
    import_source_label: str | None = None
    imported_at: str | None = None


class CashClosingReferenceContext(BaseModel):
    tse_transaction_count: int = 0
    source_document_refs: list[str] = Field(default_factory=list)


class CashClosingExceptionFlags(BaseModel):
    has_difference: bool = False
    has_import_gap: bool = False
    has_missing_posting: bool = False


class CashClosingSnapshot(BaseModel):
    id: str
    closing_date: str | None = None
    location_id: str | None = None
    location_name: str | None = None
    cash_register_id: str | None = None
    cash_register_name: str | None = None
    operator_name: str | None = None
    source: str = "POS"
    workflow_status: str = "draft"
    currency: str = "EUR"
    totals: CashClosingTotals
    posting: CashClosingPosting
    import_context: CashClosingImportContext
    reference_context: CashClosingReferenceContext
    exception_flags: CashClosingExceptionFlags


class CashClosingReadModel(BaseModel):
    tenant_id: str
    items: list[CashClosingSnapshot] = Field(default_factory=list)
    total_count: int
    schema_version: int = 1


class CashClosingAnalysisBucket(BaseModel):
    key: str
    count: int


class CashClosingAnalysisReadModel(BaseModel):
    tenant_id: str
    total_count: int
    exception_count: int
    balanced_count: int
    missing_posting_count: int
    difference_count: int
    import_context_count: int
    top_exception_operators: list[CashClosingAnalysisBucket]
    top_exception_dates: list[CashClosingAnalysisBucket]
    schema_version: int = 1


class CashClosingReportingBucket(BaseModel):
    period_key: str
    closing_count: int
    gross_total: float = 0.0
    exception_count: int = 0
    difference_total: float = 0.0
    missing_posting_count: int = 0


class CashClosingReportingReadModel(BaseModel):
    tenant_id: str
    periods: list[CashClosingReportingBucket]
    total_count: int
    total_gross: float = 0.0
    total_difference: float = 0.0
    schema_version: int = 1


# ── Projection Infrastructure ─────────────────────────────────────────────────

class ProjectionRebuildEntry(BaseModel):
    projection_key: str
    item_count: int = 0


class ProjectionRebuildResult(BaseModel):
    tenant_id: str
    rebuilt_at: str
    projections: list[ProjectionRebuildEntry] = Field(default_factory=list)
    schema_version: int = 1


class ProjectionStatusEntry(BaseModel):
    projection_key: str
    item_count: int = 0
    cached: bool = True
    cursor_status: str | None = None
    cursor_source: str | None = None
    cursor_updated_at: str | None = None
    last_processed_event_id: str | None = None


class ProjectionStatusReadModel(BaseModel):
    tenant_id: str
    projection_count: int = 0
    persisted_snapshot_count: int = 0
    persisted_cursor_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    last_rebuilt_at: str | None = None
    last_snapshot_at: str | None = None
    last_cursor_advanced_at: str | None = None
    last_processed_event_id: str | None = None
    projections: list[ProjectionStatusEntry] = Field(default_factory=list)
    schema_version: int = 1
