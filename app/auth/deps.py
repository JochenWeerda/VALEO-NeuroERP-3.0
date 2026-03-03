"""
FastAPI Authentication Dependencies
Bearer-Token-Validierung und Rollen-Check
"""

from __future__ import annotations
from typing import List, TypedDict
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .jwt import decode_token
from app.core.config import settings
from app.core.tenant_context import get_current_tenant_id

# Bearer-Token-Schema
bearer = HTTPBearer(auto_error=True)


class User(TypedDict, total=False):
    """Authenticated User Object"""
    sub: str  # User ID / Username
    roles: List[str]  # User Roles


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> User:
    """
    Dependency: Validiert JWT Token und gibt User zurück.
    Akzeptiert im Dev-Betrieb API_DEV_TOKEN (konsistent mit require_bearer_token).

    Args:
        creds: Bearer-Token aus Authorization-Header

    Returns:
        User-Objekt mit sub und roles

    Raises:
        HTTPException 401: Token ungültig oder abgelaufen
    """
    token = (creds.credentials or "").strip()
    if settings.API_DEV_TOKEN and token == settings.API_DEV_TOKEN:
        return {"sub": "dev", "roles": []}

    try:
        claims = decode_token(creds.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    roles = claims.get("roles") or []
    if not isinstance(roles, list):
        roles = []

    return {"sub": claims.get("sub", ""), "roles": roles}


def require_roles(*needed: str):
    """
    Dependency Factory: Prüft ob User eine der benötigten Rollen hat

    Args:
        *needed: Benötigte Rollen (z.B. "admin", "manager")

    Returns:
        Dependency-Function die User validiert

    Raises:
        HTTPException 403: User hat keine der benötigten Rollen

    Example:
        @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
        async def admin_only(): ...
    """

    def _dep(user: User = Depends(get_current_user)) -> User:
        roles = set(user.get("roles") or [])
        if not roles.intersection(set(needed)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {needed}",
            )
        return user

    return _dep


def get_tenant_id(x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID")) -> str:
    """
    Compatibility tenant dependency for modules importing app.auth.deps.get_tenant_id.
    """
    tenant_id = (x_tenant_id or "").strip()
    return tenant_id or get_current_tenant_id() or settings.DEFAULT_TENANT_ID

