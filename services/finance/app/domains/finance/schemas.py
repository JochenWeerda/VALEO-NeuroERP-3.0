"""Pydantic schemas for Finance domain."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_number: str
    name: str
    category: str | None = None
    currency: str = "EUR"


class JournalEntryBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    account_id: str
    description: str
    amount: Decimal
    currency: str = "EUR"
    period: str = Field(pattern=r"^\d{4}-\d{2}$")
    document_id: str | None = None
    user_id: str = Field(alias="userId")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    description: str
    amount: Decimal
    currency: str
    period: str
    document_id: str | None
    posted_at: datetime
    created_by: str


class OpenItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_number: str
    customer_id: str
    customer_name: str
    amount: Decimal
    currency: str
    due_date: date
    status: str


class JournalEntryResponse(BaseModel):
    entry: JournalEntryRead
    audit_hash: str


class AccountsResponse(BaseModel):
    items: List[AccountRead]


class JournalEntriesResponse(BaseModel):
    items: List[JournalEntryRead]


class OpenItemsResponse(BaseModel):
    items: List[OpenItemRead]

