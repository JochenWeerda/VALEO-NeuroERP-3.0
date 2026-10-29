"""PORTAL-PREISSPIEGEL-001 — Getreidekurs-API fuer Kundenportal und Innendienst.

Mandant aus dem geprueften Token. Preise pflegt nur, wer Kontrakte bearbeitet; der Pflegende kommt aus dem Token
(20.10.2026: vorher konnte jede angemeldete Person — auch ein Portalkunde — Kurse fuer alle Kunden setzen).
"""
from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import TypedObjectOut
from app.auth import bereich_roles
from app.auth.deps import require_roles
from app.core.akteur import gepruefter_akteur
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.portal_preisspiegel_service import (
    PreisQuelle,
    PreisVariante,
    get_preisspiegel_service,
)

router = APIRouter(prefix="/portal/preisspiegel", tags=["portal", "preisspiegel"])

_kurspflege = require_roles(*bereich_roles.KONTRAKT)


def _variante(wert: str | None) -> PreisVariante | None:
    if not wert:
        return None
    try:
        return PreisVariante(wert)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Unbekannte Preisvariante: {wert!r}") from e


@router.get("", response_model=TypedObjectOut, summary="Alle aktuellen Preise")
def preise_alle(
    frucht_gruppe: str | None = Query(None),
    variante: str | None = Query(None),
    ernte_jahr: int | None = Query(None),
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    preise = get_preisspiegel_service(db, tid).preise_alle(
        frucht_gruppe=frucht_gruppe,
        variante=_variante(variante),
        ernte_jahr=ernte_jahr,
    )
    return {"preise": preise, "count": len(preise), "stand": date.today().isoformat()}


@router.get("/kunde", response_model=TypedObjectOut, summary="Preisspiegel gefiltert nach Kundenfrüchten")
def preisspiegel_kunde(
    artikel_ids: str | None = Query(None, description="Kommagetrennte Artikel-IDs; ohne Angabe alle aktuellen"),
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    ids = [a.strip() for a in artikel_ids.split(",") if a.strip()] if artikel_ids else None
    return get_preisspiegel_service(db, tid).preisspiegel_fuer_kunde(ids)


class PreisSetzenBody(BaseModel):
    artikel_id: str
    artikel_name: str
    frucht_gruppe: str
    variante: str
    preis_eur_dt: float
    basis_qualitaet: str
    ernte_jahr: int
    liefermonat: str | None = None
    aufschlag_eur_dt: float = 0.0
    quelle: str = "manuell"
    gueltig_bis: date | None = None
    hinweis: str | None = None


@router.post("", response_model=TypedObjectOut, status_code=201, summary="Preis pflegen (Innendienst)")
def preis_setzen(
    body: PreisSetzenBody,
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
    nutzer: dict = Depends(_kurspflege),
) -> dict[str, Any]:
    variante = _variante(body.variante)
    if variante is None:
        raise HTTPException(status_code=422, detail="Preisvariante fehlt")
    try:
        quelle = PreisQuelle(body.quelle)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Unbekannte Preisquelle: {body.quelle!r}") from e
    try:
        return get_preisspiegel_service(db, tid).preis_setzen(
            artikel_id=body.artikel_id,
            artikel_name=body.artikel_name,
            frucht_gruppe=body.frucht_gruppe,
            variante=variante,
            preis_eur_dt=body.preis_eur_dt,
            basis_qualitaet=body.basis_qualitaet,
            ernte_jahr=body.ernte_jahr,
            gepflegt_von=gepruefter_akteur(nutzer),
            liefermonat=body.liefermonat,
            aufschlag_eur_dt=body.aufschlag_eur_dt,
            quelle=quelle,
            gueltig_bis=body.gueltig_bis,
            hinweis=body.hinweis,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
