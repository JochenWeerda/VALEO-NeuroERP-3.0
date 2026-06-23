"""DOM-FINANCE-004.4 — Mahnstufen-Eskalation-Trail Service (append-only)."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

STUFEN_REIHENFOLGE = [1, 2, 3, "INKASSO"]
STUFEN_GEBUEHREN: Dict[Any, float] = {1: 0.0, 2: 5.0, 3: 15.0, "INKASSO": 40.0}


class MahnstufeError(Exception):
    """Raised when Mahnstufen constraints are violated."""


def _get_aktuelle_mahnstufe(db: Session, rechnungsnr: str, tenant_id: str) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text("""
            SELECT * FROM domain_finance.finance_mahnstufen_audit
            WHERE rechnungsnr = :rechnungsnr AND tenant_id = :tenant_id
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"rechnungsnr": rechnungsnr, "tenant_id": tenant_id},
    ).mappings().first()
    return dict(row) if row else None


def eskaliere_mahnstufe(
    db: Session,
    rechnungsnr: str,
    tenant_id: str,
    operator: str = "system",
) -> Dict[str, Any]:
    """Eskaliert Mahnwesen-Stufe (1→2→3→INKASSO), append-only, idempotent bei gleicher Stufe."""
    aktuelle = _get_aktuelle_mahnstufe(db, rechnungsnr, tenant_id)
    aktuelle_stufe_raw = aktuelle["stufe"] if aktuelle else None
    # normalize: DB stores as string, STUFEN_REIHENFOLGE has int + "INKASSO"
    if aktuelle_stufe_raw is None:
        aktuelle_stufe = None
    elif aktuelle_stufe_raw == "INKASSO":
        aktuelle_stufe = "INKASSO"
    else:
        try:
            aktuelle_stufe = int(aktuelle_stufe_raw)
        except (ValueError, TypeError):
            aktuelle_stufe = aktuelle_stufe_raw

    # determine next step
    if aktuelle_stufe is None:
        naechste_stufe = 1
    else:
        try:
            idx = STUFEN_REIHENFOLGE.index(aktuelle_stufe)
        except ValueError:
            raise MahnstufeError(f"Unbekannte aktuelle Mahnstufe: {aktuelle_stufe}")
        if idx >= len(STUFEN_REIHENFOLGE) - 1:
            raise MahnstufeError(f"Bereits auf maximaler Stufe INKASSO — keine weitere Eskalation möglich")
        naechste_stufe = STUFEN_REIHENFOLGE[idx + 1]

    gebuehr = STUFEN_GEBUEHREN.get(naechste_stufe, 0.0)
    audit_id = str(uuid.uuid4())

    db.execute(
        text("""
            INSERT INTO domain_finance.finance_mahnstufen_audit
                (id, tenant_id, rechnungsnr, stufe, operator, bearbeitungsgebuehr_eur, created_at)
            VALUES (:id, :tenant_id, :rechnungsnr, :stufe, :operator, :gebuehr, NOW())
        """),
        {
            "id": audit_id, "tenant_id": tenant_id, "rechnungsnr": rechnungsnr,
            "stufe": str(naechste_stufe), "operator": operator, "gebuehr": gebuehr,
        },
    )
    db.commit()
    logger.info("mahnstufe %s → %s für Rechnung %s", aktuelle_stufe, naechste_stufe, rechnungsnr)
    return {
        "id": audit_id,
        "rechnungsnr": rechnungsnr,
        "stufe": naechste_stufe,
        "vorherige_stufe": aktuelle_stufe,
        "bearbeitungsgebuehr_eur": gebuehr,
        "operator": operator,
    }


def get_mahnstufen_trail(
    db: Session,
    rechnungsnr: str,
    tenant_id: str,
) -> List[Dict[str, Any]]:
    """Gibt vollständigen Mahnstufen-Trail chronologisch zurück."""
    rows = db.execute(
        text("""
            SELECT * FROM domain_finance.finance_mahnstufen_audit
            WHERE rechnungsnr = :rechnungsnr AND tenant_id = :tenant_id
            ORDER BY created_at ASC
        """),
        {"rechnungsnr": rechnungsnr, "tenant_id": tenant_id},
    ).mappings().all()
    return [dict(r) for r in rows]
