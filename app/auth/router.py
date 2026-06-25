"""
Authentication Router
Demo-Login-Endpoint für lokale Tests (NICHT für Production!)
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from .jwt import create_access_token
from app.core.config import settings
from app.middleware.rate_limit import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginBody(BaseModel):
    """Login-Request Body"""
    username: str
    role: str = "manager"  # manager | admin | operator


class LoginResponse(BaseModel):
    """Login-Response"""
    ok: bool
    access_token: str
    token_type: str
    user: dict


@router.post("/demo-login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def demo_login(request: Request, body: LoginBody) -> LoginResponse:
    """
    Demo-Login-Endpoint (NUR FÜR ENTWICKLUNG!)

    ⚠️ WARNUNG: Dieser Endpoint gibt jedem User die gewünschte Rolle!
    ⚠️ In Production durch echtes Login mit User-DB ersetzen!

    Args:
        body: LoginBody mit username und role

    Returns:
        LoginResponse mit access_token
    """
    # SC-AUTH-002: Demo-Endpoints sind nur in Entwicklung erlaubt
    if settings.APP_ENV == "production":
        raise HTTPException(status_code=403, detail="Demo-Login nicht verfügbar in Produktion")

    # Validiere Rolle
    valid_roles = ["admin", "manager", "operator"]
    if body.role not in valid_roles:
        raise HTTPException(
            status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}"
        )

    # Erstelle Token
    token = create_access_token(sub=body.username, roles=[body.role])

    logger.warning(
        f"⚠️ Demo-Login: User '{body.username}' mit Rolle '{body.role}' (UNSICHER - nur für Dev!)"
    )

    return LoginResponse(
        ok=True,
        access_token=token,
        token_type="bearer",
        user={"username": body.username, "roles": [body.role]},
    )


@router.post("/demo-multi-role", response_model=LoginResponse)
@limiter.limit("10/minute")
async def demo_multi_role_login(request: Request, username: str, roles: list[str]) -> LoginResponse:
    """
    Demo-Login mit mehreren Rollen (NUR FÜR ENTWICKLUNG!)

    Args:
        username: Username
        roles: Liste von Rollen

    Returns:
        LoginResponse mit access_token
    """
    # SC-AUTH-002: Demo-Endpoints sind nur in Entwicklung erlaubt
    if settings.APP_ENV == "production":
        raise HTTPException(status_code=403, detail="Demo-Login nicht verfügbar in Produktion")

    # Erstelle Token mit mehreren Rollen
    token = create_access_token(sub=username, roles=roles)

    logger.warning(
        f"⚠️ Demo-Login: User '{username}' mit Rollen {roles} (UNSICHER - nur für Dev!)"
    )

    return LoginResponse(
        ok=True,
        access_token=token,
        token_type="bearer",
        user={"username": username, "roles": roles},
    )

