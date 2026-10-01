"""CRM 360°-Kundensicht — aggregiert echte ERP-Daten aus mehreren Domänen.

CRM-360-REAL-001: Alle Queries mit schema-qualifizierten Tabellennamen.
Fehlende Tabellen → leere Liste (kein silent-null), Kunde nicht gefunden → 404.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

# Der Mandant kam hier aus einem **Query-Parameter** (`?tenant_id=`), den kein
# Aufrufer setzt — weder die Kunden-360-Maske noch das Frontend. Damit war der
# Filter in jeder Abfrage (`:tid IS NULL OR ...`) dauerhaft offen und jeder
# Aufruf sah die Kunden, Auftraege und Kontrakte *aller* Mandanten. Der Mandant
# kommt aus dem Header `X-Tenant-ID`, wie ueberall sonst im Haus.

from app.api.v1.schemas.base import BaseSchema, TypedObjectOut
from app.api.v1.schemas.crm_360_schemas import Crm360Out


router = APIRouter()


def _query_many(db: Session, sql: str, params: dict) -> list[dict]:
    """Schema-qualifizierte Query; gibt leere Liste bei Fehler zurück."""
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        db.rollback()
        return []


def _query_one(db: Session, sql: str, params: dict) -> dict | None:
    try:
        row = db.execute(text(sql), params).mappings().first()
        return dict(row) if row else None
    except Exception:
        db.rollback()
        return None


def _kunde_finden(db: Session, customer_id: str, tenant_id: str | None) -> dict | None:
    """Den Kunden im Stamm suchen, der ihn wirklich fuehrt.

    Gesucht wurde in ``domain_erp.business_partners`` — die Tabelle ist **leer**
    und hat die abgefragten Spalten (`name`, `kunden_nr`) gar nicht. Das
    ``except`` in `_query_one` verschluckte den Spaltenfehler, die Suche lief
    ins Leere, und **jedes** Register der Kunden-360-Maske antwortete „Kunde
    nicht gefunden" — auch fuer Kunden, die es gibt.

    Gefuehrt wird der Kunde in ``domain_crm.customers`` (operativer Stamm) und
    als Partner in ``domain_crm.business_partners``. Beide werden befragt, der
    operative zuerst: Er traegt die Kundennummer, mit der die Register weiter
    suchen.
    """
    params = {"cid": customer_id, "tid": tenant_id}
    kunde = _query_one(
        db,
        """
        SELECT id::text AS id, company_name AS name, customer_number AS kunden_nr,
               business_partner_id::text AS business_partner_id
        FROM domain_crm.customers
        WHERE (:tid IS NULL OR tenant_id::text = :tid)
          AND (
                id::text = :cid
             OR customer_number = :cid
             OR business_partner_id::text = :cid
          )
        LIMIT 1
        """,
        params,
    )
    if kunde is not None:
        return kunde

    partner = _query_one(
        db,
        """
        SELECT partner_id::text AS id, name_1 AS name, partner_number AS kunden_nr,
               partner_id::text AS business_partner_id
        FROM domain_crm.business_partners
        WHERE (:tid IS NULL OR tenant_id::text = :tid)
          AND (partner_id::text = :cid OR partner_number = :cid)
        LIMIT 1
        """,
        params,
    )
    if partner is not None:
        linked = _query_one(
            db,
            """
            SELECT id::text AS id, company_name AS name, customer_number AS kunden_nr,
                   business_partner_id::text AS business_partner_id
            FROM domain_crm.customers
            WHERE (:tid IS NULL OR tenant_id::text = :tid)
              AND business_partner_id::text = :pid
            LIMIT 1
            """,
            {"pid": partner["id"], "tid": tenant_id},
        )
        return linked or partner

    # public.kunden fuehrt name1, nicht name. Die Spalte ist in
    # kunden_bp_bridge_20260601 angelegt.
    alt = _query_one(
        db,
        """
        SELECT COALESCE(business_partner_id::text, kunden_nr) AS id,
               COALESCE(name1, kunden_nr) AS name,
               kunden_nr,
               business_partner_id::text AS business_partner_id
        FROM public.kunden
        WHERE kunden_nr = :cid
        LIMIT 1
        """,
        {"cid": customer_id},
    )
    if alt is None:
        return None
    linked = _query_one(
        db,
        """
        SELECT id::text AS id, company_name AS name, customer_number AS kunden_nr,
               business_partner_id::text AS business_partner_id
        FROM domain_crm.customers
        WHERE (:tid IS NULL OR tenant_id::text = :tid)
          AND (customer_number = :nr OR business_partner_id::text = :bid)
        LIMIT 1
        """,
        {"nr": alt.get("kunden_nr"), "bid": alt.get("id"), "tid": tenant_id},
    )
    return linked or alt


def _safe_query(db: Session, sql: str, params: dict) -> dict | None:
    """Backward-compatible single-row safe query used by older CRM 360 tests."""
    return _query_one(db, sql, params)


def _customer_tab_endpoint(customer_id: str, tab_key: str) -> str:
    return f"/api/v1/crm/customers/{customer_id}/tabs/{tab_key}"


def build_customer_screen_summary(
    *,
    customer_id: str,
    tenant_id: str | None,
    customer: dict[str, Any],
    sales_ytd: float = 0.0,
    open_items_total: float = 0.0,
    recent_activity_count: int = 0,
) -> dict[str, Any]:
    credit_status = "warning" if open_items_total > 0 else "ok"
    return {
        "schema_version": 1,
        "screen_id": "crm/customer-360",
        "customer_id": customer_id,
        "tenant_id": tenant_id,
        "title": customer.get("name") or "Kunde",
        "subtitle": customer.get("kunden_nr"),
        "summary": {
            "sales_ytd": sales_ytd,
            "open_items_total": open_items_total,
            "recent_activity_count": recent_activity_count,
            "credit_status": credit_status,
        },
        "badges": [
            {"key": "credit", "label": "Kredit", "tone": credit_status},
            {"key": "generator", "label": "Generator Pilot", "tone": "neutral"},
        ],
        "available_tabs": [
            "stammdaten",
            "masterdata",
            "address",
            "kontakte",
            "contacts",
            "angebote",
            "auftraege",
            "belege",
            "dokumente",
            "finance",
            "aktivitaeten",
            "aufgaben",
            "kontrakte",
            "praesente",
            "postfach",
            "geo",
            "historie",
        ],
        "tab_endpoints": {
            "stammdaten": _customer_tab_endpoint(customer_id, "stammdaten"),
            "masterdata": _customer_tab_endpoint(customer_id, "stammdaten"),
            "kontakte": _customer_tab_endpoint(customer_id, "kontakte"),
            "contacts": _customer_tab_endpoint(customer_id, "contacts"),
            "finance": _customer_tab_endpoint(customer_id, "dokumente"),
            "angebote": _customer_tab_endpoint(customer_id, "angebote"),
            "auftraege": _customer_tab_endpoint(customer_id, "auftraege"),
            "belege": _customer_tab_endpoint(customer_id, "auftraege"),
            "dokumente": _customer_tab_endpoint(customer_id, "dokumente"),
            "aktivitaeten": _customer_tab_endpoint(customer_id, "aktivitaeten"),
            "aufgaben": _customer_tab_endpoint(customer_id, "aufgaben"),
            "kontrakte": _customer_tab_endpoint(customer_id, "kontrakte"),
            "praesente": _customer_tab_endpoint(customer_id, "praesente"),
            "gifts": _customer_tab_endpoint(customer_id, "praesente"),
            "postfach": _customer_tab_endpoint(customer_id, "postfach"),
            "geo": _customer_tab_endpoint(customer_id, "geo"),
            "historie": _customer_tab_endpoint(customer_id, "historie"),
        },
        "summary_items": [
            {"key": "kunden_nr", "label": "Kunden-Nr.", "value": customer.get("kunden_nr"), "kind": "identity"},
            {"key": "party_status", "label": "Status", "value": "Kunde", "kind": "status", "tone": "success"},
            {"key": "sales_ytd", "label": "Umsatz 12M", "value": sales_ytd, "kind": "kpi"},
            {
                "key": "open_items_total",
                "label": "Offene Posten",
                "value": open_items_total,
                "kind": "kpi",
                "tone": "warning" if open_items_total > 0 else "neutral",
            },
            {
                "key": "recent_activity_count",
                "label": "Aktivitaeten 90T",
                "value": recent_activity_count,
                "kind": "contact",
            },
        ],
        "actions": [
            {"key": "edit", "label": "Bearbeiten", "permission": "crm.customer.update"},
            {"key": "create_activity", "label": "Aktivitaet anlegen", "permission": "crm.activity.create"},
        ],
        "performance": {
            "initial_payload_budget_kb": 48,
            "tabs_lazy": True,
            "lookup_min_chars": 2,
            "default_table_limit": 25,
        },
    }


@router.get(
    "/{customer_id}/screen-summary",
    response_model=TypedObjectOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Customer screen summary abrufen",
)
async def get_customer_screen_summary(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Kompakter Startvertrag fuer den Universal Mask Generator.

    Liefert nur Header, Kennzahlen, Badges und verfuegbare Tabs. Tab-Details
    bleiben separate, limitierte Endpunkte.
    """

    customer = _kunde_finden(db, customer_id, tenant_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")
    canonical_id = str(customer.get("id") or customer_id)

    sales_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(total_amount), 0)::float AS sales_ytd
        FROM domain_crm.sales_orders
        WHERE (
                customer_id::text = :cid
             OR (:nr IS NOT NULL AND customer_id::text = :nr)
              )
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND deleted_at IS NULL
          AND status IN ('completed', 'geliefert', 'invoiced')
          AND created_at >= NOW() - INTERVAL '12 months'
        """,
        {"cid": canonical_id, "tid": tenant_id, "nr": customer.get("kunden_nr")},
    ) or {}
    open_items_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(offen), 0)::float AS open_items_total
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
        """,
        {"cid": canonical_id, "tid": tenant_id, "kunden_nr": customer.get("kunden_nr")},
    ) or {}
    activity_row = _query_one(
        db,
        """
        SELECT COUNT(*)::int AS recent_activity_count
        FROM domain_crm.activities
        WHERE customer = :kunde
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND created_at >= NOW() - INTERVAL '90 days'
        """,
        # Die Aktivitaet kennt ihren Kunden nur beim Namen: `customer` ist ein
        # String(100), keine Kundenreferenz. Mehr gibt das Modell nicht her.
        {"kunde": customer.get("name"), "tid": tenant_id},
    ) or {}

    return build_customer_screen_summary(
        customer_id=canonical_id,
        tenant_id=tenant_id,
        customer=customer,
        sales_ytd=float(sales_row.get("sales_ytd") or 0.0),
        open_items_total=float(open_items_row.get("open_items_total") or 0.0),
        recent_activity_count=int(activity_row.get("recent_activity_count") or 0),
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


from app.core.mask_screen_summary_common import get_sortable_columns, paginate_tab_items as _paginate_tab_items


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


class CustomerTabOut(BaseSchema):
    """Die Huelle jeder Register-Antwort der Kunden-360-Maske."""

    model_config = ConfigDict(extra="allow")

    tab_key: str
    table_key: str
    total: int = 0
    page: int = 1
    limit: int = 25


class CustomerContactRowOut(BaseSchema):
    """Eine Zeile im Register Ansprechpartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str = ""
    firstName: str = ""
    position: str = ""
    email: str = ""
    phone1: str = ""


class CustomerOrderRowOut(BaseSchema):
    """Eine Zeile im Register Auftraege."""

    model_config = ConfigDict(extra="allow")

    id: str
    order_number: Optional[str] = None
    status: Optional[str] = None
    total_amount: float = 0.0
    created_at: Optional[str] = None


class CustomerActivityRowOut(BaseSchema):
    """Eine Zeile im Register Aktivitaeten."""

    model_config = ConfigDict(extra="allow")

    id: str
    activity_type: Optional[str] = None
    subject: Optional[str] = None
    status: str = ""
    assigned_to: str = ""
    created_at: Optional[str] = None


class CustomerDocumentRowOut(BaseSchema):
    """Eine Zeile im Register Dokumente — offene Posten des Kunden."""

    model_config = ConfigDict(extra="allow")

    id: str
    rechnungsnr: Optional[str] = None
    faelligkeit: Optional[str] = None
    amount: float = 0.0
    days_overdue: int = 0
    op_status: Optional[str] = None


class CustomerContactsTabOut(CustomerTabOut):
    items: list[CustomerContactRowOut] = Field(default_factory=list)


class CustomerOrdersTabOut(CustomerTabOut):
    items: list[CustomerOrderRowOut] = Field(default_factory=list)


class CustomerActivitiesTabOut(CustomerTabOut):
    items: list[CustomerActivityRowOut] = Field(default_factory=list)


class CustomerDocumentsTabOut(CustomerTabOut):
    items: list[CustomerDocumentRowOut] = Field(default_factory=list)


class CustomerTaskRowOut(BaseSchema):
    """Eine Zeile im Register Aufgaben."""

    model_config = ConfigDict(extra="allow")

    id: str
    titel: str = ""
    art: str = ""
    prioritaet: str = ""
    status: str = ""
    faellig: Optional[str] = None


class CustomerContractRowOut(BaseSchema):
    """Eine Zeile im Register Kontrakte."""

    model_config = ConfigDict(extra="allow")

    id: str
    contract_no: Optional[str] = None
    contract_type: Optional[str] = None
    status: Optional[str] = None
    contract_date: Optional[str] = None
    total_quantity: float = 0.0


class CustomerTasksTabOut(CustomerTabOut):
    items: list[CustomerTaskRowOut] = Field(default_factory=list)


class CustomerContractsTabOut(CustomerTabOut):
    items: list[CustomerContractRowOut] = Field(default_factory=list)


class CustomerOfferRowOut(BaseSchema):
    """Eine Zeile im Register Angebote — Verkaufschance aus der Pipeline."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str = ""
    stage: str = ""
    estimated_value: float = 0.0
    expected_close_date: Optional[str] = None
    probability: Optional[float] = None


class CustomerOffersTabOut(CustomerTabOut):
    items: list[CustomerOfferRowOut] = Field(default_factory=list)


class CustomerHistoryTabOut(CustomerTabOut):
    items: list[CustomerActivityRowOut] = Field(default_factory=list)


class CustomerInstructionRowOut(BaseSchema):
    """Eine Chef-Anweisung am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    instruction_priority: str = ""
    instruction_text: str = ""
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerInstructionsTabOut(CustomerTabOut):
    items: list[CustomerInstructionRowOut] = Field(default_factory=list)


class CustomerAddressRowOut(BaseSchema):
    """Eine normalisierte Anschrift am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    address_type: str = ""
    name_1: str = ""
    street: str = ""
    postal_code: str = ""
    city: str = ""
    email: str = ""
    is_default: Optional[bool] = None


class CustomerAddressesTabOut(CustomerTabOut):
    items: list[CustomerAddressRowOut] = Field(default_factory=list)


class CustomerCpdRowOut(BaseSchema):
    """Ein CPD-Konto am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    cpd_customer_number: str = ""
    debtor_account: str = ""
    name_1: str = ""
    city: str = ""
    email: str = ""


class CustomerCpdTabOut(CustomerTabOut):
    items: list[CustomerCpdRowOut] = Field(default_factory=list)


class CustomerDiscountRowOut(BaseSchema):
    """Eine Rabattzeile am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    article_number: str = ""
    description: str = ""
    discount_percent: float = 0.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerDiscountsTabOut(CustomerTabOut):
    items: list[CustomerDiscountRowOut] = Field(default_factory=list)


class CustomerPriceRowOut(BaseSchema):
    """Eine Preisvereinbarung am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    article_number: str = ""
    description: str = ""
    price_net: Optional[float] = None
    price_unit: str = ""
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerPricesTabOut(CustomerTabOut):
    items: list[CustomerPriceRowOut] = Field(default_factory=list)


# Vier benannte Register vor der generischen Route
# -----------------------------------------------
#
# Die generische Route `/{customer_id}/tabs/{tab_key}` antwortet mit
# ``TypedObjectOut`` — einer Huelle, die jede Form durchlaesst. Damit kann das
# Feldvertrags-Gate nicht pruefen, ob die Spalten der Maske (ScreenDefinition
# `crm/customer-360`) den Schluesseln der Antwort entsprechen; eine Spalte, die
# ins Leere zeigt, bliebe eine leere Zelle und faellt niemandem auf.
#
# Deshalb dieselbe Aufteilung wie bei Auftrag und Rechnung: je Register eine
# eigene Route mit deklarierter Zeilenform. Sie muessen **vor** der generischen
# Route stehen, sonst verschluckt `{tab_key}` sie.

@router.get(
    "/{customer_id}/tabs/contacts",
    response_model=CustomerContactsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Ansprechpartner",
)
async def get_customer_tab_contacts(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die Ansprechpartner des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="contacts", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/auftraege",
    response_model=CustomerOrdersTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Auftraege",
)
async def get_customer_tab_auftraege(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die letzten Auftraege des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="auftraege", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/aktivitaeten",
    response_model=CustomerActivitiesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Aktivitaeten",
)
async def get_customer_tab_aktivitaeten(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die letzten CRM-Aktivitaeten zum Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="aktivitaeten", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/dokumente",
    response_model=CustomerDocumentsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Dokumente",
)
async def get_customer_tab_dokumente(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Die offenen Posten des Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="dokumente", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/aufgaben",
    response_model=CustomerTasksTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Aufgaben",
)
async def get_customer_tab_aufgaben(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Offene Aufgaben und Wiedervorlagen zum Kunden."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="aufgaben", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/kontrakte",
    response_model=CustomerContractsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Kontrakte",
)
async def get_customer_tab_kontrakte(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Kontrakte der Partei."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="kontrakte", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/angebote",
    response_model=CustomerOffersTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Angebote",
)
async def get_customer_tab_angebote(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Verkaufschancen der Partei aus der lokalen Pipeline."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="angebote", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/historie",
    response_model=CustomerHistoryTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Historie",
)
async def get_customer_tab_historie(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Aktivitaeten des Kunden in zeitlicher Reihenfolge."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="historie", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/chefanweisungen",
    response_model=CustomerInstructionsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Chef-Anweisungen",
)
async def get_customer_tab_chefanweisungen(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Normalisierte Chef-Anweisungen des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="chefanweisungen", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/anschriften",
    response_model=CustomerAddressesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Anschriften",
)
async def get_customer_tab_anschriften(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Normalisierte Anschriften des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="anschriften", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/cpd",
    response_model=CustomerCpdTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: CPD-Konten",
)
async def get_customer_tab_cpd(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """CPD-Konten des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="cpd", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/rabatte",
    response_model=CustomerDiscountsTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Rabatte",
)
async def get_customer_tab_rabatte(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Artikelrabatte des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="rabatte", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/preise",
    response_model=CustomerPricesTabOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Kunde: Preise",
)
async def get_customer_tab_preise(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    db: Session = Depends(get_db),
):
    """Preisvereinbarungen des Partners."""
    return await get_customer_tab_data(
        customer_id=customer_id, tab_key="preise", tenant_id=tenant_id,
        page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir,
        filter_plan=filter_plan, filter_plan_legacy=None, db=db,
    )


