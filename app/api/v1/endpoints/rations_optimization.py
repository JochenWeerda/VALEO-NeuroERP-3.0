"""
Rationsoptimierung API Proxy

Proxies requests to the Rationsoptimierung microservice.
Erfordert RATIONS_OPTIMIZATION_URL und RATIONS_OPTIMIZATION_API_KEY in der Config.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agrar", "rations-optimization"])

# Timeout für Rationsoptimierungs-Service
RATIONS_TIMEOUT = 30.0


def get_rations_base_url() -> Optional[str]:
    """Rationsoptimierung-URL aus Config."""
    return getattr(settings, "RATIONS_OPTIMIZATION_URL", None) or None


def get_rations_api_key() -> str:
    """API-Key für Rationsoptimierung."""
    return getattr(settings, "RATIONS_OPTIMIZATION_API_KEY", "") or "dev-api-key-change-in-production"


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
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": get_rations_api_key(),
    }
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id

    async with httpx.AsyncClient(timeout=RATIONS_TIMEOUT) as client:
        try:
            if method.upper() == "GET":
                resp = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                resp = await client.post(
                    url, headers=headers, json=json_body or {}, params=params
                )
            else:
                raise HTTPException(status_code=405, detail="Methode nicht unterstützt")

            # Proxy response body and status
            try:
                body = resp.json()
            except Exception:
                body = {"detail": resp.text}
            return JSONResponse(status_code=resp.status_code, content=body)
        except httpx.ConnectError as e:
            logger.warning("Rationsoptimierung nicht erreichbar: %s", e)
            raise HTTPException(
                status_code=503,
                detail="Rationsoptimierungs-Service ist nicht erreichbar",
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Rationsoptimierungs-Service hat nicht rechtzeitig geantwortet",
            )


@router.get("/health")
async def rations_health():
    """Health-Check des Rationsoptimierungs-Services (ohne Auth)."""
    base_url = get_rations_base_url()
    if not base_url:
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "message": "Rationsoptimierung nicht konfiguriert",
                "configured": False,
            },
        )
    return await _proxy_request("GET", "/health")


@router.get("/feeds")
async def get_feeds(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    """Futtermittel abrufen."""
    params = dict(request.query_params)
    tenant_id = x_tenant_id or request.headers.get("x-tenant-id")
    return await _proxy_request("GET", "/api/v1/feeds", tenant_id=tenant_id, params=params)


@router.get("/feeds/{feed_id}")
async def get_feed(feed_id: str, x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")):
    """Einzelnes Futtermittel abrufen."""
    tenant_id = x_tenant_id
    return await _proxy_request("GET", f"/api/v1/feeds/{feed_id}", tenant_id=tenant_id)


@router.post("/feeds/validate")
async def validate_feeds(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    """Futtermittel validieren."""
    body = await request.json()
    return await _proxy_request(
        "POST", "/api/v1/feeds/validate", tenant_id=x_tenant_id, json_body=body
    )


@router.post("/requirements/calculate")
async def calculate_requirements(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    """Nährstoffbedarf aus Kuhprofil berechnen."""
    body = await request.json()
    return await _proxy_request(
        "POST", "/api/v1/requirements/calculate", tenant_id=x_tenant_id, json_body=body
    )


@router.post("/requirements/maintenance")
async def maintenance_requirements(
    body_weight_kg: float,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    """Erhaltungsbedarf berechnen."""
    return await _proxy_request(
        "POST",
        "/api/v1/requirements/maintenance",
        tenant_id=x_tenant_id,
        params={"body_weight_kg": body_weight_kg},
    )


@router.post("/optimize")
async def optimize(request: Request, x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")):
    """Ration optimieren (volle Anfrage)."""
    body = await request.json()
    return await _proxy_request(
        "POST", "/api/v1/optimize", tenant_id=x_tenant_id, json_body=body
    )


@router.post("/optimize/demo")
async def optimize_demo(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")):
    """Demo-Optimierung mit Beispieldaten."""
    return await _proxy_request(
        "POST", "/api/v1/optimize/demo", tenant_id=x_tenant_id
    )


@router.post("/optimize/from-profile")
async def optimize_from_profile(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    """Ration aus Kuhprofil optimieren."""
    body = await request.json()
    return await _proxy_request(
        "POST", "/api/v1/optimize/from-profile", tenant_id=x_tenant_id, json_body=body
    )
