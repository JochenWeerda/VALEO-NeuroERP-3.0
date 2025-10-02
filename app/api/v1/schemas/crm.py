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