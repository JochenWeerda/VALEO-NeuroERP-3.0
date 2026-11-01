"""Klaerliste der Partnerzuordnung (ADR Geschaeftspartnerstamm, Stufe 2).

Die Rueckfuellung ``partner_rueckfuellung_20261101`` ordnet Kunden und Lieferanten nur zu, wenn die
Regel eindeutig ist; Zweifelsfaelle liegen in ``domain_crm.partner_klaerfaelle``. Dieser Weg liest sie
mandantengenau, damit die Studio-Liste ``crm/partner-klaerfaelle-liste`` sie zeigen kann. Entschieden
werden sie mit Stufe 3.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/crm/partner-klaerfaelle", tags=["crm", "partner"])


class PartnerKlaerfallOut(BaseModel):
    id: str
    quelle: str
    satz_id: str
    nummer: Optional[str] = None
    name: Optional[str] = None
    grund: str
    kandidaten: list[str] = []
    erstellt_am: Optional[str] = None
    erledigt_am: Optional[str] = None


@router.get("", response_model=list[PartnerKlaerfallOut], summary="Klaerfaelle der Partnerzuordnung auflisten")
def list_partner_klaerfaelle(
    erledigt: bool = Query(False, description="Auch erledigte Klaerfaelle zeigen"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT k.id, k.quelle, k.satz_id, k.grund, k.kandidaten, k.erstellt_am, k.erledigt_am,
                   COALESCE(c.customer_number, l.lieferantennummer) AS nummer,
                   COALESCE(c.company_name, l.firmenname) AS name
            FROM domain_crm.partner_klaerfaelle k
            LEFT JOIN domain_crm.customers c
                   ON k.quelle = 'kunde' AND c.id = k.satz_id AND c.tenant_id = k.tenant_id
            LEFT JOIN domain_einkauf.lieferanten l
                   ON k.quelle = 'lieferant' AND l.id::text = k.satz_id AND l.tenant_id = k.tenant_id
            WHERE k.tenant_id = :tid AND (:erledigt OR k.erledigt_am IS NULL)
            ORDER BY k.erstellt_am, k.id
            LIMIT :limit
        """),
        {"tid": tenant_id, "erledigt": erledigt, "limit": limit},
    ).mappings().fetchmany(limit)
    return [
        {**dict(r), "kandidaten": list(r["kandidaten"] or []),
         "erstellt_am": r["erstellt_am"].isoformat() if r["erstellt_am"] else None,
         "erledigt_am": r["erledigt_am"].isoformat() if r["erledigt_am"] else None}
        for r in rows
    ]
