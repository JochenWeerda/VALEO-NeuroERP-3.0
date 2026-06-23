"""DOM-AGRAR-004.3 — Trocknungsabrechnung-Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_COST_EUR_PER_PCT_TON = 1.50


class TrocknungError(Exception):
    """Raised when drying calculation constraints are violated."""


def berechne_trocknung(
    db: Session,
    partie_id: str,
    tenant_id: str,
    moisture_out_pct: float,
    cost_eur_per_pct_ton: Optional[float] = None,
) -> Dict[str, Any]:
    """Calculate and persist a drying charge for a Partie.

    Idempotent: if a Trocknung record already exists for this partie_id, return it.
    Fail-closed: moisture_out >= moisture_in raises TrocknungError.
    """
    row = db.execute(
        text("SELECT * FROM domain_agrar.agrar_partien WHERE id = :id"),
        {"id": partie_id},
    ).mappings().first()
    if not row:
        raise TrocknungError(f"Partie {partie_id} nicht gefunden")
    partie = dict(row)
    if partie.get("tenant_id") and partie["tenant_id"] != tenant_id:
        raise TrocknungError(f"Partie {partie_id} gehört nicht zu Tenant {tenant_id}")
    if (partie.get("status") or "").upper() != "OFFEN":
        raise TrocknungError(
            f"Trocknungsabrechnung erfordert Status OFFEN (aktuell: {partie.get('status')!r})"
        )

    # idempotency
    existing = db.execute(
        text(
            "SELECT * FROM domain_agrar.agrar_trocknung_abrechnungen "
            "WHERE partie_id = :pid AND tenant_id = :tid LIMIT 1"
        ),
        {"pid": partie_id, "tid": tenant_id},
    ).mappings().first()
    if existing:
        logger.info("trocknung: already exists for partie %s — returning existing", partie_id)
        return {**dict(existing), "idempotent": True}

    moisture_in = float(partie.get("avg_moisture_pct") or 0)
    brutto_kg = float(partie.get("total_gross_kg") or 0)

    if moisture_out_pct >= moisture_in:
        raise TrocknungError(
            f"moisture_out ({moisture_out_pct}%) >= moisture_in ({moisture_in}%) — keine Trocknung nötig"
        )

    cost_rate = cost_eur_per_pct_ton if cost_eur_per_pct_ton is not None else DEFAULT_COST_EUR_PER_PCT_TON
    trocknung_pct = moisture_in - moisture_out_pct
    trocknungsabzug_kg = round(brutto_kg * trocknung_pct / 100, 3)
    trocknungskosten_eur = round((brutto_kg / 1000) * trocknung_pct * cost_rate, 2)

    rec_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_agrar.agrar_trocknung_abrechnungen
                (id, partie_id, tenant_id, moisture_in_pct, moisture_out_pct,
                 brutto_kg, trocknungsabzug_kg, trocknungskosten_eur)
            VALUES (:id, :partie_id, :tenant_id, :moisture_in_pct, :moisture_out_pct,
                    :brutto_kg, :trocknungsabzug_kg, :trocknungskosten_eur)
        """),
        {
            "id": rec_id,
            "partie_id": partie_id,
            "tenant_id": tenant_id,
            "moisture_in_pct": round(moisture_in, 3),
            "moisture_out_pct": round(moisture_out_pct, 3),
            "brutto_kg": round(brutto_kg, 3),
            "trocknungsabzug_kg": trocknungsabzug_kg,
            "trocknungskosten_eur": trocknungskosten_eur,
        },
    )
    db.commit()
    logger.info(
        "trocknung: partie %s — %.1f%% Trocknung, %.2f EUR Kosten",
        partie_id, trocknung_pct, trocknungskosten_eur,
    )
    return {
        "id": rec_id,
        "partie_id": partie_id,
        "tenant_id": tenant_id,
        "moisture_in_pct": round(moisture_in, 3),
        "moisture_out_pct": round(moisture_out_pct, 3),
        "trocknung_pct": round(trocknung_pct, 3),
        "brutto_kg": round(brutto_kg, 3),
        "trocknungsabzug_kg": trocknungsabzug_kg,
        "trocknungskosten_eur": trocknungskosten_eur,
        "idempotent": False,
    }
