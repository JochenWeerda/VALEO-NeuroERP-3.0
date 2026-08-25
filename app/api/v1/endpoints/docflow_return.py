"""Document return and shipping-status API."""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.docflow_bundle_schemas import (
    ReturnCreatedOut,
    ReturnEvidenceOut,
    ReturnSummaryOut,
    ReturnTransitionOut,
    ReturnWorklistOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_return_service import DocflowReturnService, DocumentReturnError

router = APIRouter(prefix="/docflow/returns", tags=["docflow", "dms"])


class ReturnCaseIn(BaseModel):
    document_ref: str
    artifact_id: str | None = None
    subject_type: Literal["customer", "personnel", "contact", "process"] = "process"
    subject_ref: str | None = None
    contact_ref: str | None = None
    assigned_user: str | None = None
    tags: list[str] = Field(default_factory=list)
    due_at: datetime | None = None
    source_route: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class TransitionIn(BaseModel):
    kind: Literal["shipping", "return"]
    target: str = Field(min_length=2, max_length=30)
    reason: str = Field(min_length=5, max_length=500)


@router.post("", response_model=ReturnCreatedOut, status_code=201, summary="Dokumentenruecklauf anlegen")
def create_return(body: ReturnCaseIn, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    actor = request.headers.get("X-User-ID") or "docflow-operator"
    try:
        return DocflowReturnService(db, tenant_id).create_case(body.model_dump(), actor=actor)
    except DocumentReturnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=ReturnWorklistOut, summary="Dokumentenruecklauf-Worklist")
def list_returns(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=200),
                 assigned_user: str | None = None, contact_ref: str | None = None,
                 subject_type: str | None = None, date_from: str | None = None, date_to: str | None = None,
                 status: str | None = None, q: str | None = None, sort: str = "created_at",
                 sort_dir: Literal["asc", "desc"] = "desc", db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return DocflowReturnService(db, tenant_id).list_page(page=page, page_size=page_size, assigned_user=assigned_user,
        contact_ref=contact_ref, subject_type=subject_type, date_from=date_from, date_to=date_to,
        status=status, q=q, sort=sort, sort_dir=sort_dir)


@router.get("/summary", response_model=ReturnSummaryOut, summary="Dokumentenruecklauf-Zusammenfassung")
def return_summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return DocflowReturnService(db, tenant_id).summary()


@router.get("/{case_id}/evidence", response_model=ReturnEvidenceOut, summary="Ruecklaufvorschau und Auditnachweis")
def return_evidence(case_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return DocflowReturnService(db, tenant_id).case_evidence(case_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{case_id}/transition", response_model=ReturnTransitionOut, summary="Versand- oder Ruecklaufstatus aktualisieren")
def transition_return(case_id: str, body: TransitionIn, request: Request, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return DocflowReturnService(db, tenant_id).transition(case_id, kind=body.kind, target=body.target,
            actor=request.headers.get("X-User-ID") or "docflow-operator", reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentReturnError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
