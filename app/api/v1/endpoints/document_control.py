"""Document control (Beleg-Kontrolle) API."""

from app.auth.finance_roles import beleg_read, beleg_write
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.docflow_bundle_schemas import (
    ControlAssignOut,
    ControlProjectionOut,
    ControlRegisteredOut,
    ControlSummaryOut,
    ControlTransitionOut,
    ControlWorklistOut,
)
from app.core.akteur import anzeigename, gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.document_control_service import (
    DocumentControlError,
    DocumentControlService,
    valid_status_transition,
)
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.document_control_projection import DocumentControlProjectionService

router = APIRouter(prefix="/document-control", tags=["document-control", "finance"])


_actor = gepruefter_akteur
_display_name = anzeigename


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


@router.post("/exceptions", response_model=ControlRegisteredOut, status_code=201, summary="Beleg-Ausnahme registrieren", dependencies=[Depends(beleg_write)])
def register_exception(
    body: ExceptionIn,
    user: dict = Depends(beleg_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    actor = _actor(user)
    try:
        return DocumentControlService(db, tenant_id).register_exception(body.model_dump(), actor=actor)
    except DocumentControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/exceptions", response_model=ControlWorklistOut, summary="Beleg-Kontrolle Worklist", dependencies=[Depends(beleg_read)])
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


@router.get("/summary", response_model=ControlSummaryOut, summary="Beleg-Kontrolle Zusammenfassung", dependencies=[Depends(beleg_read)])
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return DocumentControlService(db, tenant_id).summary()


@router.post("/project", response_model=ControlProjectionOut, summary="Belegausnahmen aus Quellbelegen projizieren", dependencies=[Depends(beleg_write)])
def project_exceptions(
    user: dict = Depends(beleg_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    actor = _actor(user)
    try:
        return DocumentControlProjectionService(db, tenant_id).refresh(actor=actor)
    except DocumentControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/exceptions/{case_id}/assign", response_model=ControlAssignOut, summary="Ausnahme zuweisen", dependencies=[Depends(beleg_write)])
def assign_exception(
    case_id: str,
    body: AssignIn,
    user: dict = Depends(beleg_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocumentControlService(db, tenant_id).assign(
            case_id,
            assigned_user=body.assigned_user,
            actor=_actor(user),
            reason=body.reason,
            due_at=body.due_at,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/exceptions/{case_id}/transition", response_model=ControlTransitionOut, summary="Ausnahmestatus wechseln", dependencies=[Depends(beleg_write)])
def transition_exception(
    case_id: str,
    body: TransitionIn,
    user: dict = Depends(beleg_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocumentControlService(db, tenant_id).transition(
            case_id,
            target=body.target,
            actor=_actor(user),
            reason=body.reason,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DocumentControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


#: Maskenaktion -> Zielstatus (``None`` = Zuweisung an den angemeldeten Bearbeiter).
_MASK_ACTIONS: dict[str, str | None] = {"assign_me": None, "start_work": "in_progress", "resolve": "resolved",
                                         "waive": "waived"}
_TERMINAL = {"resolved", "waived"}


@router.post(
    "/exceptions/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Belegkontrolle: Maskenaktion (zuweisen, in Arbeit, erledigt, verwerfen)",
)
async def run_control_action(
    entity_id: str,
    action_key: Literal["assign_me", "start_work", "resolve", "waive"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(beleg_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Derselbe Fachweg wie Zuweisen/Statuswechsel, mit Begruendung, Trockenlauf und Wiederholungsschutz.

    Bearbeiter und Zustaendiger kommen aus dem Token; die Begruendung (``_auditReason``) ist Pflicht.
    """
    from sqlalchemy import text

    from app.services.mask_action_runtime_service import run_delegated_mask_action

    actor, display = _actor(user), _display_name(user)
    reason = str(body.get("_auditReason") or "").strip()
    target = _MASK_ACTIONS[action_key]

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if len(reason) < 5 or len(reason) > 500:
            return [{"field": "_auditReason", "message": "Begruendung mit 5 bis 500 Zeichen erforderlich.",
                     "severity": "blocking"}]
        row = db_.execute(text(
            "SELECT status FROM domain_ops.document_control_exceptions WHERE id=:id AND tenant_id=:tid"
        ), {"id": eid, "tid": tid}).mappings().first()
        if row is None:
            return [{"field": "_entity", "message": "Ausnahmefall nicht gefunden.", "severity": "blocking"}]
        if row["status"] in _TERMINAL:
            return [{"field": "_entity", "message": f"Ausnahmefall ist bereits {row['status']}.", "severity": "blocking"}]
        if target is not None and not valid_status_transition(row["status"], target):
            return [{"field": "_entity", "message": f"Uebergang {row['status']} -> {target} nicht erlaubt.",
                     "severity": "blocking"}]
        return []

    async def ausfuehren(db_: Session, payload: dict, eid: str, tid: str) -> str:
        service = DocumentControlService(db_, tid)
        if target is None:
            service.assign(eid, assigned_user=display, actor=actor, reason=reason)
            return f"Ausnahme {display} zugewiesen."
        service.transition(eid, target=target, actor=actor, reason=reason)
        return f"Status {target}."

    result = await run_delegated_mask_action(
        db, action_key=action_key, entity_type="document_control_exception", entity_id=entity_id,
        tenant_id=tenant_id, body=body, check_fn=pruefen, delegate_fn=ausfuehren,
        outbox_event_type=f"document_control.exception.{action_key}", require_audit_reason=True,
    )
    return result.model_dump()
