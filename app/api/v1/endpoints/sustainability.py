"""
Sustainability API endpoints.

Runtime-only integrations for external sustainability and compliance sources.
No persistence is performed in local DB.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.integrations.bvl_psm_client import BVLPSMClient


router = APIRouter(prefix="/sustainability", tags=["Sustainability"])
bvl_client = BVLPSMClient()


class EmissionsEstimateRequest(BaseModel):
    activity_id: str = Field(..., description="Climatiq activity id")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Climatiq parameter object")
    data_version: Optional[str] = Field(None, description="Optional Climatiq data version")


@router.get("/providers/status")
async def get_provider_status() -> dict[str, Any]:
    """Return external provider availability and configuration status."""
    return {
        "providers": {
            "bvl_psm": {
                "configured": True,
                "base_url": bvl_client.base_url,
                "cache_ttl_seconds": bvl_client.ttl_seconds,
            },
            "climatiq": {
                "configured": bool(os.getenv("CLIMATIQ_API_KEY")),
                "base_url": os.getenv("CLIMATIQ_API_BASE_URL", "https://api.climatiq.io/data/v1"),
            },
            "faostat": {
                "configured": True,
                "base_url": os.getenv("FAOSTAT_API_BASE_URL", "https://fenixservices.fao.org/faostat/api/v1/en"),
            },
        }
    }


@router.get("/psm/{zulassungsnummer}")
async def get_psm_runtime(
    zulassungsnummer: str,
    tenant_id: str = Query("system", description="Tenant context for mapping"),
) -> dict[str, Any]:
    """Fetch a single PSM entry live from BVL by approval number."""
    try:
        item = await bvl_client.get_mittel_by_kennr(zulassungsnummer)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"BVL PSM API not reachable: {exc}",
        ) from exc

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PSM with Zulassungsnummer {zulassungsnummer} not found in BVL source.",
        )

    return {
        "source": "bvl_psm_api",
        "tenant_id": tenant_id,
        "zulassungsnummer": zulassungsnummer,
        "item": item,
    }


@router.post("/emissions/estimate")
async def estimate_emissions(payload: EmissionsEstimateRequest) -> dict[str, Any]:
    """
    Estimate CO2 emissions via Climatiq.

    Requires environment variable CLIMATIQ_API_KEY.
    """
    api_key = os.getenv("CLIMATIQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Climatiq not configured (missing CLIMATIQ_API_KEY).",
        )

    base_url = os.getenv("CLIMATIQ_API_BASE_URL", "https://api.climatiq.io/data/v1").rstrip("/")
    url = f"{base_url}/estimate"
    request_body: dict[str, Any] = {
        "emission_factor": {"activity_id": payload.activity_id},
        "parameters": payload.parameters,
    }
    if payload.data_version:
        request_body["emission_factor"]["data_version"] = payload.data_version

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            if resp.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Climatiq error {resp.status_code}: {resp.text}",
                )
            data = resp.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Climatiq API not reachable: {exc}",
        ) from exc

    return {
        "source": "climatiq",
        "request": request_body,
        "result": data,
    }


@router.get("/nutrients/crop")
async def get_crop_nutrients(
    dataset: str = Query(
        "inputs/fertilizersnutrientelements",
        description="FAOSTAT dataset path relative to base URL",
    ),
    item_code: Optional[str] = Query(None, description="FAOSTAT item code"),
    area_code: Optional[str] = Query(None, description="FAOSTAT area code"),
    year: Optional[int] = Query(None, description="Year filter"),
    limit: int = Query(50, ge=1, le=500),
) -> dict[str, Any]:
    """
    Fetch crop nutrient-related records from FAOSTAT runtime API.

    The endpoint forwards to FAOSTAT and returns the raw payload
    to keep source fidelity and avoid local data duplication.
    """
    base_url = os.getenv("FAOSTAT_API_BASE_URL", "https://fenixservices.fao.org/faostat/api/v1/en").rstrip("/")
    rel_dataset = dataset.strip("/")
    url = f"{base_url}/{rel_dataset}"

    params: dict[str, Any] = {"page_size": limit}
    if item_code:
        params["item_code"] = item_code
    if area_code:
        params["area_code"] = area_code
    if year is not None:
        params["year"] = year

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            if resp.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"FAOSTAT error {resp.status_code}: {resp.text}",
                )
            data = resp.json()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"FAOSTAT API not reachable: {exc}",
        ) from exc

    return {
        "source": "faostat",
        "dataset": rel_dataset,
        "params": params,
        "result": data,
    }
