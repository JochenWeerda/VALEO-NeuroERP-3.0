"""Service layer for CRM Customer management (crm-core + monolith bridge)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from math import ceil
from typing import Any, Optional, Union
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_customer_datensatz
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.integrations.crm_core_client import (
    CRMCoreCustomer,
    create_customer as _crm_create,
    delete_customer as _crm_delete,
    get_customer as _crm_get,
    list_customers as _crm_list,
    update_customer as _crm_update,
)

logger = logging.getLogger(__name__)

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"


# ── pure helpers (module-level, no state) ─────────────────────────────────────

def _extract_location(
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
            parsed = json.loads(address)
        except Exception:
            return None, None
        if isinstance(parsed, dict):
            return (
                parsed.get("city") or None,
                parsed.get("postal_code") or parsed.get("postalCode") or None,
            )
    return None, None


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _compose_notes(customer_data: Any) -> Optional[str]:
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


def _map_create_payload(customer_data: Any) -> dict[str, Optional[str]]:
    payload: dict[str, Any] = {
        "display_name": customer_data.company_name,
        "email": customer_data.email,
        "phone": customer_data.phone,
        "industry": getattr(customer_data, "industry", None),
        "region": getattr(customer_data, "city", None) or getattr(customer_data, "country", None),
        "notes": _compose_notes(customer_data),
    }
    if getattr(customer_data, "price_group", None):
        payload["price_group"] = customer_data.price_group
    if getattr(customer_data, "tax_category", None):
        payload["tax_category"] = customer_data.tax_category
    return payload


def _map_update_payload(customer_data: Any) -> dict[str, Optional[str]]:
    mapped_fields = {
        "company_name": "display_name",
        "email": "email",
        "phone": "phone",
        "industry": "industry",
        "city": "region",
        "price_group": "price_group",
        "tax_category": "tax_category",
    }
    data = customer_data.model_dump(exclude_unset=True)
    payload: dict[str, Optional[str]] = {}
    for source, target in mapped_fields.items():
        if source in data:
            payload[target] = data[source]
    if any(field in data for field in ("address", "contact_person", "website")):
        payload["notes"] = _compose_notes(customer_data)
    return payload


def _adapt_customer(core_customer: CRMCoreCustomer) -> dict[str, Any]:
    """Map crm-core payload to the Customer schema dict."""
    tenant_uuid = UUID(settings.DEFAULT_TENANT_ID)
    now = datetime.utcnow()
    customer_number = f"CRM-{core_customer.id[:8].upper()}"
    is_active = core_customer.status not in {"blacklisted", "former"}
    return {
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
        "price_group": None,
        "tax_category": None,
        "credit_limit": None,
        "payment_terms": 30,
        "tax_id": None,
        "chefanweisung": None,
        "business_partner_id": None,
        "is_active": is_active,
        "deleted_at": None,
        "created_at": _parse_datetime(core_customer.created_at) or now,
        "updated_at": _parse_datetime(core_customer.updated_at) or now,
    }


def _build_dq_datensatz(data: dict[str, object]) -> dict[str, object]:
    return {
        "debitor_nr": data.get("customer_number"),
        "name": data.get("company_name"),
        "land": data.get("country") or "DE",
    }


# ── service class ─────────────────────────────────────────────────────────────

class CustomerService:
    """Delegates to crm-core microservice and keeps the monolith stub in sync."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── monolith DB helpers ───────────────────────────────────────────────────

    def fetch_monolith_extensions(self, customer_id: str) -> dict[str, Any]:
        try:
            row = self.db.execute(
                text(
                    "SELECT chefanweisung, business_partner_id "
                    "FROM domain_crm.customers WHERE id = :cid AND tenant_id = :tid"
                ),
                {"cid": customer_id, "tid": self.tenant_id},
            ).fetchone()
        except Exception:
            return {}
        if not row:
            return {}
        return {
            "chefanweisung": row.chefanweisung,
            "business_partner_id": row.business_partner_id,
        }

    def merge_extensions(self, customer_dict: dict[str, Any]) -> dict[str, Any]:
        ext = self.fetch_monolith_extensions(customer_dict["id"])
        if ext.get("chefanweisung") is not None:
            customer_dict["chefanweisung"] = ext["chefanweisung"]
        if ext.get("business_partner_id"):
            customer_dict["business_partner_id"] = ext["business_partner_id"]
        return customer_dict

    def merge_extensions_for_list(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not items:
            return items
        ids = [str(i["id"]) for i in items]
        placeholders = ",".join([f":id{i}" for i in range(len(ids))])
        params: dict[str, str] = {f"id{i}": ids[i] for i in range(len(ids))}
        try:
            rows = self.db.execute(
                text(
                    f"SELECT id, chefanweisung, business_partner_id FROM domain_crm.customers "
                    f"WHERE id IN ({placeholders})"
                ),
                params,
            ).fetchall()
        except Exception:
            return items
        ext_map = {str(r.id): r for r in rows}
        for item in items:
            row = ext_map.get(str(item["id"]))
            if row:
                if getattr(row, "chefanweisung", None) is not None:
                    item["chefanweisung"] = row.chefanweisung
                if getattr(row, "business_partner_id", None):
                    item["business_partner_id"] = row.business_partner_id
        return items

    def upsert_monolith_stub(
        self,
        customer_id: str,
        business_partner_id: Optional[str],
        company_name: str,
        customer_number: str,
    ) -> None:
        self.db.execute(
            text("""
                INSERT INTO domain_crm.customers
                    (id, tenant_id, customer_number, company_name, business_partner_id,
                     is_active, created_at, updated_at)
                VALUES (:id, :tid, :cn, :cname, :bid, true, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    business_partner_id = EXCLUDED.business_partner_id,
                    updated_at = NOW()
            """),
            {
                "id": customer_id,
                "tid": self.tenant_id,
                "cn": customer_number[:50],
                "cname": company_name[:255],
                "bid": business_partner_id,
            },
        )
        self.db.commit()

    def ensure_bp_belongs_to_tenant(self, partner_id: str) -> None:
        ok = self.db.execute(
            text(
                "SELECT 1 FROM domain_crm.business_partners "
                "WHERE partner_id = :pid AND tenant_id = :tid"
            ),
            {"pid": partner_id, "tid": self.tenant_id},
        ).scalar()
        if not ok:
            raise ValidationFailedError("business_partner_id ungültig oder nicht im Mandanten gefunden.")

    def _create_in_monolith_db(self, customer_data: Any) -> dict[str, Any]:
        """Persist in domain_crm when crm-core is offline (fallback)."""
        from app.core.uuid7 import uuid7
        from app.infrastructure.models import Customer as CustomerModel

        cid = uuid7()
        payment_terms = customer_data.payment_terms if customer_data.payment_terms is not None else 30
        bp_link = getattr(customer_data, "business_partner_id", None)
        if bp_link:
            self.ensure_bp_belongs_to_tenant(str(bp_link).strip())
        row = CustomerModel(
            id=cid,
            tenant_id=self.tenant_id,
            customer_number=customer_data.customer_number.strip(),
            company_name=customer_data.company_name.strip(),
            contact_person=None,
            email=str(customer_data.email) if customer_data.email else None,
            phone=customer_data.phone,
            address=customer_data.address,
            credit_limit=customer_data.credit_limit,
            payment_terms=payment_terms,
            tax_id=customer_data.tax_id,
            business_partner_id=str(bp_link).strip() if bp_link else None,
            is_active=customer_data.is_active,
        )
        try:
            self.db.add(row)
            self.db.commit()
            self.db.refresh(row)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Kundennummer oder Datensatz existiert bereits.") from exc

        return {
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
            "chefanweisung": None,
            "business_partner_id": getattr(row, "business_partner_id", None),
            "is_active": row.is_active if row.is_active is not None else True,
            "deleted_at": None,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    def _list_fallback_db(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        effective_tenant: str,
    ) -> tuple[list[dict[str, Any]], int]:
        """Direct DB fallback when crm-core is unavailable."""
        where_clauses = []
        params: dict[str, Any] = {}
        where_clauses.append("tenant_id = :tenant_id")
        params["tenant_id"] = effective_tenant
        if search:
            where_clauses.append(
                "(company_name ILIKE :search OR customer_number ILIKE :search OR email ILIKE :search)"
            )
            params["search"] = f"%{search}%"
        where_sql = " AND ".join(where_clauses)
        total = self.db.execute(
            text(f"SELECT COUNT(*) FROM domain_crm.customers WHERE {where_sql}"), params
        ).scalar_one()
        params["limit"] = limit
        params["offset"] = skip
        rows = self.db.execute(
            text(f"""
                SELECT id, tenant_id, customer_number, company_name, contact_person,
                       email, phone, address, customer_type, credit_limit, payment_terms,
                       is_active, chefanweisung, business_partner_id, created_at, updated_at
                FROM domain_crm.customers WHERE {where_sql}
                ORDER BY company_name DESC LIMIT :limit OFFSET :offset
            """),
            params,
        ).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            try:
                city = postal_code = country = address_str = None
                if row.address:
                    if isinstance(row.address, dict):
                        city = row.address.get("city")
                        postal_code = row.address.get("postal_code")
                        country = row.address.get("country")
                        address_str = row.address.get("street") or str(row.address)
                    elif isinstance(row.address, str):
                        try:
                            addr = json.loads(row.address)
                            city = addr.get("city")
                            postal_code = addr.get("postal_code")
                            country = addr.get("country")
                            address_str = addr.get("street") or row.address
                        except Exception:
                            address_str = row.address
                payment_terms_val = 30
                if row.payment_terms:
                    try:
                        payment_terms_val = int(row.payment_terms) if str(row.payment_terms).isdigit() else 30
                    except Exception:
                        payment_terms_val = 30
                items.append({
                    "id": str(row.id),
                    "tenant_id": UUID(str(row.tenant_id)) if row.tenant_id else UUID(_DEFAULT_TENANT),
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
                    "industry": None,
                    "website": None,
                    "price_group": None,
                    "tax_category": None,
                    "credit_limit": float(row.credit_limit) if row.credit_limit is not None else None,
                    "payment_terms": payment_terms_val,
                    "tax_id": None,
                    "chefanweisung": getattr(row, "chefanweisung", None),
                    "business_partner_id": getattr(row, "business_partner_id", None),
                    "is_active": row.is_active if row.is_active is not None else True,
                    "deleted_at": None,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                })
            except Exception as exc:
                logger.error("Error mapping customer %s: %s", row.id, exc)
        return items, total

    # ── crm-core delegation (async) ───────────────────────────────────────────

    async def list_customers(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> tuple[list[dict[str, Any]], int]:
        effective_tenant = self.tenant_id or _DEFAULT_TENANT
        try:
            core_items, total = await _crm_list(skip=skip, limit=limit, search=search)
            items = [_adapt_customer(c) for c in core_items]
            items = self.merge_extensions_for_list(items)
            return items, total
        except Exception as exc:
            logger.warning("crm-core unavailable, DB fallback: %s: %s", type(exc).__name__, exc)
            return self._list_fallback_db(skip, limit, search, effective_tenant)

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        customer = await _crm_get(customer_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)
        d = _adapt_customer(customer)
        return self.merge_extensions(d)

    async def create_customer(self, customer_data: Any) -> dict[str, Any]:
        dq_result = evaluate_customer_datensatz(
            _build_dq_datensatz(customer_data.model_dump(mode="python"))
        )
        if not dq_result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("Debitor", dq_result))
        payload = _map_create_payload(customer_data)
        try:
            created = await _crm_create(payload)
        except httpx.RequestError as exc:
            logger.warning("crm-core unreachable, monolith fallback: %s", exc)
            return self._create_in_monolith_db(customer_data)
        if getattr(customer_data, "business_partner_id", None):
            bp_id = customer_data.business_partner_id
            self.ensure_bp_belongs_to_tenant(bp_id)
            try:
                self.upsert_monolith_stub(
                    created.id,
                    bp_id,
                    (created.display_name or customer_data.company_name or "Kunde").strip() or "Kunde",
                    f"CRM-{created.id[:8].upper()}",
                )
            except Exception:
                logger.warning("Monolith stub upsert failed for customer %s", created.id)
        d = _adapt_customer(created)
        return self.merge_extensions(d)

    async def update_customer(self, customer_id: str, customer_data: Any) -> dict[str, Any]:
        data = customer_data.model_dump(exclude_unset=True, mode="python")
        if {"customer_number", "company_name", "country"} & data.keys():
            dq_result = evaluate_customer_datensatz(
                _build_dq_datensatz({
                    "customer_number": data.get("customer_number") or customer_id,
                    "company_name": data.get("company_name") or customer_id,
                    "country": data.get("country") or "DE",
                })
            )
            if not dq_result.bestanden:
                raise ValidationFailedError(build_dq_error_detail("Debitor", dq_result))
        payload = _map_update_payload(customer_data)
        if payload:
            updated = await _crm_update(customer_id, payload)
        else:
            updated = await _crm_get(customer_id)
        if updated is None:
            raise EntityNotFoundError("Customer", customer_id)
        if "business_partner_id" in data:
            bid = data["business_partner_id"]
            if bid:
                self.ensure_bp_belongs_to_tenant(bid)
            try:
                self.upsert_monolith_stub(
                    customer_id,
                    bid,
                    (updated.display_name or "Kunde").strip() or "Kunde",
                    f"CRM-{customer_id[:8].upper()}",
                )
            except Exception:
                logger.warning("Monolith stub update failed for customer %s", customer_id)
        d = _adapt_customer(updated)
        return self.merge_extensions(d)

    async def delete_customer(self, customer_id: str) -> None:
        await _crm_delete(customer_id)
