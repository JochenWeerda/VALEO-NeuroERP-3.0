"""Response-Schemas fuer den Rations-Lebenszyklus.

SPEC-P1-06 Welle 3: ersetzt ``response_model=dict`` bzw. ``list[dict]`` in
``app/api/v1/endpoints/rations_lifecycle.py``.

Die Feldlisten folgen der Migration ``feed_advice_lifecycle_20260714``
(``domain_agrar.rations``, ``ration_versions``, ``ration_version_lifecycle``,
``ration_audit_events``) und den Joins in ``rations_lifecycle_service``.
Spaetere ALTERs auf diese Tabellen existieren nicht; kommen welche dazu,
muessen diese Schemas mitwachsen.

``snapshot`` und ``delta`` bleiben offene JSONB-Felder — ihr Inhalt ist der
Solver-Snapshot bzw. das Audit-Delta und bewusst nicht schematisiert.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class RationVersionOut(BaseSchema):
    """Unveraenderliche Rationsversion samt Lebenszyklus-Stempeln.

    ``ration_versions.*`` plus die Statusfelder aus
    ``ration_version_lifecycle``.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    ration_id: Optional[str] = None
    version_no: Optional[int] = None
    source: Optional[str] = Field(default=None, description="Herkunft, z. B. solver")
    comment: Optional[str] = None
    snapshot: Optional[Any] = Field(default=None, description="Solver-Snapshot (JSONB)")
    snapshot_checksum: Optional[str] = None
    based_on_version_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = Field(
        default=None,
        description="draft | in_review | approved | scheduled | active | retired | archived",
    )
    feeding_start: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    activated_by: Optional[str] = None
    activated_at: Optional[datetime] = None
    retired_by: Optional[str] = None
    retired_at: Optional[datetime] = None
    archived_by: Optional[str] = None
    archived_at: Optional[datetime] = None


class RationAuditEventOut(BaseSchema):
    """Zeile aus ``domain_agrar.ration_audit_events``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    ration_id: Optional[str] = None
    version_id: Optional[str] = None
    event_type: Optional[str] = None
    from_status: Optional[str] = None
    to_status: Optional[str] = None
    actor: Optional[str] = None
    reason: Optional[str] = None
    delta: Optional[Any] = Field(default=None, description="Aenderungsdelta (JSONB)")
    occurred_at: Optional[datetime] = None


class RationDetailOut(BaseSchema):
    """``GET /rations/{id}`` sowie die Antwort von Anlage und neuer Version.

    Kopf aus ``domain_agrar.rations`` plus Gruppenkontext, Versionsliste,
    Audit und die abgeleiteten ``latest_*``-Felder.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    group_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    group_name: Optional[str] = None
    animal_count: Optional[int] = None
    feeding_system: Optional[str] = None
    location: Optional[str] = None
    versions: list[RationVersionOut] = Field(default_factory=list)
    audit: list[RationAuditEventOut] = Field(default_factory=list)
    latest_version_id: Optional[str] = None
    latest_version_no: Optional[int] = None
    latest_status: Optional[str] = None
    latest_feeding_start: Optional[datetime] = None
    latest_readiness_status: Optional[str] = Field(
        default=None, description="Readiness aus dem Snapshot, sonst not_checked"
    )
    latest_readiness_blockers: Optional[int] = None
    latest_readiness_warnings: Optional[int] = None


class RationWorklistItemOut(BaseSchema):
    """``GET /rations`` — Ration mit ihrer jeweils juengsten Version."""

    id: Optional[str] = None
    group_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    group_name: Optional[str] = None
    animal_count: Optional[int] = None
    feeding_system: Optional[str] = None
    version_id: Optional[str] = None
    version_no: Optional[int] = None
    status: Optional[str] = None
    feeding_start: Optional[datetime] = None
    snapshot_checksum: Optional[str] = None
    version_created_at: Optional[datetime] = None


class ActiveRationOut(BaseSchema):
    """``GET /active-rations`` — was aktuell im Stall gefuettert wird."""

    ration_id: Optional[str] = None
    name: Optional[str] = None
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    animal_count: Optional[int] = None
    version_id: Optional[str] = None
    version_no: Optional[int] = None
    snapshot: Optional[Any] = Field(default=None, description="Solver-Snapshot (JSONB)")
    snapshot_checksum: Optional[str] = None
    feeding_start: Optional[datetime] = None
    activated_at: Optional[datetime] = None


class RationTransitionOut(BaseSchema):
    """``POST /versions/{id}/transitions``.

    Die aktualisierte Lebenszyklus-Zeile plus Versionskontext und die durch
    den Wechsel abgeloesten Versionen.
    """

    version_id: Optional[str] = None
    tenant_id: Optional[str] = None
    ration_id: Optional[str] = None
    group_id: Optional[str] = None
    status: Optional[str] = None
    feeding_start: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    activated_by: Optional[str] = None
    activated_at: Optional[datetime] = None
    retired_by: Optional[str] = None
    retired_at: Optional[datetime] = None
    archived_by: Optional[str] = None
    archived_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version_no: Optional[int] = None
    snapshot_checksum: Optional[str] = None
    superseded_version_ids: list[str] = Field(
        default_factory=list,
        description="Versionen, die durch diesen Wechsel abgeloest wurden",
    )
