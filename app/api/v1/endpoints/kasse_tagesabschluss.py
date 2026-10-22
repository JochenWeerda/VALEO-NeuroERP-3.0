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


from app.api.v1.schemas.base import BaseSchema


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


class TagesabschlussSubmitIn(BaseModel):
    datum: str
    kassenstand: float
    barverkauf: float
    kartenzahlung: float
    differenz: float


class TagesabschlussSubmitOut(BaseModel):
    id: str
    datum: str
    status: str
    belegnummer: str
    umsatz_gesamt: float


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


@router.post("", response_model=TagesabschlussSubmitOut, status_code=201, summary="Tagesabschluss einreichen")
async def submit_tagesabschluss(
    payload: TagesabschlussSubmitIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einfachen Kassen-Tagesabschluss buchen."""
    from app.services.fiscalization.contracts import CashPointClosingCommand, PaymentLine
    from app.services.fiscalization.providers import FiscalProviderError
    from app.services.fiscalization.service import FiscalizationService

    fiscal = FiscalizationService(db, tenant_id)
    config = fiscal.get_config()
    if not config.get("configured"):
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Fiskalisierungsprovider ist nicht konfiguriert")
    summary = fiscal.daily_summary(date.fromisoformat(payload.datum))
    if int(summary["incomplete_count"]) > 0:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Tagesabschluss blockiert: unvollstaendige TSE-Transaktionen")
    if abs(payload.barverkauf - float(summary["cash_total"])) > 0.01 or abs(
        payload.kartenzahlung - float(summary["card_total"])
    ) > 0.01:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Gemeldete Zahlarten stimmen nicht mit dem Fiskaljournal ueberein")

    abschluss_id = str(uuid4())
    belegnummer = f"KA-{payload.datum}"
    try:
        closing = fiscal.close_cash_point(
            CashPointClosingCommand(
                closing_id=belegnummer,
                cash_register_id=config["cash_register_id"],
                terminal_id=str(config.get("settings", {}).get("terminal_id") or config["client_id"]),
                business_date=date.fromisoformat(payload.datum),
                transaction_count=int(summary["transaction_count"]),
                gross_total=Decimal(str(summary["gross_total"])),
                payments=[
                    PaymentLine(method="BAR", amount=Decimal(str(summary["cash_total"]))),
                    PaymentLine(method="KARTE", amount=Decimal(str(summary["card_total"]))),
                ],
                payload={"counted_cash": str(payload.kassenstand), "cash_difference": str(payload.differenz)},
            )
        )
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Fiskalischer Tagesabschluss fehlgeschlagen: {exc}") from exc
    if closing.simulated:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Simulierter Tagesabschluss darf nicht als gebucht abgeschlossen werden")

    # Delegate to the existing compat POS tagesabschluss logic if needed,
    # or insert lightweight record
    try:
        import json
        items_json = json.dumps({
            "umsatz_bar": payload.barverkauf,
            "umsatz_ec": payload.kartenzahlung,
            "kassenstand": payload.kassenstand,
            "differenz": payload.differenz,
            "belegnummer": belegnummer,
        })

        db.execute(
            text("""
                INSERT INTO abschluss_checklisten
                (id, tenant_id, periode, abschluss_art, status, verantwortlicher,
                 beginn_datum, abschluss_datum, items, created_at, updated_at)
                VALUES
                (:id, :tid, :periode, 'kasse', 'gebucht', 'Kassierer',
                 NOW(), NOW(), :items, NOW(), NOW())
            """),
            {
                "id": abschluss_id,
                "tid": tenant_id,
                "periode": payload.datum,
                "items": items_json,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Tagesabschluss konnte nicht persistiert werden")

    return TagesabschlussSubmitOut(
        id=abschluss_id,
        datum=payload.datum,
        status="gebucht",
        belegnummer=belegnummer,
        umsatz_gesamt=payload.barverkauf + payload.kartenzahlung,
    )
