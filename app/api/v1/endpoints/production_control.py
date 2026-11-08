"""General production control worklist API."""

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.ops_worklist_bundle_schemas import (
    ProductionAuditOut,
    ProductionOperationPageOut,
    ProductionRegisterOut,
    ProductionSummaryOut,
    ProductionSyncOut,
    ProductionTransitionOut,
)
from app.auth.betrieb_roles import produktion_write
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion
from app.services.production_control_service import (
    STATUS_TRANSITIONS,
    ProductionControlError,
    ProductionControlService,
)

router = APIRouter(prefix="/production-control", tags=["production-control", "agrar", "inventory"])


class OperationIn(BaseModel):
    operation_type: Literal["production_order", "mill_run", "stock_transfer", "batch_posting", "rework"]
    source_type: str = Field(min_length=1, max_length=80)
    source_ref: str = Field(min_length=1, max_length=120)
    source_number: str = Field(min_length=1, max_length=120)
    source_route: str | None = None
    work_center: str | None = None
    article_ref: str | None = None
    article_name: str | None = None
    batch_ref: str | None = None
    quantity: float | None = None
    unit: str | None = None
    assigned_user: str | None = None
    planned_at: datetime | None = None
    notes: str | None = None
    reason: str = Field(min_length=5, max_length=500)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class TransitionIn(ReasonIn):
    target: Literal["queued", "released", "running", "paused", "completed", "cancelled", "rework"]


def _actor(user: dict) -> str:
    """Urheber aus dem geprueften Token (bis 19.10.2026: Client-Header ``X-User-ID``)."""
    return gepruefter_akteur(user)


@router.post("/operations", response_model=ProductionRegisterOut, status_code=201, summary="Produktionsvorgang registrieren")
def register(body: OperationIn, user: dict = Depends(produktion_write), db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return ProductionControlService(db, tenant_id).register(body.model_dump(), actor=_actor(user))
    except ProductionControlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/operations", response_model=ProductionOperationPageOut, summary="Produktionsvorgaenge auflisten")
def list_operations(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
                    operation_type: str | None = None, status: str | None = None,
                    work_center: str | None = None, assigned_user: str | None = None,
                    q: str | None = None, sort: str = "planned_at", sort_dir: Literal["asc", "desc"] = "asc",
                    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return ProductionControlService(db, tenant_id).list_page(page=page, page_size=page_size,
        operation_type=operation_type, status=status, work_center=work_center, assigned_user=assigned_user,
        q=q, sort=sort, sort_dir=sort_dir)


@router.get("/summary", response_model=ProductionSummaryOut, summary="Kennzahlen des Produktionsleitstands")
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return ProductionControlService(db, tenant_id).summary()


@router.post("/sync", response_model=ProductionSyncOut, summary="Produktionsvorgaenge synchronisieren")
def sync(body: ReasonIn, user: dict = Depends(produktion_write), db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return ProductionControlService(db, tenant_id).sync_production_orders(actor=_actor(user), reason=body.reason)


@router.post("/operations/{operation_id}/transition", response_model=ProductionTransitionOut, summary="Produktionsvorgang weiterschalten")
def transition(operation_id: str, body: TransitionIn, user: dict = Depends(produktion_write),
               db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, str]:
    try:
        return ProductionControlService(db, tenant_id).transition(operation_id, target=body.target,
            actor=_actor(user), reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProductionControlError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/operations/{operation_id}/audit", response_model=list[ProductionAuditOut], summary="Audit-Spur des Produktionsvorgangs")
def audit(operation_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict[str, Any]]:
    return ProductionControlService(db, tenant_id).audit(operation_id)


#: Maskenaktion -> Zielstatus des Produktionsvorgangs.
_MASK_TARGETS = {"release": "released", "start": "running", "complete": "completed", "mark_rework": "rework"}


@router.post(
    "/operations/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Produktionsleitstand: Maskenaktion (freigeben, starten, abschliessen, Nacharbeit)",
)
async def run_operation_action(
    entity_id: str,
    action_key: Literal["release", "start", "complete", "mark_rework"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(produktion_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Derselbe Statuswechsel wie ``/transition``, mit Begruendung, Trockenlauf und Wiederholungsschutz."""
    target = _MASK_TARGETS[action_key]
    bearbeiter = _actor(user)

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        ProductionControlService(db_, tenant_id).transition(entity_id, target=target, actor=bearbeiter,
                                                            reason=begruendung(body))
        return f"Produktionsvorgang: Status {target}."

    result = await statusaktion(
        db, action_key=action_key, entity_type="production_operation", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={s for s, ziele in STATUS_TRANSITIONS.items() if target in ziele}, ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_ops.production_operations WHERE id=:id AND tenant_id=:tid",
        event_type=f"production.operation.{action_key}",
    )
    return result.model_dump()
