"""One persisted DMS inbox model shared by the webhook and API routers."""

from __future__ import annotations

import base64
import os

from fastapi import HTTPException
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class DmsInboxEntry(Base):
    __tablename__ = "dms_inbox"
    __table_args__ = {"schema": "domain_shared"}

    id = Column(String, primary_key=True, default=uuid7)
    dms_document_id = Column(Integer, nullable=False)
    dms_url = Column(String(500), nullable=True)
    ocr_text = Column(Text, nullable=True)
    parsed_fields = Column(JSONB, nullable=True)
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    tenant_id = Column(String(120), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def verified_inbox_tenant(tenant_id: str) -> str:
    """Reject a missing verified tenant before any inbox query."""
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=403, detail="Verified tenant context required")
    return tenant_id.strip()


def require_connector_tenant(tenant_id: str) -> str:
    """The global Mayan token is bound to exactly one server-configured tenant."""
    tenant_id = verified_inbox_tenant(tenant_id)
    bound = (os.environ.get("DMS_TENANT_ID") or "").strip()
    if not bound:
        raise HTTPException(status_code=503, detail="DMS tenant binding is not configured")
    if tenant_id != bound:
        raise HTTPException(status_code=404, detail="DMS document not found")
    return tenant_id


def inbox_id_for_document(tenant_id: str, document_id: int) -> str:
    """Reversible, delimiter-safe identity; unlike legacy INBOX-N it cannot collide across tenants."""
    encoded = base64.urlsafe_b64encode(tenant_id.encode("utf-8")).decode("ascii").rstrip("=")
    return f"INBOX-v2-{encoded}-{document_id}"


def booking_not_from_inbox(inbox_id: str) -> HTTPException:
    """OCR is prefill only; an actual Beleg belongs to the domain mask/command."""
    return HTTPException(
        status_code=409,
        detail={
            "code": "booking_not_from_inbox",
            "message": "No Beleg was created. Open the purchase invoice mask and submit its domain command.",
            "open_mask": "/einkauf/rechnung-eingang-erfassung",
            "prepare_path": f"/api/mcp/documents/inbox/{inbox_id}/prepare",
        },
    )
