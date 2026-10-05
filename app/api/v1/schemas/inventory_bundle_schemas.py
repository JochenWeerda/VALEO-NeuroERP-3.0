"""Response-Schemas fuer Inventur-Hilfsstapel und die PLC-Anbindung.

SPEC-P1-06 Welle 7: ersetzt ``response_model=dict`` bzw. ``dict[str, Any]`` in
``inventory_auxiliary.py`` und ``agri_plc_stub.py``.

Beide Bereiche benennen ihre Spalten explizit im SELECT bzw. konstruieren ihre
Antworten vollstaendig im Code — die Feldlisten sind exakt ableitbar.

Bewusst NICHT in dieser Welle: ``inventory_operations.py`` und
``agri_silo_material_flow.py``. Beide lesen ``SELECT *`` ueber
``inventory_stock_movements`` bzw. die Silo-Tabellen, und allein
``inventory_stock_movements`` wird von elf Migrationen mit 23
ALTER/ADD-COLUMN-Statements fortgeschrieben. Eine aus Migrationen
rekonstruierte Spaltenliste waere dort nicht belastbar; die richtige Quelle ist
``information_schema.columns`` einer migrierten Datenbank. Siehe Slice-YAML.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Inventur-Hilfsstapel ────────────────────────────────────────────────────


class AuxiliaryBatchOut(BaseSchema):
    """Zeile aus ``domain_inventory.inventory_auxiliary_batches``."""

    id: Optional[str] = None
    inventory_count_id: Optional[str] = None
    batch_type: Optional[str] = None
    status: Optional[str] = Field(
        default=None,
        description="generated | reviewed | approved | applied | rejected",
    )
    source_hash: Optional[str] = Field(
        default=None, description="Hash der Quelldaten — Grundlage der Idempotenz"
    )
    line_count: Optional[int] = None
    difference_count: Optional[int] = None
    preliminary_value: Optional[float] = None
    maker: Optional[str] = Field(default=None, description="Ersteller (Vier-Augen-Prinzip)")
    checker: Optional[str] = None
    source_route: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuxiliaryBatchPageOut(BaseSchema):
    """``GET /inventory/auxiliary/batches``"""

    items: list[AuxiliaryBatchOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class AuxiliarySummaryOut(BaseSchema):
    """``GET /inventory/auxiliary/summary`` — Zaehlung je Status."""

    generated: Optional[int] = None
    reviewed: Optional[int] = None
    approved: Optional[int] = None
    applied: Optional[int] = None
    with_differences: Optional[int] = Field(
        default=None, description="Noch offene Stapel mit Differenzen"
    )


class AuxiliaryBatchCreatedOut(BaseSchema):
    """``POST /inventory/auxiliary/batches``.

    Der Idempotenzpfad liefert nur ``id``, ``status``, ``duplicate`` und
    ``source_hash``; die Neuanlage zusaetzlich die Zaehlwerte.
    """

    id: Optional[str] = None
    status: Optional[str] = None
    duplicate: Optional[bool] = None
    source_hash: Optional[str] = None
    line_count: Optional[int] = None
    difference_count: Optional[int] = None
    preliminary_value: Optional[float] = None


class AuxiliaryTransitionOut(BaseSchema):
    """``POST /inventory/auxiliary/batches/{id}/transition``"""

    id: Optional[str] = None
    status: Optional[str] = None


# ── PLC-/OPC-UA-Anbindung (Stub) ────────────────────────────────────────────


class PlcIngestOut(BaseSchema):
    """``POST /plc/ingest`` — Batch von Datenpunkten.

    Datenpunkte mit ``quality="bad"`` werden verworfen und in
    ``skipped_bad_quality`` gezaehlt.
    """

    ok: bool = Field(default=True)
    device_id: Optional[str] = None
    received: Optional[int] = None
    processed: Optional[int] = None
    skipped_bad_quality: Optional[int] = None


class PlcSiloLevelOut(BaseSchema):
    """``POST /plc/silo-level`` — Fuellstandsmessung einer Silozelle."""

    ok: bool = Field(default=True)
    cell_id: Optional[str] = None
    cell_code: Optional[str] = None
    level_pct: Optional[float] = None
    estimated_stock_kg: Optional[float] = Field(
        default=None, description="Aus Fuellstand und Zellvolumen geschaetzt"
    )
    temperature_celsius: Optional[float] = None
    qs_status: Optional[str] = None


class PlcDeviceStatusOut(BaseSchema):
    """``POST /plc/device-status`` — Heartbeat eines Feldgeraets."""

    ok: bool = Field(default=True)
    device_id: Optional[str] = None
    status: Optional[str] = None


class PlcInfoOut(BaseSchema):
    """``GET /plc/info`` — Selbstauskunft des Stubs.

    ``stub: true`` ist der Vertrag dieses Endpunkts: die Anbindung ist noch
    nicht produktiv, die Antwort nennt die Schritte dorthin.
    """

    stub: bool = Field(default=True, description="Immer true — noch keine Live-Anbindung")
    version: Optional[str] = None
    endpoints: list[str] = Field(default_factory=list)
    production_extensions: list[str] = Field(
        default_factory=list, description="Schritte zur produktiven OPC-UA-Anbindung"
    )
