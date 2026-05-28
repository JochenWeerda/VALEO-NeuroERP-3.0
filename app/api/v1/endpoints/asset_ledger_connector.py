"""
VALEO Suite Anlagen (Asset Ledger) – Connector API.
Konfiguration und Sync für Anlagenbuchhaltung (domain_erp.connector_configs).
Ersetzt die bisherige Quadriga-Anbindung; geschützter Name wird nicht verwendet.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.fibu_audit import log_fibu_audit

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.asset_ledger_connector_schemas import AssetLedgerConnectorOut


router = APIRouter(prefix="/asset-ledger-connector", tags=["finance", "asset-ledger", "connectors"])

CONNECTOR_CODE = "ASSET_LEDGER"
DEFAULT_NAME = "VALEO Suite Anlagen (Asset Ledger)"


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


class AssetLedgerSyncRequest(BaseModel):
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


@router.get("/config", response_model=Optional[ConnectorConfig], summary="Asset ledger config abrufen")
async def get_asset_ledger_config(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Konfiguration VALEO Suite Anlagen des Mandanten (eine pro Mandant)."""
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at
            FROM domain_erp.connector_configs
            WHERE tenant_id = :tenant_id AND connector_code = :code
        """),
        {"tenant_id": tenant_id, "code": CONNECTOR_CODE},
    ).fetchone()
    if not row:
        return None
    return _row_to_config(row)


@router.put("/config", response_model=ConnectorConfig, summary="Asset ledger config put")
async def put_asset_ledger_config(
    payload: ConnectorConfigUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Konfiguration speichern oder anlegen (Upsert)."""
    existing = db.execute(
        text("SELECT id FROM domain_erp.connector_configs WHERE tenant_id = :tenant_id AND connector_code = :code"),
        {"tenant_id": tenant_id, "code": CONNECTOR_CODE},
    ).fetchone()
    if existing:
        updates = ["updated_at = NOW()"]
        params: dict = {"tenant_id": tenant_id, "code": CONNECTOR_CODE}
        if payload.name is not None:
            updates.append("name = :name")
            params["name"] = payload.name
        if payload.config_json is not None:
            updates.append("config_json = :config_json::jsonb")
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
        log_fibu_audit(db, tenant_id, "update", "connector_config", config_id, {"connector_code": CONNECTOR_CODE}, request=None)
    else:
        config_id = str(uuid4())
        name = payload.name or DEFAULT_NAME
        config_json = payload.config_json or {}
        is_active = payload.is_active if payload.is_active is not None else True
        db.execute(
            text("""
                INSERT INTO domain_erp.connector_configs
                (id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at)
                VALUES (:id, :tenant_id, :code, :name, :config_json::jsonb, :is_active, NOW(), NOW())
            """),
            {
                "id": config_id,
                "tenant_id": tenant_id,
                "code": CONNECTOR_CODE,
                "name": name,
                "config_json": json.dumps(config_json),
                "is_active": is_active,
            },
        )
        db.commit()
        log_fibu_audit(db, tenant_id, "create", "connector_config", config_id, {"connector_code": CONNECTOR_CODE}, request=None)
    row = db.execute(
        text("""
            SELECT id, tenant_id, connector_code, name, config_json, is_active, created_at, updated_at
            FROM domain_erp.connector_configs WHERE id = :id
        """),
        {"id": config_id},
    ).fetchone()
    return _row_to_config(row)


@router.post("/sync", response_model=AssetLedgerConnectorOut, summary="Ledger sync asset")
async def asset_ledger_sync(
    payload: AssetLedgerSyncRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Sync für Anlagenbuchhaltung (Export oder Import).
    Stub: prüft Konfiguration, gibt Erfolg zurück. Echte Anbindung per Job/API später.
    """
    row = db.execute(
        text("SELECT id, is_active FROM domain_erp.connector_configs WHERE tenant_id = :tenant_id AND connector_code = :code"),
        {"tenant_id": tenant_id, "code": CONNECTOR_CODE},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=400, detail="Konfiguration VALEO Suite Anlagen fehlt. Bitte zuerst Konfiguration anlegen.")
    if not row[1]:
        raise HTTPException(status_code=400, detail="Connector ist deaktiviert.")
    log_fibu_audit(
        db, tenant_id, "sync", "connector_config", row[0],
        {"connector_code": CONNECTOR_CODE, "direction": payload.direction},
        request=None,
    )
    return {
        "success": True,
        "message": f"Anlagenbuchhaltung {payload.direction} angestoßen (Stub: keine Daten übertragen).",
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
