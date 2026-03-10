"""
Sustainability API endpoints.

Runtime-only integrations for external sustainability and compliance sources.
ESG Report (Gap 046): Aggregierte CO2/NÃ¤hrstoff-Berichte fÃ¼r Agrarkonzerne.
"""

from __future__ import annotations

import csv
import io
import os
from collections import defaultdict
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.documents.router_helpers import get_repository, list_from_store
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


# ---------------------------------------------------------------------------
# ESG Report (Gap 046: Nachhaltigkeit/CO2 Reporting fÃ¼r Agrarkonzerne)
# ---------------------------------------------------------------------------


def _compute_esg_report(*, year: int, customer_id: Optional[str], db: Session) -> dict[str, Any]:
    """Aggregiert N, P2O5, CO2e aus Lieferscheinen fÃ¼r ESG-Bericht."""
    repo = get_repository(db)
    listed = list_from_store("sales_delivery", skip=0, limit=10_000, repo=repo)
    deliveries = listed.get("data", [])

    filtered: list[dict[str, Any]] = []
    for delivery in deliveries:
        date_str = str(delivery.get("date") or "")
        if not date_str.startswith(f"{year}-"):
            continue
        if customer_id and str(delivery.get("customerId") or "") != customer_id:
            continue
        filtered.append(delivery)

    by_month: dict[str, dict[str, float]] = defaultdict(
        lambda: {"deliveries": 0.0, "n_kg": 0.0, "p2o5_kg": 0.0, "co2e_kg": 0.0}
    )
    total_n = 0.0
    total_p2o5 = 0.0
    total_co2e = 0.0

    for delivery in filtered:
        month = str(delivery.get("date", ""))[:7]
        d_n = float(delivery.get("totalNutrientNKg") or 0.0)
        d_p2o5 = float(delivery.get("totalNutrientP2o5Kg") or 0.0)
        d_co2e = float(delivery.get("totalCo2eKg") or 0.0)

        by_month[month]["deliveries"] += 1
        by_month[month]["n_kg"] += d_n
        by_month[month]["p2o5_kg"] += d_p2o5
        by_month[month]["co2e_kg"] += d_co2e

        total_n += d_n
        total_p2o5 += d_p2o5
        total_co2e += d_co2e

    return {
        "year": year,
        "customerId": customer_id,
        "deliveryCount": len(filtered),
        "totalNutrientNKg": round(total_n, 3),
        "totalNutrientP2o5Kg": round(total_p2o5, 3),
        "totalCo2eKg": round(total_co2e, 3),
        "byMonth": {
            k: {
                "deliveries": int(v["deliveries"]),
                "n_kg": round(v["n_kg"], 3),
                "p2o5_kg": round(v["p2o5_kg"], 3),
                "co2e_kg": round(v["co2e_kg"], 3),
            }
            for k, v in sorted(by_month.items())
        },
    }


@router.get("/esg-report")
async def get_esg_report(
    year: int = Query(..., ge=2020, le=2030),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    ESG-Bericht: Aggregierte NÃ¤hrstoff- und CO2-Daten aus Lieferscheinen (Gap 046).
    ESG-Berichte in <1 Tag erzeugbar.
    """
    return _compute_esg_report(year=year, customer_id=customer_id, db=db)


@router.get("/esg-report/export.csv")
async def export_esg_report_csv(
    year: int = Query(..., ge=2020, le=2030),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """ESG-Bericht als CSV exportieren."""
    data = _compute_esg_report(year=year, customer_id=customer_id, db=db)

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["ESG-Bericht", str(year)])
    writer.writerow([])
    writer.writerow(["Summe N (kg)", f"{float(data['totalNutrientNKg']):.3f}"])
    writer.writerow(["Summe P2O5 (kg)", f"{float(data['totalNutrientP2o5Kg']):.3f}"])
    writer.writerow(["Summe CO2e (kg)", f"{float(data['totalCo2eKg']):.3f}"])
    writer.writerow([])
    writer.writerow(["Monat", "Lieferscheine", "N (kg)", "P2O5 (kg)", "CO2e (kg)"])
    for month, row in data.get("byMonth", {}).items():
        writer.writerow([
            month,
            row.get("deliveries", 0),
            f"{float(row.get('n_kg', 0)):.3f}",
            f"{float(row.get('p2o5_kg', 0)):.3f}",
            f"{float(row.get('co2e_kg', 0)):.3f}",
        ])

    filename = f"esg-report-{year}.csv"
    if customer_id:
        filename = f"esg-report-{year}-{customer_id}.csv"

    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/esg-report/export.pdf")
async def export_esg_report_pdf(
    year: int = Query(..., ge=2020, le=2030),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """ESG-Bericht als PDF exportieren."""
    data = _compute_esg_report(year=year, customer_id=customer_id, db=db)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica", 16)
    c.drawString(20 * mm, 270 * mm, f"ESG-Bericht {year}")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, 255 * mm, f"N gesamt: {float(data['totalNutrientNKg']):.3f} kg")
    c.drawString(20 * mm, 245 * mm, f"P2O5 gesamt: {float(data['totalNutrientP2o5Kg']):.3f} kg")
    c.drawString(20 * mm, 235 * mm, f"CO2e gesamt: {float(data['totalCo2eKg']):.3f} kg")
    c.drawString(20 * mm, 220 * mm, "Monat | Lieferscheine | N (kg) | P2O5 (kg) | CO2e (kg)")
    y = 205 * mm
    for month, row in data.get("byMonth", {}).items():
        c.drawString(20 * mm, y, f"{month} | {row.get('deliveries', 0)} | {row.get('n_kg', 0):.3f} | {row.get('p2o5_kg', 0):.3f} | {row.get('co2e_kg', 0):.3f}")
        y -= 6 * mm
    c.save()
    buf.seek(0)

    filename = f"esg-report-{year}.pdf"
    if customer_id:
        filename = f"esg-report-{year}-{customer_id}.pdf"

    return StreamingResponse(
