"""DOM-LOG-004.2 — Tour-Dispositions-Service (Kapazität + Zeitfenster)."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_VEHICLE_CAPACITY_KG = 20_000.0


class DispositionError(Exception):
    """Raised when a disposition check fails (overloaded or invalid time windows)."""


def _fetch_tour_stops(db: Session, tour_id: str) -> List[Dict[str, Any]]:
    rows = db.execute(
        text(
            "SELECT * FROM domain_logistics.tour_stops "
            "WHERE tour_id = :tid ORDER BY stop_order"
        ),
        {"tid": tour_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def _fetch_delivery_weight(db: Session, delivery_note_ref: str, tenant_id: str) -> Optional[float]:
    """Try to read total_weight_kg from domain_sales.delivery_notes by ref."""
    try:
        row = db.execute(
            text(
                "SELECT total_weight_kg FROM domain_sales.delivery_notes "
                "WHERE (id = :ref OR delivery_note_number = :ref) AND tenant_id = :tid "
                "LIMIT 1"
            ),
            {"ref": delivery_note_ref, "tid": tenant_id},
        ).mappings().first()
        if row and row.get("total_weight_kg") is not None:
            return float(row["total_weight_kg"])
    except Exception as exc:
        logger.warning("disposition: delivery note weight lookup failed for %s: %s", delivery_note_ref, exc)
    return None


def check_tour_disposition(
    db: Session,
    tour_id: str,
    tenant_id: str,
    capacity_kg: Optional[float] = None,
) -> Dict[str, Any]:
    """Run disposition check for a tour.

    Returns a result dict. Raises DispositionError when overloaded or time
    windows are invalid.  Always persists a check record.
    """
    effective_capacity = capacity_kg if capacity_kg is not None else DEFAULT_VEHICLE_CAPACITY_KG
    stops = _fetch_tour_stops(db, tour_id)

    # --- time window validation ---
    arrivals: List[datetime] = []
    for s in stops:
        pa = s.get("planned_arrival")
        if pa is not None:
            if isinstance(pa, str):
                try:
                    pa = datetime.fromisoformat(pa)
                except ValueError:
                    pa = None
            if pa is not None:
                arrivals.append(pa)

    if len(arrivals) >= 2:
        for i in range(1, len(arrivals)):
            if arrivals[i] <= arrivals[i - 1]:
                raise DispositionError(
                    f"Zeitfenster-Verletzung: Stopp {i} ({arrivals[i]}) liegt nicht nach Stopp {i-1} ({arrivals[i-1]})"
                )

    # --- weight aggregation ---
    total_weight_kg = 0.0
    has_weight_data = False
    for s in stops:
        ref = (s.get("delivery_note_ref") or "").strip()
        if ref:
            w = _fetch_delivery_weight(db, ref, tenant_id)
            if w is not None:
                total_weight_kg += w
                has_weight_data = True

    utilization_pct = (total_weight_kg / effective_capacity * 100.0) if effective_capacity > 0 else 0.0

    if utilization_pct > 100.0:
        result = "OVERLOADED"
    elif not has_weight_data:
        result = "NO_WEIGHT_DATA"
    else:
        result = "OK"

    # --- persist check record ---
    check_id = str(uuid.uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_logistics.tour_disposition_checks
                    (id, tour_id, total_weight_kg, capacity_kg, utilization_pct,
                     stops_count, result, tenant_id)
                VALUES (:id, :tour_id, :total_weight_kg, :capacity_kg,
                        :utilization_pct, :stops_count, :result, :tenant_id)
            """),
            {
                "id": check_id,
                "tour_id": tour_id,
                "total_weight_kg": round(total_weight_kg, 2),
                "capacity_kg": round(effective_capacity, 2),
                "utilization_pct": round(utilization_pct, 2),
                "stops_count": len(stops),
                "result": result,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception as exc:
        logger.warning("disposition: could not persist check record for tour %s: %s", tour_id, exc)
        db.rollback()

    payload = {
        "check_id": check_id,
        "tour_id": tour_id,
        "result": result,
        "total_weight_kg": round(total_weight_kg, 2),
        "capacity_kg": round(effective_capacity, 2),
        "utilization_pct": round(utilization_pct, 2),
        "stops_count": len(stops),
    }

    if result == "OVERLOADED":
        raise DispositionError(
            f"Tour {tour_id} ist überbucht: {round(utilization_pct, 1)}% Auslastung "
            f"({round(total_weight_kg, 0)} kg / {round(effective_capacity, 0)} kg)"
        )

    return payload
