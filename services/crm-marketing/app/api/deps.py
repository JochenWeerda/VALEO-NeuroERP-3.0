"""FastAPI-Dependencies: Tenant, Nutzer/OIDC-Kontext."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header, HTTPException, Request

from app.api.jwt_oidc import actor_sub_from_claims, claims_from_bearer_token
from app.config.settings import settings


async def require_tenant_id(
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
) -> str:
    if not x_tenant_id or not x_tenant_id.strip():
        raise HTTPException(status_code=400, detail="Header X-Tenant-ID ist erforderlich")
    return x_tenant_id.strip()


async def resolve_actor_id(request: Request) -> str:
    """
    Akteur fuer Audit-Felder:
    1. Authorization: Bearer … (HS256 mit JWT_SECRET oder OIDC/JWKS)
    2. Header X-User-Id
    3. Fallback system nur wenn CRM_ACTOR_ALLOW_SYSTEM_FALLBACK oder DEBUG
    """
    auth = (request.headers.get("Authorization") or "").strip()
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        claims = claims_from_bearer_token(token)
        if claims:
            sub = actor_sub_from_claims(claims)
            if sub:
                return sub

    x_user = (request.headers.get("X-User-Id") or "").strip()
    if x_user:
        return x_user

    if settings.DEBUG or settings.CRM_ACTOR_ALLOW_SYSTEM_FALLBACK:
        return "system"

    raise HTTPException(status_code=401, detail="Authentication required: Bearer token or X-User-Id")
