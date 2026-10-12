"""Gutschrift: Umsatzsteuer je Position, Netto/Steuer/Brutto getrennt, Erloeskonto je Steuerschluessel.

Revision ID: gutschrift_ust_20261012
Revises: konto_sperre_20261012

Bis zum 12.10.2026 buchte die Gutschrift ihren Gesamtbetrag gegen das Erloeskonto 8400; eine
Berichtigung der Umsatzsteuer gab es nicht. Die Position trug einen Steuersatz mit Vorgabe 19 — eine
stillschweigende Annahme.

- ``sales_credit_note_lines.tax_code``: Steuerschluessel der Position (``vat_codes.id``).
  ``tax_rate`` verliert Vorgabe und Pflicht: Ein Satz, den niemand angegeben hat, steht nicht mehr da.
  Bestehende Zeilen behalten ihren Wert.
- ``sales_credit_notes.net_amount`` / ``tax_amount``: getrennt gefuehrt; ``total_amount`` ist brutto.
- ``sales_credit_notes.correction_type``: kaufmaennische Rechnungskorrektur oder Gutschrift nach
  Paragraf 14 UStG (Abrechnung durch den Leistungsempfaenger). Nur die erste ist eine Erloesminderung.
- ``vat_codes.skr03_revenue_account``: das Erloeskonto, gegen das netto korrigiert wird. Vorbelegt nur
  fuer die beiden Regelfaelle (19 % -> 8400, 7 % -> 8300). Alle anderen Schluessel bleiben leer, bis
  jemand sie einordnet; ohne Erloeskonto wird nicht automatisch gebucht.

Nichts wird ueberschrieben: nur neue Spalten, und die Vorbelegung fasst nur leere Felder an.
"""

from alembic import op

revision = "gutschrift_ust_20261012"
down_revision = "konto_sperre_20261012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines ADD COLUMN IF NOT EXISTS tax_code VARCHAR(50)")
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines ALTER COLUMN tax_rate DROP DEFAULT")
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines ALTER COLUMN tax_rate DROP NOT NULL")

    op.execute("ALTER TABLE domain_sales.sales_credit_notes ADD COLUMN IF NOT EXISTS net_amount NUMERIC(15, 2)")
    op.execute("ALTER TABLE domain_sales.sales_credit_notes ADD COLUMN IF NOT EXISTS tax_amount NUMERIC(15, 2)")
    op.execute(
        "ALTER TABLE domain_sales.sales_credit_notes "
        "ADD COLUMN IF NOT EXISTS correction_type VARCHAR(30) NOT NULL DEFAULT 'rechnungskorrektur'"
    )
    op.execute(
        "ALTER TABLE domain_sales.sales_credit_notes DROP CONSTRAINT IF EXISTS ck_sales_credit_notes_correction_type"
    )
    op.execute(
        "ALTER TABLE domain_sales.sales_credit_notes ADD CONSTRAINT ck_sales_credit_notes_correction_type "
        "CHECK (correction_type IN ('rechnungskorrektur', 'gutschrift_14_ustg'))"
    )

    op.execute("ALTER TABLE vat_codes ADD COLUMN IF NOT EXISTS skr03_revenue_account VARCHAR(10)")
    op.execute("UPDATE vat_codes SET skr03_revenue_account = '8400' WHERE id = 'DE_19' AND skr03_revenue_account IS NULL")
    op.execute("UPDATE vat_codes SET skr03_revenue_account = '8300' WHERE id = 'DE_7' AND skr03_revenue_account IS NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE vat_codes DROP COLUMN IF EXISTS skr03_revenue_account")
    op.execute(
        "ALTER TABLE domain_sales.sales_credit_notes DROP CONSTRAINT IF EXISTS ck_sales_credit_notes_correction_type"
    )
    op.execute("ALTER TABLE domain_sales.sales_credit_notes DROP COLUMN IF EXISTS correction_type")
    op.execute("ALTER TABLE domain_sales.sales_credit_notes DROP COLUMN IF EXISTS tax_amount")
    op.execute("ALTER TABLE domain_sales.sales_credit_notes DROP COLUMN IF EXISTS net_amount")
    # Zeilen ohne Satz gab es vor dieser Revision nicht; der alte Zustand verlangt einen Wert.
    op.execute("UPDATE domain_sales.sales_credit_note_lines SET tax_rate = 0 WHERE tax_rate IS NULL")
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines ALTER COLUMN tax_rate SET DEFAULT 19")
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines ALTER COLUMN tax_rate SET NOT NULL")
    op.execute("ALTER TABLE domain_sales.sales_credit_note_lines DROP COLUMN IF EXISTS tax_code")
