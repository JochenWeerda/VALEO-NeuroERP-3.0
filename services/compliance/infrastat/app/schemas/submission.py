"""Submission-bezogene Schemas."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SubmissionRequest(BaseModel):
    """Parameter für eine manuelle Übermittlung."""

    dry_run: bool = Field(default=False, description="Nur XML erzeugen, nicht an IDEV übermitteln.")
    override_reference: Optional[str] = Field(default=None, description="Optionaler Referenzcode für Übermittlung.")


class SubmissionResponse(BaseModel):
    """Antwort mit Status der Übermittlung."""

    batch_id: UUID
    status: str
    submission_id: UUID
    payload_hash: str
    success: bool
    endpoint: str
    reference_number: Optional[str] = None
    datml_res: Optional[str] = None
    dry_run: bool = False

