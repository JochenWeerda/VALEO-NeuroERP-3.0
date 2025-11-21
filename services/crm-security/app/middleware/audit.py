"""
Audit logging middleware for comprehensive security monitoring.
"""

import json
import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.settings import settings


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive audit logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Extract request information
        request_id = str(uuid4())
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        user_id = self._get_user_id(request)

        # Log request
        await self._log_request(request, request_id, client_ip, user_agent, user_id)

        try:
            # Process request
            response = await call_next(request)

            # Calculate response time
            response_time = time.time() - start_time

            # Log response
            await self._log_response(
                request, response, request_id, client_ip, user_id, response_time
            )

            # Check for security violations
            await self._check_security_violations(request, response, client_ip, user_id)

            return response

        except Exception as exc:
            # Log error
            response_time = time.time() - start_time
            await self._log_error(
                request, exc, request_id, client_ip, user_id, response_time
            )

            # Return error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id}
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client host
        return request.client.host if request.client else "unknown"

    def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request."""
        # Try to get from JWT token or session
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # In a real implementation, decode JWT to get user ID
            return "authenticated_user"

        return "anonymous"

    async def _log_request(
        self, request: Request, request_id: str, client_ip: str,
        user_agent: str, user_id: str
    ):
        """Log incoming request."""
        audit_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "event_type": "api_request",
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
            "tenant_id": settings.DEFAULT_TENANT_ID,
        }

        # Remove sensitive headers
        sensitive_headers = ["authorization", "x-api-key", "cookie"]
        for header in sensitive_headers:
            if header in audit_entry["headers"]:
                audit_entry["headers"][header] = "***REDACTED***"

        await self._store_audit_log(audit_entry)

    async def _log_response(
        self, request: Request, response: Response, request_id: str,
        client_ip: str, user_id: str, response_time: float
    ):
        """Log response."""
        audit_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "event_type": "api_response",
            "client_ip": client_ip,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "response_time": response_time,
            "tenant_id": settings.DEFAULT_TENANT_ID,
        }

        await self._store_audit_log(audit_entry)

    async def _log_error(
        self, request: Request, exc: Exception, request_id: str,
        client_ip: str, user_id: str, response_time: float
    ):
        """Log error."""
        audit_entry = {
            "timestamp": time.time(),
            "request_id": request_id,
            "event_type": "api_error",
            "client_ip": client_ip,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "response_time": response_time,
            "tenant_id": settings.DEFAULT_TENANT_ID,
        }

        await self._store_audit_log(audit_entry)

    async def _check_security_violations(
        self, request: Request, response: Response, client_ip: str, user_id: str
    ):
        """Check for security violations and log alerts."""
        violations = []

        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            violations.append("suspicious_request_pattern")

        if self._is_rate_limit_exceeded(client_ip):
            violations.append("rate_limit_exceeded")

        if self._is_unauthorized_access_attempt(request, response):
            violations.append("unauthorized_access_attempt")

        # Log violations
        for violation in violations:
            await self._log_security_alert(violation, request, client_ip, user_id)

    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request matches suspicious patterns."""
        # Check for SQL injection patterns
        sql_patterns = ["union select", "1=1", "or 1=1", "drop table", "script"]
        query_string = str(request.url).lower() + str(request.query_params).lower()

        return any(pattern in query_string for pattern in sql_patterns)

    def _is_rate_limit_exceeded(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limits."""
        # In a real implementation, check Redis or database for rate limiting
        return False

    def _is_unauthorized_access_attempt(self, request: Request, response: Response) -> bool:
        """Check for unauthorized access attempts."""
        return response.status_code in [401, 403]

    async def _log_security_alert(
        self, violation_type: str, request: Request, client_ip: str, user_id: str
    ):
        """Log security alert."""
        alert_entry = {
            "timestamp": time.time(),
            "event_type": "security_alert",
            "violation_type": violation_type,
            "client_ip": client_ip,
            "user_id": user_id,
            "method": request.method,
            "url": str(request.url),
            "severity": self._get_violation_severity(violation_type),
            "tenant_id": settings.DEFAULT_TENANT_ID,
        }

        await self._store_audit_log(alert_entry)

        # Send alert notifications if critical
        if alert_entry["severity"] == "critical":
            await self._send_security_notification(alert_entry)

    def _get_violation_severity(self, violation_type: str) -> str:
        """Get severity level for violation type."""
        severity_map = {
            "suspicious_request_pattern": "high",
            "rate_limit_exceeded": "medium",
            "unauthorized_access_attempt": "high",
        }
        return severity_map.get(violation_type, "low")

    async def _send_security_notification(self, alert: dict):
        """Send security notification to administrators."""
        # In a real implementation, send email/SMS/push notifications
        print(f"SECURITY ALERT: {alert}")

    async def _store_audit_log(self, entry: dict):
        """Store audit log entry."""
        # In a real implementation, store in Elasticsearch/PostgreSQL
        # For now, just print to console
        print(f"AUDIT: {json.dumps(entry, default=str)}")