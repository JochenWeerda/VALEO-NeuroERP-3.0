"""Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — Lücke je Betrieb × Produktgruppe."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.bedarfsdeckung_service import BedarfsdeckungService

router = APIRouter(prefix="/crm/bedarfsdeckung", tags=["crm", "bedarfsdeckung"])


@router.get("/pipeline", response_model=list[dict], summary="Durchdringungs-Pipeline (alle Betriebe nach Chance)")
def pipeline(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return BedarfsdeckungService(db, tenant_id).pipeline(limit)


@router.get("/{kunden_nr}", response_model=dict, summary="Bedarfsdeckungs-Cockpit eines Betriebs")
def cockpit(
    kunden_nr: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    data = BedarfsdeckungService(db, tenant_id).cockpit(kunden_nr)
    if not data:
        raise HTTPException(status_code=404, detail="Kein Milchvieh-Profil für diesen Betrieb")
    return data
