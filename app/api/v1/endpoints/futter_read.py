"""Guarded feed list projections preserving the existing frontend read contract."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.base import CompatBridgeOut
from app.services.inventory_compat_service import FutterCompatService

router = APIRouter()


@router.get("/futter/einzelfuttermittel", response_model=list[CompatBridgeOut], summary="Einzel futter")
async def futter_einzel(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return FutterCompatService(db, tenant_id).list_einzelfuttermittel()


@router.get("/futter/mischfuttermittel", response_model=list[CompatBridgeOut], summary="Misch futter")
async def futter_misch(
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES)
    return FutterCompatService(db, tenant_id).list_mischfuttermittel()


