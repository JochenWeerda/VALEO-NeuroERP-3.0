"""Preiskalkulation der Maske ``preise/kalkulation`` (aus ``mask_frontend_bridges`` herausgeloest, 19.10.2026).

Bis 20.10.2026 rechnete dieser Weg mit einem fest eingetragenen Basispreis (100 je Einheit), einem erfundenen
Gruppenrabatt und 19 % MwSt — die Maske zeigte Preise, die es nicht gibt. Jetzt delegiert er an die Preisfindung
(``pricing.calculate_price``: Preisliste, Kontrakt, Staffel, Rabatte, mandantengebunden) und nimmt den Steuersatz aus
dem Verkaufs-Steuerschluessel des Artikels (``domain_erp.tax_keys`` ueber ``satz_des_schluessels``). Ohne gueltigen
Schluessel wird keine Steuer genannt.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints.mask_frontend_bridges import BridgeOut
from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(tags=["mask-frontend-bridges"])
_CENT = Decimal("0.01")


class PreisBerechnenIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    artikel_id: str | None = None
    menge_kg: float | None = None
    kunde_id: str | None = None
    kontrakt_id: str | None = None


def _geld(wert: Decimal) -> float:
    return float(wert.quantize(_CENT, rounding=ROUND_HALF_UP))


@router.post("/preise/berechnen", response_model=BridgeOut, summary="Preis kalkulieren", dependencies=SCHREIBEN["BERECHNEN"])
async def preise_berechnen(body: PreisBerechnenIn, db: Session = Depends(get_db),
                           tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    from app.api.v1.endpoints.pricing import calculate_price
    from app.finance.steuerschluessel import Steuerklaerung, satz_des_schluessels

    if not body.artikel_id:
        raise HTTPException(status_code=422, detail="Artikel fehlt.")
    menge = Decimal(str(body.menge_kg or 1))
    preis = await calculate_price(article_id=body.artikel_id, customer_id=body.kunde_id, quantity=menge,
                                  contract_id=body.kontrakt_id, user_role=None, tenant_id=tenant_id, db=db)
    listen = preis.list_price * menge
    netto = preis.net_price * menge
    schluessel = db.execute(
        text("SELECT steuerschluessel_verkauf FROM domain_inventory.articles WHERE id = :id AND tenant_id = :tid"),
        {"id": body.artikel_id, "tid": tenant_id},
    ).scalar()
    weg = [
        {"schritt": f"Listenpreis ({preis.source})", "wert": _geld(listen), "delta": 0},
        {"schritt": "Rabatt" + (f" (gesperrt: {preis.rabatt_sperrgrund})" if preis.rabatt_gesperrt else ""),
         "wert": _geld(netto), "delta": _geld(netto - listen)},
    ]
    try:
        satz = satz_des_schluessels(db, tenant_id, schluessel or "", "verkauf")
    except Steuerklaerung as grund:
        return {"netto_preis": _geld(netto), "brutto_preis": None, "mwst_betrag": None, "kalkulationsweg": weg,
                "steuerhinweis": str(grund)}
    mwst = netto * satz / Decimal(100)
    weg.append({"schritt": f"Umsatzsteuer {satz.normalize()} % ({schluessel})", "wert": _geld(netto + mwst),
                "delta": _geld(mwst)})
    return {"netto_preis": _geld(netto), "brutto_preis": _geld(netto + mwst), "mwst_betrag": _geld(mwst),
            "kalkulationsweg": weg, "steuerschluessel": schluessel}
