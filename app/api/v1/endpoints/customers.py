"""CRM Customer endpoints backed by the crm-core service."""

from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import Optional, Union
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.data_quality_enforcement import build_dq_error_detail, evaluate_customer_datensatz
from ....core.database import get_db
from ....integrations.crm_core_client import (
    CRMCoreCustomer,
    create_customer as crm_create_customer,
    delete_customer as crm_delete_customer,
    get_customer as crm_get_customer,
    list_customers as crm_list_customers,
    update_customer as crm_update_customer,
)
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _build_customer_dq_datensatz(data: dict[str, object]) -> dict[str, object]:
    return {
        "debitor_nr": data.get("customer_number"),
        "name": data.get("company_name"),
        "land": data.get("country") or "DE",
    }


@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(customer_data: CustomerCreate) -> Customer:
    """Create a new customer via crm-core."""
    dq_result = evaluate_customer_datensatz(_build_customer_dq_datensatz(customer_data.model_dump(mode="python")))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Debitor", dq_result))
    payload = _map_create_payload(customer_data)
    try:
        created = await crm_create_customer(payload)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network errors handled uniformly
        raise _to_http_exception(exc) from exc
    return _adapt_customer(created)


@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in display name"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Customer]:
    """List customers from database directly (fallback if crm-core unavailable)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    
    # Try crm-core first, but fallback to direct database access if unavailable
    try:
        core_customers, total = await crm_list_customers(skip=skip, limit=limit, search=search)
        items = [_adapt_customer(customer) for customer in core_customers]
        pages = ceil(total / limit) if total else 1
        return PaginatedResponse[Customer](
            items=items,
            total=total,
            page=(skip // limit) + 1,
            size=limit,
            pages=pages,
            has_next=(skip + limit) < total,
            has_prev=skip > 0,
        )
    except (httpx.HTTPStatusError, httpx.ConnectError, Exception) as exc:
        # Fallback: Read directly from database
        from ....infrastructure.models import Customer as CustomerModel
        from sqlalchemy import or_
        
        # Log the fallback for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"crm-core unavailable, falling back to direct database access: {type(exc).__name__}: {exc}")
        
        try:
            # Use raw SQL to avoid ORM issues with missing columns
            from sqlalchemy import text
            
            # Build WHERE clause
            where_clauses = []
            params = {}
            
            if tenant_id:
                where_clauses.append("tenant_id = :tenant_id")
                params["tenant_id"] = effective_tenant
            
            if search:
                where_clauses.append("(company_name ILIKE :search OR customer_number ILIKE :search OR email ILIKE :search)")
                params["search"] = f"%{search}%"
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Count total
            count_sql = f"SELECT COUNT(*) FROM domain_crm.customers WHERE {where_sql}"
            total = db.execute(text(count_sql), params).scalar_one()
            
            # Fetch customers - only select columns that exist in the database
            select_sql = f"""
                SELECT 
                    id, tenant_id, customer_number, company_name, contact_person, 
                    email, phone, address, customer_type,
                    credit_limit, payment_terms, is_active, chefanweisung,
                    created_at, updated_at
                FROM domain_crm.customers 
                WHERE {where_sql}
                ORDER BY company_name DESC
                LIMIT :limit OFFSET :offset
            """
            params["limit"] = limit
            params["offset"] = skip
            
            rows = db.execute(text(select_sql), params).fetchall()
            
            # Map to Customer schema
            items = []
            for row in rows:
                try:
                    # Parse address JSONB if it exists
                    address_data = None
                    city = None
                    postal_code = None
                    country = None
                    address_str = None
                    if row.address:
                        if isinstance(row.address, dict):
                            address_data = row.address
                            city = address_data.get('city')
                            postal_code = address_data.get('postal_code')
                            country = address_data.get('country')
                            address_str = address_data.get('street') or str(address_data)
                        elif isinstance(row.address, str):
                            try:
                                import json
                                address_data = json.loads(row.address)
                                city = address_data.get('city')
                                postal_code = address_data.get('postal_code')
                                country = address_data.get('country')
                                address_str = address_data.get('street') or row.address
                            except:
                                address_str = row.address
                    
                    # Parse payment_terms (can be string or int)
                    payment_terms_val = 30
                    if row.payment_terms:
                        try:
                            payment_terms_val = int(row.payment_terms) if str(row.payment_terms).isdigit() else 30
                        except:
                            payment_terms_val = 30
                    
                    customer_dict = {
                        "id": str(row.id),
                        "tenant_id": UUID(str(row.tenant_id)) if row.tenant_id else UUID(DEFAULT_TENANT),
                        "customer_number": row.customer_number or f"CUST-{str(row.id)[:8].upper()}",
                        "company_name": row.company_name or "",
                        "name": row.company_name or "",
                        "contact_person": row.contact_person,
                        "email": row.email,
                        "phone": row.phone,
                        "address": address_str,
                        "city": city,
                        "postal_code": postal_code,
                        "country": country,
                        "industry": None,  # Column doesn't exist in DB
                        "website": None,  # Column doesn't exist in DB
                        "credit_limit": float(row.credit_limit) if row.credit_limit is not None else None,
                        "payment_terms": payment_terms_val,
                        "tax_id": None,  # Column doesn't exist in DB
                        "chefanweisung": getattr(row, 'chefanweisung', None),  # Chefanweisung from customer table
                        "is_active": row.is_active if row.is_active is not None else True,
                        "deleted_at": None,  # Column doesn't exist in DB
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    }
                    items.append(Customer.model_validate(customer_dict))
                except Exception as map_err:
                    logger.error(f"Error mapping customer {row.id}: {map_err}")
                    continue
            
            pages = ceil(total / limit) if total else 1
            return PaginatedResponse[Customer](
                items=items,
                total=total,
                page=(skip // limit) + 1,
                size=limit,
                pages=pages,
                has_next=(skip + limit) < total,
                has_prev=skip > 0,
            )
        except Exception as db_err:
            logger.error(f"Database fallback error: {db_err}", exc_info=True)
            # Return empty result instead of crashing
            return PaginatedResponse[Customer](
                items=[],
                total=0,
                page=1,
                size=limit,
                pages=1,
                has_next=False,
                has_prev=False,
            )


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
) -> Customer:
    """Return a customer by ID."""
    try:
        customer = await crm_get_customer(customer_id)
        adapted = _adapt_customer(customer)
        
        # Try to load chefanweisung from database directly
        try:
            from sqlalchemy import text
            
            # Try to find customer in database and load chefanweisung
            db_customer = db.execute(
                text("SELECT chefanweisung FROM domain_crm.customers WHERE id = :customer_id"),
                {"customer_id": customer_id}
            ).fetchone()
            
            if db_customer and db_customer.chefanweisung:
                # Update the adapted customer with chefanweisung
                customer_dict = adapted.model_dump()
                customer_dict["chefanweisung"] = db_customer.chefanweisung
                adapted = Customer.model_validate(customer_dict)
        except Exception as db_err:
            # If database lookup fails, continue without chefanweisung
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Could not load chefanweisung for customer {customer_id}: {db_err}")
        
        return adapted
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerUpdate) -> Customer:
    """Update customer details by delegating to crm-core."""
    data = customer_data.model_dump(exclude_unset=True, mode="python")
    if {"customer_number", "company_name", "country"} & data.keys():
        dq_result = evaluate_customer_datensatz(
            _build_customer_dq_datensatz(
                {
                    "customer_number": data.get("customer_number") or customer_id,
                    "company_name": data.get("company_name") or customer_id,
                    "country": data.get("country") or "DE",
                }
            )
        )
        if not dq_result.bestanden:
            raise HTTPException(status_code=422, detail=build_dq_error_detail("Debitor", dq_result))
    payload = _map_update_payload(customer_data)
    try:
        updated = await crm_update_customer(customer_id, payload)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return _adapt_customer(updated)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_customer(customer_id: str) -> Response:
    """Delete customer proxying the call to crm-core."""
    try:
        await crm_delete_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _adapt_customer(core_customer: CRMCoreCustomer) -> Customer:
    """Map crm-core payloads into the legacy Customer schema expected by the UI."""
    tenant_uuid = UUID(settings.DEFAULT_TENANT_ID)
    now = datetime.utcnow()
    customer_number = f"CRM-{core_customer.id[:8].upper()}"
    is_active = core_customer.status not in {"blacklisted", "former"}
    created_at = _parse_datetime(core_customer.created_at) or now
    updated_at = _parse_datetime(core_customer.updated_at) or now
    payload = {
        "id": core_customer.id,
        "tenant_id": tenant_uuid,
        "customer_number": customer_number,
        "company_name": core_customer.display_name,
        "name": core_customer.display_name,
        "contact_person": None,
        "email": core_customer.email,
        "phone": core_customer.phone,
        "address": None,
        "city": core_customer.region,
        "postal_code": None,
        "country": None,
        "industry": core_customer.industry,
        "website": None,
        "credit_limit": None,
        "payment_terms": 30,
        "tax_id": None,
        "chefanweisung": None,  # Will be loaded from database if available
        "is_active": is_active,
        "deleted_at": None,
        "created_at": created_at,
        "updated_at": updated_at,
    }
    return Customer.model_validate(payload)


def _map_create_payload(customer_data: CustomerCreate) -> dict[str, Optional[str]]:
    """Convert monolith DTO into crm-core payload."""
    payload = {
        "display_name": customer_data.company_name,
        "email": customer_data.email,
        "phone": customer_data.phone,
        "industry": customer_data.industry,
        "region": customer_data.city or customer_data.country,
        "notes": _compose_notes(customer_data),
    }
    # Neue Sales-Felder hinzufügen (werden in domain_crm.crm_customers gespeichert)
    if hasattr(customer_data, 'price_group') and customer_data.price_group:
        payload["price_group"] = customer_data.price_group
    if hasattr(customer_data, 'tax_category') and customer_data.tax_category:
        payload["tax_category"] = customer_data.tax_category
    return payload


def _map_update_payload(customer_data: CustomerUpdate) -> dict[str, Optional[str]]:
    payload: dict[str, Optional[str]] = {}
    mapped_fields = {
        "company_name": "display_name",
        "email": "email",
        "phone": "phone",
        "industry": "industry",
        "city": "region",
        # Neue Sales-Felder (SALES-CRM-02)
        "price_group": "price_group",
        "tax_category": "tax_category",
    }
    data = customer_data.model_dump(exclude_unset=True)
    for source, target in mapped_fields.items():
        if source in data:
            payload[target] = data[source]
    if any(field in data for field in ("address", "contact_person", "website")):
        payload["notes"] = _compose_notes(customer_data)
    return payload


def _compose_notes(customer_data: Union[CustomerCreate, CustomerUpdate]) -> Optional[str]:
    """Summarise legacy-only fields into a notes blob for crm-core."""
    sections: list[str] = []
    if getattr(customer_data, "contact_person", None):
        sections.append(f"Contact: {customer_data.contact_person}")
    address_parts = [getattr(customer_data, attr, None) for attr in ("address", "city", "postal_code", "country")]
    address = ", ".join(filter(None, address_parts))
    if address:
        sections.append(f"Address: {address}")
    if getattr(customer_data, "website", None):
        sections.append(f"Website: {customer_data.website}")
    return "\n".join(sections) if sections else None


def _to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    """Map downstream errors to FastAPI HTTPException."""
    detail = None
    try:
        payload = error.response.json()
        detail = payload.get("detail")
    except ValueError:
        detail = error.response.text or "crm-core request failed"
    return HTTPException(status_code=error.response.status_code, detail=detail or "crm-core request failed")


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
