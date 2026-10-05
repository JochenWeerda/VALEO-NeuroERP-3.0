"""Response-Schemas fuer Abrechnungsstapel (Maker-Checker-Lauf).

SPEC-P1-06 Welle 4: ersetzt ``response_model=dict`` bzw. ``list[dict]`` in
``app/api/v1/endpoints/billing_batch.py``.

Feldlisten aus ``billing_batch_service``. Die Listenabfragen benennen ihre
Spalten explizit im SELECT, daher sind die Schemas exakt ableitbar.

Die vier Statusaktionen (validate / release / execute / retry) liefern
unterschiedlich viele Felder desselben Grundmusters ``{id, status, ...}``; sie
teilen sich deshalb ein Schema mit optionalen Zusatzfeldern.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class BatchOut(BaseSchema):
    """Kopfzeile eines Abrechnungsstapels."""

    id: Optional[str] = None
    batch_number: Optional[str] = None
    batch_type: Optional[str] = None
    status: Optional[str] = Field(
        default=None,
        description="draft | validated | released | running | partial_failed | completed",
    )
    description: Optional[str] = None
    maker: Optional[str] = Field(default=None, description="Ersteller (Vier-Augen-Prinzip)")
    checker: Optional[str] = Field(default=None, description="Freigebender")
    currency: Optional[str] = None
    total_lines: Optional[int] = None
    processed_lines: Optional[int] = None
    failed_lines: Optional[int] = None
    total_amount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BatchLineOut(BaseSchema):
    """Positionszeile eines Abrechnungsstapels."""

    id: Optional[str] = None
    batch_id: Optional[str] = None
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    source_number: Optional[str] = None
    source_route: Optional[str] = None
    evidence_route: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    validation_error: Optional[str] = None
    retry_count: Optional[int] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class BatchCreatedOut(BaseSchema):
    """``POST /billing-batches`` — Antwort der Neuanlage."""

    id: str
    batch_number: Optional[str] = None
    status: Optional[str] = None
    total_lines: Optional[int] = None
    total_amount: Optional[float] = None


class BatchPageOut(BaseSchema):
    """``GET /billing-batches`` — seitenweise Stapelliste."""

    items: list[BatchOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class BatchSummaryOut(BaseSchema):
    """``GET /billing-batches/summary`` — Zaehlung je Status."""

    draft: Optional[int] = None
    validated: Optional[int] = None
    released: Optional[int] = None
    running: Optional[int] = None
    partial_failed: Optional[int] = None
    failed_lines: Optional[int] = Field(
        default=None, description="Summe fehlgeschlagener Positionen ueber alle Stapel"
    )


class BatchActionOut(BaseSchema):
    """Antwort der Statusaktionen.

    ``validate`` liefert zusaetzlich ``failed_lines``, ``execute`` zusaetzlich
    ``processed_lines`` und ``failed_lines``; ``release`` und ``retry`` nur
    ``id`` und ``status``.
    """

    id: str
    status: str
    failed_lines: Optional[int] = None
    processed_lines: Optional[int] = None
