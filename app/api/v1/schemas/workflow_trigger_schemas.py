"""Lesemodell der Workflow-Trigger-Regeln (Maske ``workflows/trigger``, 09.11.2026)."""
from __future__ import annotations

from typing import Optional

from app.api.v1.schemas.base import BaseSchema


class TriggerRegelOut(BaseSchema):
    trigger_id: str
    workflow_typ: str
    trigger_typ: str
    status: str
    bedingungen_anzahl: int
    beschreibung: Optional[str] = None
