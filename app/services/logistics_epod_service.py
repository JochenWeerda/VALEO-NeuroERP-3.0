"""DOM-LOG-004.3 — ePOD-Lifecycle-Service (Ablieferungsbeleg → Settlement)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

VALID_SETTLE_STATUSES = {"GELIEFERT", "SIGNED"}


class EpodError(Exception):
    """Raised when ePOD lifecycle constraints are violated."""


def _get_stop(db: Session, stop_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("SELECT * FROM domain_logistics.tour_stops WHERE id = :sid"),
        {"sid": stop_id},
    ).mappings().first()
    return dict(row) if row else None


def settle_epod(
    db: Session,
    tour_id: str,
    stop_id: str,
    tenant_id: str,
    recipient_name: Optional[str] = None,
    delivered_at_iso: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Settle an ePOD stop (fail-closed: requires GELIEFERT or SIGNED status).

    Idempotent: if a settlement already exists for this stop_id, returns it.
    """
    stop = _get_stop(db, stop_id)
    if not stop:
        raise EpodError(f"Stopp {stop_id} nicht gefunden")

    if stop.get("tour_id") and str(stop["tour_id"]) != tour_id:
        raise EpodError(f"Stopp {stop_id} gehört nicht zu Tour {tour_id}")

    # fail-closed: only allow settlement for delivered/signed stops
    current_status = (stop.get("status") or "").upper()
    epod_status = (stop.get("epod_status") or "").upper()
    if current_status not in VALID_SETTLE_STATUSES and epod_status not in VALID_SETTLE_STATUSES:
        raise EpodError(
            f"ePOD-Settlement erfordert Status GELIEFERT oder SIGNED "
            f"(aktuell: status={stop.get('status')}, epod_status={stop.get('epod_status')})"
        )

    # idempotency: check existing settlement
    existing = db.execute(
        text("SELECT * FROM domain_logistics.epod_settlements WHERE stop_id = :sid"),
        {"sid": stop_id},
    ).mappings().first()
    if existing:
        logger.info("epod: settlement already exists for stop %s — returning existing", stop_id)
        return dict(existing)

    settlement_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_logistics.epod_settlements
                (id, tour_id, stop_id, recipient_name, delivered_at, notes, tenant_id)
            VALUES (:id, :tour_id, :stop_id, :recipient_name,
                    :delivered_at::timestamptz, :notes, :tenant_id)
        """),
        {
            "id": settlement_id,
            "tour_id": tour_id,
            "stop_id": stop_id,
            "recipient_name": recipient_name,
            "delivered_at": delivered_at_iso,
            "notes": notes,
            "tenant_id": tenant_id,
        },
    )
    # update stop epod_status
    db.execute(
        text(
            "UPDATE domain_logistics.tour_stops SET epod_status = 'SETTLED' WHERE id = :sid"
        ),
        {"sid": stop_id},
    )
    db.commit()
    logger.info("epod: settled stop %s (tour %s)", stop_id, tour_id)
    return {
        "id": settlement_id,
        "tour_id": tour_id,
        "stop_id": stop_id,
        "recipient_name": recipient_name,
        "delivered_at": delivered_at_iso,
        "notes": notes,
        "tenant_id": tenant_id,
        "epod_status": "SETTLED",
    }
