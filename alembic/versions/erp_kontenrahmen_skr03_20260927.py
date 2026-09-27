"""Der Kontenrahmen bekommt die Konten, gegen die gebucht wird.

``domain_erp.chart_of_accounts`` hatte drei Eintraege. Gebucht wird aber gegen
mehr als zwanzig Konten, und jede Buchung gegen ein fehlendes Konto scheitert:
Die Bestellfreigabe blieb an "Active chart-of-accounts entry not found: 6000"
haengen, und dasselbe trifft Wareneingang, Kasse, Fracht und Lohn.

Woher die Namen kommen
----------------------

Nicht aus einer Standardtabelle, sondern aus diesem Haus. Die Zuordnung steht
an drei Stellen im Code und wird hier nur eingesammelt:

- ``app/services/pos_accounting_service.ACCOUNT_DEFINITIONS`` — die einzige
  bereits strukturierte Kontentabelle (Name, Typ, Kategorie).
- ``app/finance/router.py`` — das SKR03-Regelwerk fuer Agrar und Handel.
- Die Buchungsdienste selbst, wo der Zweck als Kommentar am Konto steht.

Was dabei auffiel und **nicht** stillschweigend entschieden wird
----------------------------------------------------------------

Drei Konten werden im Code widerspruechlich benutzt. Die Saat folgt der
SKR03-Bedeutung; wo der Code etwas anderes meint, ist das ein Fall fuer die
Buchhaltung, nicht fuer eine Migration:

- **1200** ist in SKR03 die Bank. ``pos_accounting_service`` sieht das auch so
  ("Bank / EC"), ``sales_posting_service`` bucht dagegen Forderungen darauf
  (``ACCOUNT_RECEIVABLES``). Forderungen sind 1400.
- **1600** ist in SKR03 Verbindlichkeiten aus Lieferungen und Leistungen. Der
  Kassendienst nennt es "Gutscheinverbindlichkeiten" — eine Verengung, die auf
  einem eigenen Konto besser aufgehoben waere.
- **6000** ist in SKR03 Loehne und Gehaelter. ``lohn_service`` bucht
  folgerichtig den Bruttolohn dorthin, ``procurement_service`` benutzt es als
  allgemeines Aufwandskonto fuer den Wareneingang. Fuer Handelsware waere 3200
  richtig.

Die Konten liegen unter ``tenant_id = 'system'``, wie die bereits vorhandenen
1400 und 8400. Der Buchungsdienst sucht ohnehin ohne Mandantenfilter (siehe
``FinanceTransactionService._resolve_account_id``) — auch das ist vermerkt,
aber nicht hier geaendert.

Revision ID: erp_kontenrahmen_skr03_20260927
Revises: einkauf_po_dokumente_migrieren_20260925
Create Date: 2026-09-27
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from alembic import op

revision = "erp_kontenrahmen_skr03_20260927"
down_revision = "einkauf_po_dokumente_migrieren_20260925"
branch_labels = None
depends_on = None

MANDANT = "system"

#: (Nummer, Name, Typ, Kategorie, Herkunft der Benennung)
KONTEN: list[tuple[str, str, str, str, str]] = [
    # ── Finanzkonten ────────────────────────────────────────────────────
    ("1000", "Kasse", "asset", "current_assets", "pos_accounting_service"),
    ("1200", "Bank / EC", "asset", "current_assets", "pos_accounting_service"),
    ("1210", "PayPal / Verrechnung", "asset", "current_assets", "pos_accounting_service"),
    ("1400", "Forderungen aus Lieferungen und Leistungen", "asset", "current_assets",
     "pos_accounting_service"),
    ("1500", "Waren (Bestandskonto)", "asset", "current_assets", "inventory_operations"),
    ("1576", "Abziehbare Vorsteuer 19 %", "asset", "current_assets", "SKR03"),
    ("1600", "Verbindlichkeiten aus Lieferungen und Leistungen", "liability",
     "current_liabilities", "finance/router"),
    ("1776", "Umsatzsteuer 19 %", "liability", "current_liabilities", "sales_posting_service"),
    ("1796", "Umsatzsteuer-Vorauszahlungen", "liability", "current_liabilities",
     "finance/router"),
    ("1800", "Privatentnahmen / Barauszahlungen", "equity", "equity", "pos_accounting_service"),
    # ── Bestand und Ware ────────────────────────────────────────────────
    ("2000", "Warenbestand", "asset", "current_assets", "sales_posting_service"),
    ("2150", "Kassendifferenzen", "expense", "operating_expenses", "pos_accounting_service"),
    ("3100", "Rohwarenlager", "asset", "current_assets", "produktion_mischfutter"),
    ("3200", "Fertigwarenlager / Wareneingang", "asset", "current_assets",
     "produktion_mischfutter"),
    ("3300", "Kreditorenkonto (Sammelkonto)", "liability", "current_liabilities",
     "ap_invoice_kernel_posting"),
    ("3800", "Wareneinsatz", "expense", "cost_of_sales", "inventory_operations"),
    # ── Erloese ─────────────────────────────────────────────────────────
    ("4200", "Erloese Landwirtschaft", "revenue", "revenue", "agrar_settlements"),
    ("4400", "Erloese (Sammelkonto)", "revenue", "revenue", "finance/router"),
    ("4820", "Frachtkosten", "expense", "operating_expenses", "logistics_freight"),
    ("8100", "Erloese", "revenue", "revenue", "finance/router"),
    ("8400", "Umsatzerloese 19 % USt", "revenue", "revenue", "pos_accounting_service"),
    # ── Aufwand ─────────────────────────────────────────────────────────
    ("5100", "Einkauf Handelswaren", "expense", "cost_of_sales", "finance/router"),
    ("5200", "Erhaltene Skonti", "expense", "cost_of_sales", "finance/router"),
    ("5800", "Bestandsveraenderungen", "expense", "cost_of_sales", "inventory_operations"),
    ("5810", "Lagerschwund", "expense", "operating_expenses", "inventory_operations"),
    ("6000", "Loehne und Gehaelter", "expense", "operating_expenses", "lohn_service"),
    ("6800", "Herstellungskosten", "expense", "operating_expenses", "produktion_mischfutter"),
    ("7000", "Wareneinsatz (Kostenrechnung)", "expense", "cost_of_sales",
     "sales_posting_service"),
]


def upgrade() -> None:
    verbindung = op.get_bind()

    for nummer, name, typ, kategorie, herkunft in KONTEN:
        # Nur anlegen, was fehlt — vorhandene Konten bleiben unberuehrt,
        # auch wenn sie anders heissen. Ein Name, den jemand gepflegt hat,
        # gehoert nicht von einer Migration ueberschrieben.
        schon_da = verbindung.execute(
            sa.text(
                "SELECT 1 FROM domain_erp.chart_of_accounts "
                "WHERE account_number = :nr AND is_active = TRUE"
            ),
            {"nr": nummer},
        ).first()
        if schon_da:
            continue

        verbindung.execute(
            sa.text(
                "INSERT INTO domain_erp.chart_of_accounts "
                "(id, tenant_id, account_number, account_name, account_type, "
                " category, is_active, description) "
                "VALUES (:id, :t, :nr, :name, :typ, :kat, TRUE, :beschreibung)"
            ),
            {
                "id": str(uuid.uuid4()),
                "t": MANDANT,
                "nr": nummer,
                "name": name,
                "typ": typ,
                "kat": kategorie,
                "beschreibung": (
                    f"Startbestand SKR03, Benennung aus {herkunft}. "
                    f"Von der Buchhaltung zu bestaetigen."
                ),
            },
        )


def downgrade() -> None:
    """Nur die eigenen Eintraege wieder entfernen.

    Erkennbar am Vermerk in der Beschreibung — Konten, die jemand anders
    angelegt oder umbenannt hat, bleiben stehen.
    """
    op.get_bind().execute(
        sa.text(
            "DELETE FROM domain_erp.chart_of_accounts "
            "WHERE tenant_id = :t AND description LIKE 'Startbestand SKR03%'"
        ),
        {"t": MANDANT},
    )
