"""Governance: unified master-data audit + tenant policies (FEED-RBAC-048)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agrar.rations.authz import CONNECTOR_ADMIN_ROLES, READ_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/feeding", tags=["feeding-governance"])

MasterDataEntity = Literal["business", "feed", "analysis", "grant"]


class MasterDataAuditEventOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    entity_type: MasterDataEntity
    entity_id: str
    event_type: str
    actor: str
    reason: str | None = None
    delta: dict[str, Any]
    occurred_at: datetime


class TenantPoliciesOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    four_eyes_approval: bool
    updated_by: str | None = None
    updated_at: datetime | None = None


class TenantPoliciesIn(BaseModel):
    four_eyes_approval: bool


@router.get("/audit/master-data", response_model=list[MasterDataAuditEventOut],
            summary="Fachlich lesbares Stammdaten-Audit (Betriebe, Futter, Analysen, Grants)")
async def list_master_data_audit(entity_type: MasterDataEntity | None = None,
                                 entity_id: str | None = None,
                                 db: Session = Depends(get_db),
                                 tenant_id: str = Depends(get_tenant_id),
                                 user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer das Stammdaten-Audit.")
    rows = db.execute(text("""
      SELECT id, entity_type, entity_id, event_type, actor, reason, delta, occurred_at
      FROM domain_agrar.feeding_master_data_audit_events
      WHERE tenant_id=:tenant_id
        AND (:entity_type IS NULL OR entity_type=:entity_type)
        AND (:entity_id IS NULL OR entity_id=:entity_id)
      ORDER BY occurred_at DESC, id DESC LIMIT 500
    """), {"tenant_id": tenant_id, "entity_type": entity_type,
           "entity_id": entity_id}).mappings().all()
    return [dict(row) for row in rows]


@router.get("/policies", response_model=TenantPoliciesOut,
            summary="Mandanten-Governance-Einstellungen lesen")
async def get_policies(db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Governance-Einstellungen.")
    row = db.execute(text("""
      SELECT four_eyes_approval, updated_by, updated_at
      FROM domain_agrar.feeding_tenant_policies WHERE tenant_id=:tenant_id
    """), {"tenant_id": tenant_id}).mappings().first()
    # Ohne Eintrag gilt das heutige Verhalten (Vier-Augen aus).
    return dict(row) if row else {"four_eyes_approval": False,
                                  "updated_by": None, "updated_at": None}


@router.put("/policies", response_model=TenantPoliciesOut,
            summary="Vier-Augen-Prinzip fuer Freigaben mandantenweit konfigurieren")
async def put_policies(body: TenantPoliciesIn, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, CONNECTOR_ADMIN_ROLES,
                  detail="Nur Futtermittel-Administratoren konfigurieren Governance-Einstellungen.")
    row = db.execute(text("""
      INSERT INTO domain_agrar.feeding_tenant_policies
        (tenant_id, four_eyes_approval, updated_by)
      VALUES (:tenant_id, :four_eyes, :actor)
      ON CONFLICT (tenant_id) DO UPDATE SET
        four_eyes_approval=EXCLUDED.four_eyes_approval,
        updated_by=EXCLUDED.updated_by, updated_at=now()
      RETURNING four_eyes_approval, updated_by, updated_at
    """), {"tenant_id": tenant_id, "four_eyes": body.four_eyes_approval,
           "actor": str(user.get("sub") or "unknown")}).mappings().one()
    db.commit()
    return dict(row)
