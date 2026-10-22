"""DOM-DOC-004 — Nachweisraum: Dokument-Upload, Freigabe, Wiedervorlage, GoBD-Export."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

from app.api.v1.schemas.docflow_bundle_schemas import (
    GobdExportOut,
    NachweisDokumentOut,
)
from app.core.database import get_db
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)
from app.core.akteur import gepruefter_akteur_aus_request  # Bearbeiter aus dem Token

router = APIRouter(prefix="/nachweisraum", tags=["nachweisraum"])
logger = logging.getLogger(__name__)


class DokumentCreateRequest(BaseModel):
    dokument_typ: str
    bezeichnung: str
    referenz_id: str
    referenz_typ: str
    datei_pfad: str


class DokumentTransitionRequest(BaseModel):
    new_status: str
    kommentar: str = ""
    wiedervorlage_datum: Optional[str] = None


class GoBDExportCreateRequest(BaseModel):
    periode: str
    referenz_ids: List[str]


class GoBDExportTransitionRequest(BaseModel):
    new_status: str
    export_pfad: Optional[str] = None
    fehler: Optional[str] = None


@router.post("/dokumente", response_model=NachweisDokumentOut, summary="Nachweisraum-Dokument anlegen", dependencies=SCHREIBEN["QUALITAET"])
def create_dokument(
    req: DokumentCreateRequest,
    request: Request,
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
            operator=gepruefter_akteur_aus_request(request),
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/dokumente/{dokument_id}/transition",
    response_model=NachweisDokumentOut,
    summary="Nachweisraum-Dokumentstatus wechseln", dependencies=SCHREIBEN["QUALITAET"])
def transition_dokument(
    dokument_id: str,
    req: DokumentTransitionRequest,
    request: Request,
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
            operator=gepruefter_akteur_aus_request(request),
            kommentar=req.kommentar,
            wiedervorlage_datum=req.wiedervorlage_datum,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gobd-exporte", response_model=GobdExportOut, summary="GoBD-Export anlegen", dependencies=SCHREIBEN["QUALITAET"])
def create_gobd_export(
    req: GoBDExportCreateRequest,
    request: Request,
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
            operator=gepruefter_akteur_aus_request(request),
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/gobd-exporte/{export_id}/transition",
    response_model=GobdExportOut,
    summary="GoBD-Exportstatus wechseln", dependencies=SCHREIBEN["QUALITAET"])
def transition_gobd_export(
    export_id: str,
    req: GoBDExportTransitionRequest,
    request: Request,
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
            operator=gepruefter_akteur_aus_request(request),
            export_pfad=req.export_pfad,
            fehler=req.fehler,
        )
    except NachweisraumError as e:
        raise HTTPException(status_code=400, detail=str(e))
