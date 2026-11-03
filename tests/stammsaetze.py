"""Stammsaetze, die Belegwege seit ihrer Stammdatenpruefung verlangen (Kunde, Lieferant im Mandanten).

Ausgangsrechnungen pruefen seit dem Runtime46-Stand den Kunden (``domain_crm.customers``), Eingangsrechnungen
einen aktiven Lieferanten-Geschaeftspartner (``domain_crm.business_partners``, ``is_supplier``). Tests mit
festen Kennungen wie ``kunde-1`` legen sie hier an. Die Kennungen sind systemweit Primaerschluessel; ein Rest
aus einem abgebrochenen Lauf wird in den Mandanten des Tests uebernommen statt den Lauf zu blockieren.
"""

from __future__ import annotations

from sqlalchemy import text


def lege_kunden_an(db, mandant: str, *kennungen: str) -> None:
    for kennung in kennungen:
        db.execute(text(
            "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name, is_active) "
            "VALUES (:id, :t, :nr, :name, true) "
            "ON CONFLICT (id) DO UPDATE SET tenant_id = EXCLUDED.tenant_id, customer_number = EXCLUDED.customer_number, "
            "deleted_at = NULL"),
            {"id": kennung, "t": mandant, "nr": f"{mandant}-{kennung}"[:50], "name": f"Testkunde {kennung}"})


def lege_lieferanten_an(db, mandant: str, *kennungen: str) -> None:
    for kennung in kennungen:
        db.execute(text(
            "INSERT INTO domain_crm.business_partners (partner_id, tenant_id, partner_number, name_1, is_supplier, "
            "status) VALUES (:id, :t, :nr, :name, true, 'active') "
            "ON CONFLICT (partner_id) DO UPDATE SET tenant_id = EXCLUDED.tenant_id, "
            "partner_number = EXCLUDED.partner_number, is_supplier = true, status = 'active'"),
            {"id": kennung, "t": mandant, "nr": f"{mandant}-{kennung}"[:50], "name": f"Testlieferant {kennung}"})


def entferne_stammsaetze(db, mandant: str, *kennungen: str) -> None:
    db.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id = :t AND id = ANY(:ids)"),
               {"t": mandant, "ids": list(kennungen)})
    db.execute(text("DELETE FROM domain_crm.business_partners WHERE tenant_id = :t AND partner_id = ANY(:ids)"),
               {"t": mandant, "ids": list(kennungen)})
