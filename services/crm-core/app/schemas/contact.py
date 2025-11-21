from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.base import ORMModel


class ContactCreate(BaseModel):
    customer_id: UUID
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)


class ContactRead(ORMModel):
    id: UUID
    customer_id: UUID
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    job_title: str | None
    department: str | None
    customer_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ContactListResponse(BaseModel):
    items: list[ContactRead]
    total: int
