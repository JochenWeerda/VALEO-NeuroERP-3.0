"""Auto-generated domain schemas for contacts.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class ContactsOut(BaseSchema):
    """Response schema for contacts endpoints."""
    model_config = ConfigDict(extra="allow")


class ContactDetail(BaseSchema):
    id: str
    name: str
    company: str
    email: str
    phone: str
    type: str
    address: None
    notes: str | None
    position: str | None
    createdAt: str
    updatedAt: str


class ContactDetailOut(BaseSchema):
    data: ContactDetail
