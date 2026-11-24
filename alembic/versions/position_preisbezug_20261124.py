"""Belegposition mit Preisbezugsmenge - Preis je 100 Liter, ohne die Menge umzurechnen (24.11.2026).

Revision ID: position_preisbezug_20261124
Revises: mahnstufen_verlauf_entfernen_20261123

Bisher galt der Positionspreis immer je Mengeneinheit; "Preis je 100 kg" wurde durch Umrechnen der Menge in die
Preiseinheit abgebildet (``beleg_anlage.position_in_preiseinheit``: Menge in dt). Fuer Liter mit Preis je 100 Liter
haette die Position dann Hektoliter gefuehrt. ``price_unit_quantity`` traegt die Preisbezugsmenge; die Menge bleibt in
ihrer Einheit (Golden Master Diesel 220050, Nutzer 24.11.2026).

Bestehende Positionen bekommen 1 - genau ihre bisherige Bedeutung (Preis je Mengeneinheit), kein erfundener Wert.
"""
from __future__ import annotations

from alembic import op

revision = "position_preisbezug_20261124"
down_revision = "mahnstufen_verlauf_entfernen_20261123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items "
               "ADD COLUMN IF NOT EXISTS price_unit_quantity numeric(14,4) NOT NULL DEFAULT 1")
    op.execute("ALTER TABLE domain_docflow.document_items ADD CONSTRAINT ck_document_items_preisbezug "
               "CHECK (price_unit_quantity > 0)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items DROP CONSTRAINT IF EXISTS ck_document_items_preisbezug")
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS price_unit_quantity")
