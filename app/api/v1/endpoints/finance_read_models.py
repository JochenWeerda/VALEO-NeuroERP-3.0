"""
Finance Read-Models — Wave 2 AP2
Server-side pre-aggregated cockpit KPIs for stable query contracts.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.endpoint_gateways import register_projection_status_loader
from ....core.tenant import get_tenant_id

from app.api.v1.schemas.finance_read_models_schemas import (
    APInvoiceCockpitReadModel,
    CashClosingAnalysisReadModel,
    CashClosingReadModel,
    CashClosingReportingReadModel,
    CashClosingSnapshot,
    FinanceReadModelsOut,
    PaymentRunCockpitReadModel,
    ProcessObservationReadModel,
    ProjectionRebuildResult,
    ProjectionStatusReadModel,
)
from app.services.finance_read_model_service import (
    build_cash_closing_read_model,
    build_sla_profiles,
    cache_projection,
    default_process_observation_instances,
    get_projection_status,
    load_projection,
    persist_projection_registry_entry,
    project_ap_invoice_cockpit,
    project_cash_closing_analysis,
    project_cash_closing_detail,
    project_cash_closing_reporting,
    project_payment_run_cockpit,
    project_process_observation,
    rebuild_finance_projection_store,
    _get_ap_invoice_store,
    _get_payment_run_store,
)

router = APIRouter(prefix="/finance/read-models", tags=["finance", "read-models"])

# Register the projection status loader so other modules can query it
register_projection_status_loader(get_projection_status)


@router.get("/ap-invoice-cockpit", response_model=APInvoiceCockpitReadModel, summary="Ap invoice cockpit abrufen")
async def get_ap_invoice_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> APInvoiceCockpitReadModel:
    """Pre-aggregated AP-invoice cockpit KPIs for the finance dashboard. Schema v1 — stable contract."""
    store = _get_ap_invoice_store()
    tenant_invoices = list(store[tenant_id].values()) if store and tenant_id in store else []
    return cache_projection(
        tenant_id,
        "ap-invoice-cockpit",
        project_ap_invoice_cockpit(tenant_id=tenant_id, tenant_invoices=tenant_invoices),
    )


@router.get("/payment-run-cockpit", response_model=PaymentRunCockpitReadModel, summary="Payment run cockpit abrufen")
async def get_payment_run_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> PaymentRunCockpitReadModel:
    """Pre-aggregated payment-run cockpit KPIs for the finance dashboard. Schema v1 — stable contract."""
    store = _get_payment_run_store()
    tenant_runs = list(store[tenant_id].values()) if store and tenant_id in store else []
    return cache_projection(
        tenant_id,
        "payment-run-cockpit",
        project_payment_run_cockpit(tenant_id=tenant_id, tenant_runs=tenant_runs),
    )


@router.get("/process-observation", response_model=ProcessObservationReadModel, summary="Process observation abrufen")
async def get_process_observation(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProcessObservationReadModel:
    """Cross-domain observation of active workflow instances. Schema v1 — stable contract."""
    return cache_projection(
        tenant_id,
        "process-observation",
        project_process_observation(
            tenant_id=tenant_id,
            workflow_instances=default_process_observation_instances(),
            sla_profiles=build_sla_profiles(tenant_id=tenant_id, db=db),
            overdue_instances=0,
        ),
    )


@router.get("/cash-closings", response_model=CashClosingReadModel, summary="Cash closings abrufen")
async def get_cash_closings(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingReadModel:
    """Finance-facing read model over productive POS cash closings. Schema v1 — stable contract."""
    cached = load_projection(tenant_id, "cash-closings", CashClosingReadModel)
    if cached is not None:
        return cached
    return cache_projection(tenant_id, "cash-closings", build_cash_closing_read_model(db, tenant_id))


@router.get("/cash-closings/analysis", response_model=CashClosingAnalysisReadModel, summary="Cash closing analysis abrufen")
async def get_cash_closing_analysis(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingAnalysisReadModel:
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    return cache_projection(tenant_id, "cash-closings/analysis", project_cash_closing_analysis(snapshot))


@router.get("/cash-closings/reporting", response_model=CashClosingReportingReadModel, summary="Cash closing reporting abrufen")
async def get_cash_closing_reporting(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingReportingReadModel:
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    return cache_projection(tenant_id, "cash-closings/reporting", project_cash_closing_reporting(snapshot))


@router.post("/_rebuild", response_model=ProjectionRebuildResult, summary="Finance read model projections rebuild")
async def rebuild_finance_read_model_projections(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProjectionRebuildResult:
    return rebuild_finance_projection_store(tenant_id=tenant_id, db=db)


@router.get("/_status", response_model=ProjectionStatusReadModel, summary="Finance read model projection status abrufen")
async def get_finance_read_model_projection_status(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> ProjectionStatusReadModel:
    return get_projection_status(tenant_id=tenant_id, db=db)


@router.get("/cash-closings/{closing_id}", response_model=CashClosingSnapshot, summary="Cash closing detail abrufen")
async def get_cash_closing_detail(
    closing_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> CashClosingSnapshot:
    cached = load_projection(tenant_id, f"cash-closings/detail/{closing_id}", CashClosingSnapshot)
    if cached is not None:
        persist_projection_registry_entry(
            db, tenant_id, f"cash-closings/detail/{closing_id}", 1,
            accessed_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        return cached
    snapshot = await get_cash_closings(tenant_id=tenant_id, db=db)
    item = project_cash_closing_detail(snapshot=snapshot, closing_id=closing_id)
    if item is not None:
        persist_projection_registry_entry(
            db, tenant_id, f"cash-closings/detail/{closing_id}", 1,
            accessed_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        return cache_projection(tenant_id, f"cash-closings/detail/{closing_id}", item)
    raise HTTPException(status_code=404, detail="Cash closing not found")


@router.get("/settlement-cockpit", response_model=FinanceReadModelsOut, summary="Settlement cockpit abrufen")
async def get_settlement_cockpit(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Settlement-Cockpit Read-Model (schema_version=1). Stabiler Contract."""
    from ....core.finance_read_model_contracts import SettlementCockpitSnapshot
    return SettlementCockpitSnapshot(tenant_id=tenant_id).as_dict()


@router.get("/position-exposure", response_model=FinanceReadModelsOut, summary="Position exposure abrufen")
async def get_position_exposure(
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Position-Exposure Read-Model (schema_version=1). Stabiler Contract."""
    from ....core.finance_read_model_contracts import PositionExposureSnapshot
    return PositionExposureSnapshot(tenant_id=tenant_id).as_dict()
