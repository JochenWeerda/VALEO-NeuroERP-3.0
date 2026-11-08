"""Tankanlagen adapter inbox API."""

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.ops_worklist_bundle_schemas import (
    TankIngestOut,
    TankIntakePageOut,
    TankProcessOut,
    TankRetryOut,
    TankSummaryOut,
    TankValidateOut,
)
from app.auth.betrieb_roles import tank_write
from app.auth.deps import get_current_user
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion
from app.services.tank_adapter_service import TankAdapterError, TankAdapterService
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter(prefix="/tank-adapter", tags=["tankstelle", "integration"])


class IntakeIn(BaseModel):
    adapter_key: str = Field(min_length=1, max_length=80)
    external_id: str = Field(min_length=1, max_length=160)
    payload: dict[str, Any]


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class RetryIn(ReasonIn):
    corrected_payload: dict[str, Any] | None = None


def actor(user: dict) -> str:
    """Urheber aus dem geprueften Token (bis 19.10.2026: Client-Header ``X-User-ID``)."""
    return gepruefter_akteur(user)


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TankAdapterError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/intake", response_model=TankIngestOut, status_code=202, summary="Tankdaten entgegennehmen", dependencies=SCHREIBEN["GERAET"])
def intake(
    body: IntakeIn,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).ingest(
            body.adapter_key, body.external_id, body.payload, actor=actor(user)
        )
    )


@router.get("/intake", response_model=TankIntakePageOut, summary="Tankdatenlieferungen auflisten")
def list_intake(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return TankAdapterService(db, tenant_id).list_page(
        page=page, page_size=page_size, status=status
    )


@router.get("/summary", response_model=TankSummaryOut, summary="Kennzahlen der Tankdatenlieferungen")
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return TankAdapterService(db, tenant_id).summary()


@router.post("/intake/{intake_id}/validate", response_model=TankValidateOut, summary="Tankdatenlieferung pruefen")
def validate(
    intake_id: str,
    body: ReasonIn,
    user: dict = Depends(tank_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).validate(
            intake_id, actor=actor(user), reason=body.reason
        )
    )


@router.post("/intake/{intake_id}/process", response_model=TankProcessOut, summary="Tankdatenlieferung verarbeiten")
def process(
    intake_id: str,
    body: ReasonIn,
    user: dict = Depends(tank_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).process(
            intake_id, actor=actor(user), reason=body.reason
        )
    )


@router.post("/intake/{intake_id}/retry", response_model=TankRetryOut, summary="Tankdatenlieferung erneut verarbeiten")
def retry(
    intake_id: str,
    body: RetryIn,
    user: dict = Depends(tank_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: TankAdapterService(db, tenant_id).retry(
            intake_id, body.corrected_payload, actor=actor(user), reason=body.reason
        )
    )


#: Maskenaktion -> erlaubter Status der Lieferung (wie ``visibleWhen`` der Maske).
_TANK_ACTIONS = {"validate": {"received"}, "process": {"validated"}, "retry": {"error"}}


@router.post(
    "/intake/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Tankanlagen-Eingang: Maskenaktion (pruefen, verarbeiten, wiederholen)",
)
async def run_intake_action(
    entity_id: str,
    action_key: Literal["validate", "process", "retry"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(tank_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Dieselben Fachwege wie die Einzelwege; ``retry`` nimmt optional ``corrected_payload``."""
    bearbeiter = actor(user)
    corrected = body.get("corrected_payload")
    if corrected is not None and not isinstance(corrected, dict):
        return MaskActionResultOut(actionKey=action_key, mode=str(body.get("_mode") or "execute"), success=False,
                                   error="corrected_payload muss ein JSON-Objekt sein.").model_dump()

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        service = TankAdapterService(db_, tenant_id)
        if action_key == "retry":
            service.retry(entity_id, corrected, actor=bearbeiter, reason=begruendung(body))
        else:
            getattr(service, action_key)(entity_id, actor=bearbeiter, reason=begruendung(body))
        return f"Tankanlagen-Eingang: {action_key} ausgefuehrt."

    result = await statusaktion(
        db, action_key=action_key, entity_type="tank_adapter_intake", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt=_TANK_ACTIONS[action_key], ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_ops.tank_adapter_intake WHERE id=:id AND tenant_id=:tid",
        event_type=f"tankstelle.adapter_intake.{action_key}",
    )
    return result.model_dump()
