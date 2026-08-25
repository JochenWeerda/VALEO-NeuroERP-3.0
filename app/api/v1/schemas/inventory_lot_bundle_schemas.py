"""SPEC-P1-06 Welle 8 — Antwortschemata fuer Inventur-, Lot- und Storno-Routen.

Die Feldlisten sind nicht aus Migrationen rekonstruiert, sondern aus
``information_schema.columns`` einer auf head migrierten Datenbank gezogen.
``tests/test_welle8_schema_drift.py`` verankert diese Ableitung: laeuft eine
Datenbank, wird jedes Modell hier gegen die reale DDL geprueft.

Die gelesenen Tabellen liegen in ``domain_inventory``:
``inventory_lots`` (15 Spalten) und ``inventory_stock_movements`` (35 Spalten).
"""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InventoryLotOut(BaseModel):
    """Eine Zeile aus ``domain_inventory.inventory_lots``.

    ``GET /lager/lots`` liefert ``SELECT *`` — deshalb bildet dieses Modell alle
    15 Spalten ab. ``POST /lager/lots`` gibt nur die zehn Felder zurueck, die es
    selbst gesetzt hat; die uebrigen bleiben leer.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    article_id: str
    warehouse_id: str
    lot_number: str
    mhd: Optional[date] = Field(None, description="Mindesthaltbarkeitsdatum, FEFO-Sortierschluessel")
    initial_qty: Decimal
    current_qty: Decimal
    unit: Optional[str] = None
    status: Optional[str] = Field(None, description="AKTIV | ERSCHOEPFT")
    created_at: Optional[datetime] = None
    herkunft: Optional[str] = None
    sperrgrund: Optional[str] = None
    qs_status: Optional[str] = None
    received_at: Optional[date] = None


class LotConsumeOut(BaseModel):
    """Ergebnis eines FEFO-Verbrauchs (``POST /lager/lots/{lot_id}/consume``)."""

    lot_id: str
    consumed_qty: float
    remaining_qty: float
    status: str = Field(..., description="AKTIV | ERSCHOEPFT nach dem Verbrauch")


class InventurDifferenzOut(BaseModel):
    """Ergebnis von ``POST /lager/inventur/{count_id}/differenz-buchen``.

    ``lines_skipped_idempotent`` zaehlt Zeilen, fuer die bereits ein
    Differenzbeleg existierte — der Endpunkt ist idempotent.
    """

    count_id: str
    corrections_created: int
    lines_skipped_idempotent: int
    correction_line_ids: list[str]


class StornoKorrekturOut(BaseModel):
    """Ergebnis von ``POST /lager/korrekturen/{korrektur_id}/storno``.

    Der Endpunkt hat zwei Zweige mit unterschiedlicher Feldmenge:

    * Neues Storno — die neun Felder, die der Service selbst zusammenstellt.
    * Idempotenter Treffer — die komplette bestehende Bewegungszeile aus
      ``inventory_stock_movements`` plus ``idempotent=True``.

    Damit im idempotenten Fall kein Feld still wegfaellt, deckt dieses Modell
    alle 35 Spalten der Tabelle ab. Nur ``id``, ``article_id``,
    ``warehouse_id``, ``movement_type``, ``quantity`` und ``tenant_id`` sind in
    beiden Zweigen sicher gesetzt.
    """

    model_config = ConfigDict(from_attributes=True)

    idempotent: bool = Field(..., description="True, wenn ein bestehendes Storno zurueckgegeben wurde")

    id: str
    tenant_id: str
    article_id: str
    warehouse_id: str
    movement_type: str
    quantity: Decimal

    storno_ref: Optional[str] = Field(None, description="ID der stornierten Ursprungsbewegung")
    source_document_type: Optional[str] = Field(None, description="Belegtyp, fuer Stornos 'STORNO'")
    source_document_id: Optional[str] = None

    unit: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    previous_stock: Optional[Decimal] = None
    new_stock: Optional[Decimal] = None

    reference_number: Optional[str] = None
    movement_number: Optional[str] = None
    movement_date: Optional[date] = None
    movement_time: Optional[time] = None
    notes: Optional[str] = None
    warehouse_location: Optional[str] = None
    charge: Optional[str] = None
    bin_id: Optional[str] = None
    booking_user: Optional[str] = None
    auto_created: Optional[bool] = None
    linked_order_id: Optional[UUID] = None

    ownership_type: Optional[str] = None
    owner_partner_id: Optional[str] = None
    agrar_contract_id: Optional[str] = None
    weighing_ticket_id: Optional[str] = None

    storage_fee_relevant: Optional[bool] = None
    storage_fee_start_date: Optional[date] = None
    storage_fee_monthly_rate: Optional[Decimal] = None
    storage_fee_last_charged_until: Optional[date] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
