"""CRM 360°-Kundensicht — aggregiert echte ERP-Daten aus mehreren Domänen.

CRM-360-REAL-001: Alle Queries mit schema-qualifizierten Tabellennamen.
Fehlende Tabellen → leere Liste (kein silent-null), Kunde nicht gefunden → 404.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id

# Der Mandant kam hier aus einem **Query-Parameter** (`?tenant_id=`), den kein
# Aufrufer setzt — weder die Kunden-360-Maske noch das Frontend. Damit war der
# Filter in jeder Abfrage (`:tid IS NULL OR ...`) dauerhaft offen und jeder
# Aufruf sah die Kunden, Auftraege und Kontrakte *aller* Mandanten. Der Mandant
# kommt aus dem Header `X-Tenant-ID`, wie ueberall sonst im Haus.

from app.api.v1.endpoints.crm_360_sql import _kunde_finden, _query_one
from app.api.v1.endpoints.crm_360_tabs import router as _customer_tabs_router
from app.api.v1.schemas.base import TypedObjectOut
from app.api.v1.schemas.crm_360_schemas import Crm360Out

router = APIRouter()
router.include_router(_customer_tabs_router)


def _query_many(db: Session, sql: str, params: dict) -> list[dict]:
    """Schema-qualifizierte Query, hoechstens 25 Zeilen.

    Jede Abfrage der Akte begrenzt sich im SQL auf hoechstens 25 Zeilen.
    Dieselbe Grenze gilt hier noch einmal, damit ein vergessenes LIMIT
    keine unbegrenzte Liste aus der Datenbank zieht.
    """
    try:
        rows = db.execute(text(sql), params).mappings().fetchmany(25)
        return [dict(r) for r in rows]
    except Exception:
        db.rollback()
        return []


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
            "tax",
            "bank",
            "system",
            "quality_compliance",
            "marketing",
            "cooperative",
            "output",
            "interfaces",
            "potential",
            "chefanweisungen",
            "anschriften",
            "kontoauszug",
            "cpd",
            "rabatte",
            "preise",
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
            "chefanweisungen": _customer_tab_endpoint(customer_id, "chefanweisungen"),
            "anschriften": _customer_tab_endpoint(customer_id, "anschriften"),
            "cpd": _customer_tab_endpoint(customer_id, "cpd"),
            "rabatte": _customer_tab_endpoint(customer_id, "rabatte"),
            "preise": _customer_tab_endpoint(customer_id, "preise"),
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

    kunde = _kunde_finden(db, customer_id, tenant_id)
    if kunde is None:
        return ActionResult(
            actionKey="create_activity",
            mode=mode,
            success=False,
            error="Kunde nicht gefunden.",
        )
    customer_id = str(kunde.get("id") or customer_id)

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
                "kunde": str(kunde.get("name") or "")[:100] or customer_id[:100],
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
