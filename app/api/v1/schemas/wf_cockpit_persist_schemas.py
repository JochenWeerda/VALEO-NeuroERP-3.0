"""Response-Schemas fuer das DB-gestuetzte Workflow-Cockpit (WF-COCKPIT-PERSIST-001).

SPEC-P1-06 Welle 4: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/wf_cockpit_persist.py``.

ACHTUNG — abweichende Migrationen: ``wf_cockpit_persist_20260625`` und
``feed_qs_wf_cockpit_repair_20260626`` legen dieselben Tabellen mit
unterschiedlichen Spaltensaetzen an. Die Reparaturmigration nutzt
``CREATE TABLE IF NOT EXISTS`` und ergaenzt fehlende Spalten per ALTER, sodass
je nach Installationsalter beide Formen vorkommen koennen:

  * ``wf_cockpit_instances``: ``created_at`` (kanonisch) bzw. ``started_at`` /
    ``finished_at`` (Reparatur)
  * ``wf_cockpit_blockers``: ``message`` / ``external_system`` / ``retryable`` /
    ``since`` (kanonisch) bzw. ``reason`` / ``context`` / ``resolved_by`` /
    ``created_at`` (Reparatur)

Die Schemas fuehren deshalb die **Vereinigung** beider Spaltensaetze; alles ist
optional. Der Detail-Endpunkt liest ``SELECT *`` und wuerde sonst je nach
Installation Felder verlieren.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class CockpitInstanceOut(BaseSchema):
    """Zeile aus ``domain_workflow.wf_cockpit_instances``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    process_key: Optional[str] = None
    status: Optional[str] = None
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    business_object_ref: Optional[str] = None
    current_step: Optional[str] = None
    audit_ref: Optional[str] = None
    active_blocker_count: Optional[int] = None
    replayable: Optional[bool] = None
    created_at: Optional[Any] = Field(default=None, description="kanonische Migration")
    updated_at: Optional[Any] = None
    started_at: Optional[Any] = Field(default=None, description="Reparaturmigration")
    finished_at: Optional[Any] = Field(default=None, description="Reparaturmigration")


class CockpitEventOut(BaseSchema):
    """Zeile aus ``domain_workflow.wf_cockpit_events``."""

    id: Optional[str] = None
    kind: Optional[str] = None
    message: Optional[str] = None
    source: Optional[str] = None
    payload: Optional[Any] = Field(default=None, description="Ereignis-Nutzlast (JSONB)")
    occurred_at: Optional[Any] = None


class CockpitBlockerOut(BaseSchema):
    """Zeile aus ``domain_workflow.wf_cockpit_blockers`` (Vereinigung beider DDLs)."""

    id: Optional[str] = None
    blocker_type: Optional[str] = None
    message: Optional[str] = None
    external_system: Optional[str] = None
    retryable: Optional[bool] = None
    resolved: Optional[bool] = None
    since: Optional[Any] = None
    resolved_at: Optional[Any] = None
    reason: Optional[str] = Field(default=None, description="Reparaturmigration")
    context: Optional[Any] = Field(default=None, description="Reparaturmigration")
    resolved_by: Optional[str] = Field(default=None, description="Reparaturmigration")
    created_at: Optional[Any] = Field(default=None, description="Reparaturmigration")


class CockpitInstanceListOut(BaseSchema):
    """``GET /workflow/cockpit-db/instances``"""

    items: list[CockpitInstanceOut] = Field(default_factory=list)
    count: Optional[int] = None


class CockpitInstanceDetailOut(CockpitInstanceOut):
    """``GET /workflow/cockpit-db/instances/{id}`` — Kopf plus Verlauf."""

    events: list[CockpitEventOut] = Field(default_factory=list)
    blockers: list[CockpitBlockerOut] = Field(default_factory=list)


class DeadLetterItemOut(BaseSchema):
    """Instanz in FAILED oder BLOCKED_EXTERNAL_GATE."""

    id: Optional[str] = None
    process_key: Optional[str] = None
    status: Optional[str] = None
    correlation_id: Optional[str] = None
    current_step: Optional[str] = None
    updated_at: Optional[str] = None
    replayable: Optional[bool] = None
    open_blocker_count: Optional[int] = None


class DeadLetterViewOut(BaseSchema):
    """``GET /workflow/cockpit-db/dead-letter``"""

    tenant_id: Optional[str] = None
    dead_letter_count: Optional[int] = None
    items: list[DeadLetterItemOut] = Field(default_factory=list)


class InstanceUpsertOut(BaseSchema):
    """``POST /workflow/cockpit-db/instances``"""

    process_instance_id: str
    ok: bool = Field(default=True)


class BlockerResolvedOut(BaseSchema):
    """``POST .../blockers/{id}/resolve``"""

    blocker_id: str
    resolved: bool = Field(default=True)


class InstanceStatusOut(BaseSchema):
    """``POST .../retry`` und ``.../compensate``"""

    process_instance_id: str
    status: str = Field(description="retry_pending | compensated")
