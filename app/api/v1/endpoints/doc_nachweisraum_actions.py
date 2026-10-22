"""DOM-DOC-004 — Nachweisraum: Dokument-Upload, Freigabe, Wiedervorlage, GoBD-Export."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.api.v1.schemas.docflow_bundle_schemas import (
    GobdExportOut,
    NachweisDokumentOut,
)
from app.core.database import get_db

router = APIRouter(prefix="/nachweisraum", tags=["nachweisraum"])
logger = logging.getLogger(__name__)


class DokumentCreateRequest(BaseModel):
    dokument_typ: str
    bezeichnung: str
    referenz_id: str
    referenz_typ: str
    datei_pfad: str
    operator: str = "system"


class DokumentTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    kommentar: str = ""
    wiedervorlage_datum: Optional[str] = None


class GoBDExportCreateRequest(BaseModel):
    periode: str
    referenz_ids: List[str]
    operator: str = "system"


class GoBDExportTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    export_pfad: Optional[str] = None
    fehler: Optional[str] = None


@router.post("/dokumente", response_model=NachweisDokumentOut, summary="Nachweisraum-Dokument anlegen")
def create_dokument(
    req: DokumentCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.doc_nachweisraum_lifecycle_service import (
        create_dokument as svc,
        NachweisraumError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            dokument_typ=req.dokument_typ,
            bezeichnung=req.bezeichnung,
            referenz_id=req.referenz_id,
            referenz_typ=req.referenz_typ,
            datei_pfad=req.datei_pfad,
            operator=req.operator,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/dokumente/{dokument_id}/transition",
    response_model=NachweisDokumentOut,
    summary="Nachweisraum-Dokumentstatus wechseln",
)
def transition_dokument(
    dokument_id: str,
    req: DokumentTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.doc_nachweisraum_lifecycle_service import (
        transition_dokument as svc,
        NachweisraumError,
    )
    try:
        return svc(
            db=db,
            dokument_id=dokument_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            kommentar=req.kommentar,
            wiedervorlage_datum=req.wiedervorlage_datum,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gobd-exporte", response_model=GobdExportOut, summary="GoBD-Export anlegen")
def create_gobd_export(
    req: GoBDExportCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.doc_nachweisraum_lifecycle_service import (
        create_gobd_export as svc,
        NachweisraumError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            periode=req.periode,
            referenz_ids=req.referenz_ids,
            operator=req.operator,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/gobd-exporte/{export_id}/transition",
    response_model=GobdExportOut,
    summary="GoBD-Exportstatus wechseln",
)
def transition_gobd_export(
    export_id: str,
    req: GoBDExportTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.doc_nachweisraum_lifecycle_service import (
        transition_gobd_export as svc,
        NachweisraumError,
    )
    try:
        return svc(
            db=db,
            export_id=export_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            export_pfad=req.export_pfad,
            fehler=req.fehler,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))
