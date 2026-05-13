"""Service layer for CRM Customer management (crm-core + monolith bridge)."""

from __future__ import annotations

import logging
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.data_quality_enforcement import build_dq_error_detail, evaluate_customer_datensatz
from app.core.exceptions import EntityNotFoundError, ValidationFailedError
from app.integrations.crm_core_client import (
    CRMCoreCustomer,
    create_customer as _crm_create,
    delete_customer as _crm_delete,
    get_customer as _crm_get,
    list_customers as _crm_list,
    update_customer as _crm_update,
)

logger = logging.getLogger(__name__)


def _extract_location(
    *,
    city: Any = None,
    postal_code: Any = None,
    address: Any = None,
) -> tuple[str | None, str | None]:
    """Resolve city + postal_code from various payload shapes."""
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
                    (id, tenant_id, business_partner_id, company_name, customer_number, created_at, updated_at)
                VALUES
                    (:id, :tid, :bp_id, :name, :num, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    business_partner_id = EXCLUDED.business_partner_id,
                    updated_at = now()
            """),
            {
                "id": customer_id,
                "tid": self.tenant_id,
                "bp_id": business_partner_id,
                "name": company_name,
                "num": customer_number,
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

    # ── crm-core delegation ───────────────────────────────────────────────────

    def list_customers(
        self,
        search: Optional[str] = None,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        page: int = 1,
        size: int = 25,
    ) -> tuple[list[CRMCoreCustomer], int]:
        return _crm_list(
            tenant_id=self.tenant_id,
            search=search,
            city=city,
            postal_code=postal_code,
            page=page,
            size=size,
        )

    def get_customer(self, customer_id: str) -> CRMCoreCustomer:
        customer = _crm_get(customer_id, tenant_id=self.tenant_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)
        return customer

    def create_customer(self, payload: dict) -> CRMCoreCustomer:
        city, postal_code = _extract_location(
            city=payload.get("city"),
            postal_code=payload.get("postal_code"),
            address=payload.get("address"),
        )

        dq_result = evaluate_customer_datensatz({
            "kundennummer": payload.get("customer_number"),
            "firmenname": payload.get("company_name"),
            "email": payload.get("email"),
            "plz": postal_code,
            "ort": city,
        })
        if not dq_result.bestanden:
            raise ValidationFailedError(build_dq_error_detail("Kunde", dq_result))

        if payload.get("business_partner_id"):
            self.ensure_bp_belongs_to_tenant(payload["business_partner_id"])

        customer = _crm_create(payload, tenant_id=self.tenant_id)

        try:
            self.upsert_monolith_stub(
                customer_id=customer.id,
                business_partner_id=payload.get("business_partner_id"),
                company_name=payload.get("company_name", ""),
                customer_number=payload.get("customer_number", ""),
            )
        except Exception:
            logger.warning("Monolith stub upsert failed for customer %s", customer.id)

        return customer

    def update_customer(self, customer_id: str, data: dict) -> CRMCoreCustomer:
        if data.get("business_partner_id"):
            self.ensure_bp_belongs_to_tenant(data["business_partner_id"])
        customer = _crm_update(customer_id, data, tenant_id=self.tenant_id)
        if customer is None:
            raise EntityNotFoundError("Customer", customer_id)
        if data.get("business_partner_id"):
            try:
                self.upsert_monolith_stub(
                    customer_id=customer_id,
                    business_partner_id=data["business_partner_id"],
                    company_name=data.get("company_name", ""),
                    customer_number=data.get("customer_number", ""),
                )
            except Exception:
                logger.warning("Monolith stub update failed for customer %s", customer_id)
        return customer

    def delete_customer(self, customer_id: str) -> None:
        _crm_delete(customer_id, tenant_id=self.tenant_id)
