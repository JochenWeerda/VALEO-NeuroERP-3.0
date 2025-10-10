"""
FastAPI Authentication Dependencies
Bearer-Token-Validierung und Rollen-Check
"""

from __future__ import annotations
from typing import List, TypedDict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .jwt import decode_token

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
    Dependency: Validiert JWT Token und gibt User zurück

    Args:
        creds: Bearer-Token aus Authorization-Header

    Returns:
        User-Objekt mit sub und roles

    Raises:
        HTTPException 401: Token ungültig oder abgelaufen
    """
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

