"""CRM-Kundenkarte — alle Kunden als GeoJSON (Karte + Hover-Kennzahlen)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.crm_kunden_map_service import CrmKundenMapService

router = APIRouter(prefix="/crm/kunden-karte", tags=["crm", "map"])


@router.get("/map", response_model=dict, summary="Alle Kunden als GeoJSON (CRM-Kundenkarte)")
def kunden_map(
    typ: Optional[str] = Query(None, description="gap | milchvieh | lead | stamm"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return CrmKundenMapService(db).map_features(typ=typ)
