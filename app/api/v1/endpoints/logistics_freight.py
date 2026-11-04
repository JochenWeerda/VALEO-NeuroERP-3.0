"""
Logistik – Frachtkostenberechnung (Feature 2)
Thin-router pattern: sqlalchemy.text() SQL, domain_logistics schema.
Schema/Tabelle ``freight_tariffs``: Alembic ``log_logistics_core_20260612``.

Mandant aus der Anmeldung; jede Abfrage nur im eigenen Mandanten. Bis 28.10.2026 kam er aus ``X-Tenant-ID``, und
Tarife mit ``tenant_id IS NULL`` galten als global fuer alle. Globale Tarife gab es live nicht, per API liessen sie sich
nicht anlegen; ob es gemeinsame Tarife (Mandant ``system``) geben soll, ist eine fachliche Entscheidung.

Storno: ``POST /freight-tariffs/{id}/cancel`` setzt ``status=STORNIERT``. Simulate/Calculate ignorieren stornierte Zeilen.
Alembic: ``log_freight_tariff_storno_20260613``.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import IDResponse, TypedObjectOut
from app.api.v1.schemas.logistics_freight_schemas import LogisticsFreightOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/logistik", tags=["logistik", "frachtkosten"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _postal_to_zone(plz: str) -> str:
    """Einfache Zone aus den ersten 2 Ziffern der PLZ."""
    return plz[:2] if plz and len(plz) >= 2 else "00"


def _calculate(
    db: Session,
    carrier_id: str,
    weight_kg: float,
    postal_code_from: str,
    postal_code_to: str,
    distance_km: float,
    *,
    tenant_id: str,
) -> Dict[str, Any]:
    zone_from = _postal_to_zone(postal_code_from)
    zone_to = _postal_to_zone(postal_code_to)

    row = db.execute(
        text("""
            SELECT * FROM domain_logistics.freight_tariffs
            WHERE carrier_id = :carrier_id
              AND tenant_id = :tenant_id
              AND COALESCE(status, 'AKTIV') = 'AKTIV'
              AND (zone_from IS NULL OR zone_from = :zone_from)
              AND (zone_to   IS NULL OR zone_to   = :zone_to)
              AND weight_from_kg <= :weight_kg
              AND weight_to_kg   >= :weight_kg
            ORDER BY weight_from_kg DESC
            LIMIT 1
        """),
        {
            "carrier_id": carrier_id,
            "tenant_id": tenant_id,
            "zone_from": zone_from,
            "zone_to": zone_to,
            "weight_kg": weight_kg,
        },
    ).mappings().first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Kein Tarif gefunden für Spediteur {carrier_id}, Zone {zone_from}→{zone_to}, {weight_kg} kg",
        )

    tariff = dict(row)
    raw_cost = (weight_kg / 100.0) * tariff["price_per_100kg"]
    freight_cost = max(raw_cost, tariff["min_charge"])

    return {
        "carrier_id": carrier_id,
        "freight_cost_eur": round(freight_cost, 2),
        "tariff_id": tariff["id"],
        "zone": f"{zone_from}→{zone_to}",
        "calculation_details": {
            "weight_kg": weight_kg,
            "distance_km": distance_km,
            "price_per_100kg": tariff["price_per_100kg"],
            "min_charge": tariff["min_charge"],
            "raw_cost": round(raw_cost, 2),
            "applied_minimum": freight_cost > raw_cost,
        },
    }


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class FreightTariffIn(BaseModel):
    carrier_id: str
    zone_from: Optional[str] = None
    zone_to: Optional[str] = None
    weight_from_kg: float = 0.0
    weight_to_kg: float = 999999.0
    price_per_100kg: float
    min_charge: float = 0.0


class FreightCalcIn(BaseModel):
    carrier_id: str
    distance_km: float
    weight_kg: float
    postal_code_from: str
    postal_code_to: str


class FreightTariffCancelIn(BaseModel):
    grund: str = ""


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/freight-tariffs", summary="Tariffs auflisten",
    response_model=list[LogisticsFreightOut]
)
def list_tariffs(
    carrier_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Tarif-Liste des Mandanten, optional nach Spediteur gefiltert."""
    try:
        conditions = ["tenant_id = :tenant_id"]
        params: Dict[str, Any] = {"tenant_id": tenant_id}
        if carrier_id:
            conditions.append("carrier_id = :carrier_id")
            params["carrier_id"] = carrier_id
        where = " AND ".join(conditions)
        rows = db.execute(
            text(f"SELECT * FROM domain_logistics.freight_tariffs WHERE {where} ORDER BY carrier_id, weight_from_kg"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).mappings().all()
        return [dict(r) for r in rows]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/freight-tariffs", status_code=201, summary="Tariff anlegen",
    response_model=IDResponse, dependencies=SCHREIBEN["LOGISTIK"])
