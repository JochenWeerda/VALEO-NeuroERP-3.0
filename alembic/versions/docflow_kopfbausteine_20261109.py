"""DocFlow fuehrt die Kopfbausteine des Belegvertrags (BELEG-052).

Revision ID: docflow_kopfbausteine_20261109
Revises: agent_autonomie_20261109

Lieferung, Zahlung, Texte, Kontakt und Referenzen standen bisher nur in den Eigenspeichern (z. B.
``domain_crm.sales_orders.delivery_date/payment_terms``); DocFlow als einziger Belegspeicher kannte sie nicht. Eine
Spalte je Kopf, geprueft je Belegart gegen ``app/core/belegvertrag.py`` (KOPFBAUSTEINE, BAUSTEIN_FELDER).
"""
from __future__ import annotations

from alembic import op

revision = "docflow_kopfbausteine_20261109"
down_revision = "agent_autonomie_20261109"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_headers ADD COLUMN IF NOT EXISTS bausteine JSONB "
               "NOT NULL DEFAULT '{}'::jsonb")
    op.execute("ALTER TABLE domain_docflow.document_headers DROP CONSTRAINT IF EXISTS ck_docflow_bausteine_objekt")
    op.execute("ALTER TABLE domain_docflow.document_headers ADD CONSTRAINT ck_docflow_bausteine_objekt "
               "CHECK (jsonb_typeof(bausteine) = 'object')")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_headers DROP CONSTRAINT IF EXISTS ck_docflow_bausteine_objekt")
    op.execute("ALTER TABLE domain_docflow.document_headers DROP COLUMN IF EXISTS bausteine")
