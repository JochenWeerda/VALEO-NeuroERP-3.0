"""Steuerschluessel: eine Quelle. Erloeskonto und Paragraf-24-Kennzeichen an ``tax_keys``.

Revision ID: steuerschluessel_einheit_20261012
Revises: gutschrift_ust_20261012

Es gab zwei Tabellen fuer Steuerschluessel. ``domain_erp.tax_keys`` hat die Maske, und aus ihr lesen
Eingangsrechnung, Umsatzsteuer-Voranmeldung und DATEV-Ausgabe. ``vat_codes`` benutzte sonst niemand —
die Revision ``gutschrift_ust_20261012`` hatte die Gutschrift trotzdem daran gehaengt und ihr dafuer
eine Spalte ``skr03_revenue_account`` gegeben. Das wird hier zurueckgenommen.

- ``tax_keys.revenue_account``: Erloeskonto, gegen das ein Verkaufsbeleg netto bucht. Leer heisst:
  nicht eingeordnet, mit diesem Schluessel wird nicht automatisch gebucht.
- ``tax_keys.par_24_ustg``: Durchschnittssatz nach Paragraf 24 UStG.
- ``vat_codes.skr03_revenue_account`` entfaellt (am selben Tag angelegt, von niemandem gepflegt).

``vat_codes`` selbst bleibt stehen; ob die Tabelle entfaellt, ist eine eigene Entscheidung.
"""

from alembic import op

revision = "steuerschluessel_einheit_20261012"
down_revision = "gutschrift_ust_20261012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_erp.tax_keys ADD COLUMN IF NOT EXISTS revenue_account VARCHAR(20)")
    op.execute("ALTER TABLE domain_erp.tax_keys ADD COLUMN IF NOT EXISTS par_24_ustg BOOLEAN NOT NULL DEFAULT false")
    op.execute("ALTER TABLE vat_codes DROP COLUMN IF EXISTS skr03_revenue_account")


def downgrade() -> None:
    op.execute("ALTER TABLE vat_codes ADD COLUMN IF NOT EXISTS skr03_revenue_account VARCHAR(10)")
    op.execute("UPDATE vat_codes SET skr03_revenue_account = '8400' WHERE id = 'DE_19' AND skr03_revenue_account IS NULL")
    op.execute("UPDATE vat_codes SET skr03_revenue_account = '8300' WHERE id = 'DE_7' AND skr03_revenue_account IS NULL")
    op.execute("ALTER TABLE domain_erp.tax_keys DROP COLUMN IF EXISTS par_24_ustg")
    op.execute("ALTER TABLE domain_erp.tax_keys DROP COLUMN IF EXISTS revenue_account")
