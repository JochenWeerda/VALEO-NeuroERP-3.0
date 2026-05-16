"""CRM Customer endpoints backed by the crm-core service."""

from __future__ import annotations

import logging
from math import ceil
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from ....services.customer_service import CustomerService
from ..schemas.base import PaginatedResponse
from ..schemas.crm import Customer, CustomerCreate, CustomerUpdate

router = APIRouter()

logger = logging.getLogger(__name__)

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


def _svc(db: Session, tenant_id: str) -> CustomerService:
    return CustomerService(db, tenant_id)



def _to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    """Map downstream errors to FastAPI HTTPException."""
    detail = None
    try:
        payload = error.response.json()
        detail = payload.get("detail")
    except ValueError:
        detail = error.response.text or "crm-core request failed"
    return HTTPException(status_code=error.response.status_code, detail=detail or "crm-core request failed")




@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
) -> Customer:
    """Create a new customer via crm-core, or in PostgreSQL if crm-core is unreachable."""
    try:
        d = await _svc(db, str(customer_data.tenant_id)).create_customer(customer_data)  # type: ignore[arg-type]
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.get("/", response_model=PaginatedResponse[Customer])
async def list_customers(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return"),
    search: Optional[str] = Query(None, description="Search in display name"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Customer]:
    effective_tenant = tenant_id or DEFAULT_TENANT
    items_raw, total = await _svc(db, effective_tenant).list_customers(skip=skip, limit=limit, search=search)
    items = [Customer.model_validate(d) for d in items_raw]
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


@router.get("/quick-search")
def quick_search_customers(
    q: str = Query("", description="Suchterm (Name oder Kundennummer)"),
    limit: int = Query(8, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Schlanker Typeahead-Endpoint — nur die Felder, die die Combobox braucht.

    Sortierung: Exakt-/Prefix-Matches auf Kundennummer zuerst, dann Prefix auf Name,
    danach Trigram-Ähnlichkeit. Nutzt pg_trgm GIN-Indizes
    (siehe Migration crm_customers_search_index_20260414).
    """
    return _svc(db, tenant_id or DEFAULT_TENANT).quick_search(q or "", limit=limit)


@router.get("/recent")
def recent_customers(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Zuletzt aktualisierte Kunden des Mandanten — MVP-Prefetch fuer die Combobox."""
    return _svc(db, tenant_id or DEFAULT_TENANT).recent(limit=limit)


@router.get("/{customer_id}/sales-eligibility")
async def get_customer_sales_eligibility(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, object]:
    """Verkaufs-/Lieferfreigabe aus Stammdaten (Business-Partner), für Belegmasken."""
    from ....services.customer_sales_eligibility import describe_sales_eligibility

    return describe_sales_eligibility(db, tenant_id, customer_id)


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Customer:
    try:
        d = await _svc(db, tenant_id).get_customer(customer_id)
    except EntityNotFoundError as exc:
        raise HTTPException(404, exc.detail)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Customer:
    try:
        d = await _svc(db, tenant_id).update_customer(customer_id, customer_data)
    except EntityNotFoundError:
        raise HTTPException(404, "Customer not found")
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Customer.model_validate(d)


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        await _svc(db, tenant_id).delete_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
