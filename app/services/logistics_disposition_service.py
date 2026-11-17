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


def _fetch_tour_stops(db: Session, tour_id: str, tenant_id: str) -> List[Dict[str, Any]]:
    """Stopps der Tour im Mandanten; die Tour selbst muss dem Mandanten gehoeren."""
    if not db.execute(
        text("SELECT 1 FROM domain_logistics.tours WHERE id = :tid AND tenant_id = :tenant"),
        {"tid": tour_id, "tenant": tenant_id},
    ).first():
        raise DispositionError(f"Tour {tour_id} nicht gefunden")
    rows = db.execute(
        text(
            "SELECT * FROM domain_logistics.tour_stops "
            "WHERE tour_id = :tid AND tenant_id = :tenant ORDER BY stop_order"
        ),
        {"tid": tour_id, "tenant": tenant_id},
    ).mappings().all()
    return [dict(r) for r in rows]


def _fetch_delivery_weight(db: Session, delivery_note_ref: str, tenant_id: str) -> Optional[float]:
    """Ladegewicht des DocFlow-Lieferscheins in kg: Summe der Positionen, deren Einheit ein Gewicht ist.

    Positionen in Stueck haben kein Gewicht am Beleg; hat keine Position eines, bleibt das Ergebnis ``None``
    (nicht 0 - das waere eine Angabe).
    """
    from app.core.agrar_units import globaler_faktor

    try:
        # Eigener Savepoint: ein Lesefehler darf die Transaktion des Checks nicht abbrechen.
        with db.begin_nested():
            zeilen = db.execute(
                text(
                    "SELECT i.quantity, i.unit FROM domain_docflow.document_items i "
                    "JOIN domain_docflow.document_headers h ON h.id = i.header_id AND h.tenant_id = i.tenant_id "
                    "WHERE h.tenant_id = :tid AND h.doc_type = 'sales_delivery' AND h.deleted_at IS NULL "
                    "AND (h.id = :ref OR h.doc_number = :ref)"
                ),
                {"ref": delivery_note_ref, "tid": tenant_id},
            ).mappings().all()
        gewicht, gefunden = 0.0, False
        for zeile in zeilen:
            faktor = globaler_faktor(str(zeile["unit"]), "kg") if zeile["unit"] else None
            if faktor is not None and zeile["quantity"] is not None:
                gewicht += float(zeile["quantity"]) * float(faktor)
                gefunden = True
        if gefunden:
            return gewicht
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
    stops = _fetch_tour_stops(db, tour_id, tenant_id)

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
