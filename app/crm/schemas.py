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

