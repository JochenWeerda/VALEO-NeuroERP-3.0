"""Dokument-Nachweisraum (DOM-DOC-004) — GoBD-Artefakt-/Vorgangs-Sicht (read-only)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_evidence_service import DocflowEvidenceService

router = APIRouter(prefix="/docflow", tags=["docflow", "dms", "gobd"])


@router.get("/evidence/documents", response_model=dict, summary="Dokumente mit Nachweis-Vollständigkeit (Picker)")
def list_documents(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return {"items": DocflowEvidenceService(db, tenant_id).list_documents(limit=limit)}


@router.get("/evidence/detail", response_model=dict, summary="Nachweiskette eines Dokuments (Artefakte/Kette/Buchungen/Lücken)")
def evidence(
    doc: str = Query(..., description="Dokumentnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowEvidenceService(db, tenant_id).evidence(doc)
