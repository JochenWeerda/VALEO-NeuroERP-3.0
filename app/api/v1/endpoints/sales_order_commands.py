"""Auftrag stornieren als Kommando-Weg (Studio-Katalog ``stornieren``, MASK-COMMANDS-ROLLOUT-20261019).

Aus ``sales_orders.py`` herausgeloest, damit das Godfile nicht waechst: Storno-Kommando sowie AB-Lifecycle,
Lieferschein-Status und Preisabweichung (DOM-SALES-004). Pfade unveraendert unter ``/sales/orders``; Bearbeiter
aus dem Token (bis 19.10.2026 aus dem Feld ``operator`` im Body).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import require_roles
from app.core.akteur import gepruefter_akteur, gepruefter_akteur_aus_request
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.base import TypedObjectOut
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import statusaktion

router = APIRouter()

#: Storno eines Auftrags ist Verkaufsarbeit: Sachbearbeitung oder Leitung des Verkaufs.
_sales_write = require_roles("SALES_BEARBEITEN", "SALES_ADMIN", "admin")


@router.post(
    "/{entity_id}/actions/stornieren",
    response_model=MaskActionResultOut,
    summary="Auftrag stornieren (Maskenaktion: Begruendung, Trockenlauf, Wiederholungsschutz)",
)
async def stornieren_action(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    user: dict = Depends(_sales_write),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Derselbe Zustandswechsel wie ``/cancel`` (offen/bestaetigt -> storniert), fuer Maske, Studio, CLI und MCP.

    Die Begruendung ist Pflicht und steht mit dem Bearbeiter aus dem Token im Audit der Laufzeit.
    Agenten sperrt die Maske (``forbiddenForAgents`` im Studio-Katalog).
    """
    gepruefter_akteur(user)

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        db_.execute(
            text("UPDATE domain_crm.sales_orders SET status = 'cancelled', updated_at = NOW() "
                 "WHERE id = :id AND tenant_id = :tid AND status NOT IN ('cancelled', 'completed')"),
            {"id": entity_id, "tid": tenant_id},
        )
        return "Auftrag storniert."

    result = await statusaktion(
        db, action_key="stornieren", entity_type="sales_order", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"draft", "open", "confirmed", "in_delivery"}, ausfuehren=ausfuehren,
        status_sql="SELECT status FROM domain_crm.sales_orders WHERE id::text = :id AND tenant_id = :tid",
        event_type="sales.order.cancelled",
    )
    return result.model_dump()


# ---------------------------------------------------------------------------
# DOM-SALES-004: AB-Lifecycle / Lieferschein-Close / Preisabweichung
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BM
from typing import Optional as _Opt


class ABTransitionIn(_BM):
    new_status: str
    reason: _Opt[str] = None


class LSAdvanceIn(_BM):
    new_status: str
    quittiert_von: _Opt[str] = None


class PreisabweichungIn(_BM):
    artikel_id: str
    angebots_preis: float
    rechnungs_preis: float
    schwelle_pct: _Opt[float] = 2.0


class PreisabweichungFreigabeIn(_BM):
    entscheidung: str
    grund: _Opt[str] = None


@router.post("/orders/{auftrag_id}/ab-transition", response_model=TypedObjectOut, summary="Auftragsbestätigung Status wechseln", dependencies=SCHREIBEN["VERKAUF"])
def ab_transition_endpoint(
    auftrag_id: str,
    body: ABTransitionIn,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_ab_lifecycle_service import transition_ab_status, ABLifecycleError
    try:
        return transition_ab_status(db, auftrag_id, tenant_id, body.new_status,
                                     gepruefter_akteur_aus_request(request), body.reason)
    except ABLifecycleError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/delivery-notes/{ls_id}/advance", response_model=TypedObjectOut, summary="Lieferschein-Status vorwärts", dependencies=SCHREIBEN["VERKAUF"])
def ls_advance_endpoint(
    ls_id: str,
    body: LSAdvanceIn,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_lieferschein_close_service import advance_lieferschein, LSCloseError
    try:
        return advance_lieferschein(db, ls_id, tenant_id, body.new_status,
                                     gepruefter_akteur_aus_request(request), body.quittiert_von)
    except LSCloseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/orders/{auftrag_id}/preisabweichung", response_model=TypedObjectOut, status_code=201, summary="Preisabweichung prüfen", dependencies=SCHREIBEN["VERKAUF"])
def pruefe_preisabweichung_endpoint(
    auftrag_id: str,
    body: PreisabweichungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_preisabweichung_service import pruefe_preisabweichung, PreisabweichungError
    try:
        return pruefe_preisabweichung(db, auftrag_id, tenant_id, body.artikel_id,
                                       body.angebots_preis, body.rechnungs_preis,
                                       body.schwelle_pct or 2.0)
    except PreisabweichungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/preisabweichungen/{abweichung_id}/freigabe", response_model=TypedObjectOut, summary="Preisabweichung freigeben/ablehnen", dependencies=SCHREIBEN["VERKAUF"])
def freigabe_preisabweichung_endpoint(
    abweichung_id: str,
    body: PreisabweichungFreigabeIn,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.sales_preisabweichung_service import freigabe_preisabweichung, PreisabweichungError
    try:
        return freigabe_preisabweichung(db, abweichung_id, tenant_id, body.entscheidung,
                                         gepruefter_akteur_aus_request(request), body.grund)
    except PreisabweichungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
