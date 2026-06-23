"""DOM-PROC-004.3 — Wareneingangs-Buchung + QS Service."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

QS_STATUSES = {"AUSSTEHEND", "BESTANDEN", "GESPERRT"}


class WareneingangError(Exception):
    """Raised when Wareneingang constraints are violated."""


def buche_wareneingang(
    db: Session,
    bestellung_id: str,
    tenant_id: str,
    menge_erhalten: float,
    einheit: str,
    lager_id: str,
    operator: str = "system",
    qs_status: str = "AUSSTEHEND",
) -> Dict[str, Any]:
    """Bucht Wareneingang für eine Bestellung (nur wenn VERSANDT, idempotent)."""
    if qs_status not in QS_STATUSES:
        raise WareneingangError(f"Ungültiger QS-Status: {qs_status}. Erlaubt: {QS_STATUSES}")

    # check bestellung status
    bestellung = db.execute(
        text("SELECT * FROM domain_procurement.proc_purchase_orders WHERE id = :id AND tenant_id = :tid"),
        {"id": bestellung_id, "tid": tenant_id},
    ).mappings().first()
    if not bestellung:
        raise WareneingangError(f"Bestellung {bestellung_id} nicht gefunden")

    b_status = (bestellung.get("status") or "").upper()
    if b_status not in {"VERSANDT", "WE_ERHALTEN"}:
        raise WareneingangError(
            f"WE-Buchung nur für Bestellungen im Status VERSANDT möglich (aktuell: {b_status})"
        )

    # idempotency: check for existing WE with same bestellung_id
    existing = db.execute(
        text("""
            SELECT * FROM domain_procurement.proc_wareneingaenge
            WHERE bestellung_id = :bid AND tenant_id = :tid
            ORDER BY created_at DESC LIMIT 1
        """),
        {"bid": bestellung_id, "tid": tenant_id},
    ).mappings().first()
    if existing:
        return {**dict(existing), "idempotent": True}

    we_id = str(uuid.uuid4())
    jetzt = datetime.now(timezone.utc).isoformat()

    db.execute(
        text("""
            INSERT INTO domain_procurement.proc_wareneingaenge
                (id, bestellung_id, tenant_id, menge_erhalten, einheit, lager_id,
                 qs_status, gebucht_am, operator, created_at)
            VALUES (:id, :bid, :tid, :menge, :einheit, :lager_id, :qs, NOW(), :operator, NOW())
        """),
        {
            "id": we_id, "bid": bestellung_id, "tid": tenant_id,
            "menge": menge_erhalten, "einheit": einheit, "lager_id": lager_id,
            "qs": qs_status, "operator": operator,
        },
    )
    # advance bestellung to WE_ERHALTEN
    db.execute(
        text("UPDATE domain_procurement.proc_purchase_orders SET status = 'WE_ERHALTEN' WHERE id = :id"),
        {"id": bestellung_id},
    )
    db.commit()
    logger.info("wareneingang %s gebucht für Bestellung %s, QS: %s", we_id, bestellung_id, qs_status)
    return {
        "id": we_id, "bestellung_id": bestellung_id, "tenant_id": tenant_id,
        "menge_erhalten": menge_erhalten, "einheit": einheit, "lager_id": lager_id,
        "qs_status": qs_status, "gebucht_am": jetzt, "idempotent": False,
    }


def update_qs_status(
    db: Session,
    we_id: str,
    tenant_id: str,
    qs_status: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Aktualisiert QS-Status eines Wareneingangs."""
    if qs_status not in QS_STATUSES:
        raise WareneingangError(f"Ungültiger QS-Status: {qs_status}")

    row = db.execute(
        text("SELECT * FROM domain_procurement.proc_wareneingaenge WHERE id = :id"),
        {"id": we_id},
    ).mappings().first()
    if not row:
        raise WareneingangError(f"Wareneingang {we_id} nicht gefunden")
    if row["tenant_id"] != tenant_id:
        raise WareneingangError(f"Wareneingang {we_id} gehört nicht zu Tenant {tenant_id}")

    db.execute(
        text("UPDATE domain_procurement.proc_wareneingaenge SET qs_status = :qs WHERE id = :id"),
        {"qs": qs_status, "id": we_id},
    )
    db.commit()
    logger.info("wareneingang %s QS-Status → %s von %s", we_id, qs_status, operator)
    return {**dict(row), "qs_status": qs_status}
