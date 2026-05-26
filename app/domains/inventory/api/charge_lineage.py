"""Charge lineage endpoints for agrar traceability (DOCFLOW-P0-09)."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....core.module_registry import registry
from modules.bootstrap import initialize_module_registry
from .inventory_auth import get_current_tenant_id, require_inventory_access

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class ChargeLineageCreate(BaseModel):
    article_id: str = Field(..., min_length=1, max_length=64)
    from_charge: str = Field(..., min_length=1, max_length=64)
    to_charge: str = Field(..., min_length=1, max_length=64)
    process_type: str = Field(..., pattern="^(mix|withdrawal|split|transfer)$")
    quantity_share: Decimal = Field(..., gt=0)
    share_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)
    source_movement_id: Optional[str] = None
    target_movement_id: Optional[str] = None
    notes: Optional[str] = Field(default=None, max_length=500)
    created_by: Optional[str] = Field(default=None, max_length=100)


class ChargeLineageOut(ChargeLineageCreate):
    id: str
    tenant_id: str
    created_at: datetime


def _is_agrar_enabled(db: Session, tenant_id: str) -> bool:
    row = db.execute(
        text(
            """
            SELECT settings
            FROM domain_shared.tenants
            WHERE id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    ).first()
    if row and row[0]:
        raw = row[0]
        try:
            parsed = raw if isinstance(raw, dict) else json.loads(raw)
            modules = parsed.get("enabled_modules") if isinstance(parsed, dict) else None
            if isinstance(modules, list):
                return "agrar" in [str(m).strip() for m in modules]
        except Exception:  # noqa: BLE001 — Modul-Flags nicht lesbar; Agrar-Modus wird nicht aktiviert
            pass

    initialize_module_registry()
    return registry.is_enabled("agrar", tenant_id=tenant_id)


def _ensure_agrar_enabled(db: Session, tenant_id: str) -> None:
    if not _is_agrar_enabled(db, tenant_id):
        raise HTTPException(status_code=400, detail="Agrar module disabled for tenant")


def _to_out(row: dict) -> ChargeLineageOut:
    return ChargeLineageOut(
        id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        article_id=str(row["article_id"]),
        from_charge=str(row["from_charge"]),
        to_charge=str(row["to_charge"]),
        process_type=str(row["process_type"]),
        quantity_share=Decimal(str(row["quantity_share"])),
        share_percent=Decimal(str(row["share_percent"])) if row.get("share_percent") is not None else None,
        source_movement_id=(str(row["source_movement_id"]) if row.get("source_movement_id") is not None else None),
        target_movement_id=(str(row["target_movement_id"]) if row.get("target_movement_id") is not None else None),
        notes=row.get("notes"),
        created_by=row.get("created_by"),
        created_at=row["created_at"],
    )


@router.get("/", response_model=list[ChargeLineageOut])
async def list_charge_lineage(
    tenant_id: Optional[str] = Query(None),
    charge: Optional[str] = Query(None),
    article_id: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT
    _ensure_agrar_enabled(db, effective_tenant)

    where = ["tenant_id = :tenant_id"]
    params: dict[str, object] = {"tenant_id": effective_tenant, "limit": limit}
    if charge:
        where.append("(from_charge = :charge OR to_charge = :charge)")
        params["charge"] = charge
    if article_id:
        where.append("article_id = :article_id")
        params["article_id"] = article_id

    rows = db.execute(
        text(
            f"""
            SELECT *
            FROM domain_inventory.charge_lineage_links
            WHERE {" AND ".join(where)}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [_to_out(dict(r)) for r in rows]


@router.post("/", response_model=ChargeLineageOut, status_code=201)
async def create_charge_lineage(
    payload: ChargeLineageCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_access),
    effective_tenant: str = Depends(get_current_tenant_id),
):
    effective_tenant = tenant_id or effective_tenant or DEFAULT_TENANT
    _ensure_agrar_enabled(db, effective_tenant)

    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_inventory.charge_lineage_links
            (id, tenant_id, article_id, from_charge, to_charge, process_type, quantity_share, share_percent,
             source_movement_id, target_movement_id, notes, created_by, created_at)
            VALUES
            (:id, :tenant_id, :article_id, :from_charge, :to_charge, :process_type, :quantity_share, :share_percent,
             :source_movement_id, :target_movement_id, :notes, :created_by, NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": effective_tenant,
            "article_id": payload.article_id,
            "from_charge": payload.from_charge,
            "to_charge": payload.to_charge,
            "process_type": payload.process_type,
            "quantity_share": payload.quantity_share,
            "share_percent": payload.share_percent,
            "source_movement_id": payload.source_movement_id,
            "target_movement_id": payload.target_movement_id,
            "notes": payload.notes,
            "created_by": payload.created_by,
        },
    )
    db.commit()
    row = db.execute(
        text(
            """
            SELECT *
            FROM domain_inventory.charge_lineage_links
            WHERE tenant_id = :tenant_id AND id = :id
            """
        ),
        {"tenant_id": effective_tenant, "id": item_id},
    ).mappings().first()
    return _to_out(dict(row))
