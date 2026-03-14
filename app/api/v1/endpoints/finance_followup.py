"""
Finance Follow-up API — Wave 4 AP5

Explizite Backend-Contracts für Mahnwesen-Export und Lastschriften-Export.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id
from ....core.finance_followup import (
    MahnwesenPreview,
    MahnwesenExportRequest,
    MahnwesenExportResult,
    MahnwesenExportFormat,
    LastschriftPreview,
    LastschriftExportResult,
)

router = APIRouter(prefix="/finance/followup", tags=["finance", "followup"])


# ---------------------------------------------------------------------------
# Mahnwesen
# ---------------------------------------------------------------------------

@router.get("/mahnwesen/preview", response_model=dict)
async def get_mahnwesen_preview(
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert eine Vorschau des aktuellen Mahnwesen-Stands."""
    # In-memory / stub: in Produktion DB-Query
    preview = MahnwesenPreview(
        tenant_id=tenant_id,
        open_items_count=0,
        total_overdue_amount=0.0,
        dunning_level_counts={"1": 0, "2": 0, "3": 0},
        export_ready=True,
    )
    return preview.model_dump(mode="json")


@router.post("/mahnwesen/export", response_model=dict, status_code=202)
async def export_mahnwesen(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Startet den Mahnwesen-Export und gibt das Export-Ergebnis zurück (202 Accepted)."""
    fmt = body.get("format", MahnwesenExportFormat.PDF)
    dunning_level_filter = body.get("dunning_level_filter")
    requested_by = body.get("requested_by", "system")

    result = MahnwesenExportResult(
        export_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        format=MahnwesenExportFormat(fmt) if isinstance(fmt, str) else fmt,
        record_count=0,
        download_url=None,
    )
    return result.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Lastschriften
# ---------------------------------------------------------------------------

@router.get("/lastschriften/{run_id}/preview", response_model=dict)
async def get_lastschrift_preview(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert eine Vorschau eines Lastschriften-Runs."""
    preview = LastschriftPreview(
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        total_amount=0.0,
        debitor_count=0,
        mandate_valid_count=0,
        mandate_expired_count=0,
        sepa_ready=True,
    )
    return preview.model_dump(mode="json")


@router.post("/lastschriften/{run_id}/export", response_model=dict, status_code=202)
async def export_lastschriften(
    run_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Startet den SEPA-Export eines Lastschriften-Runs (202 Accepted)."""
    result = LastschriftExportResult(
        export_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        record_count=0,
        download_url=None,
    )
    return result.model_dump(mode="json")
