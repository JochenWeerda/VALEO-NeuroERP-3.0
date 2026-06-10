"""Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004).

Bestellung ↔ Wareneingang (Basis; Rechnungs-Stufe folgt). Read-only: Mengen-/
Wertabweichung und Lücken je Bestellung sichtbar machen.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.procurement_match_service import ProcurementMatchService

router = APIRouter(prefix="/procurement", tags=["procurement", "einkauf"])


@router.get("/match/orders", summary="Bestellungen mit Match-Übersicht (Picker)")
def list_orders(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": ProcurementMatchService(db, tenant_id).list_orders(limit=limit)}


@router.get("/match", summary="3-Wege-Match je Bestellung (Bestellung ↔ Wareneingang)")
def match(
    bestellung: str = Query(..., description="Bestellnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return ProcurementMatchService(db, tenant_id).match(bestellung)
