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


@router.get("/datev-journal", summary="INT-DATEV-001: Journal-Einträge als DATEV-CSV mit KOST1/KOST2")
def datev_journal_export(
    periode_von: str = Query(..., example="2026-01", description="Von-Periode YYYY-MM"),
    periode_bis: str = Query(..., example="2026-06", description="Bis-Periode YYYY-MM"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Exportiert gebuchte Journal-Einträge als DATEV-kompatibler Buchungsstapel.
    Enthält Konto, Betrag, Soll/Haben, Belegdatum, Belegfeld1, KOST1 (KST).
    """
    return FinanceDatevService(db, tenant_id).export_journal(periode_von, periode_bis)
