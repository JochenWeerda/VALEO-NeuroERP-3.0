"""Document control (Beleg-Kontrolle) API."""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.document_control_service import DocumentControlError, DocumentControlService
from app.services.document_control_projection import DocumentControlProjectionService

router = APIRouter(prefix="/document-control", tags=["document-control", "finance"])


class ExceptionIn(BaseModel):
    exception_type: Literal[
        "open_purchase_order",
        "missing_inbound_document",
        "blocked_delivery_note",
        "uninvoiced_delivery_note",
    ]
    document_ref: str = Field(min_length=1, max_length=120)
    document_number: str | None = None
    partner_ref: str | None = None
    partner_name: str | None = None
    assigned_user: str | None = None
    due_at: datetime | None = None
    source_route: str | None = None
    source_key: str | None = None
    notes: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class AssignIn(BaseModel):
    assigned_user: str = Field(min_length=1, max_length=120)
    due_at: datetime | None = None
    reason: str = Field(min_length=5, max_length=500)


class TransitionIn(BaseModel):
    target: Literal["open", "assigned", "in_progress", "resolved", "waived"]
    reason: str = Field(min_length=5, max_length=500)


@router.post("/exceptions", response_model=dict, status_code=201, summary="Beleg-Ausnahme registrieren")
def register_exception(
    body: ExceptionIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    actor = request.headers.get("X-User-ID") or "document-control-operator"
    try:
        return DocumentControlService(db, tenant_id).register_exception(body.model_dump(), actor=actor)
    except DocumentControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/exceptions", response_model=dict, summary="Beleg-Kontrolle Worklist")
def list_exceptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
    exception_type: str | None = None,
    status: str | None = None,
    assigned_user: str | None = None,
    partner_ref: str | None = None,
    q: str | None = None,
    sort: str = "due_at",
    sort_dir: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocumentControlService(db, tenant_id).list_page(
        page=page,
        page_size=page_size,
        exception_type=exception_type,
        status=status,
        assigned_user=assigned_user,
        partner_ref=partner_ref,
        q=q,
        sort=sort,
        sort_dir=sort_dir,
    )


@router.get("/summary", response_model=dict, summary="Beleg-Kontrolle Zusammenfassung")
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return DocumentControlService(db, tenant_id).summary()


@router.post("/project", response_model=dict, summary="Belegausnahmen aus Quellbelegen projizieren")
def project_exceptions(
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    actor = request.headers.get("X-User-ID") or "document-control-operator"
    try:
        return DocumentControlProjectionService(db, tenant_id).refresh(actor=actor)
    except DocumentControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/exceptions/{case_id}/assign", response_model=dict, summary="Ausnahme zuweisen")
def assign_exception(
    case_id: str,
    body: AssignIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocumentControlService(db, tenant_id).assign(
            case_id,
            assigned_user=body.assigned_user,
            actor=request.headers.get("X-User-ID") or "document-control-operator",
            reason=body.reason,
            due_at=body.due_at,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/exceptions/{case_id}/transition", response_model=dict, summary="Ausnahmestatus wechseln")
def transition_exception(
    case_id: str,
    body: TransitionIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocumentControlService(db, tenant_id).transition(
            case_id,
            target=body.target,
            actor=request.headers.get("X-User-ID") or "document-control-operator",
            reason=body.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
