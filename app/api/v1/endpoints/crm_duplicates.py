"""Kunden-Dubletten (DOM-CRM-004) — Erkennung wahrscheinlicher Doppelanlagen.

Read-only: gruppiert Kunden über E-Mail/Telefon/Name+PLZ zu Dubletten-Clustern.
Basis für die Zusammenführung (Folge-Slice).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.crm_duplicate_service import CrmDuplicateService
from app.services.crm_merge_service import CrmMergeService, MergeError

router = APIRouter(prefix="/crm", tags=["crm", "dubletten"])


@router.get("/duplicates", summary="Kunden-Dubletten-Cluster erkennen")
def duplicates(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return CrmDuplicateService(db, tenant_id).find_duplicates(limit_groups=limit)


class MergeIn(BaseModel):
    masterNr: str
    duplicateNr: str
    bediener: str | None = None


@router.post("/duplicates/merge-preview", summary="Zusammenführung vorschauen (read-only)")
def merge_preview(
    body: MergeIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return CrmMergeService(db, tenant_id).preview(body.masterNr, body.duplicateNr)
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/duplicates/merge", summary="Dublette in Master zusammenführen")
def merge(
    body: MergeIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return CrmMergeService(db, tenant_id).merge(body.masterNr, body.duplicateNr, body.bediener or "KIM")
    except MergeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
