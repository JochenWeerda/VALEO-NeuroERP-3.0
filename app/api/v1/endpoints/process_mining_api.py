from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.endpoint_gateways import (
    get_projection_status_loader,
    get_runtime_report_loader,
    get_telemetry_device_store,
    get_telemetry_reading_store,
)
from app.core.process_mining import (
    ProcessMiningDrilldown,
    ProcessMiningProcessSummary,
    ProcessMiningReport,
    build_process_mining_drilldown,
    build_process_mining_top_processes,
)
from app.core.process_mining_application import build_process_mining_report_for_tenant
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/process-mining", tags=["process-mining", "analytics"])


@router.get("/finance/report", response_model=ProcessMiningReport)
async def get_finance_process_mining_report(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
) -> ProcessMiningReport:
    projection_status_loader = get_projection_status_loader()
    runtime_report_loader = get_runtime_report_loader()
    if projection_status_loader is None or runtime_report_loader is None:
        raise RuntimeError("Process mining dependencies not registered")
    return build_process_mining_report_for_tenant(
        tenant_id=tenant_id,
        db=db,
        projection_status_loader=projection_status_loader,
        runtime_report_loader=runtime_report_loader,
        device_store=get_telemetry_device_store(),
        reading_store=get_telemetry_reading_store(),
    )


@router.get("/finance/bottlenecks", response_model=list[dict])
async def list_finance_process_bottlenecks(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
) -> list[dict]:
    report = await get_finance_process_mining_report(tenant_id=tenant_id, db=db)
    return [entry.model_dump(mode="json") for entry in report.bottlenecks]


@router.get("/finance/top-processes", response_model=list[ProcessMiningProcessSummary])
async def list_finance_top_processes(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
    limit: int = 10,
) -> list[ProcessMiningProcessSummary]:
    report = await get_finance_process_mining_report(tenant_id=tenant_id, db=db)
    return build_process_mining_top_processes(report, limit=limit)


@router.get("/finance/drilldown/{projection_key}", response_model=ProcessMiningDrilldown)
async def get_finance_process_drilldown(
    projection_key: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
) -> ProcessMiningDrilldown:
    report = await get_finance_process_mining_report(tenant_id=tenant_id, db=db)
    return build_process_mining_drilldown(report, projection_key=projection_key)
