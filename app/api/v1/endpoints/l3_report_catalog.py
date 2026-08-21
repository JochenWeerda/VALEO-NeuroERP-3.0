"""Prioritized fixed L3 report catalog API."""

from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.l3_report_catalog_service import (
    L3ReportCatalogService,
    ReportCatalogError,
)

router = APIRouter(prefix="/l3-report-catalog", tags=["reporting", "l3-parity"])


class FactIn(BaseModel):
    source_type: str
    source_ref: str
    source_number: str | None = None
    source_route: str
    occurred_on: date
    fact_type: str
    representative_id: str | None = None
    representative_name: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    article_id: str | None = None
    article_name: str | None = None
    article_group_id: str | None = None
    article_group_name: str | None = None
    batch_id: str | None = None
    batch_name: str | None = None
    harvest_id: str | None = None
    harvest_name: str | None = None
    route_id: str | None = None
    route_name: str | None = None
    quantity: float = 0
    net_amount: float = 0
    gross_amount: float = 0
    currency: str = "EUR"


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except ReportCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "report-user"


@router.get("", response_model=dict)
def catalog(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = L3ReportCatalogService(db, tenant_id).catalog()
    return {"items": items, "count": len(items)}


@router.post("/facts", response_model=dict, status_code=202)
def project_fact(
    body: FactIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).project_fact(
            body.model_dump(mode="json")
        )
    )


@router.get("/{report_id}/run", response_model=dict)
def run_report(
    report_id: str,
    from_date: date = Query(default_factory=lambda: date.today() - timedelta(days=365)),
    to_date: date = Query(default_factory=date.today),
    representative_id: str | None = None,
    customer_id: str | None = None,
    article_id: str | None = None,
    article_group_id: str | None = None,
    batch_id: str | None = None,
    harvest_id: str | None = None,
    route_id: str | None = None,
    currency: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    filters = {
        key: value
        for key, value in locals().copy().items()
        if key
        in {
            "representative_id",
            "customer_id",
            "article_id",
            "article_group_id",
            "batch_id",
            "harvest_id",
            "route_id",
            "currency",
        }
        and value
    }
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).run(
            report_id,
            from_date=from_date,
            to_date=to_date,
            filters=filters,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/{report_id}/drilldown", response_model=list[dict])
def drilldown(
    report_id: str,
    dimension_value: str,
    from_date: date,
    to_date: date,
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).drilldown(
            report_id,
            dimension_value,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
    )


@router.get("/{report_id}/export.csv", response_class=Response)
def export_csv(
    report_id: str,
    request: Request,
    reason: str = Query(min_length=5, max_length=500),
    from_date: date = Query(default_factory=lambda: date.today() - timedelta(days=365)),
    to_date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    content = guarded(
        lambda: L3ReportCatalogService(db, tenant_id).export_csv(
            report_id,
            from_date=from_date,
            to_date=to_date,
            filters={},
            actor=actor(request),
            reason=reason,
        )
    )
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{report_id}.csv"'},
    )
