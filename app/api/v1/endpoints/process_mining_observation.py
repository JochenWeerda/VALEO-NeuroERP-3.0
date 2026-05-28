from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.endpoint_gateways import (
    get_projection_status_loader,
    get_runtime_report_loader,
    get_telemetry_device_store,
    get_telemetry_reading_store,
)
from app.core.process_mining_application import build_process_mining_report_for_tenant
from app.core.process_mining_observation import (
    ProcessMiningObservationReadModel,
    build_process_mining_observation_read_model,
)
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/process-mining", tags=["process-mining", "analytics"])


def _build_report(tenant_id: str, db: Any):
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


@router.get("/finance/observation", response_model=ProcessMiningObservationReadModel, summary="Finance process observation abrufen")
async def get_finance_process_observation(
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
    top_n: int = 10,
) -> ProcessMiningObservationReadModel:
    report = _build_report(tenant_id, db)
    return build_process_mining_observation_read_model(report, top_n=top_n)


@router.get("/finance/observation/{projection_key}", response_model=ProcessMiningObservationReadModel, summary="Finance process observation drilldown abrufen")
async def get_finance_process_observation_drilldown(
    projection_key: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Any = Depends(get_db),
    top_n: int = 10,
) -> ProcessMiningObservationReadModel:
    report = _build_report(tenant_id, db)
    observation = build_process_mining_observation_read_model(
        report,
        top_n=top_n,
        selected_projection_key=projection_key,
    )
    if observation.selected_process is None:
        raise HTTPException(status_code=404, detail=f"Projection {projection_key!r} not found")
    return observation
