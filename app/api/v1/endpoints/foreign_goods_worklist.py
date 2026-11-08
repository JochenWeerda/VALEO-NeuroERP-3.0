"""Foreign-goods operator worklist API."""

from decimal import Decimal
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.ops_worklist_bundle_schemas import (
    ForeignGoodsCompleteOut,
    ForeignGoodsPageOut,
    ForeignGoodsSummaryOut,
    ForeignGoodsTransferOut,
)
from app.auth.betrieb_roles import lager_write
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion
from app.services.foreign_goods_worklist_service import (
    ForeignGoodsError,
    ForeignGoodsWorklistService,
)

router = APIRouter(prefix="/foreign-goods", tags=["inventory", "foreign-goods"])


class TransferIn(BaseModel):
    warehouse_id: str = Field(min_length=1, max_length=120)
    location: str | None = Field(default=None, max_length=100)
    reason: str = Field(min_length=5, max_length=500)


class CompleteIn(BaseModel):
    remaining_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    reason: str = Field(min_length=5, max_length=500)


def actor(user: dict) -> str:
    """Urheber aus dem geprueften Token (bis 19.10.2026: Client-Header ``X-User-ID``)."""
    return gepruefter_akteur(user)


@router.get("", response_model=ForeignGoodsPageOut, summary="Fremdware-Worklist auflisten")
def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    owner_id: str | None = None,
    warehouse_id: str | None = None,
    status: str | None = None,
    query: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ForeignGoodsWorklistService(db, tenant_id).list_page(
        page=page,
        page_size=page_size,
        owner_id=owner_id,
        warehouse_id=warehouse_id,
        status=status,
        query=query,
    )


@router.get("/summary", response_model=ForeignGoodsSummaryOut, summary="Kennzahlen der Fremdware-Worklist")
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return ForeignGoodsWorklistService(db, tenant_id).summary()


def _handle(action) -> dict[str, Any]:  # noqa: ANN001
    try:
        return action()
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ForeignGoodsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{foreign_goods_id}/transfer", response_model=ForeignGoodsTransferOut, summary="Fremdware umlagern")
def transfer(
    foreign_goods_id: str,
    body: TransferIn,
    user: dict = Depends(lager_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ForeignGoodsWorklistService(db, tenant_id)
    return _handle(
        lambda: service.transfer(
            foreign_goods_id,
            warehouse_id=body.warehouse_id,
            location=body.location,
            actor=actor(user),
            reason=body.reason,
        )
    )


@router.post("/{foreign_goods_id}/complete", response_model=ForeignGoodsCompleteOut, summary="Fremdware-Einlagerung abschliessen")
def complete(
    foreign_goods_id: str,
    body: CompleteIn,
    user: dict = Depends(lager_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    service = ForeignGoodsWorklistService(db, tenant_id)
    return _handle(
        lambda: service.complete(
            foreign_goods_id,
            remaining_quantity=body.remaining_quantity,
            actor=actor(user),
            reason=body.reason,
        )
    )


@router.post(
    "/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Fremdware: Maskenaktion (umlagern, abschliessen)",
)
async def run_foreign_goods_action(
    entity_id: str,
    action_key: Literal["transfer", "complete"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(lager_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Dieselben Fachwege wie ``/transfer`` und ``/complete``; Ziellager bzw. Restmenge im Auftrag."""
    bearbeiter = actor(user)
    reason = begruendung(body)
    try:
        eingabe: TransferIn | CompleteIn = (
            TransferIn(reason=reason.ljust(5), warehouse_id=body.get("warehouse_id") or "", location=body.get("location"))
            if action_key == "transfer"
            else CompleteIn(reason=reason.ljust(5), remaining_quantity=body.get("remaining_quantity", 0)))
    except ValueError as exc:
        return MaskActionResultOut(actionKey=action_key, mode=str(body.get("_mode") or "execute"), success=False,
                                   error="Eingabe unvollstaendig: Ziellager bzw. Restmenge (>= 0) angeben.",
                                   validationErrors=[{"field": "_payload", "message": str(exc)[:300],
                                                      "severity": "blocking"}]).model_dump()

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        service = ForeignGoodsWorklistService(db_, tenant_id)
        if isinstance(eingabe, TransferIn):
            service.transfer(entity_id, warehouse_id=eingabe.warehouse_id, location=eingabe.location,
                             actor=bearbeiter, reason=reason)
            return f"Fremdware nach {eingabe.warehouse_id} umgelagert."
        service.complete(entity_id, remaining_quantity=eingabe.remaining_quantity, actor=bearbeiter, reason=reason)
        return f"Fremdware abgeschlossen, Restmenge {eingabe.remaining_quantity}."

    result = await statusaktion(
        db, action_key=action_key, entity_type="foreign_goods", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"eingelagert", "teilausgelagert"}, ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_einkauf.fremdwaren_einlagerung WHERE id::text=:id AND tenant_id=:tid",
        event_type=f"inventory.foreign_goods.{action_key}",
    )
    return result.model_dump()
