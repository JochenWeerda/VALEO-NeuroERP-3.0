"""SPEC-P1-06 Welle 8 — Antwortschemata fuer Siloanlagen und Materialfluss.

Die vier Listenrouten in ``agri_silo_material_flow`` lesen ``SELECT *``. Die
Feldlisten stammen deshalb aus ``information_schema.columns`` einer auf head
migrierten Datenbank, nicht aus den Migrationen;
``tests/test_welle8_schema_drift.py`` haelt die Ableitung nach.

Tabellen in ``domain_inventory``: ``silo_systems`` (8 Spalten), ``silo_cells``
(21), ``material_flow_nodes`` (15), ``material_flow_edges`` (11).
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SiloSystemOut(BaseModel):
    """Eine Zeile aus ``domain_inventory.silo_systems``."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    warehouse_id: str
    system_code: str
    name: str
    description: Optional[str] = None
    tenant_id: str
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None


class SiloCellOut(BaseModel):
    """Eine Zeile aus ``domain_inventory.silo_cells``.

    ``current_stock_kg`` und ``capacity_kg`` sind in der DDL NOT NULL, die
    Layoutkoordinaten und die Verschneidung mit Zone/Gang/Platz sind optional.
    ``legacy_silo_id`` traegt die Herkunft aus dem Altsystem.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    silo_system_id: str
    warehouse_id: str
    zone_id: Optional[str] = None
    aisle_id: Optional[str] = None
    bin_id: Optional[str] = None
    cell_code: str
    name: str
    capacity_kg: Decimal
    current_stock_kg: Decimal
    current_material_id: Optional[str] = None
    current_lot_id: Optional[str] = None
    qs_status: str = Field(..., description="frei | gesperrt | pruefung")
    contamination_risk_class: Optional[str] = Field(
        None, description="Verschleppungs-Risikoklasse fuer die Spuelchargen-Logik"
    )
    tenant_id: str
    is_active: Optional[bool] = None
    layout_x: Optional[Decimal] = None
    layout_y: Optional[Decimal] = None
    legacy_silo_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MaterialFlowNodeOut(BaseModel):
    """Ein Knoten des Materialflussgraphen (``domain_inventory.material_flow_nodes``)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    warehouse_id: str
    node_type: str
    ref_type: Optional[str] = None
    ref_id: Optional[str] = None
    code: str
    name: str
    status: str
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None
    layout_x: Optional[Decimal] = None
    layout_y: Optional[Decimal] = None
    tenant_id: str
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None


class MaterialFlowEdgeOut(BaseModel):
    """Eine Foerderstrecke (``domain_inventory.material_flow_edges``).

    ``contamination_guard_enabled`` und ``flush_required`` steuern die
    Verschleppungspruefung in ``POST /material-flow/validate-route``.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    warehouse_id: str
    from_node_id: str
    to_node_id: str
    conveyor_type: str
    status: str
    contamination_guard_enabled: bool
    flush_required: bool
    max_capacity_kg_h: Optional[Decimal] = None
    tenant_id: str
    created_at: Optional[datetime] = None
