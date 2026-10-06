"""Schadenmeldungen und Versicherungsvertraege.

Bis zum 06.10.2026 war dieser Weg vollstaendig erfunden:
``POST /schaeden/meldungen`` antwortete `201` mit einer Meldungsnummer und
``status: "gemeldet"`` und schrieb **nichts**; ``GET /schaeden/meldungen`` gab
eine Hagelschadenmeldung ueber 12.500 EUR mit Zeuge „Hans Mueller" zurueck, und
``GET /schaeden/versicherungen`` vier Vertraege mit Vertragsnummern — alles
Literale im Code.

Das ist nicht derselbe Fehler wie eine fehlende Tabelle: Dort antwortet der Weg
503 und jemand merkt es. Hier hat ein Haus eine Meldungsnummer in der Hand und
meldet deshalb nicht noch einmal, waehrend die Frist nach § 30 Abs. 1 VVG laeuft.

Zwei Dinge sagt dieser Weg jetzt ausdruecklich: Das Anlegen erzeugt einen
**Entwurf**, und das Melden ist ein eigener Schritt, der festhaelt, wann, durch
wen und auf welchem Weg der Versicherer unterrichtet wurde. Das System
uebermittelt nicht selbst.

Entscheidungen: ``docs/quality-assurance/quittung-ohne-vorgang-20261006.md``.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import schaden_service as dienst

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schaeden", tags=["schaeden", "versicherung"])

Versicherungsart = Literal[
    "hagel", "haftpflicht", "feuer", "kasko", "inhalt", "transport", "sonstige"
]
Meldeweg = Literal["TELEFON", "EMAIL", "POST", "FAX", "PORTAL", "PERSOENLICH"]


# ── Schemas ─────────────────────────────────────────────────────────────────


class VersicherungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bezeichnung: str = Field(min_length=1, max_length=160)
    vertragsnummer: str = Field(min_length=1, max_length=80)
    typ: Versicherungsart
    versicherer: str = Field(min_length=1, max_length=200)
    gueltig_von: Optional[date] = None
    gueltig_bis: Optional[date] = None
    #: Die Frist, innerhalb der ein Schaden anzuzeigen ist — sie gehoert an den
    #: Vertrag, weil sie je Police verschieden ist.
    meldefrist_tage: Optional[int] = Field(default=None, gt=0)
    ansprechpartner: Optional[str] = Field(default=None, max_length=160)
    kontakt: Optional[str] = Field(default=None, max_length=200)


class VersicherungOut(BaseModel):
    id: str
    tenant_id: str
    bezeichnung: str
    vertragsnummer: str
    typ: str
    versicherer: str
    gueltig_von: Optional[str] = None
    gueltig_bis: Optional[str] = None
    meldefrist_tage: Optional[int] = None
    ansprechpartner: Optional[str] = None
    kontakt: Optional[str] = None
    aktiv: bool
    created_at: Optional[str] = None


class SchadenMeldungIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    art: str = Field(min_length=1, max_length=30, description="hagel, frost, feuer, …")
    schadendatum: date
    ort: Optional[str] = Field(default=None, max_length=160)
    beschreibung: str = Field(min_length=1, description="Schadenhergang")
    schadenhoehe: float = Field(default=0, ge=0)
    versicherung_id: Optional[str] = None
    zeuge: Optional[str] = Field(default=None, max_length=200)
    erfasst_durch: Optional[str] = Field(default=None, max_length=120)


class MeldungMelden(BaseModel):
    """Der Versicherer wurde unterrichtet — ausserhalb des Systems."""

    model_config = ConfigDict(extra="forbid")

    meldeweg: Meldeweg
    gemeldet_durch: Optional[str] = Field(default=None, max_length=120)
    gemeldet_am: Optional[str] = Field(
        default=None, description="ISO-Zeitpunkt; ohne Angabe gilt jetzt"
    )


class MeldungStand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["IN_BEARBEITUNG", "REGULIERT", "ABGELEHNT"]
    regulierungsbetrag: Optional[float] = Field(default=None, ge=0)
    abgelehnt_grund: Optional[str] = None


class SchadenMeldungOut(BaseModel):
    id: str
    tenant_id: str
    meldungsnummer: str
    art: str
    schadendatum: Optional[str] = None
    ort: Optional[str] = None
    beschreibung: str
    schadenhoehe: float
    versicherung_id: Optional[str] = None
    zeuge: Optional[str] = None
    status: str
    gemeldet_am: Optional[str] = None
    gemeldet_durch: Optional[str] = None
    meldeweg: Optional[str] = None
    regulierungsbetrag: Optional[float] = None
    abgelehnt_grund: Optional[str] = None
    erfasst_durch: Optional[str] = None
    #: Abgeleitet aus der Frist des Vertrags, nicht gespeichert.
    meldefrist_tage: Optional[int] = None
    melden_bis: Optional[str] = None
    frist_ueberschritten: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ── Versicherungsvertraege ──────────────────────────────────────────────────


@router.get("/versicherungen", response_model=List[VersicherungOut],
            summary="Versicherungsvertraege auflisten")
async def list_versicherungen(
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Vertraege des Mandanten. Vorher standen hier vier Literale."""
    try:
        return dienst.versicherungen(db, tenant_id, limit)
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Versicherungsvertraege", tenant_id) from fehler


