"""Ist-NATS/Outbox-Topics auf den Workspace-SSE-Stream spiegeln.

Publisher in Fachmodulen werden nicht umbenannt. Soll-Namen
(assignment_confirmed / document_proposed / document_posted) bleiben Annotation.
Auf ``/api/events?stream=workspace`` landet der Ist-Typ.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)

CANONICAL_EVENTS = (
    "assignment_confirmed",
    "document_proposed",
    "document_posted",
)

SSE_CHANNEL = "workspace"

# Ist-Outbox/NATS-Event-Typ → Soll-Name. Unbekannte Typen bleiben unprojiziert.
IST_TO_SOLL: dict[str, str] = {
    "logistik.tour.created": "assignment_confirmed",
    "lkw.registered": "assignment_confirmed",
    # Verladung Ist-Typen aus EventType (tours.py → OutboxPublisher)
    "LOADING_STARTED": "assignment_confirmed",
    "LOADING_FINISHED": "assignment_confirmed",
    "finance.ap_invoice.approved": "assignment_confirmed",
    "finance.ap_invoice.approval_granted": "assignment_confirmed",
    "finance.ap_invoice.approval_requested": "document_proposed",
    "sales.invoice.proposed": "document_proposed",
    "sales.gutschrift.proposed": "document_proposed",
    "finance.ap_invoice.posted": "document_posted",
    "goods_receipt.created": "document_posted",
    "docflow.document.posted": "document_posted",
    "sales.invoice.posted": "document_posted",
    "lager.einlagerung.created": "document_posted",
    # Waage / Wiegeschein (Outbox in weighing_tickets.py)
    "agrar.weighing_ticket.allocated": "document_posted",
    # Qualitaet: Finalize schreibt Outbox in quality_protocols.py (nicht outbox.py)
    "agrar.quality_protocol.completed": "document_posted",
}

# Process-Kernel-Klassenname → dokumentierter Ist-Typ (kein neues Topic).
CLASS_NAME_TO_IST: dict[str, str] = {
    "APInvoiceApprovalRequested": "finance.ap_invoice.approval_requested",
    "APInvoiceApprovalGranted": "finance.ap_invoice.approval_granted",
    "APInvoiceApproved": "finance.ap_invoice.approved",
    "APInvoicePosted": "finance.ap_invoice.posted",
    "QualityProtocolCompleted": "agrar.quality_protocol.completed",
}

# Soll-NATS-Subjects werden nicht publiziert; nur Dokumentation der Luecke.
SOLL_NATS_SUBJECT = {
    "assignment_confirmed": "tenant.{tenantId}.workspace.assignment_confirmed",
    "document_proposed": "tenant.{tenantId}.workspace.document_proposed",
    "document_posted": "tenant.{tenantId}.workspace.document_posted",
}

_RECENT_MAX = 512
_recent_event_ids: deque[tuple[str, str]] = deque(maxlen=_RECENT_MAX)
_recent_lookup: set[tuple[str, str]] = set()
_inflight: dict[tuple[str, str], asyncio.Future] = {}


def canonical_event(ist_type: str | None) -> str | None:
    """Liefert den Soll-Namen oder None, wenn keine Abbildung existiert."""
    resolved = resolve_ist_event_type(ist_type)
    if not resolved:
        return None
    return IST_TO_SOLL.get(resolved)


def nats_subject(soll: str, tenant_id: str) -> str:
    template = SOLL_NATS_SUBJECT.get(soll, "tenant.{tenantId}.workspace." + soll)
    return template.replace("{tenantId}", tenant_id)


def resolve_ist_event_type(source: Any) -> str | None:
    """Normiert eingehende Typen auf den dokumentierten Ist-Key.

    Akzeptiert Ist-String, tenant-praefixiertes Subject, Process-Kernel-Klasse
    oder Event-Objekt/Dict. Erzwingt keine neuen Topic-Namen.
    """
    if source is None:
        return None
    if not isinstance(source, (str, bytes)):
        domain = getattr(source, "domain", None)
        aggregate = getattr(source, "aggregate", None)
        verb = getattr(source, "verb", None)
        if domain and aggregate and verb:
            return resolve_ist_event_type(f"{domain}.{aggregate}.{verb}")
        raw = None
        if isinstance(source, dict):
            header = source.get("header") if isinstance(source.get("header"), dict) else {}
            raw = source.get("event_type") or source.get("type") or header.get("event_type")
        else:
            header = getattr(source, "header", None)
            raw = (
                getattr(source, "event_type", None)
                or getattr(source, "type", None)
                or (header.get("event_type") if isinstance(header, dict) else None)
                or source.__class__.__name__
            )
        return resolve_ist_event_type(raw)

    raw = str(source).strip()
    if not raw:
        return None
    if raw in IST_TO_SOLL:
        return raw
    mapped = CLASS_NAME_TO_IST.get(raw)
    if mapped:
        return mapped
    parts = [part for part in raw.split(".") if part]
    for width in (4, 3, 2):
        if len(parts) >= width:
            candidate = ".".join(parts[-width:])
            if candidate in IST_TO_SOLL:
                return candidate
            mapped = CLASS_NAME_TO_IST.get(candidate)
            if mapped:
                return mapped
    return None


def should_mirror_ist_event(source: Any) -> bool:
    return resolve_ist_event_type(source) in IST_TO_SOLL


def project_workspace_event(
    ist_type: str,
    *,
    tenant_id: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Ist-Event → Workspace-Umschlag fuer SSE. Typ bleibt der Ist-Name."""
    resolved = resolve_ist_event_type(ist_type)
    if resolved is None:
        return None
    soll = IST_TO_SOLL[resolved]
    body = payload or {}
    return {
        "type": resolved,
        "event_type": resolved,
        "canonical": soll,
        "ist_event_type": resolved,
        "nats_subject": nats_subject(soll, tenant_id),
        "sse_channel": SSE_CHANNEL,
        "stream": SSE_CHANNEL,
        "tenant_id": tenant_id,
        "payload": body,
        "wired": True,
        "reason": "ist_mirrored_to_workspace_sse",
    }


