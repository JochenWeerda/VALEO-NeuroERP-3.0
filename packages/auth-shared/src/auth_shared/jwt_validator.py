"""JWT token validation with JWKS support."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import jwt
import httpx

from .config import AuthConfig

logger = logging.getLogger(__name__)


class JWTValidator:
    """Validates JWT tokens against OIDC provider JWKS endpoint.

    Caches the JWKS keys and refreshes them periodically.
    """

    JWKS_CACHE_TTL = 3600  # 1 hour

    def __init__(self, config: AuthConfig) -> None:
        self._config = config
        self._jwks_client: Optional[jwt.PyJWKClient] = None
        self._jwks_last_fetch: float = 0.0

    def _get_jwks_client(self) -> Optional[jwt.PyJWKClient]:
        """Get or create JWKS client with caching."""
        if not self._config.OIDC_JWKS_URI:
            return None

        now = time.time()
        if self._jwks_client is None or (now - self._jwks_last_fetch) > self.JWKS_CACHE_TTL:
            try:
                self._jwks_client = jwt.PyJWKClient(
                    self._config.OIDC_JWKS_URI,
                    cache_keys=True,
                    lifespan=self.JWKS_CACHE_TTL,
                )
                self._jwks_last_fetch = now
                logger.info("JWKS client initialized from %s", self._config.OIDC_JWKS_URI)
            except Exception as exc:
                logger.error("Failed to initialize JWKS client: %s", exc)
                return None

        return self._jwks_client

    async def validate(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return its claims.

        Returns None if validation fails.
        """
        try:
            # Try JWKS-based validation first
            jwks_client = self._get_jwks_client()
            if jwks_client is not None:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                claims = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=self._config.JWT_ALGORITHMS,
                    audience=self._config.OIDC_AUDIENCE,
                    issuer=self._config.OIDC_ISSUER or None,
                    options={
                        "verify_exp": True,
                        "verify_aud": bool(self._config.OIDC_AUDIENCE),
                        "verify_iss": bool(self._config.OIDC_ISSUER),
                    },
                )
                return claims

            # Fallback: decode without signature verification (for dev/testing)
            # This should NOT be used in production
            logger.warning("No JWKS URI configured – decoding token without signature verification")
            claims = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": True},
                algorithms=self._config.JWT_ALGORITHMS + ["HS256"],
            )
            return claims

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as exc:
            logger.warning("Invalid token: %s", exc)
            return None
        except Exception as exc:
            logger.error("Unexpected error validating token: %s", exc)
            return None