@router.post("/versicherungen", status_code=201, response_model=VersicherungOut,
             summary="Versicherungsvertrag anlegen")
async def create_versicherung(
    payload: VersicherungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Legt einen Vertrag an — samt Meldefrist, aus der die Fristen folgen."""
    try:
        ergebnis = dienst.versicherung_anlegen(db, tenant_id, str(uuid7()), payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Versicherungsvertrag nicht anlegbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={"error": "Vertrag nicht angelegt", "grund": str(fehler),
                    "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=dienst.MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


# ── Schadenmeldungen ────────────────────────────────────────────────────────


@router.get("/meldungen", response_model=List[SchadenMeldungOut],
            summary="Schadenmeldungen auflisten")
async def list_schadenmeldungen(
    status: Optional[str] = Query(None, description="ENTWURF | GEMELDET | …"),
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Schadenmeldungen des Mandanten.

    Vorher gab dieser Weg eine erfundene Hagelschadenmeldung zurueck. Eine leere
    Liste ist jetzt die Wahrheit, wenn nichts erfasst ist — ein Lesefehler ist ein
    503.
    """
    try:
        return dienst.auflisten(db, tenant_id, status, limit)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Schadenmeldungen", tenant_id) from fehler


@router.post("/meldungen", status_code=201, response_model=SchadenMeldungOut,
             summary="Schadenmeldung erfassen (Entwurf)")
async def create_schadenmeldung(
    payload: SchadenMeldungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst den Schaden als **Entwurf**.

    Nicht als „gemeldet": Es gibt keinen Versandweg zum Versicherer, und das
    System darf nicht behaupten, er sei unterrichtet. Dafuer gibt es
    ``POST /schaeden/meldungen/{id}/melden``.
    """
    try:
        nummer = dienst.naechste_meldungsnummer(db, tenant_id)
        ergebnis = dienst.anlegen(db, tenant_id, str(uuid7()), nummer, payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        logger.exception("Schadenmeldung nicht erfassbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=409,
            detail={"error": "Schadenmeldung nicht erfasst", "grund": str(fehler),
                    "migration_hint": dienst.MIGRATIONS_HINWEIS["X-Migration-Hint"]},
            headers=dienst.MIGRATIONS_HINWEIS,
        ) from fehler
    return ergebnis


@router.get("/meldungen/{meldung_id}", response_model=SchadenMeldungOut,
            summary="Schadenmeldung abrufen")
async def get_schadenmeldung(
    meldung_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        zeile = dienst.holen(db, tenant_id, meldung_id)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Schadenmeldung", tenant_id) from fehler
    return dienst.anreichern(zeile, zeile.get("frist_tage"))


@router.post("/meldungen/{meldung_id}/melden", response_model=SchadenMeldungOut,
             summary="Meldung an den Versicherer festhalten")
async def melden(
    meldung_id: str,
    payload: MeldungMelden,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Haelt fest, dass der Versicherer unterrichtet wurde.

    Das System **uebermittelt nicht**. Es verzeichnet wann, durch wen und auf
    welchem Weg — das ist der Nachweis, den § 30 Abs. 1 VVG braucht, und etwas
    anderes als die Behauptung, eine Software habe gemeldet.
    """
    try:
        ergebnis = dienst.melden(
            db, tenant_id, meldung_id, payload.meldeweg,
            payload.gemeldet_durch, payload.gemeldet_am,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=409, detail={"error": "Meldung nicht festgehalten", "grund": str(fehler)}
        ) from fehler
    return ergebnis


@router.patch("/meldungen/{meldung_id}", response_model=SchadenMeldungOut,
              summary="Bearbeitungsstand setzen")
async def set_stand(
    meldung_id: str,
    payload: MeldungStand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Bearbeitung, Regulierung oder Ablehnung — mit Betrag beziehungsweise Grund."""
    try:
        ergebnis = dienst.stand_setzen(
            db, tenant_id, meldung_id, payload.status,
            payload.regulierungsbetrag, payload.abgelehnt_grund,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=409, detail={"error": "Stand nicht gesetzt", "grund": str(fehler)}
        ) from fehler
    return ergebnis
