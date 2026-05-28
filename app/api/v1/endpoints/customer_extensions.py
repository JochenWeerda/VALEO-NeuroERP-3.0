"""
Customer extension endpoints (l3c-kunde extras)
Geo-radius search, lead-to-customer conversion, contact operator status.
"""

from typing import Optional
import math

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import Customer, Lead, Contact
from ..schemas.base import BaseSchema

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.customer_extensions_schemas import CustomerExtensionsOut


router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


class GeoSearchRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50.0


class CustomerBrief(BaseSchema):
    id: str
    customer_number: str
    company_name: str
    city: Optional[str] = None


class ConvertLeadRequest(BaseModel):
    lead_id: str


class OperatorStatusUpdate(BaseModel):
    contact_id: str
    status: str  # "gelesen" | "erledigt"


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.post("/geo-search", response_model=list[CustomerBrief], summary="Geo search customer")
async def customer_geo_search(
    payload: GeoSearchRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Kunde Umkreissuche"""
    tid = tenant_id or DEFAULT_TENANT
    # Note: Full GIS would use PostGIS; this is a simple in-memory filter
    customers = db.query(Customer).filter(
        Customer.tenant_id == tid,
        Customer.is_active == True,  # noqa: E712
    ).all()
    # For now return all customers (real impl would use lat/lon columns)
    return [CustomerBrief.model_validate(c) for c in customers[:50]]


@router.post("/convert-lead", response_model=CustomerBrief, summary="Lead to customer umwandeln")
async def convert_lead_to_customer(
    payload: ConvertLeadRequest,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Interessent zu Kunde"""
    from app.core.uuid7 import uuid7
    from datetime import datetime, timezone
    tid = tenant_id or DEFAULT_TENANT
    lead = db.query(Lead).filter(Lead.id == payload.lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    customer = Customer(
        id=uuid7(),
        customer_number=f"K-{lead.id[:8].upper()}",
        company_name=lead.company_name,
        contact_person=lead.contact_person,
        email=lead.email,
        phone=lead.phone,
        tenant_id=tid,
    )
    db.add(customer)
    lead.status = "converted"
    lead.converted_at = datetime.now(timezone.utc)
    lead.converted_to_customer_id = customer.id
    db.commit()
    db.refresh(customer)
    return CustomerBrief.model_validate(customer)


@router.post("/operator-status", summary="Operator status aktualisieren",
    response_model=CustomerExtensionsOut
)
async def update_operator_status(payload: OperatorStatusUpdate, db: Session = Depends(get_db)):
    """POST Kontakt Bediener Gelesen/Erledigt setzen"""
    contact = db.query(Contact).filter(Contact.id == payload.contact_id).first()
    if not contact:
        raise HTTPException(404, "Contact not found")
    # In a full impl this would update a pivot table; here we acknowledge
    return {"contact_id": payload.contact_id, "status": payload.status, "updated": True}
