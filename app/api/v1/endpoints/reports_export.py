"""
Reports Export — generischer Berichts-Download-Endpunkt

GET /reports/export/{report_type}?format=xlsx|csv|pdf&start_date=...&end_date=...
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Path, Query
from fastapi.responses import JSONResponse

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/reports", tags=["reports", "export"])


@router.get("/export/{report_type}", summary="Bericht exportieren")
async def export_report(
    report_type: str = Path(..., description="Berichtstyp, z.B. umsatz, lagerbestand, deckungsbeitrag"),
    format: str = Query("xlsx", description="Ausgabeformat: xlsx, csv, pdf"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
) -> JSONResponse:
    """Stub: Export-Endpunkt für Berichte. Gibt leere Erfolgsmeldung zurück."""
    return JSONResponse(
        content={
            "report_type": report_type,
            "format": format,
            "start_date": start_date,
            "end_date": end_date,
            "rows": 0,
            "message": "Export-Funktion wird implementiert.",
        }
    )
