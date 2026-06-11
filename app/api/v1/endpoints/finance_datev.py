"""DATEV-Export (DOM-FIN-004.5)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.finance_datev_service import FinanceDatevService

router = APIRouter(prefix="/finance", tags=["finance", "fibu", "datev"])


@router.get("/datev-export", summary="Offene Posten als DATEV-Buchungsstapel-CSV (vereinfacht)")
def datev_export(
    typ: str = Query("alle", description="debitor | kreditor | alle"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return FinanceDatevService(db, tenant_id).export_open_items(typ=typ)
