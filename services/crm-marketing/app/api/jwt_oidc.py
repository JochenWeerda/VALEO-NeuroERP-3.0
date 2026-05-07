"""JWT/OIDC-Validierung fuer Marketing-Service (Bearer, optional HS256 + JWKS)."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.config.settings import settings

logger = logging.getLogger(__name__)

_JWKS_CACHE: dict[str, Any] = {"url": None, "keys": None, "expires_at": 0.0}
_JWKS_TTL = 3600.0


def _resolve_jwks_url() -> str | None:
    if settings.OIDC_JWKS_URL:
        return settings.OIDC_JWKS_URL.rstrip("/")
    if settings.KEYCLOAK_URL and settings.KEYCLOAK_REALM:
        base = settings.KEYCLOAK_URL.rstrip("/")
        return f"{base}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
    return None


def _resolve_issuer() -> str | None:
    if settings.OIDC_ISSUER_URL:
        return settings.OIDC_ISSUER_URL.rstrip("/")
    if settings.KEYCLOAK_URL and settings.KEYCLOAK_REALM:
        return f"{settings.KEYCLOAK_URL.rstrip('/')}/realms/{settings.KEYCLOAK_REALM}"
    return None


def _get_jwks(jwks_url: str, *, force_refresh: bool = False) -> list[dict[str, Any]]:
    cached_url = _JWKS_CACHE.get("url")
    expires_at = float(_JWKS_CACHE.get("expires_at") or 0.0)
    if (
        not force_refresh
        and cached_url == jwks_url
        and _JWKS_CACHE.get("keys") is not None
        and time.time() < expires_at
    ):
        return _JWKS_CACHE["keys"]  # type: ignore[return-value]

    resp = httpx.get(jwks_url, timeout=5.0)
    resp.raise_for_status()
    data = resp.json()
    keys = data.get("keys", [])
    _JWKS_CACHE.update({"url": jwks_url, "keys": keys, "expires_at": time.time() + _JWKS_TTL})
    return keys


def _find_jwk(keys: list[dict[str, Any]], kid: str | None) -> dict[str, Any] | None:
    if kid:
        for k in keys:
            if k.get("kid") == kid:
                return k
    return keys[0] if len(keys) == 1 else None


def claims_from_bearer_token(token: str) -> dict[str, Any] | None:
    """Liefert JWT-Claims oder None, wenn kein gueltiger Bearer-Kontext vorliegt."""
    token = (token or "").strip()
    if not token:
        return None

    if settings.API_DEV_TOKEN and token == settings.API_DEV_TOKEN:
        return {"sub": "api-dev", "token_type": "dev"}

    secret = settings.effective_jwt_hs256_secret()
    if secret:
        try:
            return jwt.decode(token, secret, algorithms=["HS256"], options={"verify_aud": False})
        except JWTError:
            pass

    jwks_url = _resolve_jwks_url()
    if not jwks_url:
        return None

    try:
        keys = _get_jwks(jwks_url)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        algorithm = header.get("alg", "RS256")
        key_data = _find_jwk(keys, kid)
        if key_data is None:
            keys = _get_jwks(jwks_url, force_refresh=True)
            key_data = _find_jwk(keys, kid)
        if key_data is None:
            return None

        audience = settings.OIDC_CLIENT_ID or settings.KEYCLOAK_CLIENT_ID
        issuer = _resolve_issuer()
        decode_kw: dict[str, Any] = {
            "algorithms": [algorithm],
            "options": {"verify_aud": bool(audience), "verify_iss": bool(issuer)},
        }
        if audience:
            decode_kw["audience"] = audience
        if issuer:
            decode_kw["issuer"] = issuer
        return jwt.decode(token, key_data, **decode_kw)
    except (JWTError, httpx.HTTPError, json.JSONDecodeError) as exc:
        logger.warning("JWT validation failed: %s", exc)
        return None


def actor_sub_from_claims(claims: dict[str, Any]) -> str | None:
    if claims.get("token_type") == "dev":
        return "api-dev"
    sub = claims.get("sub")
    if sub:
        return str(sub)
    pref = claims.get("preferred_username")
    if pref:
        return str(pref)
    return None
