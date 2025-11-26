"""
Security middleware for encryption, access control, and threat protection.
"""

import hashlib
import hmac
import json
import re
from typing import Callable, Dict, List, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.settings import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security controls and threat protection."""

    def __init__(self, app):
        super().__init__(app)
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: set = set()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # Pre-request security checks
            await self._check_ip_blocklist(request)
            await self._check_rate_limits(request)
            await self._validate_request_signature(request)
            await self._check_sql_injection(request)
            await self._check_xss_attempts(request)

            # Process request
            response = await call_next(request)

            # Post-request security measures
            response = await self._add_security_headers(response)
            await self._log_security_metrics(request, response)

            return response

        except HTTPException:
            raise
        except Exception as exc:
            # Log security incident
            await self._log_security_incident(request, str(exc))
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Security processing error"}
            )

    async def _check_ip_blocklist(self, request: Request):
        """Check if client IP is blocked."""
        client_ip = self._get_client_ip(request)

        if client_ip in self.blocked_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: IP address blocked"
            )

        # Check against configured blacklist
        if client_ip in settings.THREAT_DETECTION_IP_BLACKLIST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: IP address blacklisted"
            )

    async def _check_rate_limits(self, request: Request):
        """Check rate limiting."""
        if not settings.THREAT_DETECTION_ENABLED:
            return

        client_ip = self._get_client_ip(request)
        current_time = request.app.state.request_time if hasattr(request.app.state, 'request_time') else 0

        # Clean old entries
        cutoff_time = current_time - settings.THREAT_DETECTION_RATE_LIMIT_WINDOW
        if client_ip in self.rate_limits:
            self.rate_limits[client_ip] = [
                ts for ts in self.rate_limits[client_ip] if ts > cutoff_time
            ]

        # Check rate limit
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = []

        self.rate_limits[client_ip].append(current_time)

        if len(self.rate_limits[client_ip]) > settings.THREAT_DETECTION_RATE_LIMIT_REQUESTS:
            # Block IP temporarily
            self.blocked_ips.add(client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

    async def _validate_request_signature(self, request: Request):
        """Validate request signature for API authentication."""
        # Skip for health checks and public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return

        # Check for API key in header
        api_key = request.headers.get("x-api-key")
        if api_key:
            # Validate API key (in real implementation, check against database)
            if not self._validate_api_key(api_key):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            return

        # Check for JWT token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # Validate JWT token
            if not self._validate_jwt_token(auth_header[7:]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

    async def _check_sql_injection(self, request: Request):
        """Check for SQL injection attempts."""
        # Check query parameters
        for key, value in request.query_params.items():
            if self._contains_sql_injection(value):
                await self._log_security_incident(request, f"SQL injection attempt in query param: {key}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request parameters"
                )

        # Check request body for JSON requests
        if request.method in ["POST", "PUT", "PATCH"] and request.headers.get("content-type") == "application/json":
            try:
                body = await request.json()
                if self._contains_sql_injection_in_dict(body):
                    await self._log_security_incident(request, "SQL injection attempt in request body")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid request data"
                    )
            except:
                pass  # Skip if body can't be parsed

    async def _check_xss_attempts(self, request: Request):
        """Check for XSS attempts."""
        # Check query parameters and headers
        for key, value in request.query_params.items():
            if self._contains_xss_patterns(value):
                await self._log_security_incident(request, f"XSS attempt in query param: {key}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request parameters"
                )

    async def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubdomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Add request ID for tracking
        import uuid
        response.headers["X-Request-ID"] = str(uuid.uuid4())

        return response

    async def _log_security_metrics(self, request: Request, response: Response):
        """Log security-related metrics."""
        # In a real implementation, send metrics to monitoring system
        pass

    async def _log_security_incident(self, request: Request, details: str):
        """Log security incident."""
        incident = {
            "timestamp": request.app.state.request_time if hasattr(request.app.state, 'request_time') else 0,
            "client_ip": self._get_client_ip(request),
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent", ""),
            "details": details,
            "severity": "medium"
        }

        # In a real implementation, store in database and send alerts
        print(f"SECURITY INCIDENT: {json.dumps(incident)}")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key."""
        # In a real implementation, check against database
        return api_key.startswith("sk_") and len(api_key) > 20

    def _validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token."""
        # In a real implementation, decode and verify JWT
        return len(token) > 20  # Basic length check

    def _contains_sql_injection(self, value: str) -> bool:
        """Check if string contains SQL injection patterns."""
        sql_patterns = [
            r"(\bunion\b|\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b|\bcreate\b|\balter\b)",
            r"(\bor\b|\band\b)\s+\d+\s*=\s*\d+",
            r"(\bscript\b|\bjavascript\b|\bonload\b|\bonerror\b)",
            r"(<script|javascript:|vbscript:|data:)",
        ]

        value_lower = value.lower()
        return any(re.search(pattern, value_lower, re.IGNORECASE) for pattern in sql_patterns)

    def _contains_sql_injection_in_dict(self, data: dict) -> bool:
        """Check dictionary for SQL injection patterns."""
        for key, value in data.items():
            if isinstance(value, str) and self._contains_sql_injection(value):
                return True
            elif isinstance(value, dict):
                if self._contains_sql_injection_in_dict(value):
                    return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and self._contains_sql_injection(item):
                        return True
                    elif isinstance(item, dict) and self._contains_sql_injection_in_dict(item):
                        return True
        return False

    def _contains_xss_patterns(self, value: str) -> bool:
        """Check if string contains XSS patterns."""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
        ]

        return any(re.search(pattern, value, re.IGNORECASE | re.DOTALL) for pattern in xss_patterns)