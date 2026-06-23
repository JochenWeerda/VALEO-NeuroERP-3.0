"""Artefakt-Upload, Versionierung & Freigabe (DOM-DOC-004.2).

Pfade unter /docflow/evidence/artifacts (NICHT /docflow/{id} — der große docflow-
Router würde das sonst als id matchen).
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.docflow_artifact_service import ArtifactError, DocflowArtifactService

router = APIRouter(prefix="/docflow/evidence", tags=["docflow", "dms", "gobd"])


@router.get("/artifacts", response_model=dict[str, Any], summary="Artefakte eines Dokuments (Version + Freigabe)")
def list_artifacts(
    doc: str = Query(..., description="Dokumentnummer oder -ID"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return DocflowArtifactService(db, tenant_id).list_artifacts(doc)


class UploadIn(BaseModel):
    doc: str
    fileName: str
    content: str                         # Inhalt (Text/Base64) → SHA-256
    artifactType: Optional[str] = "pdf"
    storageKey: Optional[str] = None
    bediener: Optional[str] = None


@router.post("/artifacts", response_model=dict[str, Any], summary="Artefakt hochladen (neue Version, SHA-256)")
def upload_artifact(
    body: UploadIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocflowArtifactService(db, tenant_id).upload_artifact(
            doc=body.doc, file_name=body.fileName, content=body.content,
            artifact_type=body.artifactType or "pdf", storage_key=body.storageKey,
            bediener=body.bediener or "KIM",
        )
    except ArtifactError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class FreigabeIn(BaseModel):
    zielStatus: str                      # freigegeben | archiviert
    bediener: Optional[str] = None


@router.post("/artifacts/{artifact_id}/freigabe", response_model=dict[str, Any], summary="Freigabe-Status setzen (Transition)")
def set_freigabe(
    artifact_id: str,
    body: FreigabeIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return DocflowArtifactService(db, tenant_id).set_freigabe(artifact_id, body.zielStatus, body.bediener or "KIM")
    except ArtifactError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