@router.get(
    "/{customer_id}/tabs/{tab_key}",
    response_model=TypedObjectOut,
    tags=["crm", "customers", "screen-summary"],
    summary="Customer tab list data abrufen",
)
async def get_customer_tab_data(
    customer_id: str,
    tab_key: str,
    tenant_id: str = Depends(get_tenant_id),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=50),
    q: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON FilterPlan"),
    filter_plan_legacy: Optional[str] = Query(
        None,
        alias="filterPlan",
        include_in_schema=False,
        description="Deprecated camelCase alias for filter_plan.",
    ),
    db: Session = Depends(get_db),
):
    """Limitierte Tab-Listen fuer den Universal Mask Generator (read-only)."""
    import json

    customer = _kunde_finden(db, customer_id, tenant_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")

    parsed_filter_plan: dict | None = None
    raw_filter_plan = filter_plan or filter_plan_legacy
    if raw_filter_plan:
        try:
            parsed_filter_plan = json.loads(raw_filter_plan)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="filter_plan must be valid JSON")

    table_key, items = _fetch_customer_tab_items(
        db,
        customer_id=str(customer.get("id") or customer_id),
        tenant_id=tenant_id,
        tab_key=tab_key,
        kunden_nr=customer.get("kunden_nr"),
        kunden_name=customer.get("name"),
        partner_id=customer.get("business_partner_id"),
    )
    paged_items, total = _paginate_items(
        items, page=page, limit=limit, q=q,
        sort=sort, sort_dir=sort_dir,
        screen_id="crm/customer-360", tab_key=tab_key,
        filter_plan=parsed_filter_plan,
    )
    return {
        "tab_key": tab_key,
        "table_key": table_key,
        "items": paged_items,
        "page": page,
        "limit": limit,
        "total": total,
    }


