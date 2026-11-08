"""Tenant-scoped projection for the complaint list."""
from __future__ import annotations

import json
from typing import Any, Callable

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.services.customer_reference import resolve_reference

_STATUS = {
    "offen": "neu",
    "in_pruefung": "in-bearbeitung",
    "teilweise_anerkannt": "in-bearbeitung",
    "anerkannt": "in-bearbeitung",
    "geschlossen": "geloest",
    "abgelehnt": "abgelehnt",
}


def read_complaint_list(db: Session, tenant_id: str, *, iso: Callable[[Any], Any]) -> list[dict[str, Any]]:
    """Return at most 200 latest complaints; unavailable priority is represented by None."""
    try:
        rows = db.execute(
            text("SELECT * FROM domain_ops.reklamationen WHERE tenant_id = :t ORDER BY erstellt_am DESC LIMIT 200"),
            {"t": tenant_id},
        ).mappings().all()
        suppliers: dict[str, str] = {}
        result = []
        for row in rows:
            supplier_ref = str(row.get("lieferant_id") or "")
            if supplier_ref not in suppliers:
                supplier = resolve_reference(db, tenant_id, "supplier", supplier_ref)
                suppliers[supplier_ref] = supplier.name or supplier.number or ""
            positions = row.get("positionen") or []
            if isinstance(positions, str):
                try:
                    positions = json.loads(positions)
                except json.JSONDecodeError:
                    positions = []
            first = positions[0] if isinstance(positions, list) and positions and isinstance(positions[0], dict) else {}
            status = str(row.get("status") or "unbekannt")
            result.append({
                "id": row.get("reklamation_id") or row.get("id"),
                "nummer": row.get("reklamation_nr") or "",
                "kunde": suppliers[supplier_ref],
                "artikel": first.get("artikel") or first.get("bezeichnung") or row.get("typ") or "",
                "grund": row.get("typ") or "",
                "datum": iso(row.get("erstellt_am") or row.get("frist_datum")) or "",
                "prioritaet": None,
                "status": _STATUS.get(status, status),
            })
        return result
    except (ProgrammingError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Reklamationsliste voruebergehend nicht verfuegbar") from exc
