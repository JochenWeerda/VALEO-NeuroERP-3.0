from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.endpoint_gateways import (
    get_projection_status_loader,
    get_runtime_report_loader,
    get_telemetry_device_store,
    get_telemetry_reading_store,
)
from app.core.process_mining import ProcessMiningReport
from app.core.process_mining_application import build_process_mining_report_for_tenant
from app.core.read_model_persistence import ReadModelSnapshotStore
from app.core.reporting_layer import (
    ReportDefinition,
    ReportResult,
    build_default_data_products,
    run_report,
)
from app.core.tenant_isolation_guard import IsolationDecision, TenantIsolationGuard

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/reporting", tags=["reporting"])
_guard = TenantIsolationGuard()


def _get_store(db: Session = Depends(get_db)) -> ReadModelSnapshotStore:
    return ReadModelSnapshotStore(db_session=db)


class RunReportRequest(BaseModel):
    requesting_tenant: str | None = None
    tenant_id: str
    wirtschaftsjahr: str | None = None
    report_id: str
    titel: str
    datenprodukt_id: str
    filter_spec: dict = Field(default_factory=dict)
    aggregationen: list[str] = Field(default_factory=list)


class ProcessMiningReportRequest(BaseModel):
    requesting_tenant: str | None = None
    tenant_id: str


@router.get("/data-products", summary="Data products abrufen",
    response_model=CompatFlexOut
)
def get_data_products(
    tenant_id: str = Query(...),
    requesting_tenant: str | None = Query(None),
    wirtschaftsjahr: str | None = Query(None),
    store: ReadModelSnapshotStore = Depends(_get_store),
) -> dict[str, object]:
    _ensure_reporting_access(
        requesting_tenant=requesting_tenant or tenant_id,
        resource_tenant=tenant_id,
        resource_type="reporting_data_product",
    )
    catalog = build_default_data_products(
        store=store,
        tenant_id=tenant_id,
        wirtschaftsjahr=wirtschaftsjahr,
    )
    products = catalog.get_by_tenant(tenant_id)
    return {"items": products, "count": len(products), "schema_version": 1}


@router.post("/run", response_model=ReportResult, summary="Run report erstellen")
def post_run_report(
    request: RunReportRequest,
    store: ReadModelSnapshotStore = Depends(_get_store),
) -> ReportResult:
    _ensure_reporting_access(
        requesting_tenant=request.requesting_tenant or request.tenant_id,
        resource_tenant=request.tenant_id,
        resource_type=_resource_type_for_product(request.datenprodukt_id),
    )
    catalog = build_default_data_products(
        store=store,
        tenant_id=request.tenant_id,
        wirtschaftsjahr=request.wirtschaftsjahr,
    )
    product = catalog.get(request.datenprodukt_id, request.tenant_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Datenprodukt nicht gefunden")
    return run_report(
        report_definition=ReportDefinition(
            report_id=request.report_id,
            titel=request.titel,
            datenprodukt_id=request.datenprodukt_id,
            filter_spec=request.filter_spec,
            aggregationen=request.aggregationen,
        ),
        data_product=product,
        store=store,
    )


@router.post("/process-mining/report", response_model=ProcessMiningReport, summary="Process mining report erstellen")
def post_process_mining_report(
    request: ProcessMiningReportRequest,
    db: Session = Depends(get_db),
) -> ProcessMiningReport:
    _ensure_reporting_access(
        requesting_tenant=request.requesting_tenant or request.tenant_id,
        resource_tenant=request.tenant_id,
        resource_type="process_mining_report",
    )
    projection_status_loader = get_projection_status_loader()
    runtime_report_loader = get_runtime_report_loader()
    if projection_status_loader is None or runtime_report_loader is None:
        raise HTTPException(status_code=503, detail="Process mining dependencies not registered")
    return build_process_mining_report_for_tenant(
        tenant_id=request.tenant_id,
        db=db,
        projection_status_loader=projection_status_loader,
        runtime_report_loader=runtime_report_loader,
        device_store=get_telemetry_device_store(),
        reading_store=get_telemetry_reading_store(),
    )


@router.get("/isolation/check", summary="Isolation check abrufen",
    response_model=CompatFlexOut
)
def get_isolation_check(
    requesting_tenant: str = Query(...),
    resource_tenant: str = Query(...),
    resource_type: str = Query(...),
) -> dict[str, object]:
    decision = _guard.check(
        requesting_tenant=requesting_tenant,
        resource_tenant=resource_tenant,
        resource_type=resource_type,
    )
    return {
        "requesting_tenant": requesting_tenant,
        "resource_tenant": resource_tenant,
        "resource_type": resource_type,
        "decision": decision,
        "schema_version": 1,
    }


def _ensure_reporting_access(
    requesting_tenant: str,
    resource_tenant: str,
    resource_type: str,
) -> None:
    decision = _guard.check(
        requesting_tenant=requesting_tenant,
        resource_tenant=resource_tenant,
        resource_type=resource_type,
    )
    if decision == IsolationDecision.DENIED:
        raise HTTPException(status_code=403, detail="Tenant isolation denied")


def _resource_type_for_product(product_id: str) -> str:
    if product_id == "finance-ap-invoice-cockpit":
        return "ap_invoice"
    if product_id == "finance-payment-run-cockpit":
        return "payment_run"
    return "reporting_data_product"
