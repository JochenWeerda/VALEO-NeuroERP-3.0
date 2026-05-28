"""
Quadriga-Connector API – Konfiguration und Sync für Quadriga-Anbindung.
CRUD für Connector-Konfiguration (domain_erp.connector_configs), Sync-Handler (Stub).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.fibu_audit import log_fibu_audit

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.quadriga_connector_schemas import QuadrigaConnectorOut


router = APIRouter(prefix="/quadriga-connector", tags=["finance", "quadriga", "connectors"])

QUADRIGA_CODE = "QUADRIGA"


class ConnectorConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    config_json: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConnectorConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    connector_code: str
    name: Optional[str] = None
    config_json: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuadrigaSyncRequest(BaseModel):
    direction: str = Field(default="export", description="export | import")
    options: Dict[str, Any] = Field(default_factory=dict)


def _row_to_config(row) -> ConnectorConfig:
    return ConnectorConfig(
        id=row[0],
        tenant_id=row[1],
        connector_code=row[2],
        name=row[3],
        config_json=row[4] or {},
        is_active=row[5] is True,
        created_at=row[6],
        updated_at=row[7],
    )


@router.get("/config", response_model=Optional[ConnectorConfig], summary="Quadriga config abrufen")
async def get_quadriga_config(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Quadriga-Konfiguration des Mandanten abrufen (eine pro Mandant)."""
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at
            FROM domain_erp.connector_configs
            WHERE tenant_id = :tenant_id AND connector_code = :code
        """),
        {"tenant_id": tenant_id, "code": QUADRIGA_CODE},
    ).fetchone()
    if not row:
        return None
    return _row_to_config(row)


@router.put("/config", response_model=ConnectorConfig, summary="Quadriga config put")
async def put_quadriga_config(
    payload: ConnectorConfigUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Quadriga-Konfiguration speichern oder anlegen (Upsert)."""
    existing = db.execute(
        text("SELECT id FROM domain_erp.connector_configs WHERE tenant_id = :tenant_id AND connector_code = :code"),
        {"tenant_id": tenant_id, "code": QUADRIGA_CODE},
    ).fetchone()
    if existing:
        updates = ["updated_at = NOW()"]
        params: dict = {"tenant_id": tenant_id, "code": QUADRIGA_CODE}
        if payload.name is not None:
            updates.append("name = :name")
            params["name"] = payload.name
        if payload.config_json is not None:
            updates.append("config_json = :config_json::jsonb")
            import json
            params["config_json"] = json.dumps(payload.config_json)
        if payload.is_active is not None:
            updates.append("is_active = :is_active")
            params["is_active"] = payload.is_active
        db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                UPDATE domain_erp.connector_configs
                SET {", ".join(updates)}
                WHERE tenant_id = :tenant_id AND connector_code = :code
            """),
            params,
        )
        db.commit()
        config_id = existing[0]
        log_fibu_audit(db, tenant_id, "update", "connector_config", config_id, {"connector_code": QUADRIGA_CODE}, request=None)
    else:
        config_id = str(uuid4())
        name = payload.name or "Quadriga"
        config_json = payload.config_json or {}
        is_active = payload.is_active if payload.is_active is not None else True
        import json
        db.execute(
            text("""
                INSERT INTO domain_erp.connector_configs
                (id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at)
                VALUES (:id, :tenant_id, :code, :name, :config_json::jsonb, :is_active, NOW(), NOW())
            """),
            {
                "id": config_id,
                "tenant_id": tenant_id,
                "code": QUADRIGA_CODE,
                "name": name,
                "config_json": json.dumps(config_json),
                "is_active": is_active,
            },
        )
        db.commit()
        log_fibu_audit(db, tenant_id, "create", "connector_config", config_id, {"connector_code": QUADRIGA_CODE}, request=None)
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at
            FROM domain_erp.connector_configs WHERE id = :id
        """),
        {"id": config_id},
    ).fetchone()
    return _row_to_config(row)


@router.post("/sync", response_model=QuadrigaConnectorOut, summary="Sync quadriga")
async def quadriga_sync(
    payload: QuadrigaSyncRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Sync mit Quadriga auslösen (Export oder Import).
    Stub: prüft Konfiguration, gibt Erfolg zurück. Echte Anbindung per Job/API später.
    """
    row = db.execute(
        text("SELECT id, is_active FROM domain_erp.connector_configs WHERE tenant_id = :tenant_id AND connector_code = :code"),
        {"tenant_id": tenant_id, "code": QUADRIGA_CODE},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=400, detail="Quadriga-Konfiguration fehlt. Bitte zuerst Konfiguration anlegen.")
    if not row[1]:
        raise HTTPException(status_code=400, detail="Quadriga-Connector ist deaktiviert.")
    log_fibu_audit(
        db, tenant_id, "sync", "connector_config", row[0],
        {"connector_code": QUADRIGA_CODE, "direction": payload.direction},
        request=None,
    )
    return {
        "success": True,
        "message": f"Quadriga {payload.direction} angestoßen (Stub: keine Daten übertragen).",
        "direction": payload.direction,
        "config_id": row[0],
    }


@router.get("/config/list", response_model=List[ConnectorConfig], summary="Connector configs auflisten")
async def list_connector_configs(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Alle Connector-Konfigurationen des Mandanten (für Übersicht)."""
    rows = db.execute(
        text("""
            SELECT id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at
            FROM domain_erp.connector_configs
            WHERE tenant_id = :tenant_id
            ORDER BY connector_code
        """),
        {"tenant_id": tenant_id},
    ).fetchall()
    return [_row_to_config(r) for r in rows]
