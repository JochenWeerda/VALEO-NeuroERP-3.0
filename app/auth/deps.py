"""
FastAPI Authentication Dependencies
Bearer-Token-Validierung und Rollen-Check
"""

from __future__ import annotations
from typing import List, Optional, TypedDict
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.tenant import get_tenant_id

# Bearer-Token-Schema
bearer = HTTPBearer(auto_error=True)

class User(TypedDict, total=False):
    """Authenticated User Object"""
    sub: str  # User ID / Username
    roles: List[str]  # User Roles
    name: str  # Anmeldename fuer Menschen (preferred_username, sonst name/email, sonst sub)


def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> User:
    """
    Dependency: Validiert JWT Token und gibt User zurück.
    Verwendet ausschliesslich die verifizierte Provideridentitaet.

    Args:
        creds: Bearer-Token aus Authorization-Header

    Returns:
        User-Objekt mit sub und roles

    Raises:
        HTTPException 401: Token ungültig oder abgelaufen
    """
    if (getattr(request.state, "tenant_verified", False)
            and creds.credentials.strip() == getattr(request.state, "authenticated_token", None)):
        from app.auth.oidc import extract_roles
        claims = request.state.token_claims
        subject = claims["sub"]
        name = next((claims[k].strip() for k in ("preferred_username", "name", "email")
                     if isinstance(claims.get(k), str) and claims[k].strip()), subject)
        return {"sub": subject, "roles": extract_roles(claims), "name": name, "raw": claims}
    from app.core.security import verified_identity
    from app.auth.oidc import extract_roles
    claims = verified_identity(request, creds.credentials.strip())
    roles = extract_roles(claims)

    kennung = claims.get("sub", "")
    name = next(
        (str(claims[k]).strip() for k in ("preferred_username", "name", "email")
         if isinstance(claims.get(k), str) and claims[k].strip()),
        kennung,
    )
    return {"sub": kennung, "roles": roles, "name": name, "raw": claims}


def anmeldename(user: Optional[dict]) -> str:
    """Wie die angemeldete Person in Belegen heisst: ihr Anmeldename, sonst ihre Kennung.

    ``sub`` ist bei Keycloak und Entra eine UUID — richtig fuer das Audit, unlesbar in
    einem Feld "Erfasst durch". Leer, wenn die Anmeldung weder Namen noch Kennung nennt.
    """
    daten = user or {}
    return str(daten.get("name") or daten.get("sub") or "").strip()[:120]


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
