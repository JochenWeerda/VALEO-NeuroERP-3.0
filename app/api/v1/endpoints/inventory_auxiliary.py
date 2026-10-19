"""Inventory auxiliary batch API."""

from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.inventory_bundle_schemas import (
    AuxiliaryBatchCreatedOut,
    AuxiliaryBatchPageOut,
    AuxiliarySummaryOut,
    AuxiliaryTransitionOut,
)
from app.auth.betrieb_roles import LAGER_LEITUNG, lager_write
from app.core.akteur import gepruefter_akteur, verlange_rolle
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.inventory_auxiliary_service import TRANSITIONS, InventoryAuxiliaryError, InventoryAuxiliaryService
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_action_runtime_service import run_delegated_mask_action
from app.services.mask_commands import begruendung, statusaktion

router = APIRouter(prefix="/inventory/auxiliary", tags=["inventory", "inventory-auxiliary"])


class BatchIn(BaseModel):
    inventory_count_id: str = Field(min_length=1)
    batch_type: Literal["count_sheet", "count_import", "control_run", "preliminary_valuation", "opening_balance"]
    reason: str = Field(min_length=5, max_length=500)
    import_rows: list[dict[str, Any]] | None = None
    declared_hash: str | None = Field(default=None, min_length=64, max_length=64)


class TransitionIn(BaseModel):
    target: Literal["reviewed", "approved", "applied", "rejected"]
    reason: str = Field(min_length=5, max_length=500)


def actor(user: dict) -> str:
    """Ersteller und Pruefer aus dem geprueften Token: Das Vier-Augen-Prinzip vergleicht sie.

    Bis zum 19.10.2026 kamen beide aus dem Client-Header ``X-User-ID``.
    """
    return gepruefter_akteur(user)


@router.post("/batches", response_model=AuxiliaryBatchCreatedOut, status_code=201, summary="Nebenbuch-Stapel anlegen")
def create_batch(body: BatchIn, user: dict = Depends(lager_write), db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    try:
        return InventoryAuxiliaryService(db, tenant_id).create(count_id=body.inventory_count_id,
            batch_type=body.batch_type, actor=actor(user), reason=body.reason,
            import_rows=body.import_rows, declared_hash=body.declared_hash)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InventoryAuxiliaryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/batches", response_model=AuxiliaryBatchPageOut, summary="Nebenbuch-Stapel auflisten")
def list_batches(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200),
                 batch_type: str | None = None, status: str | None = None,
                 inventory_count_id: str | None = None, db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return InventoryAuxiliaryService(db, tenant_id).list_page(page=page, page_size=page_size,
        batch_type=batch_type, status=status, count_id=inventory_count_id)


@router.get("/summary", response_model=AuxiliarySummaryOut, summary="Kennzahlen der Nebenbuch-Stapel")
def summary(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, int]:
    return InventoryAuxiliaryService(db, tenant_id).summary()


@router.post("/batches/{batch_id}/transition", response_model=AuxiliaryTransitionOut, summary="Nebenbuch-Stapel weiterschalten")
def transition(batch_id: str, body: TransitionIn, user: dict = Depends(lager_write), db: Session = Depends(get_db),
               tenant_id: str = Depends(get_tenant_id)) -> dict[str, str]:
    if body.target in {"approved", "applied"}:
        verlange_rolle(user, *LAGER_LEITUNG)
    try:
        return InventoryAuxiliaryService(db, tenant_id).transition(batch_id, target=body.target,
            actor=actor(user), reason=body.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InventoryAuxiliaryError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


#: Maskenaktion -> Zielstatus; Freigeben und Anwenden aendern Bestandswerte (Lagerleitung, Vier-Augen).
_MASK_TARGETS = {"review": "reviewed", "approve": "approved", "apply": "applied"}
#: Kopfaktionen der Maske -> Art des Nebenlaufs (die Eroeffnungsbilanz bleibt ein Eingabefluss der Maske).
_MASK_CREATE = {"create_count_sheet": "count_sheet", "create_control": "control_run",
                "create_valuation": "preliminary_valuation"}


@router.post(
    "/batches/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Inventur-Nebenlauf: Maskenaktion (pruefen, freigeben, anwenden)",
)
async def run_batch_action(
    entity_id: str,
    action_key: Literal["review", "approve", "apply"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(lager_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    target = _MASK_TARGETS[action_key]
    if target in {"approved", "applied"}:
        verlange_rolle(user, *LAGER_LEITUNG)
    bearbeiter = actor(user)

    def vier_augen(row: dict[str, Any]) -> str | None:
        if target in {"approved", "applied"} and row.get("maker") == bearbeiter:
            return "Vier-Augen-Prinzip: Pruefer muss vom Ersteller abweichen."
        return None

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        InventoryAuxiliaryService(db_, tenant_id).transition(entity_id, target=target, actor=bearbeiter,
                                                             reason=begruendung(body))
        return f"Inventur-Nebenlauf: Status {target}."

    result = await statusaktion(
        db, action_key=action_key, entity_type="inventory_auxiliary_batch", entity_id=entity_id,
        tenant_id=tenant_id, body=body, ausfuehren=ausfuehren, zusatzpruefung=vier_augen,
        erlaubt={s for s, ziele in TRANSITIONS.items() if target in ziele},
        status_sql="SELECT status, maker FROM domain_inventory.inventory_auxiliary_batches WHERE id=:id AND tenant_id=:tid",
        event_type=f"inventory.auxiliary_batch.{action_key}",
    )
    return result.model_dump()


@router.post(
    "/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Inventur-Nebenlauf erzeugen (Maskenaktion: Zaehlliste, Kontrolllauf, vorlaeufige Bewertung)",
)
async def run_create_action(
    action_key: Literal["create_count_sheet", "create_control", "create_valuation"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(lager_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Derselbe Fachweg wie ``POST /batches``; die Inventur (``inventory_count_id``) steht im Auftrag."""
    bearbeiter = actor(user)
    reason = begruendung(body)
    count_id = str(body.get("inventory_count_id") or "").strip()

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        if not 5 <= len(reason) <= 500:
            return [{"field": "_auditReason", "message": "Begruendung mit 5 bis 500 Zeichen erforderlich.",
                     "severity": "blocking"}]
        if not count_id:
            return [{"field": "inventory_count_id", "message": "Inventur angeben.", "severity": "blocking"}]
        if not InventoryAuxiliaryService(db_, tid).count_exists(count_id):
            return [{"field": "inventory_count_id", "message": "Inventur nicht gefunden.", "severity": "blocking"}]
        return []

    async def ausfuehren(db_: Session, payload: dict, eid: str, tid: str) -> str:
        created = InventoryAuxiliaryService(db_, tid).create(count_id=count_id, batch_type=_MASK_CREATE[action_key],
                                                             actor=bearbeiter, reason=reason)
        return f"Inventur-Nebenlauf {created.get('id')} erzeugt."

    result = await run_delegated_mask_action(
        db, action_key=action_key, entity_type="inventory_count", entity_id=count_id or "-", tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren,
        outbox_event_type=f"inventory.auxiliary_batch.{action_key}", require_audit_reason=True,
    )
    return result.model_dump()
