"""Liquidity Planning API -- Liquiditaetsplanung

Berechnet Liquiditaetslage aus OP-Debitoren, OP-Kreditoren,
offenen Auftraegen und Bank-/Kassenbestaenden.
"""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/finance/liquidity", tags=["finance", "liquidity"])
MAX_LIQUIDITY_FORECAST_BUCKETS = 13


class LiquidityBucket(BaseModel):
    zeitraum: str
    erwartete_eingaenge: float
    erwartete_ausgaenge: float
    netto: float


class LiquidityOverview(BaseModel):
    aktuell: float
    ziel: float
    forderungen_offen: float
    verbindlichkeiten_offen: float
    netto_working_capital: float
    prognose: list[LiquidityBucket]
    waehrung: str = "EUR"
    stichtag: str


def _safe_float(val) -> float:
    if val is None:
        return 0.0
    return float(val)


@router.get("/overview", response_model=LiquidityOverview, summary="Liquidity overview abrufen")
async def get_liquidity_overview(
    tage_voraus: int = Query(90, ge=7, le=365, description="Prognosehorizont in Tagen"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liquiditaetsuebersicht mit Echtdaten aus OP und Auftraegen."""

    today = date.today()

    # Sum open receivables (Debitoren-OP)
# Offene Posten liegen in `domain_erp.offene_posten` — dort schreibt der
# Belegfluss hinein (Rechnung aus Lieferschein, Sammelrechnung). Gelesen wurde
# `domain_shared.open_items`: eine Tabelle, die es gibt, die aber **leer** ist.
# Die Uebersicht meldete deshalb immer 0,00 — und eine Null sieht aus wie „nichts
# offen", nicht wie „falsche Tabelle".
#
# Die Spalten heissen dort deutsch: `offen` ist der offene Betrag (schon
# abzueglich Zahlungen), `konto_typ` traegt 'debitoren'/'kreditoren', `op_status`
# 'offen'/'storniert'.
    forderungen = _safe_float(db.execute(text(
        "SELECT COALESCE(SUM(offen), 0) "
        "FROM domain_erp.offene_posten "
        "WHERE tenant_id = :tid AND konto_typ = 'debitoren' AND op_status = 'offen'"
    ), {"tid": tenant_id}).scalar())

    # Sum open payables (Kreditoren-OP)
    verbindlichkeiten = _safe_float(db.execute(text(
        "SELECT COALESCE(SUM(offen), 0) "
        "FROM domain_erp.offene_posten "
        "WHERE tenant_id = :tid AND konto_typ = 'kreditoren' AND op_status = 'offen'"
    ), {"tid": tenant_id}).scalar())

    # Bank/cash balance from journal (Kontenklasse 1xxx = liquide Mittel)
    bank_saldo = _safe_float(db.execute(text(
        "SELECT COALESCE(SUM(CASE WHEN debit > 0 THEN debit ELSE -credit END), 0) "
        "FROM domain_shared.journal_entries "
        "WHERE tenant_id = :tid AND account_number LIKE '1%'"
    ), {"tid": tenant_id}).scalar())

    nwc = forderungen - verbindlichkeiten

    # Build forecast buckets (30-day intervals)
    prognose: list[LiquidityBucket] = []
    bucket_days = 30
    horizon_days = max(7, min(tage_voraus, 365))
    for bucket_index in range(MAX_LIQUIDITY_FORECAST_BUCKETS):
        i = bucket_index * bucket_days
        if i >= horizon_days:
            break
        von = today + timedelta(days=i)
        bis = today + timedelta(days=min(i + bucket_days, horizon_days))

        eingaenge = _safe_float(db.execute(text(
            "SELECT COALESCE(SUM(offen), 0) "
            "FROM domain_erp.offene_posten "
            "WHERE tenant_id = :tid AND konto_typ = 'debitoren' AND op_status = 'offen' "
            "AND COALESCE(faelligkeit, due_date) BETWEEN :von AND :bis"
        ), {"tid": tenant_id, "von": von, "bis": bis}).scalar())

        ausgaenge = _safe_float(db.execute(text(
            "SELECT COALESCE(SUM(offen), 0) "
            "FROM domain_erp.offene_posten "
            "WHERE tenant_id = :tid AND konto_typ = 'kreditoren' AND op_status = 'offen' "
            "AND COALESCE(faelligkeit, due_date) BETWEEN :von AND :bis"
        ), {"tid": tenant_id, "von": von, "bis": bis}).scalar())

        prognose.append(LiquidityBucket(
            zeitraum=f"{von.isoformat()} – {bis.isoformat()}",
            erwartete_eingaenge=eingaenge,
            erwartete_ausgaenge=ausgaenge,
            netto=eingaenge - ausgaenge,
        ))

    return LiquidityOverview(
        aktuell=bank_saldo,
        ziel=250000,
        forderungen_offen=forderungen,
        verbindlichkeiten_offen=verbindlichkeiten,
        netto_working_capital=nwc,
        prognose=prognose,
        stichtag=today.isoformat(),
    )
