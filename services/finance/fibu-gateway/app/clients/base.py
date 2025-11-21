"""Gemeinsame HTTP-Client-Basis."""

from __future__ import annotations

from typing import Any, Dict

import httpx

from app.config import settings


class GatewayServiceError(RuntimeError):
    """Vereinheitlichte Fehlerrepräsentation für Downstream-Aufrufe."""

    def __init__(self, service: str, status_code: int, detail: Any) -> None:
        super().__init__(f"{service} responded with {status_code}: {detail}")
        self.service = service
        self.status_code = status_code
        self.detail = detail


class BaseServiceClient:
    """Dünner Wrapper um httpx.Client für Downstream-Services."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._service_name = self.__class__.__name__

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Dict[str, Any] | None = None,
        json: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
        timeout: float | None = None,
        parse_json: bool = True,
    ) -> Any:
        url = f"{self._base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=timeout or settings.HTTP_TIMEOUT_SECONDS) as client:
            try:
                response = await client.request(method, url, params=params, json=json, headers=headers)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = self._extract_error_detail(exc.response)
                raise GatewayServiceError(self._service_name, exc.response.status_code, detail) from exc
            except httpx.RequestError as exc:
                raise GatewayServiceError(self._service_name, 0, str(exc)) from exc

            if not parse_json:
                return response
            return self._normalize_payload(response.json())

    def _normalize_payload(self, payload: Any) -> Any:
        if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], (dict, list)):
            return payload["data"]
        return payload

    def _extract_items(self, payload: Any) -> list[Any]:
        if isinstance(payload, dict) and "items" in payload and isinstance(payload["items"], list):
            return payload["items"]
        if isinstance(payload, list):
            return payload
        return [payload]

    @staticmethod
    def _extract_error_detail(response: httpx.Response | None) -> Any:
        if response is None:
            return "Unknown error"
        try:
            data = response.json()
            if isinstance(data, dict) and "detail" in data:
                return data["detail"]
            return data
        except ValueError:
            return response.text

