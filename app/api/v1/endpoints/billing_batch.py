"""Billing batch orchestration API."""

from app.auth.finance_roles import finance_admin, finance_read, finance_write
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.v1.schemas.billing_batch_schemas import (
    BatchActionOut,
    BatchCreatedOut,
    BatchLineOut,
    BatchPageOut,
    BatchSummaryOut,
)
from app.core.akteur import gepruefter_akteur, verlange_rolle
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.billing_batch_service import BillingBatchError, BillingBatchService
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import begruendung, statusaktion

router = APIRouter(
    prefix="/billing-batches", tags=["finance", "billing-batches", "self-billing"]
)


class LineIn(BaseModel):
    source_type: str = Field(min_length=1, max_length=80)
    source_ref: str = Field(min_length=1, max_length=120)
    source_number: str | None = None
    source_route: str | None = None
    evidence_route: str | None = None
    amount: float = 0
    validation_error: str | None = None
    idempotency_key: str | None = None


class BatchIn(BaseModel):
    batch_type: Literal[
        "sales_invoice",
        "purchase_invoice",
        "self_billing_sales",
        "self_billing_purchase",
    ]
    batch_number: str | None = None
    description: str | None = None
    currency: str = "EUR"
    reason: str = Field(min_length=5, max_length=500)
    lines: list[LineIn] = Field(min_length=1)


class ReasonIn(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


def actor(user: dict) -> str:
    """Ersteller und Freigeber aus dem geprueften Token: Das Vier-Augen-Prinzip vergleicht sie.

    Bis zum 19.10.2026 kamen beide aus dem Client-Header ``X-User-ID``; zwei Kopfzeilen genuegten,
    um einen eigenen Stapel selbst freizugeben.
    """
    return gepruefter_akteur(user)


@router.post("", response_model=BatchCreatedOut, status_code=201, summary="Rechnungsstapel anlegen", dependencies=[Depends(finance_write)])
def create(
    body: BatchIn,
    user: dict = Depends(finance_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return BillingBatchService(db, tenant_id).create(
            body.model_dump(), actor=actor(user)
        )
    except BillingBatchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=BatchPageOut, summary="Rechnungsstapel auflisten", dependencies=[Depends(finance_read)])
def list_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    batch_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return BillingBatchService(db, tenant_id).list_page(
        page=page, page_size=page_size, batch_type=batch_type, status=status
    )


@router.get("/summary", response_model=BatchSummaryOut, summary="Kennzahlen der Rechnungsstapel", dependencies=[Depends(finance_read)])
def summary(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, int]:
    return BillingBatchService(db, tenant_id).summary()


@router.get("/lines", response_model=list[BatchLineOut], summary="Stapelzeilen auflisten", dependencies=[Depends(finance_read)])
def lines(
    status: str | None = None,
    batch_id: str | None = None,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return BillingBatchService(db, tenant_id).list_lines(
        status=status, batch_id=batch_id, limit=limit
    )


def _batch_action(
    action: str,
    batch_id: str,
    body: ReasonIn,
    user: dict,
    db: Session,
    tenant_id: str,
) -> dict[str, Any]:
    service = BillingBatchService(db, tenant_id)
    try:
        return getattr(service, action)(
            batch_id, actor=actor(user), reason=body.reason
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except BillingBatchError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{batch_id}/validate", response_model=BatchActionOut, summary="Rechnungsstapel pruefen", dependencies=[Depends(finance_write)])
def validate(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(finance_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("validate", batch_id, body, user, db, tenant_id)


@router.post("/{batch_id}/release", response_model=BatchActionOut, summary="Rechnungsstapel freigeben", dependencies=[Depends(finance_admin)])
def release(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(finance_admin),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("release", batch_id, body, user, db, tenant_id)


@router.post("/{batch_id}/execute", response_model=BatchActionOut, summary="Rechnungsstapel ausfuehren", dependencies=[Depends(finance_admin)])
def execute(
    batch_id: str,
    body: ReasonIn,
    user: dict = Depends(finance_admin),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _batch_action("execute", batch_id, body, user, db, tenant_id)


@router.post("/lines/{line_id}/retry", response_model=BatchActionOut, summary="Stapelzeile erneut verarbeiten", dependencies=[Depends(finance_write)])
def retry(
    line_id: str,
    body: ReasonIn,
    user: dict = Depends(finance_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, str]:
    return _batch_action("retry", line_id, body, user, db, tenant_id)


#: Maskenaktion -> erlaubte Status und Rolle (Freigeben und Ausfuehren bewegen Geld: nur Finanzleitung).
_BATCH_ACTIONS: dict[str, tuple[set[str], tuple[str, ...]]] = {
    "validate": ({"draft"}, ("FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager")),
    "release": ({"validated"}, ("FINANCE_ADMIN", "admin")),
    "execute": ({"released"}, ("FINANCE_ADMIN", "admin")),
}


@router.post(
    "/{entity_id}/actions/{action_key}",
    response_model=MaskActionResultOut,
    summary="Rechnungsstapel: Maskenaktion (pruefen, freigeben, ausfuehren)",
)
async def run_batch_action(
    entity_id: str,
    action_key: Literal["validate", "release", "execute"] = Path(...),
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(finance_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Derselbe Fachweg wie die Einzelwege, mit Begruendung, Trockenlauf und Wiederholungsschutz."""
    erlaubt, rollen = _BATCH_ACTIONS[action_key]
    verlange_rolle(user, *rollen)
    bearbeiter = actor(user)

    def vier_augen(row: dict[str, Any]) -> str | None:
        if action_key == "release" and row.get("maker") == bearbeiter:
            return "Vier-Augen-Prinzip: Freigeber muss vom Ersteller abweichen."
        return None

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        getattr(BillingBatchService(db_, tenant_id), action_key)(
            entity_id, actor=bearbeiter, reason=begruendung(body))
        return f"Rechnungsstapel: {action_key} ausgefuehrt."

    result = await statusaktion(
        db, action_key=action_key, entity_type="billing_batch", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt=erlaubt, ausfuehren=ausfuehren, zusatzpruefung=vier_augen,
        status_sql="SELECT status, maker FROM domain_finance.billing_batches WHERE id=:id AND tenant_id=:tid",
        event_type=f"finance.billing_batch.{action_key}",
    )
    return result.model_dump()


@router.post(
    "/lines/{entity_id}/actions/retry",
    response_model=MaskActionResultOut,
    summary="Rechnungsstapel: Fehlerzeile erneut verarbeiten (Maskenaktion)",
)
async def run_line_retry(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(finance_write),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    bearbeiter = actor(user)

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        BillingBatchService(db_, tenant_id).retry(entity_id, actor=bearbeiter, reason=begruendung(body))
        return "Stapelzeile erneut eingereiht."

    result = await statusaktion(
        db, action_key="retry", entity_type="billing_batch_line", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"failed"}, ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_finance.billing_batch_lines WHERE id=:id AND tenant_id=:tid",
        event_type="finance.billing_batch_line.retry",
    )
    return result.model_dump()
