"""
API authentication helpers with mandatory provider identity and ERP tenant binding.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from starlette.concurrency import run_in_threadpool

from .config import settings

logger = logging.getLogger(__name__)
http_bearer = HTTPBearer(auto_error=False)

_JWKS_CACHE: Dict[str, Any] = {"url": None, "keys": None, "expires_at": 0.0}
_JWKS_CACHE_TTL = 60 * 60  # 1 hour


async def require_bearer_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer),
) -> str:
    """
    Validate bearer token and attach claims to the request state.
    Requires a signed provider identity and an unambiguous ERP tenant.
    Falls back to ?token= query param for SSE/WebSocket paths where browsers
    cannot set Authorization headers (EventSource limitation).
    """
    if _is_path_exempt(request.url.path):
        return ""

    if len(request.headers.getlist("authorization")) > 1:
        raise HTTPException(401, "Ambiguous bearer credentials")

    if not isinstance(credentials, HTTPAuthorizationCredentials):
        credentials = await http_bearer(request)

    if credentials is None or credentials.scheme.lower() != "bearer":
        # Fallback: accept token from query param for SSE and WebSocket endpoints
        query_token = request.query_params.get("token", "").strip()
        if query_token and (request.scope["type"] == "websocket" or
                            request.url.path == "/api/events" or request.url.path.startswith("/api/stream/")):
            token = query_token
            if any(value.strip() != token for value in request.query_params.getlist("token")):
                raise HTTPException(401, "Ambiguous bearer credentials")
            await run_in_threadpool(verified_identity, request, token)
            return token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials.strip()
    query_tokens = request.query_params.getlist("token")
    if query_tokens and (request.scope["type"] == "websocket" or request.url.path == "/api/events" or request.url.path.startswith("/api/stream/")):
        if any(value.strip() != token for value in query_tokens):
            raise HTTPException(401, "Ambiguous bearer credentials")
    await run_in_threadpool(verified_identity, request, token)
    return token


def verified_identity(connection, token: str) -> dict:
    """One signed provider identity for HTTP dependencies and WebSockets."""
    from app.core.tenant_binding import checked_tenant, bind_headers, check_selector
    if (getattr(connection.state, "tenant_verified", False)
            and token == getattr(connection.state, "authenticated_token", None)):
        claims = connection.state.token_claims
    else:
        try:
            claims = _validate_jwt(token)
        except jwt.PyJWTError as exc:
            raise HTTPException(401, "Invalid bearer token") from exc
    tenant = checked_tenant(claims)
    from app.core.identity_session import validate
    validate(claims, token, touch=not getattr(connection.state, "tenant_verified", False))
    bind_headers(connection.scope, tenant)
    from app.core.tenant_binding import TENANT_FIELDS, TENANT_LIST_FIELDS
    for name in TENANT_FIELDS | TENANT_LIST_FIELDS:
        if name in connection.query_params:
            check_selector(connection.query_params.getlist(name), tenant)
    connection.state.token_claims = claims
    connection.state.tenant_id = tenant
    connection.state.tenant_verified = True
    connection.state.authenticated_token = token
    return claims


def verified_websocket_context(websocket, query_token: str | None, query_tenant: str | None = None) -> dict:
    from app.auth.oidc import extract_roles
    from app.core.tenant_binding import check_selector
    headers = websocket.headers.getlist("authorization")
    if len(headers) > 1:
        raise HTTPException(401, "Ambiguous bearer credentials")
    header = headers[0] if headers else ""
    if header and not header.lower().startswith("bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = header[7:].strip() if header else (query_token or "").strip()
    values = websocket.query_params.getlist("token")
    if not token or any(value.strip() != token for value in values):
        raise HTTPException(401, "Missing or ambiguous bearer credentials")
    claims = verified_identity(websocket, token)
    check_selector(query_tenant, websocket.state.tenant_id)
    return {"user_id": claims["sub"], "roles": extract_roles(claims), "tenant_id": websocket.state.tenant_id}


def _validate_jwt(token: str) -> Dict[str, Any]:
    jwks_url = _resolve_jwks_url()
    if not jwks_url:
        logger.warning("OIDC JWKS URL is not configured; rejecting bearer token.")
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    keys = _get_jwks(jwks_url)
    header = jwt.get_unverified_header(token)  # NOSONAR - only kid/alg are read before signed JWT validation.
    kid = header.get("kid")
    algorithm = header.get("alg", "RS256")
    if algorithm not in {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512"}:
        logger.warning("Rejecting bearer token with unsupported algorithm: %s", algorithm)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    key_data = _find_jwk(keys, kid)
    if key_data is None:
        keys = _get_jwks(jwks_url, force_refresh=True)
        key_data = _find_jwk(keys, kid)
        if key_data is None:
            logger.warning("Unable to locate signing key for kid=%s", kid)
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token",
            )

    audience = settings.OIDC_CLIENT_ID or settings.KEYCLOAK_CLIENT_ID
    issuer = _resolve_issuer()

    options = {
        "verify_aud": True,
        "verify_iss": True,
        "require": ["iss", "aud", "exp", "sub"],
    }

    if not audience or not issuer:
        raise HTTPException(401, "Identity provider issuer and audience are required")

    try:
        claims = jwt.decode(
            token,
            jwt.PyJWK.from_dict(key_data).key,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options=options,
        )
    except InvalidTokenError as exc:
        logger.warning("JWT validation failed: %s", exc)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        ) from exc

    return claims


def _resolve_jwks_url() -> Optional[str]:
    if settings.OIDC_JWKS_URL:
        return settings.OIDC_JWKS_URL.rstrip("/")
    if settings.KEYCLOAK_URL and settings.KEYCLOAK_REALM:
        base = settings.KEYCLOAK_URL.rstrip("/")
        return f"{base}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    return None


def _resolve_issuer() -> Optional[str]:
    if settings.OIDC_ISSUER_URL:
        return settings.OIDC_ISSUER_URL.rstrip("/")
    if settings.KEYCLOAK_URL and settings.KEYCLOAK_REALM:
        return f"{settings.KEYCLOAK_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}"
    return None


def _get_jwks(jwks_url: str, *, force_refresh: bool = False) -> List[Dict[str, Any]]:
    cached_url = _JWKS_CACHE.get("url")
    expires_at = _JWKS_CACHE.get("expires_at", 0.0)
    if (
        not force_refresh
        and cached_url == jwks_url
        and _JWKS_CACHE.get("keys") is not None
        and time.time() < expires_at
    ):
        return _JWKS_CACHE["keys"]  # type: ignore[return-value]

    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
        keys = data.get("keys", [])
    except (httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.error("Failed to fetch JWKS: %s", exc)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Identity provider unavailable",
        ) from exc

    _JWKS_CACHE.update(
        {
            "url": jwks_url,
            "keys": keys,
            "expires_at": time.time() + _JWKS_CACHE_TTL,
        }
    )
    return keys  # type: ignore[return-value]


def _find_jwk(keys: List[Dict[str, Any]], kid: Optional[str]) -> Optional[Dict[str, Any]]:
    if kid:
        for key in keys:
            if key.get("kid") == kid:
                return key
    # fallback: return first key if only one available
    return keys[0] if len(keys) == 1 else None


def get_user_id_from_request(request: Request) -> str:
    """
    Extract user id for audit/logging. Uses request.state.token_claims (set by auth),
    else X-User-ID header, else 'system'.
    """
    if hasattr(request.state, "token_claims") and request.state.token_claims:
        claims = request.state.token_claims
        if claims.get("token_type") == "dev":
            return "dev-user"
        sub = claims.get("sub")
        if sub:
            return str(sub)
    uid = (request.headers.get("X-User-ID") or "").strip()
    return uid or "system"


def get_user_email_from_request(request: Request) -> Optional[str]:
    """Extract email for audit. From token_claims (preferred_username/email) or X-User-Email."""
    if hasattr(request.state, "token_claims") and request.state.token_claims:
        claims = request.state.token_claims
        if claims.get("token_type") == "dev":
            return "dev@local"
        for key in ("email", "preferred_username"):
            val = claims.get(key)
            if val:
                return str(val)
    email = (request.headers.get("X-User-Email") or "").strip()
    return email if email else None


def _is_path_exempt(path: str) -> bool:
    """
    Prüft ob ein Pfad von Auth exemptiert ist.
    Unterstützt exakte Matches und Prefix-Matches (endend mit /).
    """
    normalized = path.rstrip("/")
    # Explicit operational probes only; callbacks require their own documented trust boundary.
    return normalized in {"/api/v1/health", "/api/v1/health/live", "/api/v1/health/ready",
                          "/api/v1/health/startup", "/api/v1/health/database"}
