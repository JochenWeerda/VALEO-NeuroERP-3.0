"""Admin endpoints for stations, routing, scan profiles, mobile devices and connectors."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter()


class JsonPayload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


def _jsonable(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for key, value in list(out.items()):
        if isinstance(value, UUID):
            out[key] = str(value)
        if isinstance(value, datetime):
            out[key] = value.isoformat()
    return out


def _list_rows(db: Session, table: str, tenant_id: str, order_by: str, limit: int = 500) -> list[dict[str, Any]]:
    rows = db.execute(
        text(f"SELECT * FROM {table} WHERE tenant_id = :tenant_id ORDER BY {order_by} LIMIT :limit"),
        {"tenant_id": tenant_id, "limit": limit},
    ).mappings().all()
    return [_jsonable(dict(r)) for r in rows]


def _require_fields(data: dict[str, Any], keys: list[str]) -> None:
    missing = [k for k in keys if data.get(k) in (None, "")]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")


@router.get("/stations", response_model=list[dict[str, Any]])
async def list_stations(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_stations", tenant_id, "station_code ASC")


@router.post("/stations", response_model=dict, status_code=201)
async def create_station(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["station_code", "name"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_stations (id, tenant_id, station_code, name, station_type, location_name, is_active, settings, created_at, updated_at)
            VALUES (:id, :tenant_id, :station_code, :name, :station_type, :location_name, :is_active, CAST(:settings AS jsonb), NOW(), NOW())
            """
        ),
        {"id": item_id, "tenant_id": tenant_id, "station_code": payload.data["station_code"], "name": payload.data["name"],
         "station_type": payload.data.get("station_type", "workstation"), "location_name": payload.data.get("location_name"),
         "is_active": bool(payload.data.get("is_active", True)), "settings": json.dumps(payload.data.get("settings", {}))},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_shared.admin_stations WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _jsonable(dict(row))


@router.put("/stations/{item_id}", response_model=dict)
async def update_station(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["station_code", "name"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_stations
            SET station_code=:station_code, name=:name, station_type=:station_type, location_name=:location_name, is_active=:is_active,
                settings=CAST(:settings AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {"tenant_id": tenant_id, "id": item_id, "station_code": payload.data["station_code"], "name": payload.data["name"],
         "station_type": payload.data.get("station_type", "workstation"), "location_name": payload.data.get("location_name"),
         "is_active": bool(payload.data.get("is_active", True)), "settings": json.dumps(payload.data.get("settings", {}))},
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Station not found")
    db.commit()
    row = db.execute(text("SELECT * FROM domain_shared.admin_stations WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _jsonable(dict(row))


@router.get("/routing-rules", response_model=list[dict[str, Any]])
async def list_routing_rules(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_routing_rules", tenant_id, "priority ASC, rule_code ASC")


@router.post("/routing-rules", response_model=dict, status_code=201)
async def create_routing_rule(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["rule_code", "name", "document_type", "process_code"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_routing_rules
            (id, tenant_id, rule_code, name, document_type, process_code, priority, is_active, station_id, device_id, output_profile_id, conditions, actions, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :rule_code, :name, :document_type, :process_code, :priority, :is_active, :station_id, :device_id, :output_profile_id, CAST(:conditions AS jsonb), CAST(:actions AS jsonb), NOW(), NOW())
            """
        ),
        {"id": item_id, "tenant_id": tenant_id, "rule_code": payload.data["rule_code"], "name": payload.data["name"],
         "document_type": payload.data["document_type"], "process_code": payload.data["process_code"], "priority": int(payload.data.get("priority", 100)),
         "is_active": bool(payload.data.get("is_active", True)), "station_id": payload.data.get("station_id"), "device_id": payload.data.get("device_id"),
         "output_profile_id": payload.data.get("output_profile_id"), "conditions": json.dumps(payload.data.get("conditions", {})),
         "actions": json.dumps(payload.data.get("actions", {}))},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_shared.admin_routing_rules WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _jsonable(dict(row))


@router.get("/scan-profiles", response_model=list[dict[str, Any]])
async def list_scan_profiles(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_scan_profiles", tenant_id, "profile_code ASC")


@router.post("/scan-profiles", response_model=dict, status_code=201)
async def create_scan_profile(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["profile_code", "name", "target_action"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_scan_profiles
            (id, tenant_id, profile_code, name, source_type, target_action, is_active, barcode_formats, parse_rules, validation_rules, error_mode, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :profile_code, :name, :source_type, :target_action, :is_active, CAST(:barcode_formats AS jsonb), CAST(:parse_rules AS jsonb), CAST(:validation_rules AS jsonb), :error_mode, NOW(), NOW())
            """
        ),
        {"id": item_id, "tenant_id": tenant_id, "profile_code": payload.data["profile_code"], "name": payload.data["name"],
         "source_type": payload.data.get("source_type", "camera"), "target_action": payload.data["target_action"], "is_active": bool(payload.data.get("is_active", True)),
         "barcode_formats": json.dumps(payload.data.get("barcode_formats", [])), "parse_rules": json.dumps(payload.data.get("parse_rules", {})),
         "validation_rules": json.dumps(payload.data.get("validation_rules", {})), "error_mode": payload.data.get("error_mode", "dialog")},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_shared.admin_scan_profiles WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _jsonable(dict(row))


@router.get("/mobile-devices", response_model=list[dict[str, Any]])
async def list_mobile_devices(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_mobile_devices", tenant_id, "device_code ASC")


@router.get("/connectors", response_model=list[dict[str, Any]])
async def list_connectors(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_connector_configs", tenant_id, "connector_type ASC, config_code ASC")


@router.post("/connectors", response_model=dict, status_code=201)
async def create_connector(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["config_code", "name", "connector_type"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_connector_configs
            (id, tenant_id, config_code, name, connector_type, status, auth_type, credentials, scopes, mapping, retry_policy, rate_limit_per_minute, last_health_at, last_error, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :config_code, :name, :connector_type, :status, :auth_type, CAST(:credentials AS jsonb), CAST(:scopes AS jsonb), CAST(:mapping AS jsonb), CAST(:retry_policy AS jsonb), :rate_limit_per_minute, :last_health_at, :last_error, NOW(), NOW())
            """
        ),
        {"id": item_id, "tenant_id": tenant_id, "config_code": payload.data["config_code"], "name": payload.data["name"],
         "connector_type": payload.data["connector_type"], "status": payload.data.get("status", "active"), "auth_type": payload.data.get("auth_type", "api_key"),
         "credentials": json.dumps(payload.data.get("credentials", {})), "scopes": json.dumps(payload.data.get("scopes", [])),
         "mapping": json.dumps(payload.data.get("mapping", {})), "retry_policy": json.dumps(payload.data.get("retry_policy", {})),
         "rate_limit_per_minute": payload.data.get("rate_limit_per_minute"), "last_health_at": payload.data.get("last_health_at"),
         "last_error": payload.data.get("last_error")},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM domain_shared.admin_connector_configs WHERE tenant_id=:tenant_id AND id=:id"), {"tenant_id": tenant_id, "id": item_id}).mappings().first()
    return _jsonable(dict(row))


@router.get("/connector-events", response_model=list[dict[str, Any]])
async def list_connector_events(
    connector_id: str | None = Query(default=None),
    limit: int = Query(default=250, ge=1, le=2000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id, "limit": limit}
    where = ["tenant_id = :tenant_id"]
    if connector_id:
        where.append("connector_id = :connector_id")
        params["connector_id"] = connector_id
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_connector_events
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [_jsonable(dict(r)) for r in rows]