@router.get("/{customer_id}/360", response_model=Crm360Out, tags=["crm", "customers"], summary="Customer 360 abrufen")
async def get_customer_360(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """360°-Kundensicht: aggregiert Aufträge, Rechnungen, OP, Kontrakte,
    Aktivitäten, Wareneingänge und Kreditlimit aus echten ERP-Tabellen."""

    # Kunde muss existieren — gefuehrt wird er in domain_crm.customers
    # bzw. im Partnerstamm; domain_erp.business_partners ist leer.
    customer = _kunde_finden(db, customer_id, tenant_id)
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")
    customer_id = str(customer.get("id") or customer_id)
    kunden_nr = customer.get("kunden_nr")

    # 1. Letzte 10 Aufträge (domain_crm.sales_orders)
    orders = _query_many(
        db,
        """
        SELECT id, order_number, status,
               COALESCE(total_amount, 0)::float AS total_amount,
               created_at::text
        FROM domain_crm.sales_orders
        WHERE (
                customer_id::text = :cid
             OR (:nr IS NOT NULL AND customer_id::text = :nr)
              )
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id, "nr": kunden_nr},
    )

    # 2. Jahresumsatz der letzten 12 Monate. Gezaehlt werden die Status, die
    # der Auftrag wirklich schreibt: completed, geliefert, invoiced.
    umsatz_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(total_amount), 0)::float AS jahresumsatz
        FROM domain_crm.sales_orders
        WHERE (
                customer_id::text = :cid
             OR (:nr IS NOT NULL AND customer_id::text = :nr)
              )
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND deleted_at IS NULL
          AND status IN ('completed', 'geliefert', 'invoiced')
          AND created_at >= NOW() - INTERVAL '12 months'
        """,
        {"cid": customer_id, "tid": tenant_id, "nr": kunden_nr},
    )
    jahresumsatz = umsatz_row["jahresumsatz"] if umsatz_row else 0.0

    # 3. Offene Posten (domain_erp.open_items)
    open_payments = _query_many(
        db,
        """
        SELECT id, rechnungsnr, faelligkeit::text,
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
        LIMIT 20
        """,
        {"cid": customer_id, "tid": tenant_id, "kunden_nr": kunden_nr},
    )
    # Summe offener OP
    op_summe = sum(r.get("amount") or 0.0 for r in open_payments)

    # 4. Laufende Kontrakte
    #
    # Gelesen wurde ``domain_agrar.agrar_contracts`` — das Schema gibt es nicht.
    # Gefuehrt werden die Kontrakte in ``domain_inventory.agrar_contracts``, und
    # zwar mit anderen Spalten *und* anderen Statuswerten: `open` und
    # `partially_allocated`, nicht `AKTIV`. Beides zusammen haette auch nach dem
    # blossen Umhaengen des Schemas noch eine leere Liste ergeben.
    #
    # Der Schluessel partner_id ist der Geschaeftspartner (UUID) oder dessen
    # Partnernummer. Die Kunden-UUID allein trifft die geschriebenen Kontrakte nicht.
    partner_id = customer.get("business_partner_id")
    active_contracts = _query_many(
        db,
        """
        SELECT id::text AS id, contract_number, status,
               valid_from::text AS start_date,
               valid_until::text AS end_date,
               COALESCE(total_quantity_kg / 1000.0 * fixed_price, 0)::float AS total_value
        FROM domain_inventory.agrar_contracts
        WHERE (
                partner_id::text = :cid
             OR (:pid IS NOT NULL AND partner_id::text = :pid)
             OR (:nr IS NOT NULL AND partner_id::text = :nr)
             OR partner_id::text IN (
                    SELECT partner_number
                    FROM domain_crm.business_partners
                    WHERE partner_id::text = :cid
                       OR (:pid IS NOT NULL AND partner_id::text = :pid)
                )
              )
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND status IN ('open', 'partially_allocated')
        ORDER BY valid_from DESC NULLS LAST
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id, "pid": partner_id, "nr": kunden_nr},
    )

    # 5. Letzte 5 CRM-Aktivitäten (domain_crm.activities)
    recent_activities = _query_many(
        db,
        """
        SELECT id::text AS id,
               type AS activity_type,
               title AS subject,
               COALESCE(date, created_at)::text AS created_at,
               assigned_to
        FROM domain_crm.activities
        WHERE customer = :kunde
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY COALESCE(date, created_at) DESC
        LIMIT 5
        """,
        {"kunde": customer.get("name"), "tid": tenant_id},
    )

    # 6. Letzte Ernteannahme. Quelle: domain_inventory.harvest_acceptances
    # (Annahmeschein). domain_agrar.harvest_acceptances ist die Sammelabrechnung
    # und hat weder customer_id noch Annahmescheinnummer.
    last_receipt_row = _query_one(
        db,
        """
        SELECT id::text AS id,
               acceptance_number,
               delivery_date::text AS accepted_at,
               article_id::text AS product_id
        FROM domain_inventory.harvest_acceptances
        WHERE customer_id::text = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY delivery_date DESC, created_at DESC NULLS LAST
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    last_goods_receipt = None
    if last_receipt_row:
        last_goods_receipt = {
            "id": str(last_receipt_row["id"]),
            "reference_number": last_receipt_row.get("acceptance_number"),
            "received_at": last_receipt_row.get("accepted_at"),
            "product_id": last_receipt_row.get("product_id"),
            "source": "harvest_acceptances",
        }
    else:
        # Fallback, wenn kein Annahmeschein da ist. Verknuepfung ist
        # owner_partner_id, nicht ein Textsuche in notes.
        sm_row = _query_one(
            db,
            """
            SELECT id::text AS id,
                   reference_number,
                   created_at::text AS movement_date,
                   quantity::float AS quantity,
                   article_id::text AS article_id
            FROM domain_inventory.inventory_stock_movements
            WHERE movement_type = 'in'
              AND (
                    owner_partner_id::text = :cid
                 OR (:pid IS NOT NULL AND owner_partner_id::text = :pid)
              )
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY created_at DESC
            LIMIT 1
            """,
            {
                "cid": customer_id,
                "tid": tenant_id,
                "pid": customer.get("business_partner_id"),
            },
        )
        if sm_row:
            last_goods_receipt = {
                "id": str(sm_row["id"]),
                "reference_number": sm_row.get("reference_number"),
                "received_at": sm_row.get("movement_date"),
                "quantity_kg": sm_row.get("quantity"),
                "article_id": str(sm_row["article_id"]) if sm_row.get("article_id") else None,
                "source": "inventory_stock_movements",
            }

    # 7. Kreditlimit. Ausnahme in credit_limits, sonst der Stamm.
    # Die Migration legt credit_limit_eur an, nicht credit_limit/credit_used.
    ausnahme = _query_one(
        db,
        """
        SELECT credit_limit_eur::float AS credit_limit,
               warning_threshold_percent::float AS warning_threshold_percent,
               block_threshold_percent::float AS block_threshold_percent
        FROM domain_crm.credit_limits
        WHERE customer_id::text = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    if ausnahme is not None:
        credit_limit_status = {**ausnahme, "source": "ausnahme"}
    else:
        stamm_limit = _query_one(
            db,
            """
            SELECT credit_limit::float AS credit_limit
            FROM domain_crm.customers
            WHERE id::text = :cid
            LIMIT 1
            """,
            {"cid": customer_id},
        )
        credit_limit_status = (
            {"credit_limit": stamm_limit["credit_limit"], "source": "stamm"}
            if stamm_limit is not None
            else None
        )

    return {
        "customer_id": customer_id,
        "tenant_id": tenant_id,
        "jahresumsatz_eur": jahresumsatz,
        "offene_op_summe_eur": op_summe,
        "recent_orders": orders,
        "open_invoices": [],  # covered by open_payments (OP-basiert)
        "open_payments": open_payments,
        "active_contracts": active_contracts,
        "recent_activities": recent_activities,
        "open_complaints": [],
        "last_goods_receipt": last_goods_receipt,
        "credit_limit_status": credit_limit_status,
    }


# ── UIX-035: ActionRuntime Command-Endpoint ───────────────────────────────────

class CreateActivityRequest(BaseModel):
    """Payload für das Anlegen einer CRM-Aktivität via ActionRuntime."""

    betreff: str = Field(..., min_length=1, max_length=200, description="Betreff / Titel der Aktivität")
    typ: str = Field(..., description="Aktivitätstyp z.B. Anruf, Besuch, E-Mail, Aufgabe")
    datum: Optional[str] = Field(None, description="Geplantes Datum (ISO-8601), leer = heute")
    verantwortlich: Optional[str] = Field(None, max_length=120)
    notiz: Optional[str] = Field(None, max_length=2000)

    # ActionRuntime-Steuerfelder (vom useActionRuntime automatisch gesetzt)
    _mode: Literal["execute", "dryRun", "validate", "propose"] = "execute"
    _auditReason: Optional[str] = None
    _idempotencyKey: Optional[str] = None


class ActionResult(BaseModel):
    """Einheitliches ActionResult-Format — spiegelt den Frontend-Typ."""

    actionKey: str
    mode: str
    success: bool
    summary: Optional[str] = None
    proposedChanges: Optional[list[dict[str, Any]]] = None
    validationErrors: Optional[list[dict[str, Any]]] = None
    affectedIds: Optional[list[str]] = None
    auditEntryId: Optional[str] = None
    error: Optional[str] = None


def _validate_create_activity(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Fachliche Validierung; gibt leere Liste zurück wenn alles OK."""
    errors: list[dict[str, Any]] = []
    if not payload.get("betreff", "").strip():
        errors.append({"field": "betreff", "message": "Betreff ist ein Pflichtfeld.", "severity": "blocking"})
    valid_types = {"Anruf", "Besuch", "E-Mail", "Aufgabe", "Meeting", "Sonstiges"}
    if payload.get("typ") and payload["typ"] not in valid_types:
        errors.append({"field": "typ", "message": f"Ungültiger Typ. Erlaubt: {', '.join(sorted(valid_types))}.", "severity": "blocking"})
    return errors


@router.post(
    "/{customer_id}/actions/create_activity",
    response_model=ActionResult,
    summary="CRM-Aktivität anlegen (ActionRuntime)",
    tags=["crm", "customers", "actions"],
)
async def create_activity_action(
    customer_id: str,
    body: dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> ActionResult:
    """ActionRuntime-Endpoint für 'create_activity'.

    Unterstützt _mode: execute | dryRun | validate | propose.
    - validate / dryRun: validiert Payload, schreibt nichts.
    - propose: gibt vorausgefüllten Payload-Vorschlag zurück.
    - execute: legt Aktivität an, schreibt Audit-Log-Eintrag.
    """
    mode: str = body.pop("_mode", "execute")
    audit_reason: str | None = body.pop("_auditReason", None)
    idempotency_key: str | None = body.pop("_idempotencyKey", None)

    if mode == "propose":
        return ActionResult(
            actionKey="create_activity",
            mode=mode,
            success=True,
            summary="Vorschlag für neue Aktivität",
            proposedChanges=[{
                "betreff": f"Aktivität für Kunde {customer_id[:8]}",
                "typ": "Anruf",
                "datum": datetime.now(timezone.utc).date().isoformat(),
                "verantwortlich": None,
                "notiz": None,
            }],
        )

    validation_errors = _validate_create_activity(body)

    if mode in ("validate", "dryRun"):
        return ActionResult(
            actionKey="create_activity",
            mode=mode,
            success=len(validation_errors) == 0,
            summary="Validierung erfolgreich — keine Änderungen geschrieben." if not validation_errors else "Validierung fehlgeschlagen.",
            proposedChanges=[body] if not validation_errors else None,
            validationErrors=validation_errors or None,
        )

    # execute
    if validation_errors:
        return ActionResult(
            actionKey="create_activity",
            mode=mode,
            success=False,
            error="Validierung fehlgeschlagen — Aktivität wurde nicht angelegt.",
            validationErrors=validation_errors,
        )

    activity_id = str(uuid.uuid4())
    audit_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    kunde = db.execute(
        text(
            """
            SELECT COALESCE(company_name, customer_number, '') AS name
            FROM domain_crm.customers
            WHERE id::text = :cid
              AND (:tid IS NULL OR tenant_id::text = :tid)
            LIMIT 1
            """
        ),
        {"cid": customer_id, "tid": tenant_id},
    ).mappings().first()
    if kunde is None:
        return ActionResult(
            actionKey="create_activity",
            mode=mode,
            success=False,
            error="Kunde nicht gefunden.",
        )

    verantwortlich = (body.get("verantwortlich") or "Akte")[:100]
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_crm.activities
                  (id, type, title, customer, contact_person, date, status, assigned_to, description, tenant_id)
                VALUES
                  (:aid, :typ, :titel, :kunde, :person, :datum, 'offen', :verantwortlich, :notiz, :tid)
                """
            ),
            {
                "aid": activity_id,
                "typ": (body.get("typ") or "Sonstiges")[:20],
                "titel": body.get("betreff", "")[:200],
                "kunde": str(kunde["name"])[:100] or customer_id[:100],
                "person": verantwortlich,
                "datum": body.get("datum") or now.date().isoformat(),
                "verantwortlich": verantwortlich,
                "notiz": body.get("notiz"),
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Aktivität konnte nicht gespeichert werden: {exc}") from exc

    try:
        db.execute(
            text(
                """
                INSERT INTO domain_crm.crm_action_audit_log
                  (id, tenant_id, action_key, entity_type, entity_id, idempotency_key, audit_reason,
                   performed_at, result_summary)
                VALUES
                  (:id, :tid, 'create_activity', 'customer', :cid, :ikey, :areason, :now, :summary)
                """
            ),
            {
                "id": audit_id,
                "tid": tenant_id,
                "cid": customer_id,
                "ikey": idempotency_key,
                "areason": audit_reason,
                "now": now,
                "summary": f"Aktivität '{body.get('betreff')}' vom Typ '{body.get('typ')}' angelegt.",
            },
        )
        db.commit()
    except Exception:
        # Die Aktivitaet ist bereits festgeschrieben. Ein fehlendes Audit
        # darf sie nicht als Fehlschlag ausgeben.
        db.rollback()
        audit_id = None

    return ActionResult(
        actionKey="create_activity",
        mode=mode,
        success=True,
        summary=f"Aktivität '{body.get('betreff')}' vom Typ '{body.get('typ')}' erfolgreich angelegt.",
        affectedIds=[activity_id],
        auditEntryId=audit_id,
    )
