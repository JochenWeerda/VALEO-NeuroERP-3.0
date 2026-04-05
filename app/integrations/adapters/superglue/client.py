"""Transport-only Superglue client guarded by the central outbound policy."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import httpx

from app.core.config import settings
from app.core.outbound_security import validate_outbound_http_target_against_allowlists
from app.integrations.services.integration_circuit_breaker import IntegrationCircuitBreaker


class SuperglueClientConfigError(ValueError):
    """Raised when Superglue transport settings are incomplete."""


class SuperglueClientRequestError(RuntimeError):
    """Raised when a Superglue request cannot be completed successfully."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SuperglueClient:
    """Thin transport adapter for REST and GraphQL calls to Superglue."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        graphql_url: str | None = None,
        rest_url: str | None = None,
        auth_token: str | None = None,
        timeout_seconds: float | None = None,
        retry_attempts: int = 1,
        breaker: IntegrationCircuitBreaker | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url or settings.SUPERGLUE_BASE_URL
        self.graphql_url = graphql_url or settings.SUPERGLUE_GRAPHQL_URL
        self.rest_url = rest_url or settings.SUPERGLUE_REST_URL
        self.auth_token = auth_token if auth_token is not None else settings.SUPERGLUE_AUTH_TOKEN
        self.timeout_seconds = timeout_seconds or settings.SUPERGLUE_TIMEOUT_SECONDS
        self.retry_attempts = max(0, retry_attempts)
        self.breaker = breaker or IntegrationCircuitBreaker(name="superglue")
        self.transport = transport

    def execute_graphql(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        return self.request("POST", "", mode="graphql", json=payload, headers=headers)

    def request(
        self,
        method: str,
        path: str,
        *,
        mode: str = "rest",
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        allow_statuses: Iterable[int] | None = None,
    ) -> dict[str, Any]:
        if not self.breaker.allow_request():
            raise SuperglueClientRequestError("Superglue transport is temporarily blocked by the circuit breaker")

        target_url = self._resolve_target_url(mode=mode, path=path)
        request_headers = self._build_headers(headers)
        last_error: Exception | None = None
        allowed_status_codes = set(allow_statuses or [])

        for _attempt in range(self.retry_attempts + 1):
            try:
                with httpx.Client(
                    timeout=self.timeout_seconds,
                    headers=request_headers,
                    transport=self.transport,
                ) as client:
                    response = client.request(method.upper(), target_url, json=json, params=params)
                if response.status_code in allowed_status_codes:
                    self.breaker.record_success()
                    return response.json() if response.content else {}
                if response.status_code >= 500:
                    raise SuperglueClientRequestError(
                        f"Superglue request failed with status {response.status_code}",
                        status_code=response.status_code,
                    )
                response.raise_for_status()
                self.breaker.record_success()
                return response.json() if response.content else {}
            except (httpx.HTTPError, SuperglueClientRequestError) as exc:
                if isinstance(exc, httpx.HTTPStatusError):
                    last_error = SuperglueClientRequestError(
                        f"Superglue request failed with status {exc.response.status_code}",
                        status_code=exc.response.status_code,
                    )
                else:
                    last_error = exc
                self.breaker.record_failure()

        raise SuperglueClientRequestError(str(last_error) if last_error else "Superglue request failed")

    def _resolve_target_url(self, *, mode: str, path: str) -> str:
        if mode == "graphql":
            base = self.graphql_url or self._join_base_path(self.base_url, "/graphql")
        else:
            base = self.rest_url or self.base_url
        if not base:
            raise SuperglueClientConfigError("SUPERGLUE_BASE_URL or mode-specific Superglue URL must be configured")
        return validate_outbound_http_target_against_allowlists(
            self._join_base_path(base, path),
            allowed_hosts=self._effective_allowed_hosts(),
            allowed_domains=self._effective_allowed_domains(),
            allow_loopback_hosts=self._allow_loopback_dev_egress(),
        )

    def _build_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        merged_headers: dict[str, str] = {"Accept": "application/json"}
        if self.auth_token:
            merged_headers["Authorization"] = f"Bearer {self.auth_token}"
        if headers:
            merged_headers.update(headers)
        return merged_headers

    @staticmethod
    def _join_base_path(base_url: str | None, path: str) -> str | None:
        if not base_url:
            return None
        normalized_base = base_url.rstrip("/")
        normalized_path = path.strip()
        if not normalized_path:
            return normalized_base
        if normalized_path.startswith("http://") or normalized_path.startswith("https://"):
            return normalized_path
        return f"{normalized_base}/{normalized_path.lstrip('/')}"

    @staticmethod
    def _effective_allowed_hosts() -> list[str]:
        return [
            *settings.OUTBOUND_HTTP_ALLOWED_HOSTS,
            *settings.SUPERGLUE_ALLOWED_HOSTS,
        ]

    @staticmethod
    def _effective_allowed_domains() -> list[str]:
        return [
            *settings.OUTBOUND_HTTP_ALLOWED_DOMAINS,
            *settings.SUPERGLUE_ALLOWED_DOMAINS,
        ]

    @staticmethod
    def _allow_loopback_dev_egress() -> bool:
        return bool(settings.DEBUG and settings.SUPERGLUE_ALLOW_LOOPBACK_DEV_EGRESS)
