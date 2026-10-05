"""Service layer for CRM Customer management (crm-core + monolith bridge)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from math import ceil

from app.core.address import parse_address
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


def _tenant_as_uuid(value: Any) -> UUID:
    """Customer-Antwortmodell verlangt UUID; gewachsene Mandanten-IDs sind oft Slugs."""
    if value is None or value == "":
        return UUID(_DEFAULT_TENANT)
    try:
        return UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return UUID(_DEFAULT_TENANT)


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


def attach_mask_aliases(customer: dict[str, Any]) -> dict[str, Any]:
    """German Object-Page keys for ``crm/customer-360``.

    The native ScreenDefinition reads ``firma``, ``kunden_nr``, ``notizen``.
    The HTTP contract still returns ``company_name`` / ``customer_number`` /
    ``chefanweisung``; both shapes must be present so the Akte can open from
    a listen ID without a second mapping layer in the renderer.
    """
    company = customer.get("company_name") or customer.get("name") or customer.get("firma")
    number = customer.get("customer_number") or customer.get("kunden_nr")
    notes = customer.get("notizen") or customer.get("chefanweisung")
    terms = customer.get("zahlungsbedingungen")
    if terms is None and customer.get("payment_terms") is not None:
        terms = str(customer["payment_terms"])
    customer["firma"] = company
    customer["name"] = customer.get("name") or company
    customer["kunden_nr"] = number
    customer["strasse"] = customer.get("strasse") or customer.get("address")
    customer["plz"] = customer.get("plz") or customer.get("postal_code")
    customer["ort"] = customer.get("ort") or customer.get("city")
    customer["land"] = customer.get("land") or customer.get("country")
    customer["telefon"] = customer.get("telefon") or customer.get("phone")
    customer["branche"] = customer.get("branche") or customer.get("industry")
    if customer.get("kreditlimit") is None:
        customer["kreditlimit"] = customer.get("credit_limit")
    customer["zahlungsbedingungen"] = terms
    customer["notizen"] = notes
    if notes and not customer.get("chefanweisung"):
        customer["chefanweisung"] = notes
    return customer


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
                    "FROM domain_crm.customers "
                    "WHERE tenant_id = :tid AND (id::text = :cid OR customer_number = :cid "
                    "OR business_partner_id::text = :cid) "
                    "LIMIT 1"
                ),
                {"cid": customer_id, "tid": self.tenant_id},
            ).fetchone()
        except Exception:
            self.db.rollback()
            return {}
        if not row:
            return {}
        return {
            "chefanweisung": row.chefanweisung,
            "business_partner_id": row.business_partner_id,
        }

    def enrich_mask_satellites(self, customer_dict: dict[str, Any]) -> dict[str, Any]:
        """Postfach and geo for the Object Page; empty when the satellite is missing."""
        kn = customer_dict.get("customer_number") or customer_dict.get("kunden_nr")
        if kn:
            try:
                row = self.db.execute(
                    text(
                        "SELECT postfach, postfach_plz, postfach_ort "
                        "FROM public.kunden WHERE kunden_nr = :k LIMIT 1"
                    ),
                    {"k": kn},
                ).fetchone()
            except Exception:
                self.db.rollback()
                row = None
            if row:
                customer_dict["postfach"] = getattr(row, "postfach", None)
                customer_dict["postfach_plz"] = getattr(row, "postfach_plz", None)
                customer_dict["postfach_ort"] = getattr(row, "postfach_ort", None)
        # Koordinaten liegen in public.kunden_geo (kunden_geo_20260604).
        # domain_crm.customers hat dafuer keine Migration.
        if kn:
            try:
                sat = self.db.execute(
                    text(
                        "SELECT lat, lon FROM public.kunden_geo WHERE kunden_nr = :k LIMIT 1"
                    ),
                    {"k": kn},
                ).fetchone()
            except Exception:
                self.db.rollback()
                sat = None
            if sat:
                customer_dict["breitengrad"] = getattr(sat, "lat", None)
                customer_dict["laengengrad"] = getattr(sat, "lon", None)
        self._attach_partner_mask_fields(customer_dict)
        self._attach_billing_config(customer_dict)
        self._attach_potential_snapshot(customer_dict)
        self._attach_credit_exception(customer_dict)
        return customer_dict

    def _attach_partner_mask_fields(self, customer_dict: dict[str, Any]) -> None:
        """Legacy-Register Steuern, Bank, System, Qualitaet, Marketing, Genossenschaft, Ausgabe, Schnittstellen."""
        partner_id = customer_dict.get("business_partner_id")
        if not partner_id:
            return
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT vat_id, tax_number, tax_type, iban, bic, bank_name, account_holder,
                           sepa_mandate_reference, sepa_mandate_signed_at,
                           blocked_for_delivery, blocked_for_invoice, status,
                           farm_number, eu_farm_id, qs_certificate_number, bio_certified,
                           marketing_segment, newsletter_opt_in, email_opt_in,
                           membership_number, mandatory_shares, membership_terminated,
                           invoice_dispatch_channel, reminder_dispatch_channel,
                           edifact_invoic, edifact_orders, edifact_desadv, fax
                    FROM domain_crm.business_partners
                    WHERE partner_id::text = :id
                      AND (:tid IS NULL OR tenant_id::text = :tid)
                    LIMIT 1
                    """
                ),
                {"id": str(partner_id), "tid": self.tenant_id},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return
        if not row:
            return
        shares = row["mandatory_shares"]
        customer_dict.update(
            {
                "ust_id": row["vat_id"] or customer_dict.get("tax_id"),
                "steuernummer": row["tax_number"],
                "steuerart": row["tax_type"],
                "iban": row["iban"],
                "bic": row["bic"],
                "bankname": row["bank_name"],
                "kontoinhaber": row["account_holder"],
                "sepa_mandat_ref": row["sepa_mandate_reference"],
                "sepa_mandat_datum": (
                    row["sepa_mandate_signed_at"].date().isoformat()
                    if row["sepa_mandate_signed_at"] is not None
                    else None
                ),
                "gesperrt_lieferung": row["blocked_for_delivery"],
                "gesperrt_rechnung": row["blocked_for_invoice"],
                "partner_status": row["status"],
                "betriebsnummer": row["farm_number"],
                "eu_betriebsnummer": row["eu_farm_id"],
                "qs_nummer": row["qs_certificate_number"],
                "bio": row["bio_certified"],
                "marketing_segment": row["marketing_segment"],
                "segment": row["marketing_segment"],
                "newsletter": row["newsletter_opt_in"],
                "email_opt_in": row["email_opt_in"],
                "mitgliedsnummer": row["membership_number"],
                "pflichtanteile": float(shares) if shares is not None else None,
                "mitgliedschaft_beendet": row["membership_terminated"],
                "rechnungsversand": row["invoice_dispatch_channel"],
                "mahnversand": row["reminder_dispatch_channel"],
                "edifact_invoic": row["edifact_invoic"],
                "edifact_orders": row["edifact_orders"],
                "edifact_desadv": row["edifact_desadv"],
                "fax": row["fax"] or customer_dict.get("fax"),
            }
        )

    def _attach_billing_config(self, customer_dict: dict[str, Any]) -> None:
        """Kontoauszug. Quelle: domain_crm.business_partner_billing_configs."""
        partner_id = customer_dict.get("business_partner_id")
        if not partner_id:
            return
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT customer_group, customer_type,
                           account_statement_print, account_statement_separate,
                           last_account_statement_number, account_balance,
                           settlement_mode, invoice_number_range,
                           bonus_eligible, self_billing_sales, vat_optimizer
                    FROM domain_crm.business_partner_billing_configs
                    WHERE partner_id::text = :id
                    LIMIT 1
                    """
                ),
                {"id": str(partner_id)},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return
        if not row:
            return
        saldo = row["account_balance"]
        customer_dict.update(
            {
                "billing_customer_group": row["customer_group"],
                "billing_customer_type": row["customer_type"],
                "account_statement_print": row["account_statement_print"],
                "account_statement_separate": row["account_statement_separate"],
                "last_account_statement_number": row["last_account_statement_number"],
                "account_balance": float(saldo) if saldo is not None else None,
                "settlement_mode": row["settlement_mode"],
                "invoice_number_range": row["invoice_number_range"],
                "bonus_eligible": row["bonus_eligible"],
                "self_billing_sales": row["self_billing_sales"],
                "vat_optimizer": row["vat_optimizer"],
            }
        )

    def _attach_potential_snapshot(self, customer_dict: dict[str, Any]) -> None:
        """Juengster GAP-Snapshot. Quelle: public.customer_potential_snapshot."""
        customer_id = customer_dict.get("id")
        if not customer_id:
            return
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT ref_year, gap_direct_total_eur, gap_estimated_area_ha,
                           potential_seed_eur, potential_fertilizer_eur, potential_psm_eur,
                           potential_total_eur, turnover_total_last_year_eur,
                           share_of_wallet_total_pct, segment, potential_notes
                    FROM public.customer_potential_snapshot
                    WHERE customer_id::text = :cid
                    ORDER BY ref_year DESC, computed_at DESC
                    LIMIT 1
                    """
                ),
                {"cid": str(customer_id)},
            ).mappings().first()
        except Exception:
            self.db.rollback()
            return
        if not row:
            return

        def _zahl(value: Any) -> float | None:
            return float(value) if value is not None else None

        customer_dict.update(
            {
                "gap_ref_year": row["ref_year"],
                "gap_direct_total_eur": _zahl(row["gap_direct_total_eur"]),
                "gap_estimated_area_ha": _zahl(row["gap_estimated_area_ha"]),
                "potential_seed_eur": _zahl(row["potential_seed_eur"]),
                "potential_fertilizer_eur": _zahl(row["potential_fertilizer_eur"]),
                "potential_psm_eur": _zahl(row["potential_psm_eur"]),
                "potential_total_eur": _zahl(row["potential_total_eur"]),
                "turnover_total_last_year_eur": _zahl(row["turnover_total_last_year_eur"]),
                "share_of_wallet_total_pct": _zahl(row["share_of_wallet_total_pct"]),
                "potential_segment": row["segment"],
                "potential_notes": row["potential_notes"],
            }
        )

    def _attach_credit_exception(self, customer_dict: dict[str, Any]) -> None:
        """Operatives Limit. Ausnahme in credit_limits schlaegt den Stamm."""
        customer_id = customer_dict.get("id")
        if not customer_id:
            return
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT credit_limit_eur
                    FROM domain_crm.credit_limits
                    WHERE customer_id::text = :cid
                      AND (:tid IS NULL OR tenant_id::text = :tid)
                    LIMIT 1
                    """
                ),
                {"cid": str(customer_id), "tid": self.tenant_id},
            ).fetchone()
        except Exception:
            # Die Ausnahme ist optional. Fehlt die Tabelle, bleibt das Stammlimit.
            self.db.rollback()
            return
        if row is None or row.credit_limit_eur is None:
            return
        limit = float(row.credit_limit_eur)
        customer_dict["credit_limit"] = limit
        customer_dict["kreditlimit"] = limit

    def merge_extensions(self, customer_dict: dict[str, Any]) -> dict[str, Any]:
        ext = self.fetch_monolith_extensions(str(customer_dict["id"]))
        if ext.get("chefanweisung") is not None:
            customer_dict["chefanweisung"] = ext["chefanweisung"]
        if ext.get("business_partner_id"):
            customer_dict["business_partner_id"] = ext["business_partner_id"]
        self.enrich_mask_satellites(customer_dict)
        return attach_mask_aliases(customer_dict)

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
                    f"WHERE id IN ({placeholders})"  # nosec B608  # reviewed-safe: interpoliert werden nur generierte Parameternamen, Werte sind gebunden
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
        # BP-Tenant-Prüfung über die kanonische Schicht (Phase 2C: BP-Logik an einer Stelle).
        from app.services.business_partner_service import BusinessPartnerService

        BusinessPartnerService(self.db, self.tenant_id).ensure_partner_belongs_to_tenant(partner_id)

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
            "tenant_id": _tenant_as_uuid(row.tenant_id),
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
            text(f"SELECT COUNT(*) FROM domain_crm.customers WHERE {where_sql}"), params  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
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
            """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            params,
        ).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            try:
                # Kanonisches Adress-Value-Object (app/core/address.py) — normalisiert
                # dict-/JSON-String-/Freitext-Formen inkl. Alias-Keys (plz/zip/ort/…).
                city = postal_code = country = address_str = None
                if row.address:
                    _addr = parse_address(row.address)
                    city = _addr.city
                    postal_code = _addr.postal_code
                    country = _addr.country
                    address_str = _addr.street or (row.address if isinstance(row.address, str) else str(row.address))
                payment_terms_val = 30
                if row.payment_terms:
                    try:
                        payment_terms_val = int(row.payment_terms) if str(row.payment_terms).isdigit() else 30
                    except Exception:
                        payment_terms_val = 30
                items.append({
                    "id": str(row.id),
                    "tenant_id": _tenant_as_uuid(row.tenant_id),
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
        customer = None
        # crm-core speaks UUID. List/KIM IDs are kunden_nr or BP-… — skip the sidecar.
        try:
            UUID(str(customer_id))
            looks_like_uuid = True
        except (ValueError, TypeError, AttributeError):
            looks_like_uuid = False
        if looks_like_uuid:
            try:
                customer = await _crm_get(customer_id)
            except Exception as exc:
                logger.warning("crm-core get_customer failed, DB fallback: %s: %s", type(exc).__name__, exc)
                customer = None
        if customer is not None:
            return self.merge_extensions(_adapt_customer(customer))
        row = self.get_from_db_any_key(customer_id)
        if row is None:
            raise EntityNotFoundError("Customer", customer_id)
        return self.merge_extensions(row)

    def get_from_db_any_key(self, customer_id: str) -> dict[str, Any] | None:
        """Resolve UUID, kunden_nr or partner number to the operational customer."""
        params = {"cid": customer_id, "tid": self.tenant_id}
        try:
            row = self.db.execute(
                text(
                    """
                    SELECT id, tenant_id, customer_number, company_name, contact_person,
                           email, phone, address, city, postal_code, country, industry,
                           website, tax_id, credit_limit, payment_terms,
                           is_active, chefanweisung, business_partner_id, created_at, updated_at
                    FROM domain_crm.customers
                    WHERE tenant_id = :tid
                      AND (
                            id::text = :cid
                         OR customer_number = :cid
                         OR business_partner_id::text = :cid
                      )
                    LIMIT 1
                    """
                ),
                params,
            ).fetchone()
        except Exception:
            self.db.rollback()
            row = None
        if row is None:
            try:
                partner = self.db.execute(
                    text(
                        """
                        SELECT partner_id, name_1, partner_number,
                               street, postal_code, city, country, phone, email, fax
                        FROM domain_crm.business_partners
                        WHERE tenant_id = :tid
                          AND (partner_id::text = :cid OR partner_number = :cid)
                        LIMIT 1
                        """
                    ),
                    params,
                ).fetchone()
            except Exception:
                self.db.rollback()
                partner = None
            if partner is not None:
                try:
                    row = self.db.execute(
                        text(
                            """
                            SELECT id, tenant_id, customer_number, company_name, contact_person,
                                   email, phone, address, city, postal_code, country, industry,
                                   website, tax_id, credit_limit, payment_terms,
                                   is_active, chefanweisung, business_partner_id, created_at, updated_at
                            FROM domain_crm.customers
                            WHERE tenant_id = :tid AND business_partner_id::text = :pid
                            LIMIT 1
                            """
                        ),
                        {"tid": self.tenant_id, "pid": str(partner.partner_id)},
                    ).fetchone()
                except Exception:
                    self.db.rollback()
                    row = None
                if row is None:
                    return {
                        "id": str(partner.partner_id),
                        "tenant_id": _tenant_as_uuid(self.tenant_id),
                        "customer_number": str(partner.partner_number or customer_id)[:50],
                        "company_name": (partner.name_1 or customer_id)[:100],
                        "name": partner.name_1 or customer_id,
                        "contact_person": None,
                        "email": partner.email,
                        "phone": partner.phone,
                        "address": partner.street,
                        "city": partner.city,
                        "postal_code": partner.postal_code,
                        "country": partner.country,
                        "fax": partner.fax,
                        "industry": None,
                        "website": None,
                        "price_group": None,
                        "tax_category": None,
                        "credit_limit": None,
                        "payment_terms": 30,
                        "tax_id": None,
                        "chefanweisung": None,
                        "business_partner_id": str(partner.partner_id),
                        "is_active": True,
                        "deleted_at": None,
                        "created_at": None,
                        "updated_at": None,
                    }
        if row is None:
            try:
                alt = self.db.execute(
                    text(
                        """
                        SELECT kunden_nr, name1, strasse, plz, ort, land, tel, fax, email,
                               postfach, postfach_plz, postfach_ort, business_partner_id
                        FROM public.kunden WHERE kunden_nr = :cid LIMIT 1
                        """
                    ),
                    {"cid": customer_id},
                ).mappings().first()
            except Exception:
                self.db.rollback()
                alt = None
            if alt is None:
                return None
            name = str(alt.get("name1") or alt.get("kunden_nr") or customer_id)[:100]
            number = str(alt.get("kunden_nr") or customer_id)[:50]
            return {
                "id": str(alt.get("business_partner_id") or number),
                "tenant_id": _tenant_as_uuid(self.tenant_id),
                "customer_number": number,
                "company_name": name,
                "name": name,
                "contact_person": None,
                "email": alt.get("email"),
                "phone": alt.get("tel"),
                "address": alt.get("strasse"),
                "city": alt.get("ort"),
                "postal_code": alt.get("plz"),
                "country": alt.get("land"),
                "industry": None,
                "website": None,
                "price_group": None,
                "tax_category": None,
                "credit_limit": None,
                "payment_terms": 30,
                "tax_id": None,
                "chefanweisung": None,
                "business_partner_id": str(alt["business_partner_id"]) if alt.get("business_partner_id") else None,
                "is_active": True,
                "deleted_at": None,
                "created_at": None,
                "updated_at": None,
                "postfach": alt.get("postfach"),
                "postfach_plz": alt.get("postfach_plz"),
                "postfach_ort": alt.get("postfach_ort"),
                "fax": alt.get("fax"),
            }
        city = getattr(row, "city", None)
        postal_code = getattr(row, "postal_code", None)
        country = getattr(row, "country", None)
        address_str = None
        if row.address:
            parsed = parse_address(row.address)
            city = city or parsed.city
            postal_code = postal_code or parsed.postal_code
            country = country or parsed.country
            address_str = parsed.street or (row.address if isinstance(row.address, str) else str(row.address))
        payment_terms_val = 30
        if row.payment_terms:
            try:
                payment_terms_val = int(row.payment_terms) if str(row.payment_terms).isdigit() else 30
            except Exception:
                payment_terms_val = 30
        return {
            "id": str(row.id),
            "tenant_id": _tenant_as_uuid(row.tenant_id),
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
            "industry": getattr(row, "industry", None),
            "website": getattr(row, "website", None),
            "price_group": None,
            "tax_category": None,
            "credit_limit": float(row.credit_limit) if row.credit_limit is not None else None,
            "payment_terms": payment_terms_val,
            "tax_id": getattr(row, "tax_id", None),
            "chefanweisung": getattr(row, "chefanweisung", None),
            "business_partner_id": getattr(row, "business_partner_id", None),
            "is_active": row.is_active if row.is_active is not None else True,
            "deleted_at": None,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

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

    def quick_search(self, term: str, limit: int = 8) -> list[dict[str, Any]]:
        if not term.strip():
            return []
        like = f"{term.strip()}%"
        contains = f"%{term.strip()}%"
        sql = text(
            """
            SELECT id, customer_number, company_name, address, is_active,
                CASE
                    WHEN customer_number ILIKE :like THEN 0
                    WHEN company_name ILIKE :like THEN 1
                    ELSE 2
                END AS rank
            FROM domain_crm.customers
            WHERE tenant_id = :tid
              AND (company_name ILIKE :contains OR customer_number ILIKE :contains)
            ORDER BY rank ASC, company_name ASC
            LIMIT :lim
            """
        )
        rows = self.db.execute(sql, {"tid": self.tenant_id, "like": like, "contains": contains, "lim": limit}).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            city, postal_code = _extract_location(address=row.address)
            out.append({
                "id": str(row.id),
                "customer_number": row.customer_number or "",
                "company_name": row.company_name or "",
                "city": city,
                "postal_code": postal_code,
                "is_active": bool(row.is_active) if row.is_active is not None else True,
            })
        return out

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        sql = text(
            """
            SELECT id, customer_number, company_name, address, is_active, updated_at
            FROM domain_crm.customers
            WHERE tenant_id = :tid AND COALESCE(is_active, TRUE) = TRUE
            ORDER BY updated_at DESC NULLS LAST, id DESC
            LIMIT :lim
            """
        )
        rows = self.db.execute(sql, {"tid": self.tenant_id, "lim": limit}).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            city, postal_code = _extract_location(address=row.address)
            out.append({
                "id": str(row.id),
                "customer_number": row.customer_number or "",
                "company_name": row.company_name or "",
                "city": city,
                "postal_code": postal_code,
                "is_active": bool(row.is_active) if row.is_active is not None else True,
            })
        return out
