"""
Logistik – Frachtkostenberechnung (Feature 2)
Thin-router pattern: sqlalchemy.text() SQL, domain_logistics schema.
Schema/Tabelle ``freight_tariffs``: Alembic ``log_logistics_core_20260612``.

Tenant: ``GET /freight-cost/simulate``, ``POST /freight-cost/calculate`` und ``POST /freight-tariffs`` verlangen
``X-Tenant-ID`` (422). Tarifauswahl wie bei ``GET /freight-tariffs``:
``tenant_id IS NULL`` (global) oder passende ``tenant_id``.

``GET /freight-tariffs``: ohne ``X-Tenant-ID`` nur Zeilen mit ``tenant_id IS NULL`` (kein
Mandanten-Leak). Mit Header: eigener Mandant plus globale Tarife.

Storno: ``POST /freight-tariffs/{id}/cancel`` (``X-Tenant-ID``) setzt ``status=STORNIERT``;
nur Mandanten-Tarife (nicht ``tenant_id IS NULL``). Simulate/Calculate ignorieren stornierte Zeilen.
Alembic: ``log_freight_tariff_storno_20260613``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.api.v1.schemas.base import IDResponse
from app.api.v1.schemas.logistics_freight_schemas import LogisticsFreightOut


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
              AND (tenant_id IS NULL OR tenant_id = :tenant_id)
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
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Tarif-Liste, optional nach Spediteur gefiltert.

    Ohne ``X-Tenant-ID``: nur globale Tarife (``tenant_id IS NULL``).
    Mit Header: eigener Mandant plus globale Tarife.
    """
    try:
        conditions = ["1=1"]
        params: Dict[str, Any] = {}
        if carrier_id:
            conditions.append("carrier_id = :carrier_id")
            params["carrier_id"] = carrier_id
        if x_tenant_id:
            conditions.append("(tenant_id = :tenant_id OR tenant_id IS NULL)")
            params["tenant_id"] = x_tenant_id
        else:
            conditions.append("tenant_id IS NULL")
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
    response_model=IDResponse
)
def create_tariff(
    body: FreightTariffIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Neuen Frachttarif anlegen."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
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
            {"id": tariff_id, **body.model_dump(), "tenant_id": x_tenant_id},
        )
        db.commit()
        return {"id": tariff_id, **body.model_dump(), "tenant_id": x_tenant_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/freight-tariffs/{tariff_id}/cancel",
    response_model=LogisticsFreightOut,
    summary="Fracht-Tarif stornieren (soft, Mandanten-Tarife)",
)
def cancel_tariff(
    tariff_id: str,
    body: FreightTariffCancelIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Tarifzeile auf STORNIERT setzen; globale Tarife (``tenant_id IS NULL``) sind geschuetzt."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    try:
        row = db.execute(
            text("SELECT * FROM domain_logistics.freight_tariffs WHERE id = :id"),
            {"id": tariff_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Tarif {tariff_id} nicht gefunden.")
        t = dict(row)
        tid = t.get("tenant_id")
        if tid is None:
            raise HTTPException(
                status_code=403,
                detail="Globale Tarife (tenant_id IS NULL) koennen per API nicht storniert werden.",
            )
        if tid != x_tenant_id:
            raise HTTPException(status_code=403, detail="Tarif gehoert zu einem anderen Mandanten.")
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
                WHERE id = :id
                """
            ),
            {
                "id": tariff_id,
                "ts": datetime.now(timezone.utc),
                "grund": grund[:2000],
            },
        )
        db.commit()
        out = db.execute(
            text("SELECT * FROM domain_logistics.freight_tariffs WHERE id = :id"),
            {"id": tariff_id},
        ).mappings().first()
        return dict(out) if out else {}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/freight-cost/calculate", summary="Freight berechnen",
    response_model=LogisticsFreightOut
)
def calculate_freight(
    body: FreightCalcIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten berechnen (mit Buchung / Logging)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    try:
        return _calculate(
            db,
            body.carrier_id,
            body.weight_kg,
            body.postal_code_from,
            body.postal_code_to,
            body.distance_km,
            tenant_id=x_tenant_id,
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
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten simulieren (kein Buchungs-Seiteneffekt)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    try:
        return _calculate(
            db,
            carrier_id,
            weight_kg,
            postal_code_from,
            postal_code_to,
            distance_km,
            tenant_id=x_tenant_id,
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
    "/freight-cost/carrier-invoice", response_model=dict,
    status_code=201,
    summary="Spediteur-Eingangsrechnung erfassen + FiBu-Buchung (LOG-FRACHT-001)",
)
def create_carrier_invoice(
    body: CarrierInvoiceIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst Spediteur-Eingangsrechnung, verknüpft sie mit der Tour und bucht ins Hauptbuch."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")

    invoice_id = str(uuid.uuid4())
    gross = body.net_amount_eur + body.tax_amount_eur
    journal_ref: Optional[str] = None

    # 1) Spediteur-Rechnung persistieren (Tabelle muss via Migration existieren)
    try:
        db.execute(text("""
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
            "tenant_id": x_tenant_id,
            "tour_id": body.tour_id,
            "carrier_id": body.carrier_id,
            "invoice_number": body.invoice_number,
            "invoice_date": body.invoice_date,
            "net": body.net_amount_eur,
            "tax": body.tax_amount_eur,
            "gross": gross,
            "currency": body.currency,
            "bemerkung": body.bemerkung,
        })
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB-Fehler Carrier-Invoice: {exc}") from exc

    # 2) FiBu: Dr. Frachtkosten / Cr. AP Spediteur (+ Vorsteuer wenn > 0)
    try:
        from app.services.finance_transaction_service import FinanceTransactionService
        from datetime import date as _date

        inv_date = _date.fromisoformat(body.invoice_date)
        lines = [
            {"account_id": body.debit_account, "debit_amount": body.net_amount_eur,
             "credit_amount": 0.0,
             "description": f"Frachtkosten Tour {body.tour_id} ({body.carrier_id})"},
            {"account_id": body.credit_account, "debit_amount": 0.0,
             "credit_amount": gross,
             "description": f"AP Spediteur {body.carrier_id} {body.invoice_number}"},
        ]
        if body.tax_amount_eur > 0:
            lines.append({
                "account_id": body.tax_account,
                "debit_amount": body.tax_amount_eur,
                "credit_amount": 0.0,
                "description": f"Vorsteuer 19% Fracht {body.invoice_number}",
            })

        fin = FinanceTransactionService(db, x_tenant_id)
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
               SET fibu_journal_ref = :ref, status = 'gebucht'
             WHERE id = :id AND tenant_id = :tenant_id
        """), {"ref": journal_ref, "id": invoice_id, "tenant_id": x_tenant_id})

    except Exception:
        # FiBu-Fehler → Invoice gespeichert, Status bleibt 'offen', manuell nachbuchen
        pass

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
        "status": "gebucht" if journal_ref else "offen",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/freight-cost/carrier-invoices", response_model=dict,
    summary="Spediteur-Rechnungen auflisten",
)
def list_carrier_invoices(
    tour_id: Optional[str] = Query(None),
    carrier_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Spediteur-Rechnungen mit optionalem Filter auf Tour/Spediteur."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")

    where = "tenant_id = :tenant_id"
    params: dict = {"tenant_id": x_tenant_id, "limit": limit}
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
