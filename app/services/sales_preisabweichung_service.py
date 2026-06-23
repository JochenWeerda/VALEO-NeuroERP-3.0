"""DOM-SALES-004.4 — Preisabweichungs-Prüfung + Eskalation/Freigabe Service."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

DEFAULT_SCHWELLE_PCT = 2.0


class PreisabweichungError(Exception):
    """Raised when Preisabweichung constraints are violated."""


def pruefe_preisabweichung(
    db: Session,
    auftrag_id: str,
    tenant_id: str,
    artikel_id: str,
    angebots_preis: float,
    rechnungs_preis: float,
    schwelle_pct: float = DEFAULT_SCHWELLE_PCT,
) -> Dict[str, Any]:
    """Prüft Preisabweichung zwischen Angebot und Rechnung, idempotent via (auftrag_id, artikel_id)."""
    if angebots_preis <= 0:
        raise PreisabweichungError("Angebotspreis muss positiv sein")

    # idempotency check
    existing = db.execute(
        text("""
            SELECT * FROM domain_sales.sales_preisabweichungen
            WHERE auftrag_id = :auftrag_id AND artikel_id = :artikel_id AND tenant_id = :tenant_id
        """),
        {"auftrag_id": auftrag_id, "artikel_id": artikel_id, "tenant_id": tenant_id},
    ).mappings().first()
    if existing:
        return {**dict(existing), "idempotent": True}

    abweichung_abs = abs(angebots_preis - rechnungs_preis)
    abweichung_pct = round(abweichung_abs / angebots_preis * 100, 4)

    status = "AUTO_FREIGEGEBEN" if abweichung_pct <= schwelle_pct else "ESKALIERT"

    entry_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_sales.sales_preisabweichungen
                (id, auftrag_id, tenant_id, artikel_id, angebots_preis, rechnungs_preis,
                 abweichung_pct, status, created_at)
            VALUES (:id, :auftrag_id, :tenant_id, :artikel_id, :angebots_preis, :rechnungs_preis,
                    :abweichung_pct, :status, NOW())
        """),
        {
            "id": entry_id, "auftrag_id": auftrag_id, "tenant_id": tenant_id,
            "artikel_id": artikel_id, "angebots_preis": angebots_preis,
            "rechnungs_preis": rechnungs_preis, "abweichung_pct": abweichung_pct,
            "status": status,
        },
    )
    db.commit()
    logger.info("preisabweichung %s/%s: %.4f%% → %s", auftrag_id, artikel_id, abweichung_pct, status)
    return {
        "id": entry_id, "auftrag_id": auftrag_id, "artikel_id": artikel_id,
        "angebots_preis": angebots_preis, "rechnungs_preis": rechnungs_preis,
        "abweichung_pct": abweichung_pct, "status": status, "idempotent": False,
    }


def freigabe_preisabweichung(
    db: Session,
    abweichung_id: str,
    tenant_id: str,
    entscheidung: str,
    operator: str,
    grund: Optional[str] = None,
) -> Dict[str, Any]:
    """Gibt eine eskalierte Preisabweichung frei oder lehnt sie ab (fail-closed nur für ESKALIERT)."""
    if entscheidung.upper() not in {"FREIGEGEBEN", "ABGELEHNT"}:
        raise PreisabweichungError(f"Ungültige Entscheidung: {entscheidung}. Erlaubt: FREIGEGEBEN, ABGELEHNT")

    row = db.execute(
        text("SELECT * FROM domain_sales.sales_preisabweichungen WHERE id = :id"),
        {"id": abweichung_id},
    ).mappings().first()
    if not row:
        raise PreisabweichungError(f"Preisabweichung {abweichung_id} nicht gefunden")
    if row["tenant_id"] != tenant_id:
        raise PreisabweichungError(f"Preisabweichung {abweichung_id} gehört nicht zu Tenant {tenant_id}")
    if row["status"] != "ESKALIERT":
        raise PreisabweichungError(
            f"Freigabe nur für ESKALIERT möglich (aktuell: {row['status']})"
        )

    db.execute(
        text("""
            UPDATE domain_sales.sales_preisabweichungen
            SET status = :status, freigabe_operator = :operator, freigabe_grund = :grund
            WHERE id = :id
        """),
        {"status": entscheidung.upper(), "operator": operator, "grund": grund, "id": abweichung_id},
    )
    db.commit()
    logger.info("preisabweichung %s: ESKALIERT → %s von %s", abweichung_id, entscheidung, operator)
    return {**dict(row), "status": entscheidung.upper(), "freigabe_operator": operator, "freigabe_grund": grund}
