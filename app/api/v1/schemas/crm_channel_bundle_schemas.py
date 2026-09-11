"""Response-Schemas fuer CRM-Kanaele (SPEC-P1-06 Welle 11).

Ersetzt schwache ``response_model`` in:
- ``mail_workspace.py``
- ``tapi.py``
- ``whatsapp_intake.py``
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Mail-Arbeitsplatz ───────────────────────────────────────────────────────


class MailMessageOut(BaseSchema):
    id: Optional[str] = None
    role_key: Optional[str] = None
    message_id: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None
    from_address: Optional[str] = None
    to_addresses: Optional[Any] = None
    subject: Optional[str] = None
    contact_id: Optional[str] = None
    document_type: Optional[str] = None
    document_ref: Optional[str] = None
    document_route: Optional[str] = None
    assigned_to: Optional[str] = None
    provider_ref: Optional[str] = None
    error_message: Optional[str] = None
    received_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    attachment_count: Optional[int] = None


class MailMessagePageOut(BaseSchema):
    items: list[MailMessageOut] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class MailAttachmentOut(BaseSchema):
    id: Optional[str] = None
    message_id: Optional[str] = None
    filename: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    sha256: Optional[str] = None
    transfer_status: Optional[str] = None
    dms_document_id: Optional[str] = None
    created_at: Optional[datetime] = None
    subject: Optional[str] = None
    role_key: Optional[str] = None


class MailDraftCreatedOut(BaseSchema):
    id: Optional[str] = None
    status: Optional[str] = None
    message_id: Optional[str] = None


class MailAssignOut(BaseSchema):
    id: Optional[str] = None
    status: Optional[str] = None
    contact_id: Optional[str] = None
    document_type: Optional[str] = None
    document_ref: Optional[str] = None
    document_route: Optional[str] = None
    assigned_to: Optional[str] = None


class MailQueueOut(BaseSchema):
    id: Optional[str] = None
    status: Optional[str] = None
    provider_ref: Optional[str] = None


class MailTransferOut(BaseSchema):
    id: Optional[str] = None
    status: Optional[str] = None
    dms_document_id: Optional[str] = None


# ── TAPI ────────────────────────────────────────────────────────────────────


class TapiCallOut(BaseSchema):
    id: Optional[str] = None
    caller: Optional[str] = None
    called: Optional[str] = None
    richtung: Optional[str] = None
    kunden_nr: Optional[str] = None
    kunde_name: Optional[str] = None
    status: Optional[str] = None
    acked: Optional[bool] = None
    created_at: Optional[str] = None


class TapiAckOut(BaseSchema):
    ok: Optional[bool] = None


# ── WhatsApp Bestell-Inbox ──────────────────────────────────────────────────


class WhatsAppInboxOut(BaseSchema):
    id: Optional[str] = None
    raw_text: Optional[str] = None
    absender: Optional[str] = None
    quelle: Optional[str] = None
    eingegangen_am: Optional[str] = None
    status: Optional[str] = None
    parsed: Optional[Any] = None
    kunden_nr: Optional[str] = None
    kunde_text: Optional[str] = None
    beleg_typ: Optional[str] = None
    beleg_ref: Optional[str] = None
    engine: Optional[str] = None
    confidence: Optional[float] = None
