"""
IoT-/Telemetrie-Modelle — Wave 3 AP3
Waage (weighing), Silo (grain storage), Lager (warehouse inventory sensors)
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class DeviceType(str, Enum):
    weighbridge = "weighbridge"
    silo_sensor = "silo_sensor"
    warehouse_sensor = "warehouse_sensor"
    moisture_sensor = "moisture_sensor"
    temperature_sensor = "temperature_sensor"


class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    error = "error"
    calibrating = "calibrating"


class TelemetryReading(BaseModel):
    device_id: str
    device_type: DeviceType
    tenant_id: str
    timestamp: str
    value: float
    unit: str
    quality: Literal["good", "uncertain", "bad"] = "good"
    schema_version: int = 1


class DeviceManifest(BaseModel):
    device_id: str
    device_type: DeviceType
    tenant_id: str
    location: str
    status: DeviceStatus
    calibration_due: str | None = None
    process_context: str | None = None  # e.g. "harvest_acceptance", "silo_management"
    schema_version: int = 1


class TelemetryAggregation(BaseModel):
    device_id: str
    tenant_id: str
    period_from: str
    period_to: str
    readings_count: int
    avg_value: float
    min_value: float
    max_value: float
    unit: str
    schema_version: int = 1
