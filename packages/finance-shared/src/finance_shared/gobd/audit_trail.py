"""Audit-Trail-Utilities inkl. Hash-Chain-Validierung."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Sequence
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def compute_entry_hash(entry_payload: dict, previous_hash: str | None = None) -> str:
    """Bildet einen Hash über Payload + Vorgänger-Hash."""
    hasher = hashlib.sha256()
    if previous_hash:
        hasher.update(previous_hash.encode("utf-8"))
    hasher.update(json.dumps(entry_payload, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return hasher.hexdigest()


class AuditTrailEntry(BaseModel):
    """Repräsentiert einen einzelnen Audit-Trail-Eintrag."""

    entry_id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    entity_type: str
    entity_id: str
    action: str
    payload: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    user_id: str
    previous_hash: str | None = None
    hash: str


class HashVerificationError(RuntimeError):
    """Wird geworfen, wenn eine Hash-Kette beschädigt ist."""


@dataclass
class GoBDAuditTrail:
    """Minimale Hash-Chain-Verwaltung für Services ohne eigene Persistenz."""

    tenant_id: str
    _entries: List[AuditTrailEntry] = field(default_factory=list)

    def create_entry(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        payload: dict,
        user_id: str,
    ) -> AuditTrailEntry:
        previous_hash = self._entries[-1].hash if self._entries else None
        entry_payload = {
            "tenant_id": self.tenant_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "payload": payload,
            "user_id": user_id,
        }
        entry_hash = compute_entry_hash(entry_payload, previous_hash)
        return AuditTrailEntry(
            tenant_id=self.tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            payload=payload,
            user_id=user_id,
            previous_hash=previous_hash,
            hash=entry_hash,
        )

    def append_entry(self, entry: AuditTrailEntry) -> None:
        if self._entries and entry.previous_hash != self._entries[-1].hash:
            raise HashVerificationError("Vorgänger-Hash stimmt nicht überein.")
        self._entries.append(entry)

    def entries(self) -> Sequence[AuditTrailEntry]:
        return tuple(self._entries)

    def verify_chain(self, entries: Iterable[AuditTrailEntry] | None = None) -> None:
        data = list(entries or self._entries)
        previous_hash = None
        for entry in data:
            expected_hash = compute_entry_hash(
                {
                    "tenant_id": entry.tenant_id,
                    "entity_type": entry.entity_type,
                    "entity_id": entry.entity_id,
                    "action": entry.action,
                    "payload": entry.payload,
                    "user_id": entry.user_id,
                },
                previous_hash,
            )
            if entry.hash != expected_hash:
                raise HashVerificationError("Hash-Kette beschädigt.")
            previous_hash = entry.hash


