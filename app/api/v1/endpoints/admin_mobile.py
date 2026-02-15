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


@router.delete("/stations/{item_id}", status_code=204)
async def delete_station(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_stations WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Station not found")
    db.commit()
    return None


@router.get("/station-devices", response_model=list[dict[str, Any]])
async def list_station_devices(
    station_id: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if station_id:
        where.append("station_id = :station_id")
        params["station_id"] = station_id
    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_shared.admin_station_devices
            WHERE {' AND '.join(where)}
            ORDER BY station_id, device_role, priority
            """
        ),
        params,
    ).mappings().all()
    return [_jsonable(dict(r)) for r in rows]


@router.post("/station-devices", response_model=dict, status_code=201)
async def create_station_device(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["station_id", "device_id", "device_role"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_station_devices
            (id, tenant_id, station_id, device_id, device_role, priority, is_fallback, settings, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :station_id, :device_id, :device_role, :priority, :is_fallback, CAST(:settings AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "station_id": payload.data["station_id"],
            "device_id": payload.data["device_id"],
            "device_role": payload.data["device_role"],
            "priority": int(payload.data.get("priority", 1)),
            "is_fallback": bool(payload.data.get("is_fallback", False)),
            "settings": json.dumps(payload.data.get("settings", {})),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_station_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.put("/station-devices/{item_id}", response_model=dict)
async def update_station_device(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["station_id", "device_id", "device_role"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_station_devices
            SET station_id=:station_id, device_id=:device_id, device_role=:device_role,
                priority=:priority, is_fallback=:is_fallback, settings=CAST(:settings AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "station_id": payload.data["station_id"],
            "device_id": payload.data["device_id"],
            "device_role": payload.data["device_role"],
            "priority": int(payload.data.get("priority", 1)),
            "is_fallback": bool(payload.data.get("is_fallback", False)),
            "settings": json.dumps(payload.data.get("settings", {})),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Station device mapping not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_station_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/station-devices/{item_id}", status_code=204)
async def delete_station_device(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_station_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Station device mapping not found")
    db.commit()
    return None


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


@router.put("/routing-rules/{item_id}", response_model=dict)
async def update_routing_rule(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["rule_code", "name", "document_type", "process_code"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_routing_rules
            SET rule_code=:rule_code, name=:name, document_type=:document_type, process_code=:process_code,
                priority=:priority, is_active=:is_active, station_id=:station_id, device_id=:device_id,
                output_profile_id=:output_profile_id, conditions=CAST(:conditions AS jsonb), actions=CAST(:actions AS jsonb),
                updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "rule_code": payload.data["rule_code"],
            "name": payload.data["name"],
            "document_type": payload.data["document_type"],
            "process_code": payload.data["process_code"],
            "priority": int(payload.data.get("priority", 100)),
            "is_active": bool(payload.data.get("is_active", True)),
            "station_id": payload.data.get("station_id"),
            "device_id": payload.data.get("device_id"),
            "output_profile_id": payload.data.get("output_profile_id"),
            "conditions": json.dumps(payload.data.get("conditions", {})),
            "actions": json.dumps(payload.data.get("actions", {})),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_routing_rules WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/routing-rules/{item_id}", status_code=204)
async def delete_routing_rule(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_routing_rules WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    db.commit()
    return None


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


@router.put("/scan-profiles/{item_id}", response_model=dict)
async def update_scan_profile(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["profile_code", "name", "target_action"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_scan_profiles
            SET profile_code=:profile_code, name=:name, source_type=:source_type, target_action=:target_action,
                is_active=:is_active, barcode_formats=CAST(:barcode_formats AS jsonb), parse_rules=CAST(:parse_rules AS jsonb),
                validation_rules=CAST(:validation_rules AS jsonb), error_mode=:error_mode, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "profile_code": payload.data["profile_code"],
            "name": payload.data["name"],
            "source_type": payload.data.get("source_type", "camera"),
            "target_action": payload.data["target_action"],
            "is_active": bool(payload.data.get("is_active", True)),
            "barcode_formats": json.dumps(payload.data.get("barcode_formats", [])),
            "parse_rules": json.dumps(payload.data.get("parse_rules", {})),
            "validation_rules": json.dumps(payload.data.get("validation_rules", {})),
            "error_mode": payload.data.get("error_mode", "dialog"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Scan profile not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_scan_profiles WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/scan-profiles/{item_id}", status_code=204)
async def delete_scan_profile(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_scan_profiles WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan profile not found")
    db.commit()
    return None


@router.get("/mobile-devices", response_model=list[dict[str, Any]])
async def list_mobile_devices(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    return _list_rows(db, "domain_shared.admin_mobile_devices", tenant_id, "device_code ASC")


@router.post("/mobile-devices", response_model=dict, status_code=201)
async def create_mobile_device(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["device_code", "name"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_mobile_devices
            (id, tenant_id, device_code, name, device_type, ownership_type, platform, os_version, app_version,
             station_id, scan_profile_id, status, last_sync_at, capabilities, settings, is_active, created_at, updated_at)
            VALUES
            (:id, :tenant_id, :device_code, :name, :device_type, :ownership_type, :platform, :os_version, :app_version,
             :station_id, :scan_profile_id, :status, :last_sync_at, CAST(:capabilities AS jsonb), CAST(:settings AS jsonb), :is_active, NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "device_code": payload.data["device_code"],
            "name": payload.data["name"],
            "device_type": payload.data.get("device_type", "smartphone"),
            "ownership_type": payload.data.get("ownership_type", "company"),
            "platform": payload.data.get("platform", "android"),
            "os_version": payload.data.get("os_version"),
            "app_version": payload.data.get("app_version"),
            "station_id": payload.data.get("station_id"),
            "scan_profile_id": payload.data.get("scan_profile_id"),
            "status": payload.data.get("status", "active"),
            "last_sync_at": payload.data.get("last_sync_at"),
            "capabilities": json.dumps(payload.data.get("capabilities", {})),
            "settings": json.dumps(payload.data.get("settings", {})),
            "is_active": bool(payload.data.get("is_active", True)),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_mobile_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.put("/mobile-devices/{item_id}", response_model=dict)
async def update_mobile_device(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["device_code", "name"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_mobile_devices
            SET device_code=:device_code, name=:name, device_type=:device_type, ownership_type=:ownership_type, platform=:platform,
                os_version=:os_version, app_version=:app_version, station_id=:station_id, scan_profile_id=:scan_profile_id,
                status=:status, last_sync_at=:last_sync_at, capabilities=CAST(:capabilities AS jsonb), settings=CAST(:settings AS jsonb),
                is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "device_code": payload.data["device_code"],
            "name": payload.data["name"],
            "device_type": payload.data.get("device_type", "smartphone"),
            "ownership_type": payload.data.get("ownership_type", "company"),
            "platform": payload.data.get("platform", "android"),
            "os_version": payload.data.get("os_version"),
            "app_version": payload.data.get("app_version"),
            "station_id": payload.data.get("station_id"),
            "scan_profile_id": payload.data.get("scan_profile_id"),
            "status": payload.data.get("status", "active"),
            "last_sync_at": payload.data.get("last_sync_at"),
            "capabilities": json.dumps(payload.data.get("capabilities", {})),
            "settings": json.dumps(payload.data.get("settings", {})),
            "is_active": bool(payload.data.get("is_active", True)),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Mobile device not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_mobile_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/mobile-devices/{item_id}", status_code=204)
async def delete_mobile_device(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_mobile_devices WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Mobile device not found")
    db.commit()
    return None


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


@router.put("/connectors/{item_id}", response_model=dict)
async def update_connector(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["config_code", "name", "connector_type"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_connector_configs
            SET config_code=:config_code, name=:name, connector_type=:connector_type, status=:status, auth_type=:auth_type,
                credentials=CAST(:credentials AS jsonb), scopes=CAST(:scopes AS jsonb), mapping=CAST(:mapping AS jsonb),
                retry_policy=CAST(:retry_policy AS jsonb), rate_limit_per_minute=:rate_limit_per_minute,
                last_health_at=:last_health_at, last_error=:last_error, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "config_code": payload.data["config_code"],
            "name": payload.data["name"],
            "connector_type": payload.data["connector_type"],
            "status": payload.data.get("status", "active"),
            "auth_type": payload.data.get("auth_type", "api_key"),
            "credentials": json.dumps(payload.data.get("credentials", {})),
            "scopes": json.dumps(payload.data.get("scopes", [])),
            "mapping": json.dumps(payload.data.get("mapping", {})),
            "retry_policy": json.dumps(payload.data.get("retry_policy", {})),
            "rate_limit_per_minute": payload.data.get("rate_limit_per_minute"),
            "last_health_at": payload.data.get("last_health_at"),
            "last_error": payload.data.get("last_error"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Connector config not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_connector_configs WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/connectors/{item_id}", status_code=204)
async def delete_connector(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_connector_configs WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Connector config not found")
    db.commit()
    return None


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


@router.post("/connector-events", response_model=dict, status_code=201)
async def create_connector_event(payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["connector_id", "event_type"])
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_shared.admin_connector_events
            (id, tenant_id, connector_id, event_type, status, message, payload, retry_count, next_retry_at, created_at)
            VALUES
            (:id, :tenant_id, :connector_id, :event_type, :status, :message, CAST(:payload AS jsonb), :retry_count, :next_retry_at, NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "connector_id": payload.data["connector_id"],
            "event_type": payload.data["event_type"],
            "status": payload.data.get("status", "ok"),
            "message": payload.data.get("message"),
            "payload": json.dumps(payload.data.get("payload", {})),
            "retry_count": int(payload.data.get("retry_count", 0)),
            "next_retry_at": payload.data.get("next_retry_at"),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_connector_events WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.put("/connector-events/{item_id}", response_model=dict)
async def update_connector_event(item_id: str, payload: JsonPayload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _require_fields(payload.data, ["status"])
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.admin_connector_events
            SET status=:status, message=:message, payload=CAST(:payload AS jsonb), retry_count=:retry_count, next_retry_at=:next_retry_at
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "status": payload.data["status"],
            "message": payload.data.get("message"),
            "payload": json.dumps(payload.data.get("payload", {})),
            "retry_count": int(payload.data.get("retry_count", 0)),
            "next_retry_at": payload.data.get("next_retry_at"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Connector event not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_shared.admin_connector_events WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _jsonable(dict(row))


@router.delete("/connector-events/{item_id}", status_code=204)
async def delete_connector_event(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_shared.admin_connector_events WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Connector event not found")
    db.commit()
    return None
