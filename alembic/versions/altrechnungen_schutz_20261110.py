"""Schutz vor dem Entfernen des alten Rechnungswegs: keine echten Altrechnungen ausserhalb DocFlow (BELEG-052 2b).

Revision ID: altrechnungen_schutz_20261110
Revises: docflow_archiv_wartung_20261110

Der alte Rechnungsweg (``finance_invoices`` im Dokumentenspeicher ``public.documents``, ``sales_invoices`` in
``domain_sales.sales_invoices``) wird entfernt; DocFlow ist der einzige Belegspeicher. Im gewachsenen Bestand lagen
nur Testreste (Mandanten, die es nicht mehr gibt). Stehen bei einem *bestehenden* Mandanten noch Rechnungen im alten
Speicher, haelt diese Migration an: Sie muessen zuerst nach DocFlow uebernommen werden (gebuchte bitgleich, GoBD) -
nicht stillschweigend unerreichbar werden. Aendert nichts.
"""
from __future__ import annotations

from alembic import op

revision = "altrechnungen_schutz_20261110"
down_revision = "docflow_archiv_wartung_20261110"
branch_labels = None
depends_on = None


def _vorhanden(bind, tabelle: str) -> bool:
    return bool(bind.exec_driver_sql(f"SELECT to_regclass('{tabelle}') IS NOT NULL").scalar())


def upgrade() -> None:
    bind = op.get_bind()
    funde: list[str] = []
    if _vorhanden(bind, "public.documents"):
        funde += [f"public.documents {z[0]}" for z in bind.exec_driver_sql("""
            SELECT d.doc_number FROM public.documents d
            JOIN domain_shared.tenants t ON t.id = d.data->>'tenantId'
            WHERE d.doc_type IN ('sales_invoice', 'salesInvoice') LIMIT 20
        """).all()]
    if _vorhanden(bind, "domain_sales.sales_invoices"):
        funde += [f"domain_sales.sales_invoices {z[0]}" for z in bind.exec_driver_sql("""
            SELECT s.invoice_number FROM domain_sales.sales_invoices s
            JOIN domain_shared.tenants t ON t.id = s.tenant_id::text LIMIT 20
        """).all()]
    if funde:
        raise RuntimeError("Altrechnungen bestehender Mandanten ausserhalb DocFlow - erst uebernehmen: "
                           + ", ".join(funde))


def downgrade() -> None:
    """Nichts zurueckzunehmen: die Migration prueft nur."""
