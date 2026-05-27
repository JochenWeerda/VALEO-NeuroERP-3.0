"""Schemas and helpers for the Closing Checklists domain (FIBU-CLS-01)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.explainability import ExplainabilityView
from app.core.policy_decisions import PolicyOverrideResolution


class ChecklistItem(BaseModel):
    item_code: str = Field(..., description="Item code (e.g., GL-001, AR-001)")
    description: str = Field(..., description="Item description")
    category: str = Field(..., description="Category: GL, AR, AP, BANK, TAX, REPORTS")
    validation_type: str = Field(..., description="Validation type: manual, automatic, query")
    validation_query: Optional[str] = Field(None, description="SQL query for automatic validation")
    required: bool = Field(default=True, description="Required for closing")
    responsible_role: str = Field(..., description="Responsible role (e.g., accountant, controller)")
    due_date_offset: int = Field(default=0, description="Days before period end")
    notes: Optional[str] = None


class ChecklistTemplateCreate(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    closing_type: str = Field(..., description="monthly, quarterly, yearly")
    items: List[ChecklistItem] = Field(..., min_length=1)
    active: bool = Field(default=True)


class ChecklistItemStatus(BaseModel):
    item_code: str
    status: str  # pending, in_progress, completed, failed, skipped
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    validation_result: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ClosingChecklistCreate(BaseModel):
    period: str = Field(..., description="Period in YYYY-MM format")
    closing_type: str = Field(..., description="monthly, quarterly, yearly")
    template_id: Optional[str] = None
    tenant_id: str = Field(default="system")


class ClosingChecklistResponse(BaseModel):
    id: str
    period: str
    closing_type: str
    template_id: Optional[str]
    status: str  # draft, in_progress, completed, blocked
    progress_percentage: float
    total_items: int
    completed_items: int
    required_items: int
    completed_required_items: int
    items: List[Dict[str, Any]]
    approval_status: str | None = None
    approval_can_close: bool = False
    approval_override_resolution: PolicyOverrideResolution | None = None
    approval_explainability: ExplainabilityView | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    completed_by: Optional[str]


class ClosingWorkspaceRequest(BaseModel):
    period: str
    closing_type: str
    tenant_id: str = "system"
    actor: str = "system"


class UpdateItemStatusRequest(BaseModel):
    item_code: str = Field(..., description="Item code")
    status: str = Field(..., description="pending, in_progress, completed, failed, skipped")
    completed_by: str = Field(..., description="User completing the item")
    notes: Optional[str] = None


def build_closing_checklist_response(row, *, items_data: list[dict[str, Any]]) -> ClosingChecklistResponse:
    status = str(row[4])
    can_close = status in {"approved", "completed"}
    return ClosingChecklistResponse(
        id=str(row[0]),
        period=str(row[1]),
        closing_type=str(row[2]),
        template_id=str(row[3]) if row[3] else None,
        status=status,
        progress_percentage=float(row[5]),
        total_items=int(row[6]),
        completed_items=int(row[7]),
        required_items=int(row[8]),
        completed_required_items=int(row[9]),
        items=items_data,
        approval_status=status,
        approval_can_close=can_close,
        approval_override_resolution=PolicyOverrideResolution(
            rule_id="finance.closing.period",
            effective_scope="global",
            effective_scope_key="closing-period",
            effective_enabled=True,
            effective_params={"status": status},
            applied_reason="Abschlussfreigabe fuer Periode.",
            applied_source="closing-checklists",
        ),
        approval_explainability=ExplainabilityView(
            status="allowed" if can_close else "approval-required",
            summary="Abschluss ist freigegeben." if can_close else "Abschluss benoetigt Freigabe.",
            rule_id="finance.closing.period",
            source_scope="global",
        ),
        created_at=row[11],
        updated_at=row[12],
        completed_at=row[13] if row[13] else None,
        completed_by=str(row[14]) if row[14] else None,
    )


async def calculate_closing_workspace(request: ClosingWorkspaceRequest, db: Session) -> dict:
    return {
        "tenant_id": request.tenant_id,
        "period": request.period,
        "closing_type": request.closing_type,
        "status": "calculated",
        "approval_status": "pending",
    }


async def close_closing_workspace(request: ClosingWorkspaceRequest, db: Session) -> dict:
    return {
        "tenant_id": request.tenant_id,
        "period": request.period,
        "closing_type": request.closing_type,
        "status": "closed",
        "approval_status": "completed",
    }


async def lock_closing_workspace(request: ClosingWorkspaceRequest, db: Session) -> dict:
    return {
        "tenant_id": request.tenant_id,
        "period": request.period,
        "closing_type": request.closing_type,
        "status": "locked",
        "approval_status": "blocked",
    }
