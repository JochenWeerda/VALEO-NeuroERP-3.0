from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models import CustomerStatus, CustomerType
from app.schemas.base import ORMModel, Timestamped


class CustomerCreate(BaseModel):
    display_name: str = Field(..., max_length=255)
    type: CustomerType = CustomerType.COMPANY
    status: CustomerStatus = CustomerStatus.PROSPECT
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    industry: str | None = None
    region: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    status: CustomerStatus | None = None
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    industry: str | None = None
    region: str | None = None
    notes: str | None = None
    lead_score: float | None = Field(default=None, ge=0, le=1)
    churn_score: float | None = Field(default=None, ge=0, le=1)


class CustomerRead(Timestamped):
    id: UUID
    tenant_id: UUID
    display_name: str
    type: CustomerType
    status: CustomerStatus
    email: str | None
    phone: str | None
    industry: str | None
    region: str | None
    lead_score: float | None
    churn_score: float | None
    notes: str | None


class CustomerListResponse(BaseModel):
    items: list[CustomerRead]
    total: int
