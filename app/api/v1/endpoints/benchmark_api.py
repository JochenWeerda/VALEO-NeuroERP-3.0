from __future__ import annotations
from datetime import date
from fastapi import APIRouter, Query
from pydantic import BaseModel
import uuid
from app.core.betriebskennzahlen import BetriebsKennzahl, BenchmarkReport, KennzahlEinheit, DEFAULT_KZ_KATALOG
from app.core.endpoint_gateways import (
    get_projection_status_loader,
    get_runtime_report_loader,
    get_telemetry_device_store,
    get_telemetry_reading_store,
)
from app.core.process_mining_application import build_process_mining_benchmark_report

router = APIRouter(prefix="/benchmark", tags=["benchmark"])

_kennzahlen_store: dict[str, list[BetriebsKennzahl]] = {}   # tenant_id → list

class KennzahlSubmitRequest(BaseModel):
    tenant_id: str
    kz_name: str
    einheit: str
    wert: float
    periode: str

@router.post("/kennzahlen", status_code=201)
def submit_kennzahl(req: KennzahlSubmitRequest):
    kz = BetriebsKennzahl(
        kz_id=str(uuid.uuid4()),
        kz_name=req.kz_name,
        einheit=KennzahlEinheit(req.einheit),
        wert=req.wert,
        tenant_id=req.tenant_id,
        periode=req.periode,
        berechnet_am=date.today(),
    )
    if req.tenant_id not in _kennzahlen_store:
        _kennzahlen_store[req.tenant_id] = []
    _kennzahlen_store[req.tenant_id].append(kz)
    return kz

@router.get("/report/{verbund_id}")
def get_benchmark_report(verbund_id: str, periode: str = Query(...)):
    report = BenchmarkReport.build(
        verbund_id=verbund_id,
        periode=periode,
        kennzahlen_je_tenant=_kennzahlen_store,
    )
    return report


@router.get("/process-mining/{verbund_id}")
def get_process_mining_benchmark_report(
    verbund_id: str,
    periode: str = Query(...),
    tenant_ids: list[str] = Query(...),
):
    projection_status_loader = get_projection_status_loader()
    runtime_report_loader = get_runtime_report_loader()
    if projection_status_loader is None or runtime_report_loader is None:
        return BenchmarkReport.build(verbund_id=verbund_id, periode=periode, kennzahlen_je_tenant={})
    return build_process_mining_benchmark_report(
        verbund_id=verbund_id,
        periode=periode,
        tenant_ids=tenant_ids,
        projection_status_loader=projection_status_loader,
        runtime_report_loader=runtime_report_loader,
        device_store=get_telemetry_device_store(),
        reading_store=get_telemetry_reading_store(),
    )

@router.get("/katalog")
def get_kz_katalog():
    return {"katalog": DEFAULT_KZ_KATALOG, "count": len(DEFAULT_KZ_KATALOG), "schema_version": 1}
