"""Controlling module CRUD endpoints."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.read_model_cache import cached_read_model
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.services.controlling_service import ControllingService, ControllingSchemaError

router = APIRouter(prefix="/controlling", tags=["controlling"])


class Payload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


def _svc(db: Session, tenant_id: str) -> ControllingService:
    return ControllingService(db, tenant_id)


def _schema_error() -> HTTPException:
    return HTTPException(status_code=503, detail="Controlling module not initialized. Run: alembic upgrade head")


# ── KPIs ──────────────────────────────────────────────────────────────────────

@router.get("/kpis", response_model=list[dict[str, Any]], summary="Kpis auflisten")
@cached_read_model("ctrl_kpis", ttl=30)
def list_kpis(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _svc(db, tenant_id).list_kpis()


@router.post("/kpis", response_model=dict, status_code=201, summary="Kpi anlegen")
async def create_kpi(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("kpi_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="kpi_code and name are required")
    try:
        return _svc(db, tenant_id).create_kpi(d)
    except ControllingSchemaError:
        raise _schema_error()
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)


@router.put("/kpis/{item_id}", response_model=dict, summary="Kpi aktualisieren")
async def update_kpi(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("kpi_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="kpi_code and name are required")
    try:
        return _svc(db, tenant_id).update_kpi(item_id, d)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="KPI not found")


@router.delete("/kpis/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Kpi löschen")
async def delete_kpi(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        _svc(db, tenant_id).delete_kpi(item_id)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="KPI not found")


# ── Dashboards ────────────────────────────────────────────────────────────────

@router.get("/dashboards", response_model=list[dict[str, Any]], summary="Dashboards auflisten")
@cached_read_model("ctrl_dashboards", ttl=30)
def list_dashboards(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _svc(db, tenant_id).list_dashboards()


@router.post("/dashboards", response_model=dict, status_code=201, summary="Dashboard anlegen")
async def create_dashboard(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("dashboard_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="dashboard_code and name are required")
    try:
        return _svc(db, tenant_id).create_dashboard(d)
    except ControllingSchemaError:
        raise _schema_error()
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)


@router.put("/dashboards/{item_id}", response_model=dict, summary="Dashboard aktualisieren")
async def update_dashboard(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("dashboard_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="dashboard_code and name are required")
    try:
        return _svc(db, tenant_id).update_dashboard(item_id, d)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard not found")


@router.delete("/dashboards/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Dashboard löschen")
async def delete_dashboard(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        _svc(db, tenant_id).delete_dashboard(item_id)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard not found")


# ── Widgets ───────────────────────────────────────────────────────────────────

@router.get("/dashboards/{dashboard_id}/widgets", response_model=list[dict[str, Any]], summary="Widgets auflisten")
async def list_widgets(dashboard_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _svc(db, tenant_id).list_widgets(dashboard_id)


@router.post("/dashboards/{dashboard_id}/widgets", response_model=dict, status_code=201, summary="Widget anlegen")
async def create_widget(dashboard_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("widget_type") or not d.get("title"):
        raise HTTPException(status_code=400, detail="widget_type and title are required")
    try:
        return _svc(db, tenant_id).create_widget(dashboard_id, d)
    except ControllingSchemaError:
        raise _schema_error()


@router.put("/widgets/{item_id}", response_model=dict, summary="Widget aktualisieren")
async def update_widget(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("widget_type") or not d.get("title"):
        raise HTTPException(status_code=400, detail="widget_type and title are required")
    try:
        return _svc(db, tenant_id).update_widget(item_id, d)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Widget not found")


@router.delete("/widgets/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Widget löschen")
async def delete_widget(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        _svc(db, tenant_id).delete_widget(item_id)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Widget not found")


# ── Timeseries ────────────────────────────────────────────────────────────────

@router.get("/timeseries", response_model=list[dict[str, Any]], summary="Timeseries auflisten")
@cached_read_model("ctrl_timeseries", ttl=60)
def list_timeseries(kpi_id: Optional[str] = Query(default=None), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _svc(db, tenant_id).list_timeseries(kpi_id)


@router.post("/timeseries", response_model=dict, status_code=201, summary="Timeseries anlegen")
async def create_timeseries(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for k in ("kpi_id", "period_start", "period_end", "value"):
        if d.get(k) in (None, ""):
            raise HTTPException(status_code=400, detail=f"{k} is required")
    try:
        return _svc(db, tenant_id).create_timeseries(d)
    except ControllingSchemaError:
        raise _schema_error()


@router.delete("/timeseries/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Timeseries löschen")
async def delete_timeseries(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        _svc(db, tenant_id).delete_timeseries(item_id)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Timeseries item not found")


# ── Actions ───────────────────────────────────────────────────────────────────

@router.get("/actions", response_model=list[dict[str, Any]], summary="Actions auflisten")
@cached_read_model("ctrl_actions", ttl=15)
def list_actions(status: Optional[str] = Query(default=None), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _svc(db, tenant_id).list_actions(status)


@router.post("/actions", response_model=dict, status_code=201, summary="Action anlegen")
async def create_action(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("title"):
        raise HTTPException(status_code=400, detail="title is required")
    try:
        return _svc(db, tenant_id).create_action(d)
    except ControllingSchemaError:
        raise _schema_error()


@router.put("/actions/{item_id}", response_model=dict, summary="Action aktualisieren")
async def update_action(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("title"):
        raise HTTPException(status_code=400, detail="title is required")
    try:
        return _svc(db, tenant_id).update_action(item_id, d)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Action not found")


@router.delete("/actions/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Action löschen")
async def delete_action(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        _svc(db, tenant_id).delete_action(item_id)
    except ControllingSchemaError:
        raise _schema_error()
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Action not found")
