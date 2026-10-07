"""Tenant-bound lead CRUD and qualification on public.crm_leads."""
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema, PaginatedResponse
from app.auth.deps import require_roles
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services import crm_lead_service as service
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

read_leads = require_roles("CRM_LESEN", "CRM_BEARBEITEN", "CRM_ADMIN", "admin", "manager")
write_leads = require_roles("CRM_BEARBEITEN", "CRM_ADMIN", "admin", "manager")
router = APIRouter()


class LeadData(BaseSchema):
    company_name: str = Field(min_length=1, max_length=255)
    contact_person: str | None = Field(None, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    source: str = Field("unknown", max_length=100)
    status: str = "NEW"
    priority: str = Field("medium", max_length=20)
    estimated_value: Decimal | None = Field(None, ge=0)
    assigned_to: str | None = Field(None, max_length=100)


class LeadCreate(LeadData):
    tenant_id: str | None = None  # accepted for old clients; context is authoritative


class Lead(LeadData):
    id: str
    tenant_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    qualified_opportunity_id: str | None = None


class LeadUpdate(BaseSchema):
    company_name: str | None = Field(None, min_length=1, max_length=255)
    contact_person: str | None = Field(None, max_length=255)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    source: str | None = Field(None, max_length=100)
    status: str | None = None
    priority: str | None = Field(None, max_length=20)
    estimated_value: Decimal | None = Field(None, ge=0)
    assigned_to: str | None = Field(None, max_length=100)


def unavailable(db):
    db.rollback()
    return HTTPException(503, "Lead-Daten konnten nicht gespeichert oder gelesen werden.")


@router.get("", response_model=PaginatedResponse[Lead], dependencies=[Depends(read_leads)], include_in_schema=True)
@router.get("/", response_model=PaginatedResponse[Lead], summary="Leads auflisten", dependencies=[Depends(read_leads)])
async def list_leads(status_filter: str | None = Query(None, alias="status"), search: str | None = None,
                     skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000),
                     db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    try:
        items, total = service.list_rows(db, tenant_id, status_filter, search, skip, limit)
    except SQLAlchemyError as exc:
        raise unavailable(db) from exc
    return PaginatedResponse[Lead](items=items, total=total, page=skip//limit+1, size=limit,
                                  pages=(total+limit-1)//limit, has_next=skip+limit<total, has_prev=skip>0)


@router.get("/{lead_id}", response_model=Lead, summary="Lead abrufen", dependencies=[Depends(read_leads)])
async def get_lead(lead_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    try:
        return service.project(service.get_row(db, tenant_id, lead_id))
    except SQLAlchemyError as exc:
        raise unavailable(db) from exc


@router.post("", response_model=Lead, status_code=201, dependencies=[Depends(write_leads)], include_in_schema=True)
@router.post("/", response_model=Lead, status_code=201, summary="Lead anlegen", dependencies=[Depends(write_leads)])
async def create_lead(payload: LeadCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    try:
        result = service.create(db, tenant_id, payload.model_dump(exclude={"tenant_id"}))
        db.commit()
        return result
    except SQLAlchemyError as exc:
        raise unavailable(db) from exc


@router.put("/{lead_id}", response_model=Lead, summary="Lead aktualisieren", dependencies=[Depends(write_leads)])
async def update_lead(lead_id: str, payload: LeadUpdate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    if "company_name" in payload.model_fields_set and payload.company_name is None:
        raise HTTPException(422, "Unternehmen darf nicht leer sein.")
    try:
        result = service.update(db, tenant_id, lead_id, payload.model_dump(exclude_unset=True))
        db.commit()
        return result
    except (HTTPException, SQLAlchemyError) as exc:
        db.rollback()
        if isinstance(exc, HTTPException):
            raise
        raise unavailable(db) from exc


@router.delete("/{lead_id}", status_code=204, response_model=None, summary="Lead loeschen", dependencies=[Depends(write_leads)])
async def delete_lead(lead_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    try:
        service.get_row(db, tenant_id, lead_id, lock=True)
        db.execute(text("DELETE FROM public.crm_leads WHERE id::text = :id AND tenant_id = :tid"), {"id": lead_id, "tid": tenant_id})
        db.commit()
        return Response(status_code=204)
    except (HTTPException, SQLAlchemyError) as exc:
        db.rollback()
        if isinstance(exc, HTTPException):
            raise
        raise unavailable(db) from exc


@router.post("/{entity_id}/actions/qualifizieren", response_model=MaskActionResult,
            summary="Lead als Opportunity qualifizieren", dependencies=[Depends(write_leads)])
async def qualify_lead(entity_id: str, body: dict = Body(default_factory=dict),
                       db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    async def check(session, payload, lead_id, tenant):
        service.qualification_inputs(session, tenant, lead_id, str(payload.get("customer_id") or ""))
        return []

    async def execute(session, payload, lead_id, tenant):
        opportunity = service.qualify(session, tenant, lead_id, str(payload.get("customer_id") or ""))
        return f"Lead qualifiziert; Opportunity {opportunity} angelegt."

    return await run_delegated_mask_action(db, action_key="qualifizieren", entity_type="lead",
        entity_id=entity_id, tenant_id=tenant_id, body=body, check_fn=check, delegate_fn=execute,
        outbox_event_type="crm.lead.qualified")
