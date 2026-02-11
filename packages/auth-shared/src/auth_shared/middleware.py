"""FastAPI Auth Middleware – validates tokens at the middleware level."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Callable, Dict, List

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import AuthConfig
from .jwt_validator import JWTValidator

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces authentication on all non-public endpoints.

    In DEV_MODE, all requests are allowed through.
    In production, a valid Bearer token is required.
    """

    def __init__(self, app, config: AuthConfig | None = None) -> None:
        super().__init__(app)
        self._config = config or AuthConfig()
        self._validator = JWTValidator(self._config)
        self._rate_limits: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Always allow public paths
        if self._is_public_path(path):
            return await call_next(request)

        # Allow OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Dev mode – allow everything
        if self._config.DEV_MODE:
            return await call_next(request)

        # Check for Bearer token
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header[7:]
        claims = await self._validator.validate(token)

        if claims is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Rate limiting (if enabled)
        if self._config.RATE_LIMIT_ENABLED:
            client_ip = self._get_client_ip(request)
            if self._is_rate_limited(client_ip):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded"},
                )

        # Proceed with request
        response = await call_next(request)
        return response

    def _is_public_path(self, path: str) -> bool:
        """Check if the path is in the public paths list."""
        for public_path in self._config.PUBLIC_PATHS:
            if path == public_path or path.startswith(public_path + "/"):
                return True
        return False

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Simple sliding window rate limiter."""
        now = time.time()
        window_start = now - 60  # 1-minute window

        # Clean old entries
        self._rate_limits[client_ip] = [
            ts for ts in self._rate_limits[client_ip] if ts > window_start
        ]

        if len(self._rate_limits[client_ip]) >= self._config.RATE_LIMIT_PER_MINUTE:
            return True

        self._rate_limits[client_ip].append(now)
        return False

