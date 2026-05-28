"""Pydantic schemas for the sales credit notes domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class CreditNoteLineOut(CreditNoteLineInput):
    id: str
    line_total: Decimal


class CreditNoteCreate(CreditNoteBase):
    tenant_id: Optional[str] = None


class CreditNoteOut(CreditNoteBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReturnCreate(ReturnBase):
    tenant_id: Optional[str] = None


class ReturnOut(ReturnBase):
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

