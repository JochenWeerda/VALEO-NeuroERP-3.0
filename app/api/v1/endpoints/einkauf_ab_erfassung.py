"""Erfassung eingehender Auftragsbestaetigungen (STAMMDATEN-BEARBEITEN-20261019, Folgepunkt).

Bis 20.10.2026 schrieb niemand in ``einkauf_auftragsbestaetigungen``: Die alte Anlageseite sendete an einen Weg, den
es nicht gab, und der Lesedienst fragte falsche Spalten ab. Hier entsteht die AB **zu einer Bestellung**: Lieferant,
Bestellnummer und Waehrung kommen aus der Bestellung des Mandanten, nie aus dem Client. Die Zustandsschritte
Pruefen/Bestaetigen liegen in ``stammdaten_bearbeiten``.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.business_time import business_today
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(tags=["einkauf"])


class AuftragsbestaetigungAnlage(BaseModel):
    bestellung: str = Field(..., min_length=1, max_length=100, description="Kennung oder Nummer der Bestellung")
    ab_nummer: str = Field(..., min_length=1, max_length=100, description="Nummer der AB des Lieferanten")
    datum: Optional[date] = None
    lieferdatum: Optional[date] = None
    gesamtbetrag: Optional[Decimal] = Field(default=None, ge=0)
    abweichungen: Optional[str] = Field(default=None, max_length=4000)
    notizen: Optional[str] = Field(default=None, max_length=4000)


class AuftragsbestaetigungAngelegt(BaseModel):
    id: str
    bestaetigungsNummer: str
    bestellung: str
    lieferant: str
    status: str
    createdAt: Optional[str] = None


def _lege_an(db: Session, tenant_id: str, bestellung: dict[str, Any], nummer: str, *, datum: Optional[date],
             lieferdatum: Optional[date], gesamtbetrag: Optional[Decimal], waehrung: Optional[str],
             abweichungen: Optional[str], notizen: Optional[str]) -> str:
    """Legt die AB zur Bestellung an (ohne Commit). Lieferant und Bestellnummer stammen aus der Bestellung."""
    vorhanden = db.execute(
        text("SELECT 1 FROM einkauf_auftragsbestaetigungen WHERE tenant_id = :tid AND ab_nummer = :nr"),
        {"tid": tenant_id, "nr": nummer},
    ).first()
    if vorhanden:
        raise HTTPException(status_code=409, detail=f"Auftragsbestaetigung {nummer} ist bereits erfasst.")
    kennung = str(uuid.uuid4())
    db.execute(
        text(
            "INSERT INTO einkauf_auftragsbestaetigungen (id, tenant_id, lieferant_id, lieferant_name, ab_nummer, "
            "bestell_nr, datum, lieferdatum, gesamtbetrag, waehrung, status, abweichungen, notizen, created_at, "
            "updated_at) VALUES (:id, :tid, :lid, :lname, :nr, :bnr, :datum, :ldatum, :betrag, :wae, 'OFFEN', "
            ":abw, :notiz, now(), now())"
        ),
        {"id": kennung, "tid": tenant_id, "lid": bestellung.get("supplierId"),
         "lname": bestellung.get("supplierName") or "", "nr": nummer,
         "bnr": bestellung.get("purchaseOrderNumber") or str(bestellung.get("id")),
         "datum": datum or business_today(), "ldatum": lieferdatum, "betrag": gesamtbetrag,
         "wae": waehrung or bestellung.get("currency") or "EUR", "abw": abweichungen, "notiz": notizen},
    )
    return kennung


@router.post("/einkauf/auftragsbestaetigungen", status_code=201, response_model=AuftragsbestaetigungAngelegt,
             summary="Auftragsbestaetigung zu einer Bestellung erfassen", dependencies=SCHREIBEN["EINKAUF"])
async def ab_erfassen(daten: AuftragsbestaetigungAnlage, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    from app.api.v1.endpoints.compat import po_get
    from app.services.einkauf_compat_service import EinkaufCompatService

    bestellung = await po_get(daten.bestellung.strip(), tenant_id=tenant_id, db=db)  # 404 im fremden Mandanten
    kennung = _lege_an(db, tenant_id, bestellung, daten.ab_nummer.strip(), datum=daten.datum,
                       lieferdatum=daten.lieferdatum, gesamtbetrag=daten.gesamtbetrag, waehrung=None,
                       abweichungen=daten.abweichungen, notizen=daten.notizen)
    db.commit()
    return EinkaufCompatService(db, tenant_id).get_auftragsbestaetigung(kennung)


class OrdrspEingang(BaseModel):
    nachricht: str = Field(..., min_length=10, max_length=2_000_000, description="EDIFACT ORDRSP (D.96A)")


class Abweichung(BaseModel):
    art: str
    position: str
    bestellt: Optional[str] = None
    bestaetigt: Optional[str] = None


class OrdrspErgebnis(AuftragsbestaetigungAngelegt):
    abweichungen: list[Abweichung]
    positionsabgleich: bool


def _bestellpositionen(db: Session, tenant_id: str, bestellung: dict[str, Any]) -> Optional[list[dict[str, Any]]]:
    """Positionen der Bestellung aus dem Einkaufsspeicher; ``None``, wenn die Bestellung keinen hat."""
    if bestellung.get("herkunft") != "einkauf":
        return None
    zeilen = db.execute(
        text("SELECT p.pos_nr, p.artikel_nr, p.lieferanten_artnr, p.menge, p.einzelpreis, p.lieferdatum "
             "FROM domain_einkauf.bestellung_positionen p JOIN domain_einkauf.bestellungen b ON b.id = p.bestellung_id "
             "WHERE b.id::text = :id AND b.tenant_id = :tid ORDER BY p.pos_nr LIMIT 5000"),
        {"id": str(bestellung["id"]), "tid": tenant_id},
    ).mappings().fetchmany(5000)  # eine Bestellung, harte Obergrenze
    return [dict(z) for z in zeilen]


@router.post("/einkauf/auftragsbestaetigungen/edi-ordrsp", status_code=201, response_model=OrdrspErgebnis,
             summary="Bestellantwort (EDIFACT ORDRSP) einlesen und mit der Bestellung abgleichen",
             dependencies=SCHREIBEN["EINKAUF"])
async def ab_aus_ordrsp(eingang: OrdrspEingang, db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    from app.api.v1.endpoints.compat import po_get
    from app.services.einkauf_compat_service import EinkaufCompatService
    from app.services.ordrsp_service import OrdrspFehler, abgleich, abweichungstext, parse_ordrsp

    try:
        antwort = parse_ordrsp(eingang.nachricht)
    except OrdrspFehler as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    bestellung = await po_get(antwort.bestellnummer, tenant_id=tenant_id, db=db)  # 404 im fremden Mandanten
    positionen = _bestellpositionen(db, tenant_id, bestellung)
    abweichungen = abgleich(positionen, antwort) if positionen is not None else []
    text_abw = abweichungstext(abweichungen)
    if positionen is None:
        text_abw = "Positionsabgleich nicht moeglich: Bestellung ohne Positionsspeicher im Einkauf."
    if antwort.funktion == "abgelehnt":
        text_abw = "\n".join(filter(None, ["Bestellung vom Lieferanten abgelehnt.", text_abw]))
    kennung = _lege_an(db, tenant_id, bestellung, antwort.ab_nummer, datum=antwort.datum,
                       lieferdatum=antwort.lieferdatum, gesamtbetrag=antwort.gesamtbetrag,
                       waehrung=antwort.waehrung, abweichungen=text_abw, notizen="Eingang per EDI (ORDRSP)")
    db.commit()
    ab = EinkaufCompatService(db, tenant_id).get_auftragsbestaetigung(kennung)
    return {**ab, "abweichungen": abweichungen, "positionsabgleich": positionen is not None}
