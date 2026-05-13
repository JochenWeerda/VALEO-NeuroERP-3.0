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


def _extract_customer_picker_location(
    *,
    city: Any = None,
    postal_code: Any = None,
    address: Any = None,
) -> tuple[str | None, str | None]:
    resolved_city = str(city).strip() if city else None
    resolved_postal_code = str(postal_code).strip() if postal_code else None

    if resolved_city or resolved_postal_code:
        return resolved_city, resolved_postal_code

    if isinstance(address, dict):
        return (
            address.get("city") or None,
            address.get("postal_code") or address.get("postalCode") or None,
        )

    if isinstance(address, str):
        try:
            import json as _json
            parsed = _json.loads(address)
        except Exception:
            return None, None
        if isinstance(parsed, dict):
            return (
                parsed.get("city") or None,
                parsed.get("postal_code") or parsed.get("postalCode") or None,
            )

    return None, None


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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Customer:
    """Create a new customer via crm-core, or in PostgreSQL if crm-core is unreachable."""
    try:
        d = await _svc(db, tenant_id).create_customer(customer_data)
    except ValidationFailedError as exc:
        raise HTTPException(422, exc.detail)
    except ConflictError as exc:
        raise HTTPException(409, exc.detail)
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
    from sqlalchemy import text

    effective_tenant = tenant_id or DEFAULT_TENANT
    term = (q or "").strip()
    if not term:
        return []

    like = f"{term}%"
    contains = f"%{term}%"
    sql = text(
        """
        SELECT
            id,
            customer_number,
            company_name,
            address,
            is_active,
            CASE
                WHEN customer_number ILIKE :like THEN 0
                WHEN company_name ILIKE :like THEN 1
                ELSE 2
            END AS rank
        FROM domain_crm.customers
        WHERE tenant_id = :tid
          AND (
              company_name ILIKE :contains
              OR customer_number ILIKE :contains
          )
        ORDER BY rank ASC, company_name ASC
        LIMIT :lim
        """
    )
    rows = db.execute(
        sql,
        {"tid": effective_tenant, "like": like, "contains": contains, "lim": limit},
    ).fetchall()

    out: list[dict[str, Any]] = []
    for row in rows:
        city, postal_code = _extract_customer_picker_location(address=row.address)
        out.append(
            {
                "id": str(row.id),
                "customer_number": row.customer_number or "",
                "company_name": row.company_name or "",
                "city": city,
                "postal_code": postal_code,
                "is_active": bool(row.is_active) if row.is_active is not None else True,
            }
        )
    return out


@router.get("/recent")
def recent_customers(
    limit: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Zuletzt aktualisierte Kunden des Mandanten — MVP-Prefetch fuer die Combobox."""
    from sqlalchemy import text

    effective_tenant = tenant_id or DEFAULT_TENANT
    sql = text(
        """
        SELECT id, customer_number, company_name, address, is_active, updated_at
        FROM domain_crm.customers
        WHERE tenant_id = :tid AND COALESCE(is_active, TRUE) = TRUE
        ORDER BY updated_at DESC NULLS LAST
        LIMIT :lim
        """
    )
    rows = db.execute(sql, {"tid": effective_tenant, "lim": limit}).fetchall()
    out: list[dict[str, Any]] = []
    for row in rows:
        city, postal_code = _extract_customer_picker_location(address=row.address)
        out.append(
            {
                "id": str(row.id),
                "customer_number": row.customer_number or "",
                "company_name": row.company_name or "",
                "city": city,
                "postal_code": postal_code,
                "is_active": bool(row.is_active) if row.is_active is not None else True,
            }
        )
    return out


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
    except EntityNotFoundError as exc:
        raise HTTPException(404, exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(422, exc.detail)
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
