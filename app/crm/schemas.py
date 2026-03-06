"""
CRM Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ContactType(str, Enum):
    customer = "customer"
    supplier = "supplier"
    lead = "lead"


class LeadPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class LeadStatus(str, Enum):
    new = "new"
    qualified = "qualified"
    converted = "converted"
    lost = "lost"


class ActivityType(str, Enum):
    call = "call"
    email = "email"
    meeting = "meeting"
    visit = "visit"


class ActivityStatus(str, Enum):
    planned = "planned"
    completed = "completed"
    cancelled = "cancelled"


# --- Contact Schemas ---

class ContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    type: ContactType = ContactType.customer
    address_street: Optional[str] = None
    address_zip: Optional[str] = None
    address_city: Optional[str] = None
    address_country: str = "Deutschland"
    notes: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    type: Optional[ContactType] = None
    address_street: Optional[str] = None
    address_zip: Optional[str] = None
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    notes: Optional[str] = None


class Contact(ContactBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Lead Schemas ---

class LeadBase(BaseModel):
    company: str = Field(..., min_length=1, max_length=255)
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    potential: float = 0
    priority: LeadPriority = LeadPriority.medium
    status: LeadStatus = LeadStatus.new
    assigned_to: Optional[str] = None
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadAssignBody(BaseModel):
    assigned_to: str = Field(..., min_length=1)


class LeadUpdate(BaseModel):
    company: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    potential: Optional[float] = None
    priority: Optional[LeadPriority] = None
    status: Optional[LeadStatus] = None
    assigned_to: Optional[str] = None
    expected_close_date: Optional[datetime] = None
    notes: Optional[str] = None


class Lead(LeadBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Activity Schemas ---

class ActivityBase(BaseModel):
    contact_id: Optional[str] = None
    type: ActivityType
    date: datetime
    subject: Optional[str] = None
    notes: Optional[str] = None
    status: ActivityStatus = ActivityStatus.planned
    created_by: Optional[str] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    contact_id: Optional[str] = None
    type: Optional[ActivityType] = None
    date: Optional[datetime] = None
    subject: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[ActivityStatus] = None


class Activity(ActivityBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- BetriebsProfil Schemas ---

class BetriebsProfilBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    betriebsform: Optional[str] = None
    flaeche_ha: Optional[float] = None
    tierbestand: Optional[int] = None
    contact_id: Optional[str] = None
    notes: Optional[str] = None


class BetriebsProfilCreate(BetriebsProfilBase):
    pass


class BetriebsProfilUpdate(BaseModel):
    name: Optional[str] = None
    betriebsform: Optional[str] = None
    flaeche_ha: Optional[float] = None
    tierbestand: Optional[int] = None
    contact_id: Optional[str] = None
    notes: Optional[str] = None


class BetriebsProfil(BetriebsProfilBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Opportunity Schemas ---

class OpportunityStage(str, Enum):
    prospecting = "prospecting"
    qualification = "qualification"
    initial_contact = "initial_contact"
    needs_analysis = "needs_analysis"
    proposal = "proposal"
    negotiation = "negotiation"
    negotiation_review = "negotiation_review"
    closed_won = "closed_won"
    closed_lost = "closed_lost"


STAGE_PROBABILITY = {
    "prospecting": 10,
    "qualification": 20,
    "initial_contact": 30,
    "needs_analysis": 40,
    "proposal": 60,
    "negotiation": 75,
    "negotiation_review": 85,
    "closed_won": 100,
    "closed_lost": 0,
}


class OpportunityBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    customer_id: str
    description: Optional[str] = None
    product_category: Optional[str] = None
    estimated_value: Optional[float] = None
    estimated_quantity: Optional[float] = None
    currency: str = "EUR"
    stage: OpportunityStage = OpportunityStage.prospecting
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    source: Optional[str] = None
    competitors: Optional[list] = None


class OpportunityCreate(OpportunityBase):
    pass


class OpportunityLinkBody(BaseModel):
    sales_offer_id: Optional[str] = None
    sales_order_id: Optional[str] = None


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    customer_id: Optional[str] = None
    description: Optional[str] = None
    product_category: Optional[str] = None
    estimated_value: Optional[float] = None
    estimated_quantity: Optional[float] = None
    currency: Optional[str] = None
    stage: Optional[OpportunityStage] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    source: Optional[str] = None
    competitors: Optional[list] = None
    loss_reason: Optional[str] = None
    sales_offer_id: Optional[str] = None
    sales_order_id: Optional[str] = None


class Opportunity(OpportunityBase):
    id: str
    tenant_id: str
    status: str = "aktiv"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PipelineStageInfo(BaseModel):
    key: str
    label: str
    probability: int
    order: int


# --- Consent Schemas ---

class ConsentChannel(str, Enum):
    email = "email"
    phone = "phone"
    sms = "sms"
    post = "post"
    all = "all"


class ConsentBase(BaseModel):
    partner_id: str
    channel: ConsentChannel
    purpose: str = Field(..., min_length=1, max_length=200)
    granted: bool = True
    source: str = "manual"
    ip_address: Optional[str] = None
    notes: Optional[str] = None


class ConsentCreate(ConsentBase):
    pass


class ConsentResponse(ConsentBase):
    id: str
    tenant_id: str
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Segment Schemas ---

class SegmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    criteria: Optional[dict] = None
    segment_type: str = "static"


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[dict] = None
    segment_type: Optional[str] = None


class Segment(SegmentBase):
    id: str
    tenant_id: str
    member_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

