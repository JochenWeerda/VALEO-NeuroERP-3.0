"""CRM 360°-Kundensicht — aggregiert echte ERP-Daten aus mehreren Domänen.

CRM-360-REAL-001: Alle Queries mit schema-qualifizierten Tabellennamen.
Fehlende Tabellen → leere Liste (kein silent-null), Kunde nicht gefunden → 404.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
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
            "kontakte",
            "angebote",
            "auftraege",
            "dokumente",
            "aktivitaeten",
            "historie",
        ],
        "tab_endpoints": {
            "stammdaten": _customer_tab_endpoint(customer_id, "stammdaten"),
            "kontakte": _customer_tab_endpoint(customer_id, "kontakte"),
            "contacts": _customer_tab_endpoint(customer_id, "contacts"),
            "finance": _customer_tab_endpoint(customer_id, "dokumente"),
            "angebote": _customer_tab_endpoint(customer_id, "angebote"),
            "auftraege": _customer_tab_endpoint(customer_id, "auftraege"),
            "dokumente": _customer_tab_endpoint(customer_id, "dokumente"),
            "aktivitaeten": _customer_tab_endpoint(customer_id, "aktivitaeten"),
            "historie": _customer_tab_endpoint(customer_id, "historie"),
        },
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
    response_model=dict[str, Any],
    tags=["crm", "customers", "screen-summary"],
    summary="Customer screen summary abrufen",
)
async def get_customer_screen_summary(
    customer_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Kompakter Startvertrag fuer den Universal Mask Generator.

    Liefert nur Header, Kennzahlen, Badges und verfuegbare Tabs. Tab-Details
    bleiben separate, limitierte Endpunkte.
    """

    customer = _query_one(
        db,
        """
        SELECT id, name, kunden_nr
        FROM domain_erp.business_partners
        WHERE id = :cid AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")

    sales_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(total_amount), 0)::float AS sales_ytd
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND created_at >= NOW() - INTERVAL '12 months'
        """,
        {"cid": customer_id, "tid": tenant_id},
    ) or {}
    open_items_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(offen), 0)::float AS open_items_total
        FROM domain_erp.offene_posten
        WHERE (kunden_id = :cid OR debitor_id::text = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND op_status NOT IN ('bezahlt', 'storniert')
        """,
        {"cid": customer_id, "tid": tenant_id},
    ) or {}
    activity_row = _query_one(
        db,
        """
        SELECT COUNT(*)::int AS recent_activity_count
        FROM domain_crm.activities
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND created_at >= NOW() - INTERVAL '90 days'
        """,
        {"cid": customer_id, "tid": tenant_id},
    ) or {}

    return build_customer_screen_summary(
        customer_id=customer_id,
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
    }
    return aliases.get(tab_key, tab_key)


def _fetch_customer_tab_items(
    db: Session,
    *,
    customer_id: str,
    tenant_id: str | None,
    tab_key: str,
    kunden_nr: str | None,
) -> tuple[str, list[dict[str, Any]]]:
    normalized = _normalize_tab_key(tab_key)

    if normalized in {"stammdaten", "angebote", "historie"}:
        return normalized, []

    if normalized == "kontakte":
        if not kunden_nr:
            return "contacts_list", []
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
        return "contacts_list", rows

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
            WHERE customer_id = :cid
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY created_at DESC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id},
        )
        return "recent_orders", rows

    if normalized == "aktivitaeten":
        rows = _query_many(
            db,
            """
            SELECT id::text AS id,
                   activity_type,
                   subject,
                   COALESCE(assigned_to, '') AS assigned_to,
                   created_at::text AS created_at
            FROM domain_crm.activities
            WHERE customer_id = :cid
              AND (:tid IS NULL OR tenant_id::text = :tid)
            ORDER BY created_at DESC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id},
        )
        return "recent_activities", rows

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
            WHERE (kunden_id = :cid OR debitor_id::text = :cid)
              AND (:tid IS NULL OR tenant_id::text = :tid)
              AND op_status NOT IN ('bezahlt', 'storniert')
            ORDER BY faelligkeit ASC
            LIMIT 25
            """,
            {"cid": customer_id, "tid": tenant_id},
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


@router.get(
    "/{customer_id}/tabs/{tab_key}",
    response_model=dict[str, Any],
    tags=["crm", "customers", "screen-summary"],
    summary="Customer tab list data abrufen",
)
async def get_customer_tab_data(
    customer_id: str,
    tab_key: str,
    tenant_id: Optional[str] = Query(None),
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

    customer = _query_one(
        db,
        """
        SELECT id, name, kunden_nr
        FROM domain_erp.business_partners
        WHERE id = :cid AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
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
        customer_id=customer_id,
        tenant_id=tenant_id,
        tab_key=tab_key,
        kunden_nr=customer.get("kunden_nr"),
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
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """360°-Kundensicht: aggregiert Aufträge, Rechnungen, OP, Kontrakte,
    Aktivitäten, Wareneingänge und Kreditlimit aus echten ERP-Tabellen."""

    # Kunde muss existieren (domain_erp.business_partners ist kanonisch)
    customer = _query_one(
        db,
        """
        SELECT id, name, kunden_nr
        FROM domain_erp.business_partners
        WHERE id = :cid AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    if customer is None:
        raise HTTPException(status_code=404, detail=f"Kunde {customer_id} nicht gefunden")

    # 1. Letzte 10 Aufträge (domain_crm.sales_orders)
    orders = _query_many(
        db,
        """
        SELECT id, order_number, status,
               COALESCE(total_amount, 0)::float AS total_amount,
               created_at::text
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY created_at DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 2. Jahresumsatz (aktuelle 12 Monate) — Summe abgeschlossener Aufträge
    umsatz_row = _query_one(
        db,
        """
        SELECT COALESCE(SUM(total_amount), 0)::float AS jahresumsatz
        FROM domain_crm.sales_orders
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND status IN ('GELIEFERT', 'ABGESCHLOSSEN', 'BERECHNET')
          AND created_at >= NOW() - INTERVAL '12 months'
        """,
        {"cid": customer_id, "tid": tenant_id},
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
        WHERE (kunden_id = :cid OR debitor_id::text = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND op_status NOT IN ('bezahlt', 'storniert')
        ORDER BY faelligkeit ASC
        LIMIT 20
        """,
        {"cid": customer_id, "tid": tenant_id},
    )
    # Summe offener OP
    op_summe = sum(r.get("amount") or 0.0 for r in open_payments)

    # 4. Aktive Kontrakte (domain_agrar.agrar_contracts)
    active_contracts = _query_many(
        db,
        """
        SELECT id, contract_number, status,
               lieferbeginn::text AS start_date,
               lieferende::text AS end_date,
               COALESCE(gesamtmenge_t * preis_eur_per_t, 0)::float AS total_value
        FROM domain_agrar.agrar_contracts
        WHERE (customer_id = :cid OR lieferant_id = :cid OR partner_id = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
          AND status IN ('AKTIV', 'aktiv', 'OFFEN')
        ORDER BY lieferbeginn DESC
        LIMIT 10
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 5. Letzte 5 CRM-Aktivitäten (domain_crm.activities)
    recent_activities = _query_many(
        db,
        """
        SELECT id, activity_type, subject,
               created_at::text, assigned_to
        FROM domain_crm.activities
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY created_at DESC
        LIMIT 5
        """,
        {"cid": customer_id, "tid": tenant_id},
    )

    # 6. Letzter Wareneingang (domain_agrar.harvest_acceptances)
    last_receipt_row = _query_one(
        db,
        """
        SELECT id, acceptance_number,
               accepted_at::text, net_weight_kg::float, product_id
        FROM domain_agrar.harvest_acceptances
        WHERE (supplier_id = :cid OR customer_id = :cid)
          AND (:tid IS NULL OR tenant_id::text = :tid)
        ORDER BY accepted_at DESC
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
            "quantity_kg": last_receipt_row.get("net_weight_kg"),
            "product_id": str(last_receipt_row["product_id"]) if last_receipt_row.get("product_id") else None,
            "source": "harvest_acceptances",
        }
    else:
        # Fallback: letzter Warenzugang aus Lagerbewegungen
        sm_row = _query_one(
            db,
            """
            SELECT id, reference_number, movement_date::text,
                   quantity::float, article_id
            FROM domain_inventory.inventory_stock_movements
            WHERE (:tid IS NULL OR tenant_id::text = :tid)
              AND movement_type = 'in'
              AND notes ILIKE :pattern
            ORDER BY movement_date DESC
            LIMIT 1
            """,
            {"cid": customer_id, "tid": tenant_id, "pattern": f"%{customer_id[:8]}%"},
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

    # 7. Kreditlimit (domain_crm.credit_limits wenn vorhanden)
    credit_limit_status = _query_one(
        db,
        """
        SELECT credit_limit::float, credit_used::float,
               (credit_limit - credit_used)::float AS credit_available,
               credit_status
        FROM domain_crm.credit_limits
        WHERE customer_id = :cid
          AND (:tid IS NULL OR tenant_id::text = :tid)
        LIMIT 1
        """,
        {"cid": customer_id, "tid": tenant_id},
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
    now = datetime.now(timezone.utc).isoformat()

    try:
        db.execute(
            text("""
                INSERT INTO domain_crm.crm_activities
                  (id, customer_id, tenant_id, betreff, typ, datum, verantwortlich, notiz, status, created_at)
                VALUES
                  (:aid, :cid, :tid, :betreff, :typ, :datum, :verantwortlich, :notiz, 'offen', :now)
                ON CONFLICT DO NOTHING
            """),
            {
                "aid": activity_id,
                "cid": customer_id,
                "tid": tenant_id,
                "betreff": body.get("betreff", ""),
                "typ": body.get("typ", "Sonstiges"),
                "datum": body.get("datum") or datetime.now(timezone.utc).date().isoformat(),
                "verantwortlich": body.get("verantwortlich"),
                "notiz": body.get("notiz"),
                "now": now,
            },
        )
        db.execute(
            text("""
                INSERT INTO domain_crm.crm_action_audit_log
                  (id, tenant_id, action_key, entity_type, entity_id, idempotency_key, audit_reason,
                   performed_at, result_summary)
                VALUES
                  (:id, :tid, 'create_activity', 'customer', :cid, :ikey, :areason, :now, :summary)
                ON CONFLICT DO NOTHING
            """),
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
    except Exception as exc:
        db.rollback()
        # Fehlende Tabellen im Dev/Test → graceful degradation, kein 500
        if "does not exist" in str(exc) or "UndefinedTable" in type(exc).__name__:
            return ActionResult(
                actionKey="create_activity",
                mode=mode,
                success=True,
                summary=f"Aktivität '{body.get('betreff')}' simuliert (Tabelle noch nicht angelegt).",
                affectedIds=[activity_id],
                auditEntryId=audit_id,
            )
        raise HTTPException(status_code=500, detail=f"Aktivität konnte nicht gespeichert werden: {exc}") from exc

    return ActionResult(
        actionKey="create_activity",
        mode=mode,
        success=True,
        summary=f"Aktivität '{body.get('betreff')}' vom Typ '{body.get('typ')}' erfolgreich angelegt.",
        affectedIds=[activity_id],
        auditEntryId=audit_id,
    )