def create_tariff(
    body: FreightTariffIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Neuen Frachttarif anlegen."""
    try:
        tariff_id = str(uuid.uuid4())
        db.execute(
            text("""
                INSERT INTO domain_logistics.freight_tariffs
                    (id, carrier_id, zone_from, zone_to, weight_from_kg, weight_to_kg,
                     price_per_100kg, min_charge, tenant_id)
                VALUES (:id, :carrier_id, :zone_from, :zone_to, :weight_from_kg, :weight_to_kg,
                        :price_per_100kg, :min_charge, :tenant_id)
            """),
            {"id": tariff_id, **body.model_dump(), "tenant_id": tenant_id},
        )
        db.commit()
        return {"id": tariff_id, **body.model_dump(), "tenant_id": tenant_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/freight-tariffs/{tariff_id}/cancel",
    response_model=LogisticsFreightOut,
    summary="Fracht-Tarif stornieren (soft, Mandanten-Tarife)", dependencies=SCHREIBEN["LOGISTIK"])
def cancel_tariff(
    tariff_id: str,
    body: FreightTariffCancelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Tarifzeile des Mandanten auf STORNIERT setzen."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_logistics.freight_tariffs WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": tariff_id, "tenant_id": tenant_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Tarif {tariff_id} nicht gefunden.")
        t = dict(row)
        st = (t.get("status") or "AKTIV").upper()
        if st == "STORNIERT":
            raise HTTPException(status_code=409, detail="Tarif ist bereits storniert.")
        grund = (body.grund or "").strip() or "STORNO"
        db.execute(
            text(
                """
                UPDATE domain_logistics.freight_tariffs
                SET status = 'STORNIERT',
                    storno_ts = :ts,
                    storno_grund = :grund
                WHERE id = :id AND tenant_id = :tenant_id
                """
            ),
            {
                "id": tariff_id,
                "tenant_id": tenant_id,
                "ts": datetime.now(timezone.utc),
                "grund": grund[:2000],
            },
        )
        db.commit()
        out = db.execute(
            text("SELECT * FROM domain_logistics.freight_tariffs WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": tariff_id, "tenant_id": tenant_id},
        ).mappings().first()
        return dict(out) if out else {}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/freight-cost/calculate", summary="Freight berechnen",
    response_model=LogisticsFreightOut, dependencies=SCHREIBEN["LOGISTIK"])
def calculate_freight(
    body: FreightCalcIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten berechnen (mit Buchung / Logging)."""
    try:
        return _calculate(
            db,
            body.carrier_id,
            body.weight_kg,
            body.postal_code_from,
            body.postal_code_to,
            body.distance_km,
            tenant_id=tenant_id,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/freight-cost/simulate", summary="Freight simulate",
    response_model=LogisticsFreightOut
)
def simulate_freight(
    carrier_id: str = Query(...),
    distance_km: float = Query(...),
    weight_kg: float = Query(...),
    postal_code_from: str = Query(...),
    postal_code_to: str = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten simulieren (kein Buchungs-Seiteneffekt)."""
    try:
        return _calculate(
            db,
            carrier_id,
            weight_kg,
            postal_code_from,
            postal_code_to,
            distance_km,
            tenant_id=tenant_id,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# LOG-FRACHT-001: Spediteur-Rechnung → Tour-Link + FiBu-Buchung
# ---------------------------------------------------------------------------

class CarrierInvoiceIn(BaseModel):
    tour_id: str
    carrier_id: str
    invoice_number: str
    invoice_date: str  # YYYY-MM-DD
    net_amount_eur: float
    tax_amount_eur: float = 0.0
    currency: str = "EUR"
    debit_account: str = "4820"       # Frachtkosten (SKR03)
    credit_account: str = "1600"      # Verbindlichkeiten Spediteur
    tax_account: str = "1576"         # Vorsteuer 19%
    bemerkung: Optional[str] = None


@router.post(
    "/freight-cost/carrier-invoice", response_model=TypedObjectOut,
    status_code=201,
    summary="Spediteur-Eingangsrechnung erfassen + FiBu-Buchung (LOG-FRACHT-001)", dependencies=SCHREIBEN["LOGISTIK"])
def create_carrier_invoice(
    body: CarrierInvoiceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst Spediteur-Eingangsrechnung, verknüpft sie mit der Tour und bucht ins Hauptbuch.

    Bis 28.10.2026: Eine doppelte Rechnungsnummer wurde still verworfen (``ON CONFLICT DO NOTHING``), gebucht wurde
    trotzdem, und die Antwort meldete eine Rechnung, die es nicht gab; die Tour wurde nicht auf den Mandanten
    geprueft; ein Buchungsfehler liess die Transaktion abgebrochen zurueck. Jetzt: 404 fuer eine fremde Tour, 409 fuer
    eine vorhandene Nummer, der Buchungsentwurf in einem eigenen Savepoint (scheitert er, bleibt die Rechnung ``offen``).
    Gemeldet wurde ``gebucht``, angelegt war nur ein Buchungsentwurf; der Status heisst jetzt ``entwurf``.
    """
    if not db.execute(
        text("SELECT 1 FROM domain_logistics.tours WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": body.tour_id, "tenant_id": tenant_id},
    ).first():
        raise HTTPException(status_code=404, detail=f"Tour {body.tour_id} nicht gefunden")

    invoice_id = str(uuid.uuid4())
    gross = body.net_amount_eur + body.tax_amount_eur
    journal_ref: Optional[str] = None

    # 1) Spediteur-Rechnung persistieren (Tabelle muss via Migration existieren)
    try:
        eingefuegt = db.execute(text("""
            INSERT INTO domain_logistics.carrier_invoices
              (id, tenant_id, tour_id, carrier_id, invoice_number, invoice_date,
               net_amount_eur, tax_amount_eur, gross_amount_eur, currency, bemerkung,
               status, created_at)
            VALUES
              (:id, :tenant_id, :tour_id, :carrier_id, :invoice_number, :invoice_date,
               :net, :tax, :gross, :currency, :bemerkung,
               'offen', NOW())
            ON CONFLICT (tenant_id, invoice_number) DO NOTHING
        """), {
            "id": invoice_id,
            "tenant_id": tenant_id,
            "tour_id": body.tour_id,
            "carrier_id": body.carrier_id,
            "invoice_number": body.invoice_number,
            "invoice_date": body.invoice_date,
            "net": body.net_amount_eur,
            "tax": body.tax_amount_eur,
            "gross": gross,
            "currency": body.currency,
            "bemerkung": body.bemerkung,
        }).rowcount
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler Carrier-Invoice: {exc}") from exc
    if eingefuegt != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Spediteur-Rechnung {body.invoice_number} ist bereits erfasst.")
    buchungsfehler: Optional[str] = None

    # 2) FiBu: Dr. Frachtkosten / Cr. AP Spediteur (+ Vorsteuer wenn > 0)
    try:
        # Eigener Savepoint: scheitert die Buchung, bleibt die Rechnung gespeichert und 'offen'.
        with db.begin_nested():
            from app.services.finance_transaction_service import FinanceTransactionService
            fin = FinanceTransactionService(db, tenant_id, commit_on_success=False)
            from datetime import date as _date

            inv_date = _date.fromisoformat(body.invoice_date)
            lines = [
                {"account_id": fin.account_id_for_number(body.debit_account), "debit_amount": body.net_amount_eur,
                 "credit_amount": 0.0,
                 "description": f"Frachtkosten Tour {body.tour_id} ({body.carrier_id})"},
                {"account_id": fin.account_id_for_number(body.credit_account), "debit_amount": 0.0,
                 "credit_amount": gross,
                 "description": f"AP Spediteur {body.carrier_id} {body.invoice_number}"},
            ]
            if body.tax_amount_eur > 0:
                lines.append({
                    "account_id": fin.account_id_for_number(body.tax_account),
                    "debit_amount": body.tax_amount_eur,
                    "credit_amount": 0.0,
                    "description": f"Vorsteuer 19% Fracht {body.invoice_number}",
                })

            je = fin.create(
                entry_number=f"JE-FRACHT-{body.invoice_number}",
                description=f"Spediteur-Rechnung {body.invoice_number} Tour {body.tour_id}",
                entry_date=inv_date,
                lines=lines,
                reference=body.invoice_number,
                source="logistics_freight",
                document_type="carrier_invoice",
                period=body.invoice_date[:7],
            )
            journal_ref = str(je.entry_number)

            db.execute(text("""
                UPDATE domain_logistics.carrier_invoices
                   SET fibu_journal_ref = :ref, status = 'entwurf'
                 WHERE id = :id AND tenant_id = :tenant_id
            """), {"ref": journal_ref, "id": invoice_id, "tenant_id": tenant_id})

    except Exception as exc:
        journal_ref = None
        buchungsfehler = str(exc)
        # Nicht blockierend: Rechnung ist gespeichert, Status bleibt 'offen' und
        # wird manuell nachgebucht. Der Fehlschlag wird gemeldet, damit die
        # fehlende Buchung nicht unbemerkt bleibt.
        from app.core.metrics import critical_data_path_errors_total

        critical_data_path_errors_total.labels(
            endpoint="logistics_freight_fibu", error_type="posting_failed"
        ).inc()
        logger.error(
            "FiBu-Buchung fuer Frachtrechnung %s fehlgeschlagen: %s",
            invoice_id, exc, exc_info=True,
        )

    db.commit()

    return {
        "id": invoice_id,
        "tour_id": body.tour_id,
        "carrier_id": body.carrier_id,
        "invoice_number": body.invoice_number,
        "invoice_date": body.invoice_date,
        "net_amount_eur": body.net_amount_eur,
        "tax_amount_eur": body.tax_amount_eur,
        "gross_amount_eur": gross,
        "fibu_journal_ref": journal_ref,
        # Ein Buchungsentwurf, keine Buchung: gebucht wird in der FiBu (Freigaberegeln der Eingangsrechnung).
        "status": "entwurf" if journal_ref else "offen",
        "buchungsfehler": buchungsfehler,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/freight-cost/carrier-invoices", response_model=TypedObjectOut,
    summary="Spediteur-Rechnungen auflisten",
)
def list_carrier_invoices(
    tour_id: Optional[str] = Query(None),
    carrier_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Spediteur-Rechnungen mit optionalem Filter auf Tour/Spediteur."""

    where = "tenant_id = :tenant_id"
    params: dict = {"tenant_id": tenant_id, "limit": limit}
    if tour_id:
        where += " AND tour_id = :tour_id"
        params["tour_id"] = tour_id
    if carrier_id:
        where += " AND carrier_id = :carrier_id"
        params["carrier_id"] = carrier_id

    try:
        rows = db.execute(text(f"""
            SELECT id, tour_id, carrier_id, invoice_number, invoice_date,
                   net_amount_eur, tax_amount_eur, gross_amount_eur,
                   fibu_journal_ref, status, created_at
              FROM domain_logistics.carrier_invoices
             WHERE {where}
             ORDER BY created_at DESC
             LIMIT :limit
        """), params).mappings().all()  # nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden
        items = [dict(r) for r in rows]
        for item in items:
            for k, v in item.items():
                if hasattr(v, "isoformat"):
                    item[k] = v.isoformat()
        return {"items": items, "count": len(items)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
