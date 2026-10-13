"""Steuerschluessel tragen ein Aufwandskonto fuer Eingangsbelege.

Revision ID: steuerschluessel_aufwandskonto_20261013
Revises: artikel_steuerschluessel_20261013

Fuer Verkaufsbelege traegt der Steuerschluessel seit ``steuerschluessel_einheit_20261012`` das Erloeskonto.
Das Gegenstueck fuer Eingangsbelege fehlte: Die Eingangsrechnung buchte den Nettobetrag auf ein Konto „6000“,
wenn die Rechnung keines nannte. Ohne Angabe wird jetzt nicht gebucht; mit ``expense_account`` kommt das
Aufwandskonto aus dem Steuerschluessel der Position (SKR03: Wareneingang 7 % = 3300, 19 % = 3400).
"""

from alembic import op

revision = "steuerschluessel_aufwandskonto_20261013"
down_revision = "artikel_steuerschluessel_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_erp.tax_keys ADD COLUMN IF NOT EXISTS expense_account VARCHAR(20)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_erp.tax_keys DROP COLUMN IF EXISTS expense_account")
