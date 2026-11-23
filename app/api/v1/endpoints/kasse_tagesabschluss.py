"""
Kasse – Tagesabschluss: Aktueller Tag + Buchung
Light endpoint for the simple kasse/tagesabschluss page (not the enhanced POS version).
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id




router = APIRouter(prefix="/kasse/tagesabschluss", tags=["Kasse - Tagesabschluss"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TagesabschlussAktuell(BaseModel):
    datum: str
    barverkauf: float
    kartenzahlung: float
    umsatz_gesamt: float
    transaktionen: int
    stornos: int
    retouren: int


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/aktuell", response_model=TagesabschlussAktuell, summary="Aktuell abrufen")
async def get_aktuell(
    datum: Optional[str] = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Tagesabschluss-Daten fuer den aktuellen (oder angegebenen) Tag."""
    target_date = datum or date.today().isoformat()

    # Try to aggregate from pos transactions for the given date
    try:
        row = db.execute(
            text("""
                SELECT
                    COALESCE(SUM(CASE WHEN items::text LIKE '%%umsatz_bar%%'
                        THEN (items::json->>'umsatz_bar')::float ELSE 0 END), 0) AS barverkauf,
                    COALESCE(SUM(CASE WHEN items::text LIKE '%%umsatz_ec%%'
                        THEN (items::json->>'umsatz_ec')::float ELSE 0 END), 0) AS kartenzahlung
                FROM abschluss_checklisten
                WHERE tenant_id = :tid
                  AND abschluss_art = 'kasse'
                  AND periode = :datum
            """),
            {"tid": tenant_id, "datum": target_date},
        ).fetchone()

        if row and (row[0] > 0 or row[1] > 0):
            bar = float(row[0])
            karte = float(row[1])
            return TagesabschlussAktuell(
                datum=target_date,
                barverkauf=bar,
                kartenzahlung=karte,
                umsatz_gesamt=bar + karte,
                transaktionen=0,
                stornos=0,
                retouren=0,
            )
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        db.rollback()

    from app.services.fiscalization.service import FiscalizationService
    summary = FiscalizationService(db, tenant_id).daily_summary(date.fromisoformat(target_date))
    return TagesabschlussAktuell(
        datum=target_date,
        barverkauf=float(summary["cash_total"]),
        kartenzahlung=float(summary["card_total"]),
        umsatz_gesamt=float(summary["gross_total"]),
        transaktionen=int(summary["transaction_count"]),
        stornos=0,
        retouren=0,
    )


# Gebucht wird der Kassentag ausschliesslich ueber POST /pos/tagesabschluss (fiskalischer Abschluss, Buchung ueber
# den Buchungsdienst, Stand in domain_pos.pos_tagesabschluesse). Der fruehere POST hier meldete "gebucht", ohne
# zu buchen (entfernt 19.11.2026).


def merke_kassentag_abgeschlossen(db: Session, tenant_id: str, kasse_id: str, datum, z_bon_nr: str,
                                  tse_referenz, umsatz_brutto, kassierer) -> None:
    """Stand des Kassentags fuer Z-Bon und Kassenmasken (``domain_pos.pos_tagesabschluesse``), in der Transaktion
    des Abschlusses. Bis 19.11.2026 schrieb ihn nur eine zweite, ueberdeckte Zustandsmaschine mit simulierter
    TSE-Signatur; nach einem echten Abschluss blieb der Tag dort offen."""
    db.execute(
        text("""
            INSERT INTO domain_pos.pos_tagesabschluesse
            (id, tenant_id, kasse_id, datum, status, z_bon_nr, tse_signatur, umsatz_brutto_eur, operator,
             created_at, updated_at)
            VALUES (CAST(:id AS uuid), :tid, :kasse, :datum, 'ABGESCHLOSSEN', :zbon, :tse, :umsatz, :operator,
                    NOW(), NOW())
            ON CONFLICT (tenant_id, kasse_id, datum) DO UPDATE SET
              status = 'ABGESCHLOSSEN', z_bon_nr = EXCLUDED.z_bon_nr, tse_signatur = EXCLUDED.tse_signatur,
              umsatz_brutto_eur = EXCLUDED.umsatz_brutto_eur, fehler_grund = NULL, updated_at = NOW()
        """),
        {"id": str(uuid4()), "tid": tenant_id, "kasse": kasse_id, "datum": datum.isoformat(), "zbon": z_bon_nr,
         "tse": tse_referenz, "umsatz": Decimal(str(umsatz_brutto or 0)), "operator": kassierer or "Kasse"},
    )
