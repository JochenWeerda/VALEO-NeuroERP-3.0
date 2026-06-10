"""Supply-Chain-Traceability (DOM-SUPPLY-004).

Durchgängige, prüfbare Kette Wiegung → Annahme → Lager → Abrechnung je Lieferung
(Rückgrat: weighing_ticket). Read-only; macht Rückverfolgbarkeit, Mengen-Konsistenz
(Schwund) und Lücken (fehlende Folgeobjekte) sichtbar.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.supply_chain_trace_service import SupplyChainTraceService

router = APIRouter(prefix="/supply-chain", tags=["supply-chain", "agrar", "lager"])


@router.get("/traceability/tickets", summary="Wiegescheine mit Ketten-Vollständigkeit (Übersicht/Picker)")
def list_tickets(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": SupplyChainTraceService(db, tenant_id).list_tickets(limit=limit)}


@router.get("/traceability", summary="Durchgängige Kette je Lieferung (Rückverfolgbarkeit)")
def traceability(
    ticket: Optional[str] = Query(None, description="Wiegeschein-Nr oder -ID"),
    acceptance: Optional[str] = Query(None, description="Annahme-Nr oder -ID"),
    lot: Optional[str] = Query(None, description="Silo-Lot-Nr oder -ID"),
    settlement: Optional[str] = Query(None, description="Abrechnungs-Nr oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return SupplyChainTraceService(db, tenant_id).trace(
        ticket=ticket, acceptance=acceptance, lot=lot, settlement=settlement
    )
