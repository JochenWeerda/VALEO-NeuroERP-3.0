"""Journal-Service mit GoBD-Logging & Event-Erzeugung."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Dict
from uuid import UUID, uuid4

from finance_shared.events import BookingCreatedEvent, serialize_event
from finance_shared.gobd import GoBDAuditTrail

logger = logging.getLogger(__name__)


class JournalService:
    """Enkapsuliert GoBD-Audit und Event-Erzeugung."""

    def __init__(self, audit_trail: GoBDAuditTrail) -> None:
        self._audit_trail = audit_trail

    def create_entry(self, payload: Dict[str, Any], *, user_id: str) -> Dict[str, Any]:
        booking_uuid = self._resolve_booking_id(payload)

        entry = self._audit_trail.create_entry(
            entity_type="journal_entry",
            entity_id=str(booking_uuid),
            action="create",
            payload=payload,
            user_id=user_id,
        )
        self._audit_trail.append_entry(entry)

        event = BookingCreatedEvent.from_values(
            tenant_id=self._audit_trail.tenant_id,
            booking_id=booking_uuid,
            account_id=payload.get("account_id", ""),
            amount=Decimal(str(payload.get("amount", "0"))),
            currency=payload.get("currency", "EUR"),
            period=payload.get("period", ""),
            document_id=payload.get("document_id"),
            approved=payload.get("approved", False),
        )
        serialized_event = serialize_event(event)
        logger.info("JournalEntry gespeichert", extra={"event": serialized_event})
        return {"journal": payload, "event": serialized_event, "audit_entry": entry.model_dump()}

    def _resolve_booking_id(self, payload: Dict[str, Any]) -> UUID:
        raw = payload.get("id")
        if raw:
            try:
                booking_uuid = UUID(str(raw))
                payload["id"] = str(booking_uuid)
                return booking_uuid
            except ValueError:
                pass
        booking_uuid = uuid4()
        payload["id"] = str(booking_uuid)
        return booking_uuid


