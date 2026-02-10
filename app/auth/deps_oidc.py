"""
OIDC FastAPI Dependencies
Bearer-Token-Validierung mit OIDC Provider
"""

from __future__ import annotations
from typing import List, TypedDict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .oidc import oidc, extract_roles, extract_scopes
import logging

logger = logging.getLogger(__name__)

# Bearer-Token-Schema
bearer = HTTPBearer(auto_error=True)


class User(TypedDict, total=False):
    """Authenticated User Object (OIDC)"""
    sub: str  # Subject (User ID)
    roles: List[str]  # User Roles
    scopes: List[str]  # Token Scopes
    raw: dict  # Raw Claims


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> User:
    """
    Dependency: Validiert OIDC Token und gibt User zurück

    Args:
        creds: Bearer-Token aus Authorization-Header

    Returns:
        User-Objekt mit sub, roles, scopes und raw claims

    Raises:
        HTTPException 401: Token ungültig oder abgelaufen
    """
    try:
        claims = await oidc.verify(creds.credentials)
    except Exception as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid: {str(e)}",
        )

    roles = extract_roles(claims)
    scopes = extract_scopes(claims)

    return {
        "sub": str(claims.get("sub", "")),
        "roles": roles,
        "scopes": scopes,
        "raw": claims,
    }


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

    async def _dep(user: User = Depends(get_current_user)) -> User:
        roles = set(user.get("roles") or [])
        if not roles.intersection(set(needed)):
            logger.warning(
                f"User {user['sub']} lacks required roles. Has: {roles}, needs: {needed}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {needed}",
            )
        return user

    return _dep


def require_scopes(*needed: str):
    """
    Dependency Factory: Prüft ob Token die benötigten Scopes hat

    Args:
        *needed: Benötigte Scopes (z.B. "policy:write", "policy:read")

    Returns:
        Dependency-Function die Scopes validiert

    Raises:
        HTTPException 403: Token hat nicht die benötigten Scopes

    Example:
        @router.post("/restore", dependencies=[Depends(require_scopes("policy:write"))])
        async def restore(): ...
    """

    async def _dep(user: User = Depends(get_current_user)) -> User:
        scopes = set(user.get("scopes") or [])
        if not scopes.issuperset(set(needed)):
            logger.warning(
                f"User {user['sub']} lacks required scopes. Has: {scopes}, needs: {needed}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing scope. Required: {needed}",
            )
        return user

    return _dep


def require_roles_and_scopes(roles: List[str], scopes: List[str]):
    """
    Dependency Factory: Prüft Rollen UND Scopes

    Args:
        roles: Benötigte Rollen
        scopes: Benötigte Scopes

    Returns:
        Dependency-Function die beides validiert

    Example:
        @router.post("/restore", dependencies=[
            Depends(require_roles_and_scopes(["admin"], ["policy:write"]))
        ])
        async def restore(): ...
    """

    async def _dep(user: User = Depends(get_current_user)) -> User:
        # Rollen-Check
        user_roles = set(user.get("roles") or [])
        if not user_roles.intersection(set(roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {roles}",
            )

        # Scope-Check
        user_scopes = set(user.get("scopes") or [])
        if not user_scopes.issuperset(set(scopes)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing scope. Required: {scopes}",
            )

        return user

    return _dep

