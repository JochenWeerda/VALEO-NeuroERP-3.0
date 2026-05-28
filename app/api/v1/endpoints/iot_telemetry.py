"""
IoT / Telemetrie Endpoints — Wave 3 AP3
Waage, Silo, Lager sensor management and telemetry ingestion.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ....core.endpoint_gateways import register_telemetry_stores
from ....core.tenant import get_tenant_id
from ....core.iot_telemetry import (
    DeviceManifest,
    TelemetryReading,
    TelemetryAggregation,
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter(prefix="/iot", tags=["iot", "telemetry"])

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_DEVICES: dict[str, dict[str, Any]] = {}   # tenant_id → {device_id → manifest dict}
_READINGS: dict[str, dict[str, list[Any]]] = {}  # tenant_id → {device_id → [reading dicts]}

register_telemetry_stores(device_store=_DEVICES, reading_store=_READINGS)


def _device_store(tenant_id: str) -> dict[str, Any]:
    return _DEVICES.setdefault(tenant_id, {})


def _readings_store(tenant_id: str) -> dict[str, list[Any]]:
    return _READINGS.setdefault(tenant_id, {})


# ---------------------------------------------------------------------------
# Device management
# ---------------------------------------------------------------------------

@router.get("/devices", response_model=list[DeviceManifest], summary="Devices auflisten")
async def list_devices(tenant_id: str = Depends(get_tenant_id)):
    """List all registered IoT devices for the tenant."""
    store = _device_store(tenant_id)
    return list(store.values())


@router.post("/devices", response_model=DeviceManifest, status_code=201, summary="Device registrieren")
async def register_device(
    manifest: DeviceManifest,
    tenant_id: str = Depends(get_tenant_id),
):
    """Register a new IoT device."""
    store = _device_store(tenant_id)
    manifest = manifest.model_copy(update={"tenant_id": tenant_id})
    store[manifest.device_id] = manifest.model_dump()
    return manifest


# ---------------------------------------------------------------------------
# Telemetry readings
# ---------------------------------------------------------------------------

@router.get("/devices/{device_id}/readings", response_model=list[TelemetryReading], summary="Readings abrufen")
async def get_readings(
    device_id: str,
    limit: int = 100,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get the last N telemetry readings for a device."""
    store = _device_store(tenant_id)
    if device_id not in store:
        raise HTTPException(status_code=404, detail="Device not found")
    readings_store = _readings_store(tenant_id)
    readings = readings_store.get(device_id, [])
    return readings[-limit:]


@router.post("/devices/{device_id}/readings", response_model=TelemetryReading, status_code=201, summary="Reading ingest")
async def ingest_reading(
    device_id: str,
    reading: TelemetryReading,
    tenant_id: str = Depends(get_tenant_id),
):
    """Ingest a telemetry reading for a device."""
    store = _device_store(tenant_id)
    if device_id not in store:
        raise HTTPException(status_code=404, detail="Device not found")
    reading = reading.model_copy(update={"device_id": device_id, "tenant_id": tenant_id})
    readings_store = _readings_store(tenant_id)
    readings_store.setdefault(device_id, []).append(reading.model_dump())
    return reading


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

@router.get("/devices/{device_id}/aggregation", response_model=TelemetryAggregation, summary="Aggregation abrufen")
async def get_aggregation(
    device_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get pre-computed stats aggregation for a device."""
    store = _device_store(tenant_id)
    if device_id not in store:
        raise HTTPException(status_code=404, detail="Device not found")

    readings_store = _readings_store(tenant_id)
    readings = readings_store.get(device_id, [])

    now = datetime.now(timezone.utc).isoformat()

    if not readings:
        # Return empty aggregation
        return TelemetryAggregation(
            device_id=device_id,
            tenant_id=tenant_id,
            period_from=now,
            period_to=now,
            readings_count=0,
            avg_value=0.0,
            min_value=0.0,
            max_value=0.0,
            unit="",
        )

    values = [r["value"] for r in readings]
    unit = readings[-1].get("unit", "") if readings else ""
    timestamps = [r.get("timestamp", now) for r in readings]

    return TelemetryAggregation(
        device_id=device_id,
        tenant_id=tenant_id,
        period_from=min(timestamps),
        period_to=max(timestamps),
        readings_count=len(values),
        avg_value=sum(values) / len(values),
        min_value=min(values),
        max_value=max(values),
        unit=unit,
    )