def _remember_event_id(event_id: tuple[str, str] | None) -> bool:
    if not event_id:
        return False
    if event_id in _recent_lookup:
        return True
    if len(_recent_event_ids) == _RECENT_MAX:
        expired = _recent_event_ids[0]
        _recent_lookup.discard(expired)
    _recent_event_ids.append(event_id)
    _recent_lookup.add(event_id)
    return False


def reset_workspace_sse_dedup() -> None:
    _recent_event_ids.clear()
    _recent_lookup.clear()


async def publish_workspace_sse(
    ist_type: str,
    *,
    tenant_id: str,
    payload: dict[str, Any] | None = None,
    event_id: str | None = None,
    hub: Any | None = None,
) -> dict[str, Any] | None:
    """Spiegelt ein Ist-Event auf den vorhandenen SSE-Kanal ``workspace``.

    Best-effort. Kein NATS-Rename, keine Buchung, kein MCP-WRITE.
    """
    if not tenant_id:
        return None
    envelope = project_workspace_event(ist_type, tenant_id=tenant_id, payload=payload)
    if envelope is None:
        return None
    if event_id:
        envelope["event_id"] = event_id
    target = hub
    if target is None:
        from app.core.sse import sse_hub

        target = sse_hub
    key = (tenant_id, event_id) if event_id else None
    if key is not None:
        if key in _recent_lookup:
            return None
        pending = _inflight.get(key)
        if pending is not None:
            await asyncio.shield(pending)
            return None
        pending = asyncio.get_running_loop().create_future()
        _inflight[key] = pending
    try:
        try:
            await target.broadcast(SSE_CHANNEL, envelope, tenant_id=tenant_id)
        except Exception:
            logger.warning(
                "Workspace-SSE-Spiegel fehlgeschlagen: type=%s tenant=%s",
                envelope.get("event_type"), tenant_id, exc_info=True,
            )
            return None
        # Failed or cancelled attempts never consume the delivery identity.
        _remember_event_id(key)
        return envelope
    finally:
        if key is not None:
            _inflight.pop(key, None)
            if not pending.done():
                pending.set_result(None)



def _source_payload(source: Any) -> dict[str, Any]:
    if isinstance(source, dict):
        payload = source.get("payload")
        if isinstance(payload, dict):
            return payload
        return {key: value for key, value in source.items() if key != "payload"}
    payload = getattr(source, "payload", None)
    if isinstance(payload, dict):
        return payload
    return {}


def _source_tenant_id(source: Any, fallback: str | None = None) -> str | None:
    if fallback:
        return fallback
    if isinstance(source, dict):
        return source.get("tenant_id") or (source.get("payload") or {}).get("tenant_id")
    return getattr(source, "tenant_id", None)


def _source_event_id(source: Any) -> str | None:
    if isinstance(source, dict):
        return source.get("event_id") or source.get("id")
    return getattr(source, "event_id", None) or getattr(source, "id", None)


async def mirror_ist_event_to_workspace(
    source: Any,
    *,
    tenant_id: str | None = None,
    hub: Any | None = None,
) -> dict[str, Any] | None:
    """Publisher-/Hub-Adapter: erkennt Ist-Typ und spiegelt auf workspace."""
    resolved = resolve_ist_event_type(source)
    if resolved is None:
        return None
    tenant = _source_tenant_id(source, tenant_id)
    if not tenant:
        return None
    return await publish_workspace_sse(
        resolved,
        tenant_id=str(tenant),
        payload=_source_payload(source),
        event_id=_source_event_id(source),
        hub=hub,
    )


async def handle_nats_event_for_workspace(event: dict[str, Any], *, hub: Any | None = None) -> None:
    """NATS-Handler: Ist-Events additiv auf stream=workspace legen."""
    await mirror_ist_event_to_workspace(event, hub=hub)


def register_workspace_sse_mirror(consumer: Any) -> None:
    """Registriert Spiegel-Handler ohne NC-G3-Handler zu ersetzen."""
    for ist_type in IST_TO_SOLL:
        consumer.register_handler(ist_type, handle_nats_event_for_workspace)
    for class_name in CLASS_NAME_TO_IST:
        consumer.register_handler(class_name, handle_nats_event_for_workspace)
    consumer.register_default_handler(handle_nats_event_for_workspace)
