from __future__ import annotations

from datetime import date
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.pos_fiscalization_schemas import (
    FiscalConfigOut,
    FiscalDailySummaryOut,
    FiscalReadinessOut,
)
from app.services.fiscalization.contracts import (
    CashPointClosingCommand,
    ExportCommand,
    FinishTransactionCommand,
    FiscalTransactionResult,
    ProviderResult,
    StartTransactionCommand,
)
from app.services.fiscalization.providers import FiscalProviderError
from app.services.fiscalization.service import FiscalizationService


router = APIRouter(prefix="/pos/fiscalization", tags=["pos", "fiscalization"])


class FiscalProviderConfigIn(BaseModel):
    provider: Literal["fiskaly", "swissbit_cloud", "swissbit_gateway", "simulation"]
    dsfinvk_provider: Literal["fiskaly", "simulation"] = "fiskaly"
    cash_register_id: str = Field(min_length=1, max_length=120)
    client_id: str = Field(min_length=1, max_length=120)
    simulation_allowed: bool = False
    settings: dict[str, Any] = Field(default_factory=dict)


def _service(db: Session, tenant_id: str) -> FiscalizationService:
    return FiscalizationService(db, tenant_id)


def _provider_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@router.get("/config", response_model=FiscalConfigOut, summary="Fiskalisierungsprovider abrufen")
async def get_config(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(db, tenant_id).get_config()


@router.put("/config", response_model=FiscalConfigOut, summary="Fiskalisierungsprovider konfigurieren")
async def put_config(
    payload: FiscalProviderConfigIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).save_config(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/readiness", response_model=FiscalReadinessOut, summary="Provider-Readiness pruefen")
async def readiness(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(db, tenant_id).readiness()


@router.post("/transactions/start", response_model=FiscalTransactionResult, summary="Fiskaltransaktion idempotent starten")
async def start_transaction(
    payload: StartTransactionCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).start(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/transactions/finish", response_model=FiscalTransactionResult, summary="Fiskaltransaktion idempotent abschliessen")
async def finish_transaction(
    payload: FinishTransactionCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).finish(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.get("/daily-summary", response_model=FiscalDailySummaryOut, summary="Signierte Tageswerte abrufen")
async def daily_summary(
    business_date: date = Query(...),
    terminal_id: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(db, tenant_id).daily_summary(business_date, terminal_id)


@router.post("/cash-point-closings", response_model=ProviderResult, summary="DSFinV-K Cash Point Closing uebertragen")
async def close_cash_point(
    payload: CashPointClosingCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).close_cash_point(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/exports", response_model=ProviderResult, summary="TSE- oder DSFinV-K-Export anfordern")
async def request_export(
    payload: ExportCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).request_export(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/exports/{export_type}", response_model=ProviderResult, summary="Export mit generierter ID anfordern")
async def request_generated_export(
    export_type: Literal["tse", "dsfinvk"],
    cash_register_id: str,
    period_from: date,
    period_to: date,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    payload = ExportCommand(
        export_id=str(uuid4()),
        export_type=export_type,
        cash_register_id=cash_register_id,
        period_from=period_from,
        period_to=period_to,
    )
    try:
        return _service(db, tenant_id).request_export(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc
