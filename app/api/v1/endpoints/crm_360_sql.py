"""CRM-360: sichere Leseabfragen und die Kundensuche."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

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
