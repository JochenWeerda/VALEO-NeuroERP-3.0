"""CRM Customer endpoints backed by the crm-core service."""

from __future__ import annotations

import logging
from datetime import datetime
from math import ceil
from typing import Any, Optional, Union
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.data_quality_enforcement import build_dq_error_detail, evaluate_customer_datensatz
from ....core.database import get_db
from ....core.tenant import get_tenant_id
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

logger = logging.getLogger(__name__)

DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


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


def _ensure_bp_belongs_to_tenant(partner_id: str, tenant_id: str, db: Session) -> None:
    """Prüft, dass der Business-Partner im gleichen Mandanten existiert."""
    from sqlalchemy import text

    ok = db.execute(
        text(
            "SELECT 1 FROM domain_crm.business_partners WHERE partner_id = :pid AND tenant_id = :tid"
        ),
        {"pid": partner_id, "tid": tenant_id},
    ).scalar()
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="business_partner_id ungültig oder nicht im Mandanten gefunden.",
        )


def _fetch_monolith_extensions(customer_id: str, db: Session, tenant_id: str | None = None) -> dict[str, Any]:
    """Felder, die nur in domain_crm.customers liegen (nicht in crm-core)."""
    from sqlalchemy import text

    try:
        query = "SELECT chefanweisung, business_partner_id FROM domain_crm.customers WHERE id = :cid"
        params: dict[str, Any] = {"cid": customer_id}
        if tenant_id:
            query += " AND tenant_id = :tid"
            params["tid"] = tenant_id
        row = db.execute(text(query), params).fetchone()
    except Exception:
        return {}
    if not row:
        return {}
    return {
        "chefanweisung": row.chefanweisung,
        "business_partner_id": row.business_partner_id,
    }


def _upsert_monolith_customer_stub(
    customer_id: str,
    business_partner_id: str | None,
    db: Session,
    tenant_id: str,
    company_name: str,
    customer_number: str,
) -> None:
    """Legt bei Bedarf eine Zeile in domain_crm.customers an (crm-core-Kunden ohne Monolith-Zeile)."""
    from sqlalchemy import text

    db.execute(
        text(
            """
            INSERT INTO domain_crm.customers (
                id, tenant_id, customer_number, company_name, business_partner_id,
                is_active, created_at, updated_at
            ) VALUES (
                :id, :tid, :cn, :cname, :bid, true, NOW(), NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                business_partner_id = EXCLUDED.business_partner_id,
                updated_at = NOW()
            """
        ),
        {
            "id": customer_id,
            "tid": tenant_id,
            "cn": customer_number[:50],
            "cname": company_name[:255],
            "bid": business_partner_id,
        },
    )
    db.commit()


def _persist_business_partner_link(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: Session,
    tenant_id: str,
    *,
    core_customer: CRMCoreCustomer | None = None,
) -> None:
    data = customer_data.model_dump(exclude_unset=True)
    if "business_partner_id" not in data:
        return
    bid = data["business_partner_id"]
    if bid:
        _ensure_bp_belongs_to_tenant(bid, tenant_id, db)
    if core_customer is not None:
        company_name = (core_customer.display_name or "Kunde").strip() or "Kunde"
        customer_number = f"CRM-{core_customer.id[:8].upper()}"
        _upsert_monolith_customer_stub(customer_id, bid, db, tenant_id, company_name, customer_number)
        return
    from sqlalchemy import text

    db.execute(
        text(
            "UPDATE domain_crm.customers SET business_partner_id = :bid, updated_at = NOW() "
            "WHERE id = :cid AND tenant_id = :tid"
        ),
        {"bid": bid, "cid": customer_id, "tid": tenant_id},
    )
    db.commit()


def _merge_extensions_for_customer_list(db: Session, items: list[Customer]) -> list[Customer]:
    """Reichert crm-core-Listeneinträge mit Monolith-Feldern an (chefanweisung, business_partner_id)."""
    if not items:
        return items
    from sqlalchemy import text

    ids = [str(i.id) for i in items]
    placeholders = ",".join([f":id{i}" for i in range(len(ids))])
    params: dict[str, str] = {f"id{i}": ids[i] for i in range(len(ids))}
    rows = db.execute(
        text(
            f"SELECT id, chefanweisung, business_partner_id FROM domain_crm.customers "
            f"WHERE id IN ({placeholders})"
        ),
        params,
    ).fetchall()
    ext_map = {str(r.id): r for r in rows}
    merged: list[Customer] = []
    for item in items:
        row = ext_map.get(str(item.id))
        if not row:
            merged.append(item)
            continue
        d = item.model_dump()
        if getattr(row, "chefanweisung", None) is not None:
            d["chefanweisung"] = row.chefanweisung
        if getattr(row, "business_partner_id", None):
            d["business_partner_id"] = row.business_partner_id
        merged.append(Customer.model_validate(d))
    return merged


