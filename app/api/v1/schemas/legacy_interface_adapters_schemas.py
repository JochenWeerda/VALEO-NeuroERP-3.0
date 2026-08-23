"""Response-Schemas fuer die Legacy-Schnittstellenadapter.

SPEC-P1-06 Welle 5: ersetzt ``response_model=dict`` in
``app/api/v1/endpoints/legacy_interface_adapters.py``.

Feldlisten aus ``legacy_interface_adapter_service``. Auffaellig und bewusst
erhalten: jede Antwort fuehrt ``execution_enabled: false`` — der Adapter ist
repo-seitig vorbereitet, die Ausfuehrung aber extern gegated. Das Feld ist Teil
des Vertrags und darf nicht wegtypisiert werden.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class AdapterProfileOut(BaseSchema):
    """Profil aus dem Adapterkatalog.

    Der Katalog mischt die statische Spezifikation (``profile_key``, ``title``,
    ``required_contract_fields``) mit der Mandantenkonfiguration; ohne
    Konfiguration steht nur ``status: inactive``.
    """

    profile_key: Optional[str] = None
    title: Optional[str] = None
    required_contract_fields: list[str] = Field(default_factory=list)
    execution_enabled: Optional[bool] = None
    status: Optional[str] = None
    format_version: Optional[str] = None
    mapping_version: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdapterProfileListOut(BaseSchema):
    """``GET /profiles``"""

    items: list[AdapterProfileOut] = Field(default_factory=list)
    total: Optional[int] = None
    execution_enabled: Optional[bool] = None


class AdapterConfigureOut(BaseSchema):
    """``PUT /profiles/{profile_key}``"""

    profile_key: Optional[str] = None
    status: Optional[str] = None
    execution_enabled: Optional[bool] = None


class AdapterIntakeOut(BaseSchema):
    """``POST /{profile_key}/intake`` — Annahme eines Fremdbelegs."""

    id: Optional[str] = None
    status: Optional[str] = None
    duplicate: Optional[bool] = Field(
        default=None, description="True, wenn derselbe Payload-Hash schon vorlag"
    )
    payload_hash: Optional[str] = None


class AdapterBatchOut(BaseSchema):
    """Zeile aus ``domain_integration.legacy_adapter_batches``."""

    id: Optional[str] = None
    profile_key: Optional[str] = None
    external_id: Optional[str] = None
    payload_hash: Optional[str] = None
    mapping_version: Optional[str] = None
    status: Optional[str] = None
    record_count: Optional[int] = None
    staged_count: Optional[int] = None
    mismatch_count: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdapterMonitorOut(BaseSchema):
    """``GET /batches`` — Stapeluebersicht mit Profilkatalog."""

    items: list[AdapterBatchOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    profiles: list[AdapterProfileOut] = Field(default_factory=list)
    execution_enabled: Optional[bool] = None


class AdapterBatchActionOut(BaseSchema):
    """Antwort von ``stage``, ``reconcile`` und ``approve``.

    ``reconcile`` liefert zusaetzlich ``record_count``, ``approve``
    zusaetzlich ``next_gate``.
    """

    id: Optional[str] = None
    status: Optional[str] = None
    record_count: Optional[int] = None
    staged_count: Optional[int] = None
    mismatch_count: Optional[int] = None
    execution_enabled: Optional[bool] = None
    next_gate: Optional[str] = Field(
        default=None, description="Naechstes externes Gate vor der Ausfuehrung"
    )
