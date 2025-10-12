"""
Role-Based Access Control (RBAC) for VALEO NeuroERP
Provides role checking and permission management
"""

from typing import List, Optional
from fastapi import HTTPException, Request, status
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """System roles"""
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"
    FINANCE_MANAGER = "finance_manager"
    INVENTORY_MANAGER = "inventory_manager"
    CRM_MANAGER = "crm_manager"


class Permission(str, Enum):
    """System permissions"""
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_SYSTEM = "manage_system"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    
    # Finance permissions
    VIEW_FINANCE = "view_finance"
    CREATE_FINANCE = "create_finance"
    APPROVE_PAYMENTS = "approve_payments"
    EXPORT_FINANCE = "export_finance"
    
    # Inventory permissions
    VIEW_INVENTORY = "view_inventory"
    CREATE_INVENTORY = "create_inventory"
    ADJUST_STOCK = "adjust_stock"
    
    # CRM permissions
    VIEW_CUSTOMERS = "view_customers"
    CREATE_CUSTOMERS = "create_customers"
    MANAGE_LEADS = "manage_leads"


# Role -> Permissions mapping
ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    
    Role.USER: [
        Permission.VIEW_INVENTORY,
        Permission.VIEW_CUSTOMERS,
        Permission.VIEW_FINANCE,
    ],
    
    Role.AUDITOR: [
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_FINANCE,
        Permission.VIEW_INVENTORY,
        Permission.VIEW_CUSTOMERS,
    ],
    
    Role.FINANCE_MANAGER: [
        Permission.VIEW_FINANCE,
        Permission.CREATE_FINANCE,
        Permission.APPROVE_PAYMENTS,
        Permission.EXPORT_FINANCE,
    ],
    
    Role.INVENTORY_MANAGER: [
        Permission.VIEW_INVENTORY,
        Permission.CREATE_INVENTORY,
        Permission.ADJUST_STOCK,
    ],
    
    Role.CRM_MANAGER: [
        Permission.VIEW_CUSTOMERS,
        Permission.CREATE_CUSTOMERS,
        Permission.MANAGE_LEADS,
    ],
}


def get_user_roles(request: Request) -> List[str]:
    """Extract user roles from token claims."""
    if not hasattr(request.state, 'token_claims'):
        return []
    
    claims = request.state.token_claims
    
    # Dev token
    if claims.get('token_type') == 'dev':
        return [Role.ADMIN]  # Dev token has admin access
    
    # OIDC token - extract roles from claims
    roles = claims.get('roles', [])
    if isinstance(roles, str):
        roles = [roles]
    
    # Also check realm_access (Keycloak format)
    realm_access = claims.get('realm_access', {})
    if 'roles' in realm_access:
        roles.extend(realm_access['roles'])
    
    return list(set(roles))  # Deduplicate


def get_user_permissions(request: Request) -> List[Permission]:
    """Get all permissions for the current user based on their roles."""
    user_roles = get_user_roles(request)
    permissions = set()
    
    for role_name in user_roles:
        try:
            role = Role(role_name)
            role_perms = ROLE_PERMISSIONS.get(role, [])
            permissions.update(role_perms)
        except ValueError:
            logger.warning(f"Unknown role: {role_name}")
    
    return list(permissions)


def require_role(*allowed_roles: Role):
    """
    Dependency to require specific roles.
    
    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_role(Role.ADMIN))])
        async def list_users():
            ...
    """
    def check_role(request: Request):
        user_roles = get_user_roles(request)
        
        if not any(role.value in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        
        return True
    
    return check_role


def require_permission(*required_permissions: Permission):
    """
    Dependency to require specific permissions.
    
    Usage:
        @router.post("/finance/payment", 
                     dependencies=[Depends(require_permission(Permission.APPROVE_PAYMENTS))])
        async def approve_payment():
            ...
    """
    def check_permission(request: Request):
        user_permissions = get_user_permissions(request)
        
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[p.value for p in required_permissions]}"
            )
        
        return True
    
    return check_permission


def get_tenant_id(request: Request) -> Optional[str]:
    """Extract tenant_id from token claims."""
    if not hasattr(request.state, 'token_claims'):
        return None
    
    claims = request.state.token_claims
    
    # Dev token
    if claims.get('token_type') == 'dev':
        return 'system'
    
    # OIDC token
    return claims.get('tenant_id') or claims.get('tid')


def has_role(request: Request, role: Role) -> bool:
    """Check if user has a specific role."""
    user_roles = get_user_roles(request)
    return role.value in user_roles


def has_permission(request: Request, permission: Permission) -> bool:
    """Check if user has a specific permission."""
    user_permissions = get_user_permissions(request)
    return permission in user_permissions

