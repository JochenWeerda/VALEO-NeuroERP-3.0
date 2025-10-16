"""
CRM domain schemas for VALEO-NeuroERP
Schemas for customers, leads, and CRM-related entities
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, EmailStr
from decimal import Decimal

from .base import BaseSchema, TimestampMixin, SoftDeleteMixin


# Customer Schemas
class CustomerBase(BaseSchema):
    """Base customer schema"""
    customer_number: str = Field(..., min_length=1, max_length=50, description="Unique customer number")
    company_name: str = Field(..., min_length=1, max_length=100, description="Company name")
    contact_person: Optional[str] = Field(None, max_length=100, description="Primary contact person")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    address: Optional[str] = Field(None, max_length=200, description="Company address")
    city: Optional[str] = Field(None, max_length=50, description="City")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    country: Optional[str] = Field(None, max_length=50, description="Country")
    industry: Optional[str] = Field(None, max_length=50, description="Industry sector")
    website: Optional[str] = Field(None, max_length=100, description="Company website")


class CustomerCreate(CustomerBase):
    """Schema for creating a customer"""
    tenant_id: str = Field(..., description="Tenant ID")


class CustomerUpdate(BaseSchema):
    """Schema for updating a customer"""
    customer_number: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique customer number")
    company_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Company name")
    contact_person: Optional[str] = Field(None, max_length=100, description="Primary contact person")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    address: Optional[str] = Field(None, max_length=200, description="Company address")
    city: Optional[str] = Field(None, max_length=50, description="City")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    country: Optional[str] = Field(None, max_length=50, description="Country")
    industry: Optional[str] = Field(None, max_length=50, description="Industry sector")
    website: Optional[str] = Field(None, max_length=100, description="Company website")
    is_active: Optional[bool] = Field(None, description="Whether customer is active")


class Customer(CustomerBase, TimestampMixin, SoftDeleteMixin):
    """Full customer schema"""
    id: str = Field(..., description="Customer ID")
    tenant_id: str = Field(..., description="Tenant ID")
    credit_limit: Optional[Decimal] = Field(None, ge=0, description="Credit limit")
    payment_terms: Optional[str] = Field(None, max_length=50, description="Payment terms")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax identification number")


# Lead Schemas
class LeadBase(BaseSchema):
    """Base lead schema"""
    source: str = Field(..., max_length=50, description="Lead source")
    status: str = Field(..., max_length=20, description="Lead status")
    priority: str = Field(default="medium", max_length=10, description="Lead priority")
    estimated_value: Optional[Decimal] = Field(None, ge=0, description="Estimated deal value")
    company_name: str = Field(..., min_length=1, max_length=100, description="Company name")
    contact_person: str = Field(..., min_length=1, max_length=100, description="Contact person")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")


class LeadCreate(LeadBase):
    """Schema for creating a lead"""
    tenant_id: str = Field(..., description="Tenant ID")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")


class LeadUpdate(BaseSchema):
    """Schema for updating a lead"""
    source: Optional[str] = Field(None, max_length=50, description="Lead source")
    status: Optional[str] = Field(None, max_length=20, description="Lead status")
    priority: Optional[str] = Field(None, max_length=10, description="Lead priority")
    estimated_value: Optional[Decimal] = Field(None, ge=0, description="Estimated deal value")
    company_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Company name")
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100, description="Contact person")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")


class Lead(LeadBase, TimestampMixin, SoftDeleteMixin):
    """Full lead schema"""
    id: str = Field(..., description="Lead ID")
    tenant_id: str = Field(..., description="Tenant ID")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    converted_at: Optional[datetime] = Field(None, description="Conversion timestamp")
    converted_to_customer_id: Optional[str] = Field(None, description="Converted customer ID")


# Contact Schemas
class ContactBase(BaseSchema):
    """Base contact schema"""
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    position: Optional[str] = Field(None, max_length=50, description="Job position")
    department: Optional[str] = Field(None, max_length=50, description="Department")


class ContactCreate(ContactBase):
    """Schema for creating a contact"""
    customer_id: str = Field(..., description="Customer ID")


class ContactUpdate(BaseSchema):
    """Schema for updating a contact"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    position: Optional[str] = Field(None, max_length=50, description="Job position")
    department: Optional[str] = Field(None, max_length=50, description="Department")


