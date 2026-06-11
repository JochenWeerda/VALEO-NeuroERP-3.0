"""Bescheid/Rückmeldung & Wiedervorlage am Vorgang (DOM-DOC-004.3)."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_followup_service import DocflowFollowupService, FollowupError

router = APIRouter(prefix="/docflow/evidence", tags=["docflow", "dms", "gobd"])


@router.get("/wiedervorlagen", summary="Offene Wiedervorlagen (Worklist, überfällig markiert)")
def wiedervorlagen(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": DocflowFollowupService(db, tenant_id).open_wiedervorlagen(limit=limit)}


@router.get("/followups", summary="Bescheide/Rückmeldungen/Wiedervorlagen eines Vorgangs")
def list_followups(
    doc: str = Query(..., description="Dokumentnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowFollowupService(db, tenant_id).list_followups(doc)


class FollowupIn(BaseModel):
    doc: str
    art: str = "wiedervorlage"           # bescheid | rueckmeldung | wiedervorlage
    betreff: str
    text: Optional[str] = None
    faelligAm: Optional[str] = None      # ISO; Pflicht bei wiedervorlage
    bediener: Optional[str] = None


@router.post("/followups", summary="Bescheid/Rückmeldung/Wiedervorlage erfassen")
def create_followup(
    body: FollowupIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    fa: Optional[date] = None
    if body.faelligAm:
        try:
            fa = date.fromisoformat(body.faelligAm[:10])
        except ValueError:
            raise HTTPException(status_code=422, detail="Ungültiges Datum (erwartet ISO YYYY-MM-DD).")
    try:
        return DocflowFollowupService(db, tenant_id).create_followup(
            doc=body.doc, art=body.art, betreff=body.betreff, text_body=body.text,
            faellig_am=fa, bediener=body.bediener or "KIM",
        )
    except FollowupError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class CompleteIn(BaseModel):
    bediener: Optional[str] = None


@router.post("/followups/{followup_id}/complete", summary="Followup erledigen")
def complete_followup(
    followup_id: str,
    body: CompleteIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocflowFollowupService(db, tenant_id).complete_followup(followup_id, body.bediener or "KIM")
    except FollowupError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
