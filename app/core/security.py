"""
API authentication helpers with optional OIDC/JWT validation.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

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
    Supports a development token (API_DEV_TOKEN) and OIDC JWT validation.
    """
    if _is_path_exempt(request.url.path):
        return ""

    if not isinstance(credentials, HTTPAuthorizationCredentials):
        credentials = await http_bearer(request)

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = credentials.credentials.strip()
    expected = settings.API_DEV_TOKEN

    if expected and token == expected:
        request.state.token_claims = {"token_type": "dev"}
        return token

    claims = _validate_jwt(token)
    request.state.token_claims = claims
    return token


def _validate_jwt(token: str) -> Dict[str, Any]:
    jwks_url = _resolve_jwks_url()
    if not jwks_url:
        logger.warning("OIDC JWKS URL is not configured; rejecting bearer token.")
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )

    keys = _get_jwks(jwks_url)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    algorithm = header.get("alg", "RS256")

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
        "verify_aud": bool(audience),
        "verify_iss": bool(issuer),
    }

    try:
        claims = jwt.decode(
            token,
            key_data,
            algorithms=[algorithm],
            audience=audience,
            issuer=issuer,
            options=options,
        )
    except JWTError as exc:
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


def _is_path_exempt(path: str) -> bool:
    """
    Prüft ob ein Pfad von Auth exemptiert ist.
    Unterstützt exakte Matches und Prefix-Matches (endend mit /).
    """
    if not path.startswith("/api"):
        return True

    normalized = path.rstrip("/")
    
    for exempt_path in settings.API_AUTH_EXEMPT_PATHS:
        # Prefix-Match für Pfade mit / am Ende
        if exempt_path.endswith("/"):
            prefix = exempt_path.rstrip("/")
            if normalized.startswith(prefix):
                return True
        # Exakter Match
        elif normalized == exempt_path.rstrip("/"):
            return True
    
    return False
