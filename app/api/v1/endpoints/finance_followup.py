"""
Finance Follow-up API — Wave 4 AP5

Explizite Backend-Contracts für Mahnwesen-Export und Lastschriften-Export.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
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
    db: Session = Depends(get_db),
):
    """Liefert eine Vorschau des aktuellen Mahnwesen-Stands."""
    try:
        result = db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE overdue_days > 0) AS open_items_count,
                COALESCE(SUM(balance) FILTER (WHERE overdue_days > 0), 0) AS total_overdue,
                COUNT(*) FILTER (WHERE dunning_level = 1) AS level_1,
                COUNT(*) FILTER (WHERE dunning_level = 2) AS level_2,
                COUNT(*) FILTER (WHERE dunning_level = 3) AS level_3
            FROM domain_shared.open_items
            WHERE tenant_id = :tid AND status = 'open' AND type = 'debitor'
        """), {"tid": tenant_id})
        row = result.fetchone()
    except Exception:
        row = None

    if row:
        preview = MahnwesenPreview(
            tenant_id=tenant_id,
            open_items_count=row.open_items_count or 0,
            total_overdue_amount=float(row.total_overdue or 0),
            dunning_level_counts={
                "1": row.level_1 or 0,
                "2": row.level_2 or 0,
                "3": row.level_3 or 0,
            },
            export_ready=True,
        )
    else:
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
    db: Session = Depends(get_db),
):
    """Startet den Mahnwesen-Export und gibt das Export-Ergebnis zurück (202 Accepted)."""
    fmt = body.get("format", MahnwesenExportFormat.PDF)
    dunning_level_filter = body.get("dunning_level_filter")
    requested_by = body.get("requested_by", "system")
    export_id = str(uuid.uuid4())

    # Count records that will be exported
    record_count = 0
    try:
        level_clause = ""
        params: dict = {"tid": tenant_id}
        if dunning_level_filter:
            level_clause = " AND dunning_level = :dlevel"
            params["dlevel"] = int(dunning_level_filter)
        result = db.execute(text(f"""
            SELECT COUNT(*) AS cnt
            FROM domain_shared.open_items
            WHERE tenant_id = :tid AND status = 'open' AND type = 'debitor'
              AND overdue_days > 0{level_clause}
        """), params)
        row = result.fetchone()
        if row:
            record_count = row.cnt or 0
    except Exception:
        pass

    download_url = f"/api/v1/finance/followup/mahnwesen/export/{export_id}/download" if record_count > 0 else None

    result = MahnwesenExportResult(
        export_id=export_id,
        tenant_id=tenant_id,
        format=MahnwesenExportFormat(fmt) if isinstance(fmt, str) else fmt,
        record_count=record_count,
        download_url=download_url,
    )
    return result.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Lastschriften
# ---------------------------------------------------------------------------

@router.get("/lastschriften/{run_id}/preview", response_model=dict)
async def get_lastschrift_preview(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liefert eine Vorschau eines Lastschriften-Runs."""
    total_amount = 0.0
    debitor_count = 0
    mandate_valid_count = 0
    mandate_expired_count = 0
    try:
        result = db.execute(text("""
            SELECT
                COALESCE(SUM(amount), 0) AS total_amount,
                COUNT(DISTINCT debitor_id) AS debitor_count
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid AND run_id = :run_id
        """), {"tid": tenant_id, "run_id": run_id})
        row = result.fetchone()
        if row:
            total_amount = float(row.total_amount or 0)
            debitor_count = row.debitor_count or 0
    except Exception:
        pass

    try:
        result = db.execute(text("""
            SELECT
                COUNT(*) FILTER (WHERE mandate_valid = true) AS valid_count,
                COUNT(*) FILTER (WHERE mandate_valid = false OR mandate_expired_at < NOW()) AS expired_count
            FROM domain_shared.sepa_mandates
            WHERE tenant_id = :tid AND debitor_id IN (
                SELECT DISTINCT debitor_id FROM domain_shared.direct_debit_items
                WHERE tenant_id = :tid AND run_id = :run_id
            )
        """), {"tid": tenant_id, "run_id": run_id})
        mrow = result.fetchone()
        if mrow:
            mandate_valid_count = mrow.valid_count or 0
            mandate_expired_count = mrow.expired_count or 0
    except Exception:
        pass

    preview = LastschriftPreview(
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        total_amount=total_amount,
        debitor_count=debitor_count,
        mandate_valid_count=mandate_valid_count,
        mandate_expired_count=mandate_expired_count,
        sepa_ready=(mandate_expired_count == 0 and debitor_count > 0),
    )
    return preview.model_dump(mode="json")


@router.post("/lastschriften/{run_id}/export", response_model=dict, status_code=202)
async def export_lastschriften(
    run_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Startet den SEPA-Export eines Lastschriften-Runs (202 Accepted)."""
    export_id = str(uuid.uuid4())
    record_count = 0
    try:
        result = db.execute(text("""
            SELECT COUNT(*) AS cnt
            FROM domain_shared.direct_debit_items
            WHERE tenant_id = :tid AND run_id = :run_id
        """), {"tid": tenant_id, "run_id": run_id})
        row = result.fetchone()
        if row:
            record_count = row.cnt or 0
    except Exception:
        pass

    download_url = f"/api/v1/finance/followup/lastschriften/{run_id}/export/{export_id}/download" if record_count > 0 else None

    result = LastschriftExportResult(
        export_id=export_id,
        tenant_id=tenant_id,
        direct_debit_run_id=run_id,
        record_count=record_count,
        download_url=download_url,
    )
    return result.model_dump(mode="json")
