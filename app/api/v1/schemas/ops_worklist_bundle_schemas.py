"""Response-Schemas fuer Ops-Worklists (SPEC-P1-06 Welle 9).

Ersetzt ``response_model=dict`` / ``list[dict]`` in:
- ``production_control.py``
- ``tank_adapter.py``
- ``foreign_goods_worklist.py``

Feldlisten stammen aus den expliziten SELECT-/Return-Dicts der Services.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Produktionsleitstand ────────────────────────────────────────────────────


class ProductionOperationOut(BaseSchema):
    """Zeile aus ``domain_ops.production_operations``."""

    id: Optional[str] = None
    operation_type: Optional[str] = None
    status: Optional[str] = None
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    source_number: Optional[str] = None
    source_route: Optional[str] = None
    work_center: Optional[str] = None
    article_ref: Optional[str] = None
    article_name: Optional[str] = None
    batch_ref: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    assigned_user: Optional[str] = None
    planned_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductionOperationPageOut(BaseSchema):
    """``GET /production-control/operations``"""

    items: list[ProductionOperationOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ProductionRegisterOut(BaseSchema):
    """``POST /production-control/operations`` — Neuanlage oder Duplikat."""

    id: Optional[str] = None
    status: Optional[str] = None
    duplicate: Optional[bool] = None


class ProductionSummaryOut(BaseSchema):
    """``GET /production-control/summary``"""

    waiting: Optional[int] = None
    running: Optional[int] = None
    attention: Optional[int] = None
    completed: Optional[int] = None
    mill_runs: Optional[int] = None


class ProductionSyncOut(BaseSchema):
    """``POST /production-control/sync``"""

    synchronized: Optional[int] = None


class ProductionTransitionOut(BaseSchema):
    """``POST /production-control/operations/{id}/transition``"""

    id: Optional[str] = None
    status: Optional[str] = None


class ProductionAuditOut(BaseSchema):
    """Eintrag aus ``domain_ops.production_operation_audit``."""

    action: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None


# ── Tank-Adapter ────────────────────────────────────────────────────────────


class TankIntakeOut(BaseSchema):
    """Zeile aus ``domain_ops.tank_adapter_intake`` (Listenansicht)."""

    id: Optional[str] = None
    adapter_key: Optional[str] = None
    external_id: Optional[str] = None
    payload_hash: Optional[str] = None
    status: Optional[str] = None
    validation_errors: Optional[Any] = None
    rule_result: Optional[Any] = None
    zapfung_id: Optional[str] = None
    delivery_handover_id: Optional[str] = None
    retry_count: Optional[int] = None
    received_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TankIntakePageOut(BaseSchema):
    """``GET /tank-adapter/intake``"""

    items: list[TankIntakeOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class TankIngestOut(BaseSchema):
    """``POST /tank-adapter/intake`` — Neu oder idempotent."""

    id: Optional[str] = None
    status: Optional[str] = None
    payload_hash: Optional[str] = None
    idempotent: Optional[bool] = None


class TankSummaryOut(BaseSchema):
    """``GET /tank-adapter/summary``"""

    received: Optional[int] = None
    validated: Optional[int] = None
    error: Optional[int] = None
    processed: Optional[int] = None
    delivery_handover: Optional[int] = None


class TankValidateOut(BaseSchema):
    """``POST /tank-adapter/intake/{id}/validate``"""

    id: Optional[str] = None
    status: Optional[str] = None
    validation_errors: list[str] = Field(default_factory=list)
    rule_result: Optional[dict[str, Any]] = None


class TankProcessOut(BaseSchema):
    """``POST /tank-adapter/intake/{id}/process``"""

    id: Optional[str] = None
    status: Optional[str] = None
    zapfung_id: Optional[str] = None
    delivery_handover_id: Optional[str] = None
    idempotent: Optional[bool] = None


class TankRetryOut(BaseSchema):
    """``POST /tank-adapter/intake/{id}/retry``"""

    id: Optional[str] = None
    status: Optional[str] = None
    payload_hash: Optional[str] = None


# ── Fremdware-Worklist ──────────────────────────────────────────────────────


class ForeignGoodsItemOut(BaseSchema):
    """Zeile aus ``domain_einkauf.fremdwaren_einlagerung`` inkl. source_route."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    einlagerungs_nr: Optional[str] = None
    eigentuemer_id: Optional[str] = None
    eigentuemer_name: Optional[str] = None
    warehouse_id: Optional[str] = None
    lagerort: Optional[str] = None
    artikel_nr: Optional[str] = None
    artikel_bezeichnung: Optional[str] = None
    charge: Optional[str] = None
    einlagerungstyp: Optional[str] = None
    menge_eingelagert: Optional[float] = None
    menge_aktuell: Optional[float] = None
    einheit: Optional[str] = None
    einlagerungsdatum: Optional[date] = None
    geplante_auslagerung: Optional[date] = None
    auslagerungsdatum: Optional[date] = None
    gebuehr_pro_tag: Optional[float] = None
    gebuehr_einheit: Optional[str] = None
    status: Optional[str] = None
    notiz: Optional[str] = None
    updated_at: Optional[datetime] = None
    source_route: Optional[str] = None


class ForeignGoodsPageOut(BaseSchema):
    """``GET /foreign-goods``"""

    items: list[ForeignGoodsItemOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ForeignGoodsSummaryOut(BaseSchema):
    """``GET /foreign-goods/summary``"""

    stored: Optional[int] = None
    partial: Optional[int] = None
    completed: Optional[int] = None
    owners: Optional[int] = None
    warehouses: Optional[int] = None


class ForeignGoodsTransferOut(BaseSchema):
    """``POST /foreign-goods/{id}/transfer``"""

    id: Optional[str] = None
    status: Optional[str] = None
    warehouse_id: Optional[str] = None
    lagerort: Optional[str] = None


class ForeignGoodsCompleteOut(BaseSchema):
    """``POST /foreign-goods/{id}/complete``"""

    id: Optional[str] = None
    status: Optional[str] = None
    menge_aktuell: Optional[float] = None
