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


@router.post("/einkauf/auftragsbestaetigungen", status_code=201, response_model=AuftragsbestaetigungAngelegt,
             summary="Auftragsbestaetigung zu einer Bestellung erfassen", dependencies=SCHREIBEN["EINKAUF"])
async def ab_erfassen(daten: AuftragsbestaetigungAnlage, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    from app.api.v1.endpoints.compat import po_get
    from app.services.einkauf_compat_service import EinkaufCompatService

    bestellung = await po_get(daten.bestellung.strip(), tenant_id=tenant_id, db=db)  # 404 im fremden Mandanten
    nummer = daten.ab_nummer.strip()
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
         "datum": daten.datum or business_today(), "ldatum": daten.lieferdatum, "betrag": daten.gesamtbetrag,
         "wae": bestellung.get("currency") or "EUR", "abw": daten.abweichungen, "notiz": daten.notizen},
    )
    db.commit()
    return EinkaufCompatService(db, tenant_id).get_auftragsbestaetigung(kennung)