def _create_customer_in_monolith_db(customer_data: CustomerCreate, db: Session) -> Customer:
    """Persist customer in domain_crm when crm-core is offline (dev / degraded mode)."""
    from ....core.uuid7 import uuid7
    from ....infrastructure.models import Customer as CustomerModel

    cid = uuid7()
    tid = str(customer_data.tenant_id)
    payment_terms = customer_data.payment_terms if customer_data.payment_terms is not None else 30
    bp_link = getattr(customer_data, "business_partner_id", None)
    if bp_link:
        _ensure_bp_belongs_to_tenant(str(bp_link).strip(), tid, db)
    row = CustomerModel(
        id=cid,
        tenant_id=tid,
        customer_number=customer_data.customer_number.strip(),
        company_name=customer_data.company_name.strip(),
        contact_person=None,
        email=str(customer_data.email) if customer_data.email else None,
        phone=customer_data.phone,
        address=customer_data.address,
        city=None,
        postal_code=None,
        country=None,
        industry=None,
        website=None,
        customer_type=None,
        credit_limit=customer_data.credit_limit,
        payment_terms=payment_terms,
        tax_id=customer_data.tax_id,
        chefanweisung=None,
        business_partner_id=str(bp_link).strip() if bp_link else None,
        is_active=customer_data.is_active,
    )
    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Kundennummer oder Datensatz existiert bereits.",
        ) from exc

    customer_dict = {
        "id": row.id,
        "tenant_id": UUID(str(row.tenant_id)),
        "customer_number": row.customer_number,
        "company_name": row.company_name,
        "name": row.company_name,
        "contact_person": row.contact_person,
        "email": row.email,
        "phone": row.phone,
        "address": row.address,
        "city": None,
        "postal_code": None,
        "country": None,
        "industry": None,
        "website": None,
        "price_group": None,
        "tax_category": None,
        "credit_limit": row.credit_limit,
        "payment_terms": payment_terms,
        "tax_id": row.tax_id,
        "chefanweisung": row.chefanweisung,
        "business_partner_id": getattr(row, "business_partner_id", None),
        "is_active": row.is_active if row.is_active is not None else True,
        "deleted_at": None,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }
    return Customer.model_validate(customer_dict)


def _build_customer_dq_datensatz(data: dict[str, object]) -> dict[str, object]:
    return {
        "debitor_nr": data.get("customer_number"),
        "name": data.get("company_name"),
        "land": data.get("country") or "DE",
    }


@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
) -> Customer:
    """Create a new customer via crm-core, or in PostgreSQL if crm-core is unreachable."""
    dq_result = evaluate_customer_datensatz(_build_customer_dq_datensatz(customer_data.model_dump(mode="python")))
    if not dq_result.bestanden:
        raise HTTPException(status_code=422, detail=build_dq_error_detail("Debitor", dq_result))
    payload = _map_create_payload(customer_data)
    try:
        created = await crm_create_customer(payload)
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network errors handled uniformly
        raise _to_http_exception(exc) from exc
    except httpx.RequestError as exc:
        logger.warning(
            "crm-core unreachable, persisting customer in domain_crm: %s: %s",
            type(exc).__name__,
            exc,
        )
        return _create_customer_in_monolith_db(customer_data, db)
    if customer_data.business_partner_id:
        _ensure_bp_belongs_to_tenant(customer_data.business_partner_id, str(customer_data.tenant_id), db)
        _upsert_monolith_customer_stub(
            created.id,
            customer_data.business_partner_id,
            db,
            str(customer_data.tenant_id),
            (created.display_name or customer_data.company_name or "Kunde").strip() or "Kunde",
            f"CRM-{created.id[:8].upper()}",
        )
    adapted = _adapt_customer(created)
    ext = _fetch_monolith_extensions(created.id, db, str(customer_data.tenant_id))
    if ext:
        d = adapted.model_dump()
        if ext.get("business_partner_id"):
            d["business_partner_id"] = ext["business_partner_id"]
        adapted = Customer.model_validate(d)
    return adapted


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
        items = _merge_extensions_for_customer_list(db, items)
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
                    business_partner_id,
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
                            except Exception:
                                address_str = row.address
                    
                    # Parse payment_terms (can be string or int)
                    payment_terms_val = 30
                    if row.payment_terms:
                        try:
                            payment_terms_val = int(row.payment_terms) if str(row.payment_terms).isdigit() else 30
                        except Exception:
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
                        "business_partner_id": getattr(row, "business_partner_id", None),
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
        city, postal_code = _extract_customer_picker_location(
            address=row.address,
        )
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
    """Zuletzt aktualisierte Kunden des Mandanten — MVP-Prefetch fuer die Combobox.

    Sobald ein echtes user-last-used-Log existiert, pro User sortieren.
    """
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
        city, postal_code = _extract_customer_picker_location(
            address=row.address,
        )
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
    """Return a customer by ID."""
    try:
        customer = await crm_get_customer(customer_id)
        adapted = _adapt_customer(customer)
        ext = _fetch_monolith_extensions(customer_id, db, tenant_id)
        if ext:
            customer_dict = adapted.model_dump()
            if ext.get("chefanweisung") is not None:
                customer_dict["chefanweisung"] = ext["chefanweisung"]
            if ext.get("business_partner_id"):
                customer_dict["business_partner_id"] = ext["business_partner_id"]
            adapted = Customer.model_validate(customer_dict)
        return adapted
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Customer:
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
        if payload:
            updated = await crm_update_customer(customer_id, payload)
        else:
            updated = await crm_get_customer(customer_id)
    except httpx.HTTPStatusError as exc:
        raise _to_http_exception(exc) from exc
    _persist_business_partner_link(customer_id, customer_data, db, tenant_id, core_customer=updated)
    adapted = _adapt_customer(updated)
    ext = _fetch_monolith_extensions(customer_id, db, tenant_id)
    if ext:
        d = adapted.model_dump()
        if ext.get("chefanweisung") is not None:
            d["chefanweisung"] = ext["chefanweisung"]
        if ext.get("business_partner_id"):
            d["business_partner_id"] = ext["business_partner_id"]
        adapted = Customer.model_validate(d)
    return adapted


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
        "business_partner_id": None,
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