class Contact(ContactBase, TimestampMixin, SoftDeleteMixin):
    """Full contact schema"""
    id: str = Field(..., description="Contact ID")
    customer_id: str = Field(..., description="Customer ID")


# Activity Schemas
class ActivityBase(BaseSchema):
    """Base activity schema"""
    type: str = Field(..., max_length=20, description="Activity type (meeting, call, email, note)")
    title: str = Field(..., min_length=1, max_length=200, description="Activity title")
    customer: str = Field(..., min_length=1, max_length=100, description="Customer name")
    contact_person: str = Field(..., min_length=1, max_length=100, description="Contact person")
    date: datetime = Field(..., description="Activity date")
    status: str = Field(..., max_length=20, description="Activity status (planned, completed, overdue)")
    assigned_to: str = Field(..., max_length=100, description="Assigned user")
    description: Optional[str] = Field(None, description="Activity description")


class ActivityCreate(ActivityBase):
    """Schema for creating an activity"""
    pass


class ActivityUpdate(BaseSchema):
    """Schema for updating an activity"""
    type: Optional[str] = Field(None, max_length=20, description="Activity type")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Activity title")
    customer: Optional[str] = Field(None, min_length=1, max_length=100, description="Customer name")
    contact_person: Optional[str] = Field(None, min_length=1, max_length=100, description="Contact person")
    date: Optional[datetime] = Field(None, description="Activity date")
    status: Optional[str] = Field(None, max_length=20, description="Activity status")
    assigned_to: Optional[str] = Field(None, max_length=100, description="Assigned user")
    description: Optional[str] = Field(None, description="Activity description")


class Activity(ActivityBase, TimestampMixin):
    """Full activity schema"""
    id: str = Field(..., description="Activity ID")


# Farm Profile Schemas
class CropItem(BaseSchema):
    """Crop item schema"""
    crop: str = Field(..., max_length=100, description="Crop name")
    area: float = Field(..., ge=0, description="Area in hectares")


class LivestockItem(BaseSchema):
    """Livestock item schema"""
    type: str = Field(..., max_length=100, description="Livestock type")
    count: int = Field(..., ge=0, description="Number of animals")


class LocationInfo(BaseSchema):
    """Location information schema"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: str = Field(..., max_length=500, description="Full address")


class FarmProfileBase(BaseSchema):
    """Base farm profile schema"""
    farm_name: str = Field(..., min_length=1, max_length=200, description="Farm name")
    owner: str = Field(..., min_length=1, max_length=100, description="Farm owner")
    total_area: float = Field(..., ge=0, description="Total area in hectares")
    crops: list[CropItem] = Field(default_factory=list, description="Crops grown")
    livestock: list[LivestockItem] = Field(default_factory=list, description="Livestock")
    location: Optional[LocationInfo] = Field(None, description="Farm location")
    certifications: list[str] = Field(default_factory=list, description="Certifications")
    notes: Optional[str] = Field(None, description="Additional notes")


class FarmProfileCreate(FarmProfileBase):
    """Schema for creating a farm profile"""
    pass


class FarmProfileUpdate(BaseSchema):
    """Schema for updating a farm profile"""
    farm_name: Optional[str] = Field(None, min_length=1, max_length=200, description="Farm name")
    owner: Optional[str] = Field(None, min_length=1, max_length=100, description="Farm owner")
    total_area: Optional[float] = Field(None, ge=0, description="Total area in hectares")
    crops: Optional[list[CropItem]] = Field(None, description="Crops grown")
    livestock: Optional[list[LivestockItem]] = Field(None, description="Livestock")
    location: Optional[LocationInfo] = Field(None, description="Farm location")
    certifications: Optional[list[str]] = Field(None, description="Certifications")
    notes: Optional[str] = Field(None, description="Additional notes")


class FarmProfile(FarmProfileBase, TimestampMixin):
    """Full farm profile schema"""
    id: str = Field(..., description="Farm profile ID")