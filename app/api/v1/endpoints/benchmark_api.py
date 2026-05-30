from __future__ import annotations

from datetime import date
from typing import Optional

import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.betriebskennzahlen import BenchmarkReport, KennzahlEinheit, DEFAULT_KZ_KATALOG
from app.core.database import get_db
from app.core.endpoint_gateways import (
    get_projection_status_loader,
    get_runtime_report_loader,
    get_telemetry_device_store,
    get_telemetry_reading_store,
)
from app.core.process_mining_application import build_process_mining_benchmark_report
from app.domains.operations.models import BetriebsKennzahlDB

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.benchmark_api_schemas import BenchmarkApiOut


router = APIRouter(prefix="/benchmark", tags=["benchmark"])


class KennzahlSubmitRequest(BaseModel):
    tenant_id: str
    kz_name: str
    einheit: str
    wert: float
    periode: str


@router.post("/kennzahlen", status_code=201, summary="Kennzahl einreichen",
    response_model=BenchmarkApiOut
)
def submit_kennzahl(req: KennzahlSubmitRequest, db: Session = Depends(get_db)):
    kz_id = str(uuid.uuid4())
    row = BetriebsKennzahlDB(
        kz_id=kz_id,
        tenant_id=req.tenant_id,
        kz_name=req.kz_name,
        einheit=KennzahlEinheit(req.einheit).value,
        wert=req.wert,
        periode=req.periode,
        berechnet_am=date.today(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "kz_id": row.kz_id,
        "tenant_id": row.tenant_id,
        "kz_name": row.kz_name,
        "einheit": row.einheit,
        "wert": float(row.wert),
        "periode": row.periode,
        "berechnet_am": row.berechnet_am.isoformat() if row.berechnet_am else None,
    }


@router.get("/report/{verbund_id}", summary="Benchmark report abrufen",
    response_model=BenchmarkApiOut
)
def get_benchmark_report(verbund_id: str, periode: str = Query(...), db: Session = Depends(get_db)):
    rows = db.query(BetriebsKennzahlDB).filter(BetriebsKennzahlDB.periode == periode).all()
    from app.core.betriebskennzahlen import BetriebsKennzahl
    kennzahlen_je_tenant: dict[str, list] = {}
    for r in rows:
        kz = BetriebsKennzahl(
            kz_id=r.kz_id,
            kz_name=r.kz_name,
            einheit=KennzahlEinheit(r.einheit),
            wert=float(r.wert),
            tenant_id=r.tenant_id,
            periode=r.periode,
            berechnet_am=r.berechnet_am,
        )
        kennzahlen_je_tenant.setdefault(r.tenant_id, []).append(kz)
    report = BenchmarkReport.build(
        verbund_id=verbund_id,
        periode=periode,
        kennzahlen_je_tenant=kennzahlen_je_tenant,
    )
    return report


@router.get("/process-mining/{verbund_id}", summary="Process mining benchmark report abrufen",
    response_model=BenchmarkApiOut
)
def get_process_mining_benchmark_report(
    verbund_id: str,
    periode: str = Query(...),
    tenant_ids: list[str] = Query(...),
):
    projection_status_loader = get_projection_status_loader()
    runtime_report_loader = get_runtime_report_loader()
    if projection_status_loader is None or runtime_report_loader is None:
        return BenchmarkReport.build(verbund_id=verbund_id, periode=periode, kennzahlen_je_tenant={}).model_dump()
    result = build_process_mining_benchmark_report(
        verbund_id=verbund_id,
        periode=periode,
        tenant_ids=tenant_ids,
        projection_status_loader=projection_status_loader,
        runtime_report_loader=runtime_report_loader,
        device_store=get_telemetry_device_store(),
        reading_store=get_telemetry_reading_store(),
    )
    return result.model_dump()


@router.get("/katalog", summary="Kz katalog abrufen",
    response_model=BenchmarkApiOut
)
def get_kz_katalog():
    return {"katalog": DEFAULT_KZ_KATALOG, "count": len(DEFAULT_KZ_KATALOG), "schema_version": 1}
