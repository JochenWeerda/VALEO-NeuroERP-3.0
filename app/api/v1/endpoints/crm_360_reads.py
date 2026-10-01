"""CRM-360: Register lesen und seitenweise ausliefern."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.api.v1.endpoints.crm_360_sql import _query_many
from app.core.mask_screen_summary_common import (
    get_sortable_columns,
    paginate_tab_items as _paginate_tab_items,
)

def _normalize_tab_key(tab_key: str) -> str:
    aliases = {
        "contacts": "kontakte",
        "kontakte": "kontakte",
        "stammdaten": "stammdaten",
        "masterdata": "stammdaten",
        "finance": "dokumente",
        "belege": "auftraege",
        "aufgaben": "aufgaben",
        "kontrakte": "kontrakte",
        "angebote": "angebote",
        "quotes": "angebote",
        "offers": "angebote",
        "opportunities": "angebote",
        "historie": "historie",
        "history": "historie",
        "timeline": "historie",
        "praesente": "praesente",
        "präsente": "praesente",
        "gifts": "praesente",
        "postfach": "postfach",
        "mailbox": "postfach",
        "geo": "geo",
        "karte": "geo",
        "chefanweisungen": "chefanweisungen",
        "tab21": "chefanweisungen",
        "anschriften": "anschriften",
        "addresses": "anschriften",
        "tab23": "anschriften",
        "cpd": "cpd",
        "tab25": "cpd",
        "rabatte": "rabatte",
        "discounts": "rabatte",
        "preise": "preise",
        "prices": "preise",
    }
    return aliases.get(tab_key, tab_key)


def _fetch_customer_tab_items(
    db: Session,
    *,
    customer_id: str,
    tenant_id: str | None,
    tab_key: str,
    kunden_nr: str | None,
    kunden_name: str | None = None,
    partner_id: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    normalized = _normalize_tab_key(tab_key)

    if normalized == "stammdaten":
        return normalized, []

    if normalized == "kontakte":
        rows: list[dict[str, Any]] = []
        if kunden_nr:
            rows = _query_many(
                db,
                """
                SELECT id::text AS id,
                       COALESCE(nachname, '') AS name,
                       COALESCE(vorname, '') AS "firstName",
                       COALESCE(position, '') AS position,
                       COALESCE(email, '') AS email,
                       COALESCE(telefon1, '') AS phone1
                FROM public.kunden_ansprechpartner
                WHERE kunden_nr = :kunden_nr
                ORDER BY prioritaet NULLS LAST, nachname
                LIMIT 25
                """,
                {"kunden_nr": kunden_nr},
            )
        partner = []
        if partner_id:
            partner = _query_many(
                db,
                """
                SELECT id::text AS id,
                       COALESCE(last_name, '') AS name,
                       COALESCE(first_name, '') AS "firstName",
                       COALESCE(position, '') AS position,
                       COALESCE(email, '') AS email,
                       COALESCE(phone_1, '') AS phone1
                FROM domain_crm.business_partner_contacts
                WHERE partner_id::text = :pid
                ORDER BY priority, last_name
                LIMIT 25
                """,
                {"pid": partner_id},
            )
        return "contacts_list", rows + partner

    if normalized == "auftraege":
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   order_number,
                   status,
                   COALESCE(total_amount, 0)::float AS total_amount,
                   created_at::text AS created_at
            FROM domain_crm.sales_orders
            WHERE (
                    customer_id::text = :cid
                 OR (:nr IS NOT NULL AND customer_id::text = :nr)
                  )
              AND (:tid IS NULL OR tenant_id::text = :tid)
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id, "nr": kunden_nr},
        )
        return "recent_orders", rows

    if normalized in {"aktivitaeten", "historie"}:
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   type AS activity_type,
                   title AS subject,
                   COALESCE(status, '') AS status,
                   COALESCE(assigned_to, '') AS assigned_to,
                   COALESCE(date, created_at)::text AS created_at
            FROM domain_crm.activities
            WHERE customer = :kunde
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY COALESCE(date, created_at) DESC
            LIMIT 25
            """,
            {"kunde": kunden_name, "tid": tenant_id},
        )
        return ("historie" if normalized == "historie" else "recent_activities"), rows

    if normalized == "angebote":
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(title, '') AS title,
                   COALESCE(stage, status, '') AS stage,
                   COALESCE(estimated_value, 0)::float AS estimated_value,
                   probability,
                   expected_close_date::text AS expected_close_date
            FROM domain_crm.crm_opportunities
            WHERE (:tid IS NULL OR tenant_id::text = :tid)
              AND (
                    customer_id::text = :cid
                 OR customer_id::text = :kunden_nr
              )
            ORDER BY expected_close_date DESC NULLS LAST, created_at DESC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id, "kunden_nr": kunden_nr},
        )
        return "angebote", rows

    if normalized == "aufgaben":
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(title, '') AS titel,
                   COALESCE(type, '') AS art,
                   COALESCE(status, '') AS status,
                   COALESCE(date, created_at)::text AS faellig
            FROM domain_crm.activities
            WHERE customer = :kunde
              AND (:tid IS NULL OR tenant_id::text = :tid)
              AND (
                    COALESCE(type, '') ILIKE '%task%'
                 OR COALESCE(type, '') ILIKE '%aufgabe%'
                 OR COALESCE(status, '') ILIKE '%offen%'
              )
            ORDER BY COALESCE(date, created_at) DESC
            LIMIT 25
            """,
            {"kunde": kunden_name, "tid": tenant_id},
        )
        return "aufgaben", rows

    if normalized == "kontrakte":
        rows = _query_many(
            db,
            """
            SELECT contract_id AS id,
                   contract_no,
                   contract_type,
                   status,
                   contract_date::text AS contract_date,
                   COALESCE(total_quantity, 0)::float AS total_quantity
            FROM domain_ops.kon_contract
            WHERE (
                    party_id::text = :cid
                 OR party_id::text = :kunden_nr
                 OR (:pid IS NOT NULL AND party_id::text = :pid)
                  )
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY contract_date DESC
            LIMIT 25
            """,
            {"cid": customer_id, "kunden_nr": kunden_nr, "pid": partner_id, "tid": tenant_id},
        )
        return "kontrakte", rows

    if normalized == "praesente":
        if not kunden_nr:
            return "praesente", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   year,
                   gift_date::text AS gift_date,
                   COALESCE(occasion, '') AS occasion,
                   COALESCE(gift_name, '') AS gift_name,
                   COALESCE(quantity, 0)::float AS quantity
            FROM public.crm_gifts
            WHERE kunden_nr = :kunden_nr
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY gift_date DESC NULLS LAST, created_at DESC
            LIMIT 25
            """,
            {"kunden_nr": kunden_nr, "tid": tenant_id},
        )
        return "praesente", rows

    if normalized in {"postfach", "geo"}:
        return normalized, []

    if normalized == "chefanweisungen":
        if not partner_id:
            return "chefanweisungen", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(instruction_priority, '') AS instruction_priority,
                   COALESCE(instruction_text, '') AS instruction_text,
                   valid_from::text AS valid_from,
                   valid_to::text AS valid_to
            FROM domain_crm.business_partner_instructions
            WHERE partner_id::text = :pid
            ORDER BY created_at DESC
            LIMIT 25
            """,
            {"pid": partner_id},
        )
        return "chefanweisungen", rows

    if normalized == "anschriften":
        if not partner_id:
            return "anschriften", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(address_type, '') AS address_type,
                   COALESCE(name_1, '') AS name_1,
                   COALESCE(street, '') AS street,
                   COALESCE(postal_code, '') AS postal_code,
                   COALESCE(city, '') AS city,
                   COALESCE(email, '') AS email,
                   is_default
            FROM domain_crm.business_partner_addresses
            WHERE partner_id::text = :pid
            ORDER BY is_default DESC, address_type
            LIMIT 25
            """,
            {"pid": partner_id},
        )
        return "anschriften", rows

    if normalized == "cpd":
        if not partner_id:
            return "cpd", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(cpd_customer_number, '') AS cpd_customer_number,
                   COALESCE(debtor_account, '') AS debtor_account,
                   COALESCE(name_1, '') AS name_1,
                   COALESCE(city, '') AS city,
                   COALESCE(email, '') AS email
            FROM domain_crm.business_partner_cpd_accounts
            WHERE partner_id::text = :pid
            ORDER BY cpd_customer_number
            LIMIT 25
            """,
            {"pid": partner_id},
        )
        return "cpd", rows

    if normalized == "rabatte":
        if not partner_id:
            return "rabatte", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(article_number, '') AS article_number,
                   COALESCE(description, '') AS description,
                   COALESCE(discount_percent, 0)::float AS discount_percent,
                   valid_from::text AS valid_from,
                   valid_to::text AS valid_to
            FROM domain_crm.business_partner_discount_items
            WHERE partner_id::text = :pid
            ORDER BY article_number
            LIMIT 25
            """,
            {"pid": partner_id},
        )
        return "rabatte", rows

    if normalized == "preise":
        if not partner_id:
            return "preise", []
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   COALESCE(article_number, '') AS article_number,
                   COALESCE(description, '') AS description,
                   price_net::float AS price_net,
                   COALESCE(price_unit, '') AS price_unit,
                   valid_from::text AS valid_from,
                   valid_to::text AS valid_to
            FROM domain_crm.business_partner_price_agreements
            WHERE partner_id::text = :pid
            ORDER BY article_number
            LIMIT 25
            """,
            {"pid": partner_id},
        )
        return "preise", rows

    if normalized == "dokumente":
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   rechnungsnr,
                   faelligkeit::text AS faelligkeit,
                   offen::float AS amount,
                   GREATEST(0, (CURRENT_DATE - faelligkeit::date))::int AS days_overdue,
                   op_status
            FROM domain_erp.offene_posten
            WHERE (
                    kunde_id::text = :cid
                 OR debtor_id::text = :cid
                 OR (:kunden_nr IS NOT NULL AND (
                        kunde_id::text = :kunden_nr OR debtor_id::text = :kunden_nr
                    ))
                  )
              AND (:tid IS NULL OR tenant_id::text = :tid)
              AND COALESCE(op_status, '') NOT IN ('bezahlt', 'storniert')
            ORDER BY faelligkeit ASC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id, "kunden_nr": kunden_nr},
        )
        table_key = "open_documents" if tab_key == "dokumente" else "open_items"
        return table_key, rows

    return normalized, []


def _paginate_items(
    items: list[dict[str, Any]],
    *,
    page: int = 1,
    limit: int = 25,
    q: str | None = None,
    sort: str | None = None,
    sort_dir: str | None = None,
    screen_id: str | None = None,
    tab_key: str | None = None,
    filter_plan: dict | None = None,
) -> tuple[list[dict[str, Any]], int]:
    allowed = get_sortable_columns(screen_id, tab_key) if screen_id and tab_key else None
    return _paginate_tab_items(
        items, page=page, limit=limit, q=q,
        sort=sort, sort_dir=sort_dir, allowed_sort_columns=allowed,
        filter_plan=filter_plan,
    )

