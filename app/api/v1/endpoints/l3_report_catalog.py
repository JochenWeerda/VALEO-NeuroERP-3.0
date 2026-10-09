"""Prioritized fixed L3 report catalog API."""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.schemas.reporting_bundle_schemas import (
    L3BonusCorrectionOut,
    L3BonusRunCreatedOut,
    L3BonusRunListOut,
    L3DrilldownRowOut,
    L3FactProjectedOut,
    L3ReportCatalogOut,
    L3ReportRunOut,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.l3_report_catalog_service import (
    L3ReportCatalogService,
    ReportCatalogError,
)
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

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


class BonusRunIn(BaseModel):
    report_id: str
    from_date: date
    to_date: date
    rate_pct: Decimal
    reason: str


class BonusCorrectionIn(BaseModel):
    amount: Decimal
    reason: str


def guarded(call):  # noqa: ANN001, ANN201
    try:
        return call()
    except ReportCatalogError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def actor(request: Request) -> str:
    return request.headers.get("X-User-ID") or "report-user"


@router.get("", response_model=L3ReportCatalogOut, summary="Berichtskatalog abrufen")
def catalog(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    items = L3ReportCatalogService(db, tenant_id).catalog()
    return {"items": items, "count": len(items)}


@router.get("/bonus-runs", response_model=L3BonusRunListOut, summary="Bonuslaeufe auflisten")
def list_bonus_runs(
    db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    return L3ReportCatalogService(db, tenant_id).list_bonus_runs()


@router.post("/bonus-runs", response_model=L3BonusRunCreatedOut, status_code=201, summary="Bonuslauf anlegen")
def create_bonus_run(
    body: BonusRunIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).create_bonus_run(
            report_id=body.report_id,
            from_date=body.from_date,
            to_date=body.to_date,
            rate_pct=body.rate_pct,
            actor=actor(request),
            reason=body.reason,
            commit=True,
        )
    )


@router.post(
    "/bonus-runs/actions/calculate",
    response_model=MaskActionResult,
    summary="Bonuslauf berechnen als Masken-CommandEndpoint",
)
def action_bonus_calculate(
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """CE fuer auswertungen/bonus-berechnung:calculate — dryRun ohne INSERT."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="calculate",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    report_id = str(payload.get("report_id") or "").strip()
    reason = str(payload.get("reason") or audit_reason or "").strip()
    try:
        from_date = date.fromisoformat(str(payload.get("from_date") or ""))
        to_date = date.fromisoformat(str(payload.get("to_date") or ""))
        rate_pct = Decimal(str(payload.get("rate_pct")))
    except Exception:
        return MaskActionResult(
            actionKey="calculate",
            mode=mode,
            success=False,
            error="from_date, to_date und rate_pct sind erforderlich.",
            validationErrors=[
                {"field": "from_date", "message": "ISO-Datum/rate_pct Pflicht", "severity": "blocking"}
            ],
        )

    preview = {
        "report_id": report_id,
        "from_date": from_date.isoformat(),
        "to_date": to_date.isoformat(),
        "rate_pct": str(rate_pct),
        "reason": reason,
        "tenant_id": tenant_id,
    }
    svc = L3ReportCatalogService(db, tenant_id)
    try:
        svc.validate_bonus_run_params(
            report_id=report_id,
            from_date=from_date,
            to_date=to_date,
            rate_pct=rate_pct,
            reason=reason,
        )
    except ReportCatalogError as exc:
        db.rollback()
        return MaskActionResult(
            actionKey="calculate",
            mode=mode,
            success=False,
            error=str(exc),
            validationErrors=[{"field": "_entity", "message": str(exc), "severity": "blocking"}],
        )
    db.rollback()

    if mode != "execute":
        return MaskActionResult(
            actionKey="calculate",
            mode=mode,
            success=True,
            summary="Bonuslauf wuerde berechnet — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )

    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = svc.create_bonus_run(
            report_id=report_id,
            from_date=from_date,
            to_date=to_date,
            rate_pct=rate_pct,
            actor=actor(request),
            reason=reason,
        )
        run_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="calculate",
            entity_type="bonus_run",
            entity_id=run_id,
            audit_reason=audit_reason or reason,
            idempotency_key=idempotency_key,
            summary=f"Bonuslauf {report_id} berechnet ({created.get('lines')} Zeilen)",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="reporting.bonus_run.calculated",
            aggregate_id=run_id,
            payload={"run_id": run_id, "report_id": report_id, "tenant_id": tenant_id},
        )
        db.commit()
    except ReportCatalogError as exc:
        db.rollback()
        return MaskActionResult(
            actionKey="calculate", mode=mode, success=False, error=str(exc),
        )
    except Exception:
        db.rollback()
        return MaskActionResult(
            actionKey="calculate",
            mode=mode,
            success=False,
            error="Bonuslauf konnte nicht berechnet werden.",
        )

    return MaskActionResult(
        actionKey="calculate",
        mode=mode,
        success=True,
        summary=f"Bonuslauf berechnet: {created.get('total_bonus')} EUR.",
        affectedIds=[run_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[{**preview, **{k: str(v) if isinstance(v, Decimal) else v for k, v in created.items()}}],
    )


@router.post("/bonus-runs/{run_id}/corrections", response_model=L3BonusCorrectionOut, status_code=201, summary="Bonuslauf korrigieren")
def correct_bonus_run(
    run_id: str,
    body: BonusCorrectionIn,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).correct_bonus_run(
            run_id,
            amount=body.amount,
            actor=actor(request),
            reason=body.reason,
        )
    )


@router.get("/bonus-runs/{run_id}/export.csv", response_class=Response, summary="Bonuslauf als CSV exportieren")
def export_bonus_run(
    run_id: str,
    request: Request,
    reason: str = Query(min_length=5, max_length=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    content = guarded(
        lambda: L3ReportCatalogService(db, tenant_id).export_bonus_run(
            run_id,
            actor=actor(request),
            reason=reason,
        )
    )
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="bonus-{run_id}.csv"'},
    )


@router.post("/facts", response_model=L3FactProjectedOut, status_code=202, summary="Berichtsfakt projizieren")
def project_fact(
    body: FactIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)
) -> dict[str, Any]:
    return guarded(
        lambda: L3ReportCatalogService(db, tenant_id).project_fact(
            body.model_dump(mode="json")
        )
    )


@router.get("/{report_id}/run", response_model=L3ReportRunOut, summary="Bericht ausfuehren")
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


@router.get("/{report_id}/drilldown", response_model=list[L3DrilldownRowOut], summary="Bericht auf einen Dimensionswert aufreissen")
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


@router.get("/{report_id}/export.csv", response_class=Response, summary="Bericht als CSV exportieren")
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
