"""
Inventory-specific authentication and authorization middleware
"""

import json
from typing import Optional
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.security import require_bearer_token
from ....infrastructure.models import User as UserModel


def require_inventory_access(
    request: Request,
    token: str = Depends(require_bearer_token),
    db: Session = Depends(get_db)
) -> str:
    """
    Require inventory access permissions.
    Checks if user has inventory-related roles or permissions.
    """
    # Get user claims from request state
    claims = getattr(request.state, 'token_claims', {})

    # For development token, allow all access
    if claims.get('token_type') == 'dev':
        return token

    # Extract user ID from JWT claims
    user_id = claims.get('sub') or claims.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Check user permissions in database
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")

    # Check roles - allow if user has inventory, admin, or manager roles
    user_roles = user.roles or "[]"
    try:
        roles = json.loads(user_roles) if isinstance(user_roles, str) else user_roles
        allowed_roles = ['admin', 'inventory_manager', 'inventory_user', 'manager']

        if not any(role in roles for role in allowed_roles):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for inventory access"
            )
    except (json.JSONDecodeError, TypeError):
        # If roles parsing fails, deny access for security
        raise HTTPException(status_code=403, detail="Invalid user roles configuration")

    return token


def require_inventory_admin(
    request: Request,
    token: str = Depends(require_inventory_access),
    db: Session = Depends(get_db)
) -> str:
    """
    Require inventory admin permissions.
    Only allows users with admin or inventory_manager roles.
    """
    # Get user claims from request state
    claims = getattr(request.state, 'token_claims', {})

    # For development token, allow all access
    if claims.get('token_type') == 'dev':
        return token

    # Extract user ID from JWT claims
    user_id = claims.get('sub') or claims.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Check user permissions in database
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or inactive")

    # Check for admin roles
    user_roles = user.roles or "[]"
    try:
        roles = json.loads(user_roles) if isinstance(user_roles, str) else user_roles
        admin_roles = ['admin', 'inventory_manager']

        if not any(role in roles for role in admin_roles):
            raise HTTPException(
                status_code=403,
                detail="Admin permissions required for this operation"
            )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=403, detail="Invalid user roles configuration")

    return token


def get_current_tenant_id(
    request: Request,
    token: str = Depends(require_inventory_access)
) -> str:
    """
    Extract tenant ID from authenticated user.
    """
    claims = getattr(request.state, 'token_claims', {})

    # For development token, return default tenant
    if claims.get('token_type') == 'dev':
        return "system"

    # Extract tenant ID from JWT claims
    tenant_id = claims.get('tenant_id')
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID not found in token")

    return tenant_id


def require_tenant_access(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db)
) -> str:
    """
    Ensure user has access to the specified tenant.
    """
    claims = getattr(request.state, 'token_claims', {})

    # For development token, allow all tenant access
    if claims.get('token_type') == 'dev':
        return tenant_id

    user_tenant_id = claims.get('tenant_id')
    if user_tenant_id != tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: tenant mismatch"
        )

    return tenant_id