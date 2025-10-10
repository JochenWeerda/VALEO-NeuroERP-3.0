"""
OIDC Verifier mit Auto-JWKS & Key-Rotation
Unterstützt Azure AD, Auth0, Keycloak, etc.
"""

from __future__ import annotations
import os
import time
import httpx
from typing import Any, Dict, List
from jose import jwt
import logging

logger = logging.getLogger(__name__)

# Environment Configuration
OIDC_ISSUER = os.environ.get("OIDC_ISSUER", "")
OIDC_CLIENT_ID = os.environ.get("OIDC_CLIENT_ID", "")
OIDC_AUDIENCE = os.environ.get("OIDC_AUDIENCE", OIDC_CLIENT_ID)
OIDC_METADATA_URL = os.environ.get("OIDC_METADATA_URL") or (
    f"{OIDC_ISSUER}/.well-known/openid-configuration" if OIDC_ISSUER else ""
)

# Cache-Dauer für JWKS (5 Minuten)
JWKS_CACHE_SECONDS = 300


class OIDC:
    """
    OIDC Token Verifier mit automatischer JWKS-Rotation
    
    Features:
    - Auto-Fetch von OIDC Metadata
    - JWKS Caching mit Auto-Refresh
    - Key-Rotation-Support
    - Multi-Provider-Support (Azure AD, Auth0, Keycloak)
    """

    def __init__(self) -> None:
        self.meta: Dict[str, Any] = {}
        self.jwks: Dict[str, Any] = {}
        self.exp: float = 0.0

    async def _fetch_meta(self) -> None:
        """Holt OIDC Metadata vom Provider"""
        if not OIDC_METADATA_URL:
            raise ValueError("OIDC_METADATA_URL not configured")

        async with httpx.AsyncClient(timeout=10) as c:
            response = await c.get(OIDC_METADATA_URL)
            response.raise_for_status()
            self.meta = response.json()
            logger.info(f"Fetched OIDC metadata from {OIDC_METADATA_URL}")

    async def _fetch_jwks(self) -> None:
        """Holt JWKS (Public Keys) vom Provider"""
        if not self.meta:
            await self._fetch_meta()

        jwks_uri = self.meta.get("jwks_uri")
        if not jwks_uri:
            raise ValueError("jwks_uri not found in OIDC metadata")

        async with httpx.AsyncClient(timeout=10) as c:
            response = await c.get(jwks_uri)
            response.raise_for_status()
            self.jwks = response.json()
            logger.info(f"Fetched JWKS from {jwks_uri}")

        # Cache für 5 Minuten
        self.exp = time.time() + JWKS_CACHE_SECONDS

    async def _ensure_keys(self) -> None:
        """Stellt sicher dass JWKS aktuell ist"""
        if time.time() > self.exp or not self.jwks:
            await self._fetch_jwks()

    async def verify(self, token: str) -> Dict[str, Any]:
        """
        Verifiziert und dekodiert OIDC Token

        Args:
            token: JWT Token String

        Returns:
            Claims-Dictionary

        Raises:
            ValueError: Token ungültig oder Key nicht gefunden
            jwt.JWTError: Token-Validierung fehlgeschlagen
        """
        await self._ensure_keys()

        # Header lesen um KID zu kriegen
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        if not kid:
            raise ValueError("Token has no kid in header")

        # Key aus JWKS suchen
        key = next(
            (k for k in self.jwks.get("keys", []) if k.get("kid") == kid), None
        )

        if not key:
            # Key-Rotation? JWKS nochmal holen
            logger.warning(f"Key {kid} not found in cache, refreshing JWKS")
            await self._fetch_jwks()
            key = next(
                (k for k in self.jwks.get("keys", []) if k.get("kid") == kid), None
            )

            if not key:
                raise ValueError(f"JWKS key not found for kid: {kid}")

        # Token validieren
        claims = jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            audience=OIDC_AUDIENCE,
            issuer=OIDC_ISSUER,
            options={"verify_at_hash": False},
        )

        logger.debug(f"Token verified for sub: {claims.get('sub')}")
        return claims


# Global OIDC Instance
oidc = OIDC()


def extract_roles(claims: Dict[str, Any]) -> List[str]:
    """
    Extrahiert Rollen aus Token Claims
    
    Unterstützt mehrere Provider-Formate:
    - Azure AD: "roles" claim
    - Keycloak: "realm_access.roles"
    - Auth0: "https://app/roles" (custom namespace)
    - Generic: "groups"

    Args:
        claims: Token Claims

    Returns:
        Liste von Rollen-Strings
    """
    # Azure AD: roles claim
    if isinstance(claims.get("roles"), list):
        return [str(r) for r in claims["roles"]]

    # Keycloak: realm_access.roles
    ra = claims.get("realm_access", {})
    if isinstance(ra, dict) and isinstance(ra.get("roles"), list):
        return [str(r) for r in ra["roles"]]

    # Generic: groups
    if isinstance(claims.get("groups"), list):
        return [g.strip("/") for g in claims["groups"]]

    # Auth0: custom namespace
    appmd = claims.get("https://app/roles")
    if isinstance(appmd, list):
        return [str(r) for r in appmd]

    logger.warning(f"No roles found in token for sub: {claims.get('sub')}")
    return []


def extract_scopes(claims: Dict[str, Any]) -> List[str]:
    """
    Extrahiert Scopes aus Token Claims

    Args:
        claims: Token Claims

    Returns:
        Liste von Scope-Strings
    """
    # Azure AD: "scp" claim (space-separated)
    scp = claims.get("scp", "")
    if isinstance(scp, str) and scp:
        return scp.split()

    # Generic: "scope" claim (space-separated)
    scope = claims.get("scope", "")
    if isinstance(scope, str) and scope:
        return scope.split()

    return []

