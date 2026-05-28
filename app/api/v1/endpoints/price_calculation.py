"""
Preis-Kalkulations-Engine (dynamisch).

POST /preis-kalkulation/berechne — compute price for artikel/kunde/menge
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/preis-kalkulation", tags=["preis-kalkulation"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PreisKalkulationInput(BaseModel):
    artikel_nr: str
    kunden_nr: str
    menge: float
    einheit: str                   # KG / T / STK / L
    lieferdatum: date
    kontrakt_nr: Optional[str] = None
    preisliste_nr: Optional[str] = None
    sorte_klasse: Optional[str] = None   # A / B / C


class KalkulationsSchritt(BaseModel):
    bezeichnung: str
    wert: float
    einheit: str = "EUR/Einheit"


class PreisKalkulationResult(BaseModel):
    basis_preis: float
    rabatt_prozent: float
    rabatt_betrag: float
    zu_abschlaege: List[KalkulationsSchritt]
    netto_preis: float
    mwst_prozent: float
    brutto_preis: float
    kalkulationsweg: List[str]
    status: str = "OK"           # OK / FALLBACK


# ---------------------------------------------------------------------------
# Sorte-Klassen-Faktoren
# ---------------------------------------------------------------------------

SORTE_FAKTOR = {"A": 1.00, "B": 0.98, "C": 0.95}
MWST = 19.0


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/berechne", response_model=PreisKalkulationResult, summary="Preis berechne")
def berechne_preis(
    payload: PreisKalkulationInput,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    kalkulationsweg: List[str] = []
    zu_abschlaege: List[KalkulationsSchritt] = []
    fallback = False

    # 1. Basispreis aus Preisliste
    basis_preis: float = 0.0
    try:
        query_params: dict = {"artikel_nr": payload.artikel_nr}
        sql = (
            "SELECT preis FROM domain_shared.preislisten"
            " WHERE artikel_nr=:artikel_nr AND is_active=TRUE"
        )
        if payload.preisliste_nr:
            sql += " AND preisliste_nr=:preisliste_nr"
            query_params["preisliste_nr"] = payload.preisliste_nr
        sql += " ORDER BY gueltig_ab DESC LIMIT 1"
        row = db.execute(text(sql), query_params).first()
        if row:
            basis_preis = float(row[0])
            kalkulationsweg.append(f"Basispreis aus Preisliste: {basis_preis:.4f} EUR/{payload.einheit}")
        else:
            kalkulationsweg.append("Basispreis: kein Eintrag gefunden → 0.00")
            fallback = True
    except Exception:
        kalkulationsweg.append("Basispreis: DB-Fehler → 0.00 (FALLBACK)")
        fallback = True

    # 2. Kundenrabatt
    rabatt_prozent: float = 0.0
    try:
        row = db.execute(
            text(
                "SELECT rabatt_prozent FROM domain_shared.rabatte"
                " WHERE kunden_nr=:kunden_nr AND is_active=TRUE"
                " ORDER BY gueltig_ab DESC LIMIT 1"
            ),
            {"kunden_nr": payload.kunden_nr},
        ).first()
        if row:
            rabatt_prozent = float(row[0])
            kalkulationsweg.append(f"Kundenrabatt: {rabatt_prozent:.2f}%")
        else:
            kalkulationsweg.append("Kundenrabatt: kein Eintrag → 0.00%")
    except Exception:
        kalkulationsweg.append("Kundenrabatt: DB-Fehler → 0.00% (FALLBACK)")
        fallback = True

    # 3. Sorte-Klassen-Faktor
    sorte_faktor = 1.0
    if payload.sorte_klasse and payload.sorte_klasse.upper() in SORTE_FAKTOR:
        sorte_faktor = SORTE_FAKTOR[payload.sorte_klasse.upper()]
        if sorte_faktor != 1.0:
            abschlag = basis_preis * (1.0 - sorte_faktor)
            zu_abschlaege.append(
                KalkulationsSchritt(
                    bezeichnung=f"Sorte-Klasse {payload.sorte_klasse.upper()}",
                    wert=-abschlag,
                )
            )
        kalkulationsweg.append(
            f"Sorte-Klasse {payload.sorte_klasse.upper()}: Faktor {sorte_faktor}"
        )

    # 4. Kontrakt-Preis-Override
    if payload.kontrakt_nr:
        try:
            row = db.execute(
                text(
                    "SELECT preis FROM domain_agrar.kontrakte"
                    " WHERE kontraktnummer=:kontrakt_nr AND is_active=TRUE LIMIT 1"
                ),
                {"kontrakt_nr": payload.kontrakt_nr},
            ).first()
            if row:
                kontrakt_preis = float(row[0])
                basis_preis = kontrakt_preis
                kalkulationsweg.append(
                    f"Kontrakt-Preis-Override ({payload.kontrakt_nr}): {kontrakt_preis:.4f} EUR/{payload.einheit}"
                )
        except Exception:
            kalkulationsweg.append(f"Kontrakt {payload.kontrakt_nr}: DB-Fehler → kein Override (FALLBACK)")
            fallback = True

    # 5. Netto-Preis berechnen
    rabatt_betrag = basis_preis * (rabatt_prozent / 100.0)
    netto_preis = basis_preis * (1.0 - rabatt_prozent / 100.0) * sorte_faktor
    kalkulationsweg.append(
        f"Netto = {basis_preis:.4f} × (1 - {rabatt_prozent:.2f}%) × {sorte_faktor} = {netto_preis:.4f}"
    )

    # 6. Brutto
    brutto_preis = netto_preis * (1.0 + MWST / 100.0)
    kalkulationsweg.append(f"Brutto = Netto × {1 + MWST/100:.2f} = {brutto_preis:.4f}")

    return PreisKalkulationResult(
        basis_preis=round(basis_preis, 4),
        rabatt_prozent=rabatt_prozent,
        rabatt_betrag=round(rabatt_betrag, 4),
        zu_abschlaege=zu_abschlaege,
        netto_preis=round(netto_preis, 4),
        mwst_prozent=MWST,
        brutto_preis=round(brutto_preis, 4),
        kalkulationsweg=kalkulationsweg,
        status="FALLBACK" if fallback else "OK",
    )
