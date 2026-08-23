"""EXTERNAL-MOCK-HARNESS-001 — Dev-Only API fuer simulierte externe Systeme."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.schemas.external_mock_harness_schemas import (
    BankCamtImportOut,
    DatevExportStartOut,
    DatevExportStatusOut,
    DmsSearchOut,
    DmsUploadOut,
    DsfinvkExportOut,
    ElsterStatusOut,
    ElsterSubmitOut,
    SystemsOverviewOut,
    TseSignOut,
)
from app.services.external_mock_harness_service import external_mock_harness_service

router = APIRouter(prefix="/dev/external-mocks", tags=["dev", "mock"])


class DatevExportRequest(BaseModel):
    mandant_nr: str
    zeitraum_von: str
    zeitraum_bis: str


class TseSignRequest(BaseModel):
    kasse_id: str
    bon_nr: str
    betrag_ct: int


class DsfinvkExportRequest(BaseModel):
    kasse_id: str
    abschluss_datum: str


class ElsterSubmitRequest(BaseModel):
    steuer_nr: str
    formular_typ: str
    zeitraum: str
    daten: dict[str, Any] = Field(default_factory=dict)


class DmsUploadRequest(BaseModel):
    titel: str
    dokument_typ: str
    inhalt_base64: str = ""


class BankCamtRequest(BaseModel):
    iban: str
    kontoauszug_nr: int = 1


@router.get("/", summary="Verfuegbare Mock-Systeme auflisten", response_model=SystemsOverviewOut)
async def systems_overview() -> dict[str, Any]:
    return external_mock_harness_service.systems_overview()


@router.post("/datev/export", response_model=DatevExportStartOut, summary="DATEV-Export starten (simuliert)")
async def datev_export_start(req: DatevExportRequest) -> dict[str, Any]:
    return external_mock_harness_service.datev_export_start(
        mandant_nr=req.mandant_nr,
        zeitraum_von=req.zeitraum_von,
        zeitraum_bis=req.zeitraum_bis,
    )


@router.get("/datev/export/{job_id}", response_model=DatevExportStatusOut, summary="DATEV-Exportstatus (simuliert)")
async def datev_export_status(job_id: str) -> dict[str, Any]:
    return external_mock_harness_service.datev_export_status(job_id=job_id)


@router.post("/tse/sign", response_model=TseSignOut, summary="TSE-Signatur (simuliert)")
async def tse_sign(req: TseSignRequest) -> dict[str, Any]:
    return external_mock_harness_service.tse_sign_transaction(
        kasse_id=req.kasse_id,
        bon_nr=req.bon_nr,
        betrag_ct=req.betrag_ct,
    )


@router.post("/dsfinvk/export", response_model=DsfinvkExportOut, summary="DSFinV-K-Export (simuliert)")
async def dsfinvk_export(req: DsfinvkExportRequest) -> dict[str, Any]:
    return external_mock_harness_service.dsfinvk_export(
        kasse_id=req.kasse_id,
        abschluss_datum=req.abschluss_datum,
    )


@router.post("/elster/submit", response_model=ElsterSubmitOut, summary="ELSTER-Uebermittlung (simuliert)")
async def elster_submit(req: ElsterSubmitRequest) -> dict[str, Any]:
    return external_mock_harness_service.elster_submit(
        steuer_nr=req.steuer_nr,
        formular_typ=req.formular_typ,
        zeitraum=req.zeitraum,
        daten=req.daten,
    )


@router.get("/elster/status/{ticket_id}", response_model=ElsterStatusOut, summary="ELSTER-Status (simuliert)")
async def elster_status(ticket_id: str) -> dict[str, Any]:
    return external_mock_harness_service.elster_status(ticket_id=ticket_id)


@router.post("/dms/upload", response_model=DmsUploadOut, summary="DMS-Upload (simuliert)")
async def dms_upload(req: DmsUploadRequest) -> dict[str, Any]:
    return external_mock_harness_service.dms_upload(
        titel=req.titel,
        dokument_typ=req.dokument_typ,
        inhalt_base64=req.inhalt_base64,
    )


@router.get("/dms/search", response_model=DmsSearchOut, summary="DMS-Suche (simuliert)")
async def dms_search(q: str = "") -> dict[str, Any]:
    if not q:
        raise HTTPException(status_code=400, detail="Suchbegriff 'q' ist erforderlich")
    return external_mock_harness_service.dms_search(suchbegriff=q)


@router.post("/bank/camt-import", response_model=BankCamtImportOut, summary="CAMT-Import (simuliert)")
async def bank_camt_import(req: BankCamtRequest) -> dict[str, Any]:
    return external_mock_harness_service.bank_camt_import(
        iban=req.iban,
        kontoauszug_nr=req.kontoauszug_nr,
    )
