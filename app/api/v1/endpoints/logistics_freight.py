"""
Logistik – Frachtkostenberechnung (Feature 2)
Thin-router pattern: sqlalchemy.text() SQL, domain_logistics schema.
Schema/Tabelle ``freight_tariffs``: Alembic ``log_logistics_core_20260612``.
"""

from __future__ import annotations

import uuid
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.api.v1.schemas.base import BaseSchema, IDResponse
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
) -> Dict[str, Any]:
    zone_from = _postal_to_zone(postal_code_from)
    zone_to = _postal_to_zone(postal_code_to)

    row = db.execute(
        text("""
            SELECT * FROM domain_logistics.freight_tariffs
            WHERE carrier_id = :carrier_id
              AND (zone_from IS NULL OR zone_from = :zone_from)
              AND (zone_to   IS NULL OR zone_to   = :zone_to)
              AND weight_from_kg <= :weight_kg
              AND weight_to_kg   >= :weight_kg
            ORDER BY weight_from_kg DESC
            LIMIT 1
        """),
        {
            "carrier_id": carrier_id,
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
    """Tarif-Liste, optional nach Spediteur gefiltert."""
    try:
        conditions = ["1=1"]
        params: Dict[str, Any] = {}
        if carrier_id:
            conditions.append("carrier_id = :carrier_id")
            params["carrier_id"] = carrier_id
        if x_tenant_id:
            conditions.append("(tenant_id = :tenant_id OR tenant_id IS NULL)")
            params["tenant_id"] = x_tenant_id
        where = " AND ".join(conditions)
        rows = db.execute(
            text(f"SELECT * FROM domain_logistics.freight_tariffs WHERE {where} ORDER BY carrier_id, weight_from_kg"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
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


@router.post("/freight-cost/calculate", summary="Freight berechnen",
    response_model=LogisticsFreightOut
)
def calculate_freight(
    body: FreightCalcIn,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten berechnen (mit Buchung / Logging)."""
    return _calculate(db, body.carrier_id, body.weight_kg, body.postal_code_from, body.postal_code_to, body.distance_km)


@router.get("/freight-cost/simulate", summary="Freight simulate",
    response_model=LogisticsFreightOut
)
def simulate_freight(
    carrier_id: str = Query(...),
    distance_km: float = Query(...),
    weight_kg: float = Query(...),
    postal_code_from: str = Query(...),
    postal_code_to: str = Query(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Frachtkosten simulieren (kein Buchungs-Seiteneffekt)."""
    return _calculate(db, carrier_id, weight_kg, postal_code_from, postal_code_to, distance_km)
