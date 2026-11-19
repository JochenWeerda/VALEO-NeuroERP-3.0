"""Die alten Belegspeicher entfallen - DocFlow ist der einzige Belegspeicher (BELEG-052 S5).

Revision ID: beleg_altspeicher_entfernen_20261117
Revises: journal_periode_nachfuellen_20261119

Seit den Schnitten S1-S4 schreibt und liest niemand mehr die alten Speicher fuer Lieferschein, Rechnung, Gutschrift,
Bestellung und Auftrag (Ratschen tests/test_altspeicher_schreiber_ratsche.py, tests/test_sicht_auftraege_ratsche.py).
Entfernt werden die Tabellen und die Uebergangssichten des Auftrags. Ihr Inhalt sind nach Nutzerentscheidung vom
10.11.2026 Testdaten; er wird nicht uebernommen.

Haelt an, wenn ein bestehender Mandant noch *gebuchte* Rechnungen oder Gutschriften im alten Speicher hat - die
gehoeren GoBD-gerecht nach DocFlow, nicht stillschweigend weg.

Der Rueckweg legt die Speicher leer wieder an (Schluessel, Indizes, RLS, Schreibschutz und Sichten aus
``beleg_altspeicher_entfernen_20261117.sql``, per pg_dump aus einer frisch migrierten Datenbank).
"""
from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "beleg_altspeicher_entfernen_20261117"
down_revision = "journal_periode_nachfuellen_20261119"
branch_labels = None
depends_on = None

# Reihenfolge: Positionen vor Koepfen (Fremdschluessel), Sichten zuerst.
SICHTEN = ("domain_crm.sales_order_items", "domain_crm.sales_orders")
TABELLEN = (
    "domain_sales.delivery_note_positions", "domain_sales.delivery_notes", "domain_sales.sales_delivery_notes",
    "domain_sales.sales_invoice_lines", "domain_sales.sales_invoices",
    "domain_sales.sales_credit_note_lines", "domain_sales.sales_credit_notes",
    "domain_einkauf.bestellung_positionen", "domain_einkauf.bestellungen",
    "domain_crm.sales_order_items_vor_docflow", "domain_crm.sales_orders_vor_docflow",
)
GEBUCHT = {
    "domain_sales.sales_invoices": "invoice_number",
    "domain_sales.sales_credit_notes": "credit_note_number",
}


def _vorhanden(bind, name: str) -> bool:
    return bool(bind.exec_driver_sql(f"SELECT to_regclass('{name}') IS NOT NULL").scalar())  # nosec B608


def upgrade() -> None:
    bind = op.get_bind()
    funde: list[str] = []
    for tabelle, nummer in GEBUCHT.items():
        if _vorhanden(bind, tabelle):
            funde += [f"{tabelle} {z[0]}" for z in bind.exec_driver_sql(  # nosec B608 - Namen aus GEBUCHT
                f"SELECT a.{nummer} FROM {tabelle} a JOIN domain_shared.tenants t ON t.id = a.tenant_id::text "
                f"WHERE a.status = 'posted' LIMIT 20").all()]
    if funde:
        raise RuntimeError("Gebuchte Altbelege bestehender Mandanten - erst nach DocFlow uebernehmen: "
                           + ", ".join(funde))
    for sicht in SICHTEN:
        op.execute(f"DROP VIEW IF EXISTS {sicht}")
    for tabelle in TABELLEN:
        op.execute(f"DROP TABLE IF EXISTS {tabelle}")


def downgrade() -> None:
    bind = op.get_bind()
    if all(_vorhanden(bind, t) for t in TABELLEN):
        return
    sql = (Path(__file__).with_suffix(".sql")).read_text(encoding="utf-8")
    bind.exec_driver_sql(sql)
