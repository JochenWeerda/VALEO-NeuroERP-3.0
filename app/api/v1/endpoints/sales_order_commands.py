"""Lieferschein-Status und Preisabweichung (DOM-SALES-004) unter ``/sales/orders``; Bearbeiter aus dem Token.

Auftragsstorno und AB-Statuswechsel liefen hier auf den Eigenspeichern ``domain_crm.sales_orders`` und
``domain_sales.sales_orders``. Seit BELEG-052 (09.11.2026) ist DocFlow der einzige Belegspeicher: Der Auftrag wird in
der Belegmaske storniert (``/api/v1/belege/sales_order/{id}/actions/stornieren``).
"""
from __future__ import annotations

from typing import Optional as _Opt

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel as _BM
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.akteur import gepruefter_akteur_aus_request
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.base import TypedObjectOut

router = APIRouter()

# ---------------------------------------------------------------------------
# DOM-SALES-004: AB-Lifecycle / Lieferschein-Close / Preisabweichung
# ---------------------------------------------------------------------------



class PreisabweichungIn(_BM):
    artikel_id: str
    angebots_preis: float
    rechnungs_preis: float
    schwelle_pct: _Opt[float] = 2.0


class PreisabweichungFreigabeIn(_BM):
    entscheidung: str
    grund: _Opt[str] = None


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
