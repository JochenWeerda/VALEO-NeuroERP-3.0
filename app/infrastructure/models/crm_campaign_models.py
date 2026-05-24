"""
CRM Campaign Models
Campaigns, Campaign Templates, Campaign Recipients
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.uuid7 import uuid7
from app.core.database import Base


class CrmCampaignTemplate(Base):
    """Wiederverwendbare Kampagnen-Vorlagen"""
    __tablename__ = "crm_campaign_templates"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    campaign_type = Column(String(50), nullable=False, default="email")
    subject_line = Column(String(500), nullable=True)
    message_body = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(String, nullable=True)
    meta = Column(JSONB, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CrmCampaign(Base):
    """Kampagnen-Instanzen"""
    __tablename__ = "crm_campaigns"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # draft | active | paused | completed | archived
    state = Column(String(20), nullable=False, default="draft")
    campaign_type = Column(String(50), nullable=False, default="email")
    template_id = Column(String, nullable=True)
    segment_id = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    budget = Column(DECIMAL(12, 2), nullable=True)
    owner_id = Column(String, nullable=True)
    # KPI-Aggregationen (nächtlich neu berechnet)
    total_sent = Column(Integer, nullable=False, default=0)
    total_delivered = Column(Integer, nullable=False, default=0)
    total_bounced = Column(Integer, nullable=False, default=0)
    total_opens = Column(Integer, nullable=False, default=0)
    total_clicks = Column(Integer, nullable=False, default=0)
    total_conversions = Column(Integer, nullable=False, default=0)
    revenue_generated = Column(DECIMAL(12, 2), nullable=False, default=0)
    # Zeitstempel State-Machine
    activated_at = Column(DateTime(timezone=True), nullable=True)
    paused_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    # Agrar-spezifische Felder
    campaign_channel = Column(String(50), nullable=True)       # email, sms, post, event
    target_customer_type = Column(String(50), nullable=True)   # farm, merchant, member
    seasonal_context = Column(String(50), nullable=True)       # harvest, planting, off_season
    meta = Column(JSONB, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CrmCampaignRecipient(Base):
    """Empfänger-Tracking pro Kampagne"""
    __tablename__ = "crm_campaign_recipients"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=uuid7)
    tenant_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=False, index=True)
    recipient_id = Column(String, nullable=False)
    recipient_type = Column(String(50), nullable=False, default="contact")
    # queued | sent | bounced | opened | clicked | converted | unsubscribed
    status = Column(String(20), nullable=False, default="queued")
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    bounce_reason = Column(String(255), nullable=True)
    meta = Column(JSONB, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
