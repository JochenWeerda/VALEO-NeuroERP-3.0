"""Auth configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AuthConfig:
    """Configuration for JWT validation.

    All values are read from environment variables with sensible defaults
    for local development (where auth is bypassed via DEV_MODE).
    """

    # OIDC / JWT
    OIDC_ISSUER: str = os.getenv("OIDC_ISSUER", "")
    OIDC_JWKS_URI: str = os.getenv("OIDC_JWKS_URI", "")
    OIDC_AUDIENCE: str = os.getenv("OIDC_AUDIENCE", "valeo-neuro-erp")
    JWT_ALGORITHMS: List[str] = field(
        default_factory=lambda: os.getenv("JWT_ALGORITHMS", "RS256").split(",")
    )

    # Dev mode – NEVER enable in production!
    DEV_MODE: bool = os.getenv("AUTH_DEV_MODE", "true").lower() in ("true", "1", "yes")
    DEV_USER_ID: str = os.getenv("AUTH_DEV_USER_ID", "dev-user")
    DEV_TENANT_ID: str = os.getenv("AUTH_DEV_TENANT_ID", "default")
    DEV_ROLES: List[str] = field(
        default_factory=lambda: os.getenv("AUTH_DEV_ROLES", "admin").split(",")
    )

    # Public paths that never require auth
    PUBLIC_PATHS: List[str] = field(
        default_factory=lambda: [
            "/health",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/openapi.json",
            "/metrics",
        ]
    )

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "false").lower() in ("true", "1")
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

