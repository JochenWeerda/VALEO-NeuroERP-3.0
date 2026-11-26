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
    FiscalProductRowOut,
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
from app.services.fiscalization.service import FiscalizationService, FiscalTaxRateError
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/pos/fiscalization", tags=["pos", "fiscalization"])


class FiscalProviderConfigIn(BaseModel):
    provider: Literal["fiskaly", "swissbit_cloud", "swissbit_gateway", "simulation"]
    dsfinvk_provider: Literal["fiskaly", "simulation"] = "fiskaly"
    cash_register_id: str = Field(min_length=1, max_length=120)
    client_id: str = Field(min_length=1, max_length=120)
    simulation_allowed: bool = False
    settings: dict[str, Any] = Field(default_factory=dict)
    # Flaches Studio-Feld — wird in settings.terminal_id gemerged (Paritaet Legacy-UI).
    terminal_id: str | None = Field(default=None, max_length=120)


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


@router.put("/config", response_model=FiscalConfigOut, summary="Fiskalisierungsprovider konfigurieren", dependencies=SCHREIBEN["VERKAUF"])
async def put_config(
    payload: FiscalProviderConfigIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    data = payload.model_dump()
    terminal_id = data.pop("terminal_id", None)
    settings = dict(data.get("settings") or {})
    if terminal_id:
        settings["terminal_id"] = terminal_id.strip()
    elif not settings.get("terminal_id") and data.get("client_id"):
        settings["terminal_id"] = str(data["client_id"]).strip()
    data["settings"] = settings
    try:
        return _service(db, tenant_id).save_config(**data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/readiness", response_model=FiscalReadinessOut, summary="Provider-Readiness pruefen")
async def readiness(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _service(db, tenant_id).readiness()


@router.get("/overview", summary="POS-Fiskalisierung KPI-Ueberblick")
async def fiscalization_overview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Flache Config+Readiness-KPIs fuer Studio-Cockpit (Human/CI/MCP)."""
    svc = _service(db, tenant_id)
    cfg = svc.get_config()
    ready = svc.readiness()
    cfg_dict = cfg if isinstance(cfg, dict) else (cfg.model_dump() if hasattr(cfg, "model_dump") else dict(cfg))
    ready_dict = ready if isinstance(ready, dict) else (ready.model_dump() if hasattr(ready, "model_dump") else dict(ready))
    sign = ready_dict.get("sign") or {}
    dsfinvk = ready_dict.get("dsfinvk") or {}
    if hasattr(sign, "model_dump"):
        sign = sign.model_dump()
    if hasattr(dsfinvk, "model_dump"):
        dsfinvk = dsfinvk.model_dump()
    settings = cfg_dict.get("settings") or {}
    blockers = list(ready_dict.get("config_blockers") or [])
    blockers.extend(sign.get("blockers") or [])
    blockers.extend(dsfinvk.get("blockers") or [])
    return {
        "configured": bool(cfg_dict.get("configured")),
        "ready": bool(ready_dict.get("ready")),
        "provider": cfg_dict.get("provider") or "",
        "dsfinvk_provider": cfg_dict.get("dsfinvk_provider") or "",
        "cash_register_id": cfg_dict.get("cash_register_id") or "",
        "client_id": cfg_dict.get("client_id") or "",
        "terminal_id": settings.get("terminal_id") or "",
        "simulation_allowed": bool(cfg_dict.get("simulation_allowed")),
        "sign_ready": bool(sign.get("ready")),
        "sign_provider": sign.get("provider") or "",
        "dsfinvk_ready": bool(dsfinvk.get("ready")),
        "dsfinvk_provider_live": dsfinvk.get("provider") or "",
        "product_count": len(ready_dict.get("products") or []),
        "blocker_text": " · ".join(blockers) if blockers else "keine",
    }


@router.get("/products", response_model=list[FiscalProductRowOut], summary="Optionale fiskaly-Produkte auflisten")
async def list_fiscal_products(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[FiscalProductRowOut]:
    """Flache Produkt-Readiness fuer Studio-Cockpit-Tabelle."""
    ready = _service(db, tenant_id).readiness()
    ready_dict = ready if isinstance(ready, dict) else (ready.model_dump() if hasattr(ready, "model_dump") else dict(ready))
    rows: list[FiscalProductRowOut] = []
    for product in ready_dict.get("products") or []:
        item = product.model_dump() if hasattr(product, "model_dump") else dict(product)
        details = item.get("details") or {}
        if hasattr(details, "model_dump"):
            details = details.model_dump()
        rows.append(
            FiscalProductRowOut(
                id=item.get("product") or item.get("label"),
                product=item.get("product"),
                label=item.get("label"),
                ready=bool(item.get("ready")),
                blockers="; ".join(item.get("blockers") or []),
                execution_note=(details or {}).get("execution_note") or "",
            )
        )
    return rows


@router.post("/transactions/start", response_model=FiscalTransactionResult, summary="Fiskaltransaktion idempotent starten", dependencies=SCHREIBEN["VERKAUF"])
async def start_transaction(
    payload: StartTransactionCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).start(payload)
    except FiscalTaxRateError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/transactions/finish", response_model=FiscalTransactionResult, summary="Fiskaltransaktion idempotent abschliessen", dependencies=SCHREIBEN["VERKAUF"])
async def finish_transaction(
    payload: FinishTransactionCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).finish(payload)
    except FiscalTaxRateError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
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


@router.post("/cash-point-closings", response_model=ProviderResult, summary="DSFinV-K Cash Point Closing uebertragen", dependencies=SCHREIBEN["VERKAUF"])
async def close_cash_point(
    payload: CashPointClosingCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).close_cash_point(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/exports", response_model=ProviderResult, summary="TSE- oder DSFinV-K-Export anfordern", dependencies=SCHREIBEN["VERKAUF"])
async def request_export(
    payload: ExportCommand,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _service(db, tenant_id).request_export(payload)
    except (FiscalProviderError, RuntimeError, ValueError) as exc:
        raise _provider_error(exc) from exc


@router.post("/exports/{export_type}", response_model=ProviderResult, summary="Export mit generierter ID anfordern", dependencies=SCHREIBEN["VERKAUF"])
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
