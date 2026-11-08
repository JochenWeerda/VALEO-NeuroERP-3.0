"""DocFlow-Positionen tragen ihren Steuerschluessel.

Revision ID: docflow_steuerschluessel_20261013
Revises: steuerschluessel_aufwandskonto_20261013

DocFlow fuehrt die Verkaufsbelege (Auftrag, Lieferschein, Rechnung). Die Position trug nur ``tax_rate`` mit der
Vorgabe 0; gebucht wurde die Rechnung mit den Kopfsummen fest auf 8400 und 1776. Mit ``tax_code`` nennt die
Position ihren Steuerschluessel (``domain_erp.tax_keys``); ``tax_rate`` ist dann sein Abbild.
"""

from alembic import op

revision = "docflow_steuerschluessel_20261013"
down_revision = "steuerschluessel_aufwandskonto_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items ADD COLUMN IF NOT EXISTS tax_code VARCHAR(2)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS tax_code")
