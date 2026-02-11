"""FastAPI dependencies for authentication & authorization."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, Request, status

from .config import AuthConfig
from .jwt_validator import JWTValidator

logger = logging.getLogger(__name__)

_config = AuthConfig()
_validator = JWTValidator(_config)


@dataclass
class CurrentUser:
    """Represents the authenticated user extracted from the JWT token."""

    user_id: str
    tenant_id: str
    email: str = ""
    name: str = ""
    roles: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)

    def has_role(self, role: str) -> bool:
        return role in self.roles or "admin" in self.roles

    def has_scope(self, scope: str) -> bool:
        return scope in self.scopes or "admin:all" in self.scopes


async def get_current_user(request: Request) -> CurrentUser:
    """Extract and validate the current user from the request.

    In DEV_MODE, returns a dev user without token validation.
    In production, validates the Bearer token and extracts claims.

    Raises:
        HTTPException 401 if no valid token is present.
    """
    if _config.DEV_MODE:
        return CurrentUser(
            user_id=_config.DEV_USER_ID,
            tenant_id=request.headers.get("x-tenant-id", _config.DEV_TENANT_ID),
            email="dev@valeo-erp.local",
            name="Dev User",
            roles=list(_config.DEV_ROLES),
            scopes=["admin:all"],
        )

    # Extract Bearer token
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]
    claims = await _validator.validate(token)

    if claims is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user info from claims
    tenant_id = (
        claims.get("tenant_id")
        or claims.get("tid")
        or request.headers.get("x-tenant-id", "default")
    )

    roles = (
        claims.get("roles", [])
        or claims.get("realm_access", {}).get("roles", [])
        or claims.get("https://valeo-erp.com/roles", [])
    )

    scopes_raw = claims.get("scope", "")
    scopes = scopes_raw.split(" ") if isinstance(scopes_raw, str) else scopes_raw

    return CurrentUser(
        user_id=claims.get("sub", "unknown"),
        tenant_id=tenant_id,
        email=claims.get("email", ""),
        name=claims.get("name", claims.get("preferred_username", "")),
        roles=roles if isinstance(roles, list) else [roles],
        scopes=scopes if isinstance(scopes, list) else [scopes],
    )


async def get_optional_user(request: Request) -> Optional[CurrentUser]:
    """Like get_current_user but returns None instead of raising 401."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


def require_role(*roles: str) -> Callable:
    """Dependency factory that checks if the user has at least one of the given roles."""

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(user.has_role(r) for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role(s): {', '.join(roles)}",
            )
        return user

    return _check


def require_scope(*scopes: str) -> Callable:
    """Dependency factory that checks if the user has at least one of the given scopes."""

    async def _check(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(user.has_scope(s) for s in scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scope(s): {', '.join(scopes)}",
            )
        return user

    return _check

