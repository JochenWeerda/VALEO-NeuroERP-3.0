"""Etikettendrucker und Druckauftraege.

Bis zum 06.10.2026 antwortete ``POST /etiketten/druckauftrag`` mit `201`, einer
Auftragsnummer und ``status: "erstellt"`` — und schrieb nichts und druckte nichts
(„In production: INSERT INTO domain_erp.druckauftraege + send to print spooler").
``GET /etiketten/drucker`` gab drei Drucker mit IP-Adressen und dem Status
„online" zurueck, die es nicht gab; jede beliebige Druckerkennung ging durch.

Der Auftrag wird jetzt gespeichert. Gedruckt wird er nicht: Es ist kein Spooler
angebunden, und die Antwort sagt das (``uebermittlung: "NICHT_ANGEBUNDEN"``). Ein
Etikett ist ein Rueckverfolgbarkeitsbeleg; ein Auftrag, der „fertig" meldet, ohne
dass etwas gedruckt wurde, ist schlimmer als einer, der ehrlich wartet.

Entscheidungen: ``docs/quality-assurance/quittung-ohne-vorgang-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import List, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import etikettendruck_service as dienst

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/etiketten", tags=["etiketten", "druck"])

Druckerstand = Literal["online", "offline", "fehler", "wartung"]


# ── Schemas ─────────────────────────────────────────────────────────────────


class DruckerIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=160)
    standort: Optional[str] = Field(default=None, max_length=160)
    typ: Optional[str] = Field(default=None, max_length=30, description="zebra, cab, sato, …")
    modell: Optional[str] = Field(default=None, max_length=80)
    status: Druckerstand = "offline"
    ip: Optional[str] = Field(default=None, max_length=60)


class DruckerOut(BaseModel):
    id: str
    tenant_id: str
    name: str
    standort: Optional[str] = None
    typ: Optional[str] = None
    modell: Optional[str] = None
    status: str
    ip: Optional[str] = None
    aktiv: bool
    created_at: Optional[str] = None


class DruckauftragIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chargen_id: str = Field(min_length=1, description="Chargenkennung")
    artikel: Optional[str] = Field(default=None, max_length=200)
    menge: Optional[float] = Field(default=None, ge=0, description="Menge in t")
    lieferant: Optional[str] = Field(default=None, max_length=200)
    eingang: Optional[date] = None
    anzahl_etiketten: int = Field(default=1, ge=1)
    drucker_id: str = Field(min_length=1, description="Kennung des Zieldruckers")
    erfasst_durch: Optional[str] = Field(default=None, max_length=120)


class DruckauftragOut(BaseModel):
    id: str
    tenant_id: str
    auftrags_nr: str
    chargen_id: str
    artikel: Optional[str] = None
    menge: Optional[float] = None
    lieferant: Optional[str] = None
    eingang: Optional[str] = None
    anzahl_etiketten: int
    drucker_id: str
    drucker_name: Optional[str] = None
    status: str
    #: Der Versandstand, getrennt vom Auftragsstand: Ein Auftrag kann angelegt
    #: sein, ohne dass ihn ein Drucker gesehen hat.
    uebermittlung: str
    uebermittelt_am: Optional[str] = None
    gedruckt_am: Optional[str] = None
    fehler: Optional[str] = None
    erfasst_durch: Optional[str] = None
    created_at: Optional[str] = None


# ── Drucker ─────────────────────────────────────────────────────────────────


@router.get("/drucker", response_model=List[DruckerOut], summary="Drucker auflisten")
async def list_drucker(
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Etikettendrucker des Mandanten. Vorher standen hier drei Literale."""
    try:
        return dienst.drucker(db, tenant_id, limit)
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Drucker", tenant_id) from fehler


@router.post("/drucker", status_code=201, response_model=DruckerOut, summary="Drucker anlegen")
async def create_drucker(
    payload: DruckerIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        ergebnis = dienst.drucker_anlegen(db, tenant_id, str(uuid7()), payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Drucker nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={"error": "Drucker nicht angelegt", "grund": str(fehler),
                    "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=dienst.MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


# ── Druckauftraege ──────────────────────────────────────────────────────────


@router.get("/druckauftrag", response_model=List[DruckauftragOut],
            summary="Druckauftraege auflisten")
async def list_druckauftraege(
    status: Optional[str] = Query(None, description="ANGELEGT | UEBERMITTELT | …"),
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Druckauftraege des Mandanten — mit Versandstand."""
    try:
        return dienst.auftraege(db, tenant_id, status, limit)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Druckauftraege", tenant_id) from fehler


@router.post("/druckauftrag", response_model=DruckauftragOut, status_code=201,
             summary="Druckauftrag anlegen")
async def create_druckauftrag(
    payload: DruckauftragIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Legt den Druckauftrag an.

    Der Auftrag wird gespeichert, **nicht** gedruckt: Es ist kein Spooler
    angebunden, und die Antwort nennt das im Feld ``uebermittlung``. Ein
    unbekannter Drucker ist ein 422 — vorher ging jede Kennung durch, weil die
    Liste aus Literalen bestand.
    """
    try:
        drucker_satz = dienst.drucker_holen(db, tenant_id, payload.drucker_id)
        nummer = dienst.naechste_auftragsnummer(db, tenant_id)
        ergebnis = dienst.auftrag_anlegen(
            db, tenant_id, str(uuid7()), nummer, payload, drucker_satz
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Druckauftrag nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={"error": "Druckauftrag nicht angelegt", "grund": str(fehler),
                    "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=dienst.MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


@router.delete("/druckauftrag/{auftrag_id}", response_model=DruckauftragOut,
               summary="Druckauftrag abbrechen")
async def cancel_druckauftrag(
    auftrag_id: str,
    grund: str = Body(..., embed=True, min_length=1),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Bricht einen Auftrag ab. Ein gedruckter Auftrag wird nicht abgebrochen —
    Etiketten im Umlauf macht kein Abbruch rueckgaengig."""
    try:
        ergebnis = dienst.auftrag_abbrechen(db, tenant_id, auftrag_id, grund)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=409, detail={"error": "Abbruch abgewiesen", "grund": str(fehler)}
        ) from fehler
    return ergebnis
