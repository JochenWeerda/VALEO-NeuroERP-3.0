"""CRM Einwilligungen (DSGVO) — Stamm in domain_crm."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.sql import func

from app.core.database import Base
from app.core.uuid7 import uuid7


class CrmConsent(Base):
    """Einwilligung eines Kontakts fuer einen Kanal (Double-Opt-in)."""

    __tablename__ = "crm_contact_consents"
    __table_args__ = (
        Index("ix_crm_contact_consents_tenant_contact", "tenant_id", "contact_id"),
        Index("ix_crm_contact_consents_tenant_status", "tenant_id", "status"),
        {"schema": "domain_crm"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False)
    contact_id = Column(String, nullable=False)
    channel = Column(String(20), nullable=False)
    consent_type = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    source = Column(String(20), nullable=False, default="manual")
    granted_at = Column(DateTime(timezone=True), nullable=True)
    denied_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    double_opt_in_token = Column(String, nullable=True, unique=True)
    double_opt_in_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    updated_by = Column(String(255), nullable=True)


class CrmConsentHistory(Base):
    """Revisionssichere Historie einer Einwilligung."""

    __tablename__ = "crm_contact_consent_history"
    __table_args__ = (
        Index("ix_crm_contact_consent_history_consent", "consent_id"),
        {"schema": "domain_crm"},
    )

    id = Column(String, primary_key=True, default=uuid7)
    consent_id = Column(
        String,
        ForeignKey("domain_crm.crm_contact_consents.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String(20), nullable=False)
    old_status = Column(String(20), nullable=True)
    new_status = Column(String(20), nullable=False)
    reason = Column(Text, nullable=True)
    changed_by = Column(String(255), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
