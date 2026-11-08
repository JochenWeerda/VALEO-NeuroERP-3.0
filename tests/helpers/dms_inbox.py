"""Seed-Helper fuer domain_shared.dms_inbox — gleiches SQL/Schema wie Router-Tests.

Keine neuen Spalten. Tenant muss der laufenden Queue-Session entsprechen
(X-Tenant / ersetze_mandant), sonst filtert die Inbox-API die Zeile weg.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text


def has_tenant_column(db: Any) -> bool:
    return (
        db.execute(
            text(
                """
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'domain_shared'
                  AND table_name = 'dms_inbox'
                  AND column_name = 'tenant_id'
                """
            )
        ).scalar()
        is not None
    )


def insert_inbox(
    db: Any,
    *,
    item_id: str,
    tenant_id: str,
    number: str,
    ocr: str | None = None,
    parsed_fields: dict[str, Any] | None = None,
    confidence: float = 0.8,
) -> None:
    """Eine pending-Zeile in domain_shared.dms_inbox anlegen (bestehende Spalten)."""
    cols = "id, dms_document_id, dms_url, ocr_text, parsed_fields, confidence, status"
    vals = ":id, 91001, 'http://localhost/doc/91001', :ocr, CAST(:parsed AS jsonb), :confidence, 'pending'"
    parsed = parsed_fields or {
        "invoice_number": number,
        "supplier": "Nordkorn AG",
        "supplier_id": "L-22",
    }
    params = {
        "id": item_id,
        "ocr": ocr if ocr is not None else f"Rechnung {number} Lieferant Nordkorn",
        "parsed": json.dumps(parsed),
        "confidence": confidence,
    }
    if has_tenant_column(db):
        cols += ", tenant_id"
        vals += ", :tenant_id"
        params["tenant_id"] = tenant_id
    db.execute(
        text(f"INSERT INTO domain_shared.dms_inbox ({cols}) VALUES ({vals})"),
        params,
    )
