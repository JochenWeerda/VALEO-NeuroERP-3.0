"""GoBD-Exportpaket & DMS-/Paperless-Liveprobe (DOM-DOC-004.4)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_gobd_service import DocflowGobdService

router = APIRouter(prefix="/docflow/evidence", tags=["docflow", "dms", "gobd"])


@router.get("/paperless-probe", response_model=dict, summary="DMS-/Paperless-Liveprobe (ehrlich gegated)")
def paperless_probe(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowGobdService(db, tenant_id).paperless_probe()


class GobdExportIn(BaseModel):
    doc: str
    bediener: Optional[str] = None


@router.post("/gobd-export", response_model=dict, summary="GoBD-Exportpaket je Vorgang erzeugen (+ Export vermerken)")
def gobd_export(
    body: GobdExportIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowGobdService(db, tenant_id).export_package(body.doc, bediener=body.bediener or "KIM")
