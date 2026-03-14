"""
Inventory-specific authentication and authorization helpers.
"""

from __future__ import annotations

import json

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import require_bearer_token
from app.infrastructure.models import User as UserModel


def require_inventory_access(
    request: Request,
    token: str = Depends(require_bearer_token),
    db: Session = Depends(get_db),
) -> str:
    claims = getattr(request.state, "token_claims", {})

    if claims.get("token_type") == "dev":
        return token

    user_id = claims.get("sub") or claims.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")

    user_roles = user.roles or "[]"
    try:
        roles = json.loads(user_roles) if isinstance(user_roles, str) else user_roles
        allowed_roles = ["admin", "inventory_manager", "inventory_user", "manager"]
        if not any(role in roles for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions for inventory access")
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid user roles configuration")

    return token


def require_inventory_admin(
    request: Request,
    token: str = Depends(require_inventory_access),
    db: Session = Depends(get_db),
) -> str:
    claims = getattr(request.state, "token_claims", {})

    if claims.get("token_type") == "dev":
        return token

    user_id = claims.get("sub") or claims.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")

    user_roles = user.roles or "[]"
    try:
        roles = json.loads(user_roles) if isinstance(user_roles, str) else user_roles
        admin_roles = ["admin", "inventory_manager"]
        if not any(role in roles for role in admin_roles):
            raise HTTPException(status_code=403, detail="Admin permissions required for this operation")
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid user roles configuration")

    return token


def get_current_inventory_tenant_id(
    request: Request,
    token: str = Depends(require_inventory_access),
) -> str:
    claims = getattr(request.state, "token_claims", {})

    if claims.get("token_type") == "dev":
        return settings.DEFAULT_TENANT_ID

    tenant_id = claims.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in token")

    return tenant_id


def require_inventory_tenant_access(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> str:
    claims = getattr(request.state, "token_claims", {})

    if claims.get("token_type") == "dev":
        return tenant_id

    user_tenant_id = claims.get("tenant_id")
    if user_tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied: tenant mismatch")

    return tenant_id
