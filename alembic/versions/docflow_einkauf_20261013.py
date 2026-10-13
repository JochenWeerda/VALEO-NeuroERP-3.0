"""DocFlow-Positionen tragen ein Aufwandskonto (Einkaufsbelege).

Revision ID: docflow_einkauf_20261013
Revises: docflow_teilmengen_statushistorie_20261013

DocFlow fuehrt jetzt auch die Einkaufsbelege (Bestellung, Wareneingang, Eingangsrechnung, Einkaufsgutschrift).
Finance bucht den Nettobetrag der Eingangsrechnung auf das Aufwandskonto der Position, sonst auf das des
Steuerschluessels. Die Belegarten selbst brauchen kein Schema: ``doc_type`` ist frei.
"""

from alembic import op

revision = "docflow_einkauf_20261013"
down_revision = "docflow_teilmengen_statushistorie_20261013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items ADD COLUMN IF NOT EXISTS expense_account VARCHAR(20)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS expense_account")
