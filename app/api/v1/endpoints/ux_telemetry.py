"""UX-Telemetrie — Omnibox-Intent-Signale (UIX-060).

Nimmt datenschutzfreundliche Signale des Intent-Compilers entgegen: nur der
SHA-256-Hash des normalisierten Eingabetexts (kein Klartext), die getroffene
ScreenDefinition, die Konfidenz und ob der Vorschlag angenommen wurde. Dient als
Aggregat-Basis fuer das M2-Tuning (Synonyme/Schwellwerte). Tenant-isoliert,
in-memory (keine DB-Migration im M1-Scope).
"""
from __future__ import annotations

import re
from collections import defaultdict

from fastapi import APIRouter, Depends, Response
from pydantic import Field, field_validator

from ....core.tenant import get_tenant_id
from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/ux-telemetry", tags=["ui", "telemetry"])

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class OmniboxTelemetryIn(BaseSchema):
    """Ein Omnibox-Intent-Signal. intent_hash ist SHA-256(normalisierter Text)."""

    intent_hash: str = Field(..., description="SHA-256-Hex des normalisierten Eingabetexts")
    matched_screen_id: str | None = Field(default=None, description="Getroffene SD oder null")
    confidence: float = Field(..., ge=0.0, le=1.0)
    accepted: bool = Field(..., description="Wurde der Vorschlag via Enter/Klick angenommen?")

    @field_validator("intent_hash")
    @classmethod
    def _reject_cleartext(cls, value: str) -> str:
        # Erzwingt einen 64-stelligen Hex-Hash — verhindert versehentliches
        # Durchreichen von Klartext-Eingaben (Datenschutz-Vertrag M1).
        normalized = value.strip().lower()
        if not _SHA256_RE.match(normalized):
            raise ValueError("intent_hash muss ein SHA-256-Hex (64 Zeichen) sein — kein Klartext")
        return normalized


class OmniboxAggregateEntry(BaseSchema):
    matched_screen_id: str | None
    total: int
    accepted: int
    avg_confidence: float


class OmniboxAggregateOut(BaseSchema):
    entries: list[OmniboxAggregateEntry]


# tenant_id -> matched_screen_id -> [total, accepted, confidence_sum]
_AGGREGATE: dict[str, dict[str | None, list[float]]] = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0.0]))


@router.post(
    "/omnibox",
    status_code=204,
    response_class=Response,
    summary="Omnibox-Intent-Signal erfassen",
)
async def record_omnibox_signal(
    payload: OmniboxTelemetryIn,
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    """Erfasst ein anonymisiertes Omnibox-Signal (kein Klartext) fuer M2-Tuning."""
    bucket = _AGGREGATE[tenant_id][payload.matched_screen_id]
    bucket[0] += 1
    bucket[1] += 1 if payload.accepted else 0
    bucket[2] += payload.confidence
    return Response(status_code=204)


@router.get(
    "/omnibox/aggregate",
    response_model=OmniboxAggregateOut,
    summary="Aggregierte Omnibox-Signale abrufen",
)
async def get_omnibox_aggregate(tenant_id: str = Depends(get_tenant_id)) -> OmniboxAggregateOut:
    """Aggregat je getroffener Maske (Basis fuer Synonym-/Schwellwert-Tuning)."""
    per_screen = _AGGREGATE.get(tenant_id, {})
    entries = [
        OmniboxAggregateEntry(
            matched_screen_id=screen_id,
            total=int(stats[0]),
            accepted=int(stats[1]),
            avg_confidence=round(stats[2] / stats[0], 4) if stats[0] else 0.0,
        )
        for screen_id, stats in per_screen.items()
    ]
    entries.sort(key=lambda e: e.total, reverse=True)
    return OmniboxAggregateOut(entries=entries)
