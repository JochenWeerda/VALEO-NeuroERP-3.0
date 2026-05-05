"""HTTP-Proxy fuer den externen Rationsoptimierungs-Microservice.

Enthaelt ``get_rations_base_url`` (oeffentliche Testschnittstelle),
``_rations_api_key`` und ``_proxy_request`` (async) samt
``RATIONS_TIMEOUT``.

Extrahiert 2026-04-23 aus ``app.api.v1.endpoints.rations_optimization``
ohne Verhaltensaenderung (Schritt 1c der Refactoring-Roadmap).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

RATIONS_TIMEOUT: float = 30.0


def get_rations_base_url() -> Optional[str]:
    """Liefert die Proxy-URL zum externen Rationsoptimierungs-Microservice.

    Oeffentliche Schnittstelle (wave74-Kontrakt): Tests duerfen diese
    Funktion mit ``unittest.mock.patch.object(...)`` ueberschreiben, um
    das Verhalten ohne konfigurierten externen Proxy zu pruefen.
    """
    return getattr(settings, "RATIONS_OPTIMIZATION_URL", None) or None


def _rations_api_key() -> str:
    return (
        getattr(settings, "RATIONS_OPTIMIZATION_API_KEY", "")
        or "dev-api-key-change-in-production"
    )


def _tenant_from_request(request: Request, x_tenant_id: Optional[str]) -> Optional[str]:
    if x_tenant_id:
        return x_tenant_id
    return (
        request.headers.get("x-tenant-id")
        or request.headers.get("X-Tenant-Id")
        or request.headers.get("X-Tenant-ID")
    )


async def _proxy_request(
    method: str,
    path: str,
    tenant_id: Optional[str] = None,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    base_url = get_rations_base_url()
    if not base_url:
        raise HTTPException(
            status_code=503,
            detail="Rationsoptimierungs-Service ist nicht konfiguriert (RATIONS_OPTIMIZATION_URL fehlt)",
        )
    url = f"{base_url.rstrip('/')}{path}"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "X-API-Key": _rations_api_key(),
    }
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id

    async with httpx.AsyncClient(timeout=RATIONS_TIMEOUT) as client:
        try:
            if method.upper() == "GET":
                resp = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                resp = await client.post(url, headers=headers, json=json_body or {}, params=params)
            else:
                raise HTTPException(status_code=405, detail="Methode nicht unterstützt")
            try:
                body = resp.json()
            except Exception:
                body = {"detail": resp.text}
            return JSONResponse(status_code=resp.status_code, content=body)
        except httpx.ConnectError as exc:
            logger.warning("Rationsoptimierung nicht erreichbar: %s", exc)
            raise HTTPException(status_code=503, detail="Rationsoptimierungs-Service ist nicht erreichbar")
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Rationsoptimierungs-Service hat nicht rechtzeitig geantwortet",
            )
