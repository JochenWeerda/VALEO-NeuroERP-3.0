"""WM-AGRI-PLC-005 — PLC/OPC-UA Stub-Endpoint.

Empfaengt Sensor-Werte von speicherprogrammierbaren Steuerungen (SPS) und OPC-UA-Servern
(Fuellstandsensoren, Temperaturfuehler, Foerderbandstatus) und delegiert an AgriPlcService.
Kein echtes OPC-UA SDK in diesem Stub — Payload wird per REST angeliefert (z.B. vom IoT-Gateway).
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────


class PlcDataPoint(BaseModel):
    """Einzelner Messwert von einer SPS/OPC-UA-Quelle."""

    node_id: str = Field(..., description="OPC-UA NodeId oder PLC-Tag, z.B. 'ns=2;s=Silo1.Fuellstand'")
    tag: str = Field(..., description="Lesbarer Tag-Name, z.B. 'silo1.level_pct'")
    value: float
    unit: Optional[str] = None
    quality: Literal["good", "uncertain", "bad"] = "good"
    source_timestamp: Optional[str] = None


class PlcIngestIn(BaseModel):
    """Batch-Payload: ein Geraet sendet mehrere Datenpunkte in einem Aufruf."""

    device_id: str = Field(..., description="PLC/SCADA-Geraete-ID, eindeutig je Tenant")
    warehouse_id: Optional[str] = None
    data_points: list[PlcDataPoint]
    sequence: Optional[int] = None


class PlcSiloLevelIn(BaseModel):
    """Vereinfachter Endpunkt: Fuellstand einer Silozelle direkt updaten."""

    warehouse_id: str
    cell_id: str
    level_pct: float = Field(..., ge=0, le=100)
    weight_kg: Optional[float] = None
    temperature_celsius: Optional[float] = None
    device_id: Optional[str] = None


class PlcDeviceStatusIn(BaseModel):
    """Heartbeat / Statusmeldung vom Feldgeraet."""

    device_id: str
    warehouse_id: Optional[str] = None
    status: Literal["online", "offline", "error", "maintenance"]
    firmware_version: Optional[str] = None
    uptime_seconds: Optional[int] = None


# ── Service (Stub-Implementierung) ────────────────────────────────────────────


class AgriPlcService:
    """Stub-Service: verarbeitet PLC-Daten und schreibt sie in Silozellen-Metriken.

    Produktions-Erweiterung: OPC-UA-SDK (asyncua) anbinden, Polling-Loop in NATS publizieren.
    """

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def ingest_data_points(self, payload: PlcIngestIn) -> dict[str, Any]:
        """Verarbeitet einen Batch von Datenpunkten.

        Stub: loggt Werte, gibt Zusammenfassung zurueck.
        Erweiterung: Tag-Mapping-Tabelle pflegen, Werte auf silo_cells schreiben.
        """
        processed = 0
        skipped = 0
        for dp in payload.data_points:
            if dp.quality == "bad":
                logger.warning(
                    "PLC bad quality: device=%s tag=%s val=%s",
                    payload.device_id,
                    dp.tag,
                    dp.value,
                )
                skipped += 1
                continue
            logger.info(
                "PLC ingest: tenant=%s device=%s tag=%s val=%s %s",
                self.tenant_id,
                payload.device_id,
                dp.tag,
                dp.value,
                dp.unit or "",
            )
            processed += 1

        return {
            "ok": True,
            "device_id": payload.device_id,
            "received": len(payload.data_points),
            "processed": processed,
            "skipped_bad_quality": skipped,
        }

    def update_silo_level(self, payload: PlcSiloLevelIn) -> dict[str, Any]:
        """Schreibt Fuellstand einer Silozelle aus PLC-Messung.

        Stub: validiert und gibt Echo zurueck.
        Erweiterung: silo_cells.current_stock_kg + plc_measurements-Tabelle beschreiben.
        """
        from sqlalchemy import text

        row = self.db.execute(
            text("""
                SELECT id, cell_code, capacity_kg, qs_status
                FROM domain_inventory.silo_cells
                WHERE id = :cell_id
                  AND warehouse_id = :warehouse_id
                  AND tenant_id = :tenant_id
            """),
            {"cell_id": payload.cell_id, "warehouse_id": payload.warehouse_id, "tenant_id": self.tenant_id},
        ).fetchone()

        if row is None:
            raise ValueError(f"Silozelle {payload.cell_id} nicht gefunden")

        capacity_kg = float(row.capacity_kg) if row.capacity_kg else None
        estimated_kg = None
        if capacity_kg and payload.level_pct is not None:
            estimated_kg = round(capacity_kg * payload.level_pct / 100, 2)

        if estimated_kg is not None:
            self.db.execute(
                text("""
                    UPDATE domain_inventory.silo_cells
                    SET current_stock_kg = :kg,
                        updated_at = now()
                    WHERE id = :cell_id AND tenant_id = :tenant_id
                """),
                {"kg": estimated_kg, "cell_id": payload.cell_id, "tenant_id": self.tenant_id},
            )
            self.db.commit()

        logger.info(
            "PLC level update: tenant=%s cell=%s level=%.1f%% est_kg=%s device=%s",
            self.tenant_id,
            payload.cell_id,
            payload.level_pct,
            estimated_kg,
            payload.device_id or "—",
        )

        return {
            "ok": True,
            "cell_id": payload.cell_id,
            "cell_code": row.cell_code,
            "level_pct": payload.level_pct,
            "estimated_stock_kg": estimated_kg,
            "temperature_celsius": payload.temperature_celsius,
            "qs_status": row.qs_status,
        }

    def update_device_status(self, payload: PlcDeviceStatusIn) -> dict[str, Any]:
        logger.info(
            "PLC heartbeat: tenant=%s device=%s status=%s uptime=%s",
            self.tenant_id,
            payload.device_id,
            payload.status,
            payload.uptime_seconds,
        )
        return {
            "ok": True,
            "device_id": payload.device_id,
            "status": payload.status,
        }


# ── Endpoints ─────────────────────────────────────────────────────────────────


def _svc(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> AgriPlcService:
    return AgriPlcService(db, tenant_id)


@router.post(
    "/plc/ingest",
    status_code=200,
    summary="POST /plc/ingest — PLC/OPC-UA Batch-Datenpunkte einlesen (WM-AGRI-PLC-005)",
)
def plc_ingest(payload: PlcIngestIn, svc: AgriPlcService = Depends(_svc)) -> Any:
    """Batch-Endpoint: IoT-Gateway sendet mehrere Messwerte in einem Aufruf."""
    try:
        return svc.ingest_data_points(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/plc/silo-level",
    status_code=200,
    summary="POST /plc/silo-level — Fuellstand-Update von PLC/Sensor (WM-AGRI-PLC-005)",
)
def plc_silo_level(payload: PlcSiloLevelIn, svc: AgriPlcService = Depends(_svc)) -> Any:
    """Direkt-Update: Sensor meldet Fuellstand einer Silozelle (Gewicht in %, ggf. kg)."""
    try:
        return svc.update_silo_level(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/plc/device-status",
    status_code=200,
    summary="POST /plc/device-status — Heartbeat/Statusmeldung vom PLC-Feldgeraet",
)
def plc_device_status(payload: PlcDeviceStatusIn, svc: AgriPlcService = Depends(_svc)) -> Any:
    """Heartbeat vom SCADA/PLC-System: Online-Status und Firmware-Version."""
    return svc.update_device_status(payload)


@router.get(
    "/plc/info",
    status_code=200,
    summary="GET /plc/info — PLC-Stub-Informationen und Integrations-Anleitung",
)
def plc_info() -> Any:
    """Gibt Informationen zum PLC-Stub zurueck.

    Produktions-Anbindung:
    - OPC-UA-SDK: pip install asyncua
    - NATS-Subscriber: Publish auf subject 'agri.plc.<warehouse_id>.<device_id>'
    - Tag-Mapping: Tabelle domain_inventory.plc_tag_mappings (cell_id → tag_pattern)
    - Polling-Intervall: konfigurierbar per Tenant (Standard 5s)
    """
    return {
        "stub": True,
        "version": "WM-AGRI-PLC-005",
        "endpoints": [
            "POST /plc/ingest — Batch OPC-UA/PLC Datenpunkte",
            "POST /plc/silo-level — Fuellstand-Update direkt",
            "POST /plc/device-status — Heartbeat",
        ],
        "production_extensions": [
            "asyncua OPC-UA client (asyncio polling loop)",
            "domain_inventory.plc_tag_mappings (tag → cell mapping)",
            "NATS publish agri.plc.<warehouse>.<device>",
            "Alembic migration fuer plc_measurements-Tabelle",
        ],
    }
