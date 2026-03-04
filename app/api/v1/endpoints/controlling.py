"""Controlling module CRUD endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/controlling", tags=["controlling"])


class Payload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


def _clean(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for k, v in list(out.items()):
        if isinstance(v, UUID):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
    return out


def _list(db: Session, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        return [_clean(dict(r)) for r in db.execute(text(sql), params).mappings().all()]
    except (OperationalError, ProgrammingError):
        # In dev/staging setups the controlling schema may be absent; keep reads non-fatal.
        db.rollback()
        return []


@router.get("/kpis", response_model=list[dict[str, Any]])
async def list_kpis(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list(
        db,
        "SELECT * FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id ORDER BY kpi_code ASC",
        {"tenant_id": tenant_id},
    )


@router.post("/kpis", response_model=dict, status_code=201)
async def create_kpi(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("kpi_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="kpi_code and name are required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_controlling.kpi_definitions
                (id, tenant_id, kpi_code, name, description, formula, target_value, unit, ampel_logic, filters, is_active, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :kpi_code, :name, :description, :formula, :target_value, :unit, CAST(:ampel_logic AS jsonb), CAST(:filters AS jsonb), :is_active, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "kpi_code": d["kpi_code"],
                "name": d["name"],
                "description": d.get("description"),
                "formula": d.get("formula"),
                "target_value": d.get("target_value"),
                "unit": d.get("unit"),
                "ampel_logic": json.dumps(d.get("ampel_logic", {})),
                "filters": json.dumps(d.get("filters", {})),
                "is_active": bool(d.get("is_active", True)),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"KPI conflict: {exc}") from exc
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.put("/kpis/{item_id}", response_model=dict)
async def update_kpi(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("kpi_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="kpi_code and name are required")
    updated = db.execute(
        text(
            """
            UPDATE domain_controlling.kpi_definitions
            SET kpi_code=:kpi_code, name=:name, description=:description, formula=:formula, target_value=:target_value, unit=:unit,
                ampel_logic=CAST(:ampel_logic AS jsonb), filters=CAST(:filters AS jsonb), is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "kpi_code": d["kpi_code"],
            "name": d["name"],
            "description": d.get("description"),
            "formula": d.get("formula"),
            "target_value": d.get("target_value"),
            "unit": d.get("unit"),
            "ampel_logic": json.dumps(d.get("ampel_logic", {})),
            "filters": json.dumps(d.get("filters", {})),
            "is_active": bool(d.get("is_active", True)),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="KPI not found")
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.delete("/kpis/{item_id}", status_code=204)
async def delete_kpi(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(text("DELETE FROM domain_controlling.kpi_definitions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="KPI not found")
    db.commit()
    return None


@router.get("/dashboards", response_model=list[dict[str, Any]])
async def list_dashboards(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list(db, "SELECT * FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id ORDER BY dashboard_code ASC", {"tenant_id": tenant_id})


@router.post("/dashboards", response_model=dict, status_code=201)
async def create_dashboard(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("dashboard_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="dashboard_code and name are required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_controlling.dashboard_configs
                (id, tenant_id, dashboard_code, name, description, layout, default_filters, role_scope, is_active, created_at, updated_at)
                VALUES
                (:id, :tenant_id, :dashboard_code, :name, :description, CAST(:layout AS jsonb), CAST(:default_filters AS jsonb), CAST(:role_scope AS jsonb), :is_active, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "dashboard_code": d["dashboard_code"],
                "name": d["name"],
                "description": d.get("description"),
                "layout": json.dumps(d.get("layout", {})),
                "default_filters": json.dumps(d.get("default_filters", {})),
                "role_scope": json.dumps(d.get("role_scope", [])),
                "is_active": bool(d.get("is_active", True)),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Dashboard conflict: {exc}") from exc
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.put("/dashboards/{item_id}", response_model=dict)
async def update_dashboard(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("dashboard_code") or not d.get("name"):
        raise HTTPException(status_code=400, detail="dashboard_code and name are required")
    updated = db.execute(
        text(
            """
            UPDATE domain_controlling.dashboard_configs
            SET dashboard_code=:dashboard_code, name=:name, description=:description, layout=CAST(:layout AS jsonb),
                default_filters=CAST(:default_filters AS jsonb), role_scope=CAST(:role_scope AS jsonb), is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "dashboard_code": d["dashboard_code"],
            "name": d["name"],
            "description": d.get("description"),
            "layout": json.dumps(d.get("layout", {})),
            "default_filters": json.dumps(d.get("default_filters", {})),
            "role_scope": json.dumps(d.get("role_scope", [])),
            "is_active": bool(d.get("is_active", True)),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.delete("/dashboards/{item_id}", status_code=204)
async def delete_dashboard(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(text("DELETE FROM domain_controlling.dashboard_configs WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    db.commit()
    return None


@router.get("/dashboards/{dashboard_id}/widgets", response_model=list[dict[str, Any]])
async def list_widgets(dashboard_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list(db, "SELECT * FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND dashboard_id=:dashboard_id ORDER BY position_y, position_x", {"tenant_id": tenant_id, "dashboard_id": dashboard_id})


@router.post("/dashboards/{dashboard_id}/widgets", response_model=dict, status_code=201)
async def create_widget(dashboard_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("widget_type") or not d.get("title"):
        raise HTTPException(status_code=400, detail="widget_type and title are required")
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_controlling.dashboard_widgets
            (id, tenant_id, dashboard_id, widget_type, title, kpi_id, position_x, position_y, size_w, size_h, settings, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :dashboard_id, :widget_type, :title, :kpi_id, :position_x, :position_y, :size_w, :size_h, CAST(:settings AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "dashboard_id": dashboard_id,
            "widget_type": d["widget_type"],
            "title": d["title"],
            "kpi_id": d.get("kpi_id"),
            "position_x": int(d.get("position_x", 0)),
            "position_y": int(d.get("position_y", 0)),
            "size_w": int(d.get("size_w", 4)),
            "size_h": int(d.get("size_h", 3)),
            "settings": json.dumps(d.get("settings", {})),
        },
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.put("/widgets/{item_id}", response_model=dict)
async def update_widget(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("widget_type") or not d.get("title"):
        raise HTTPException(status_code=400, detail="widget_type and title are required")
    updated = db.execute(
        text(
            """
            UPDATE domain_controlling.dashboard_widgets
            SET widget_type=:widget_type, title=:title, kpi_id=:kpi_id, position_x=:position_x, position_y=:position_y, size_w=:size_w, size_h=:size_h,
                settings=CAST(:settings AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "widget_type": d["widget_type"],
            "title": d["title"],
            "kpi_id": d.get("kpi_id"),
            "position_x": int(d.get("position_x", 0)),
            "position_y": int(d.get("position_y", 0)),
            "size_w": int(d.get("size_w", 4)),
            "size_h": int(d.get("size_h", 3)),
            "settings": json.dumps(d.get("settings", {})),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.delete("/widgets/{item_id}", status_code=204)
async def delete_widget(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(text("DELETE FROM domain_controlling.dashboard_widgets WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.commit()
    return None


@router.get("/timeseries", response_model=list[dict[str, Any]])
async def list_timeseries(kpi_id: str | None = Query(default=None), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    where = ["tenant_id=:tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if kpi_id:
        where.append("kpi_id=:kpi_id")
        params["kpi_id"] = kpi_id
    return _list(db, f"SELECT * FROM domain_controlling.kpi_timeseries WHERE {' AND '.join(where)} ORDER BY period_start DESC", params)


@router.post("/timeseries", response_model=dict, status_code=201)
async def create_timeseries(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for k in ("kpi_id", "period_start", "period_end", "value"):
        if d.get(k) in (None, ""):
            raise HTTPException(status_code=400, detail=f"{k} is required")
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_controlling.kpi_timeseries
            (id, tenant_id, kpi_id, period_start, period_end, value, dimensions, source, created_at)
            VALUES
            (:id, :tenant_id, :kpi_id, :period_start, :period_end, :value, CAST(:dimensions AS jsonb), :source, NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "kpi_id": d["kpi_id"],
            "period_start": d["period_start"],
            "period_end": d["period_end"],
            "value": d["value"],
            "dimensions": json.dumps(d.get("dimensions", {})),
            "source": d.get("source"),
        },
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.kpi_timeseries WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.delete("/timeseries/{item_id}", status_code=204)
async def delete_timeseries(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(text("DELETE FROM domain_controlling.kpi_timeseries WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Timeseries item not found")
    db.commit()
    return None


@router.get("/actions", response_model=list[dict[str, Any]])
async def list_actions(status: str | None = Query(default=None), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    where = ["tenant_id=:tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if status:
        where.append("status=:status")
        params["status"] = status
    return _list(db, f"SELECT * FROM domain_controlling.controlling_actions WHERE {' AND '.join(where)} ORDER BY created_at DESC", params)


@router.post("/actions", response_model=dict, status_code=201)
async def create_action(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("title"):
        raise HTTPException(status_code=400, detail="title is required")
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_controlling.controlling_actions
            (id, tenant_id, kpi_id, dashboard_id, title, description, owner_user_id, status, due_date, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :kpi_id, :dashboard_id, :title, :description, :owner_user_id, :status, :due_date, NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "kpi_id": d.get("kpi_id"),
            "dashboard_id": d.get("dashboard_id"),
            "title": d["title"],
            "description": d.get("description"),
            "owner_user_id": d.get("owner_user_id"),
            "status": d.get("status", "open"),
            "due_date": d.get("due_date"),
        },
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.controlling_actions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.put("/actions/{item_id}", response_model=dict)
async def update_action(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    if not d.get("title"):
        raise HTTPException(status_code=400, detail="title is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_controlling.controlling_actions
            SET kpi_id=:kpi_id, dashboard_id=:dashboard_id, title=:title, description=:description, owner_user_id=:owner_user_id,
                status=:status, due_date=:due_date, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "kpi_id": d.get("kpi_id"),
            "dashboard_id": d.get("dashboard_id"),
            "title": d["title"],
            "description": d.get("description"),
            "owner_user_id": d.get("owner_user_id"),
            "status": d.get("status", "open"),
            "due_date": d.get("due_date"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Action not found")
    db.commit()
    row = db.execute(text("SELECT * FROM domain_controlling.controlling_actions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _clean(dict(row))


@router.delete("/actions/{item_id}", status_code=204)
async def delete_action(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(text("DELETE FROM domain_controlling.controlling_actions WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Action not found")
    db.commit()
    return None
