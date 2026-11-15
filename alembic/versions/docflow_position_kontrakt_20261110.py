"""DocFlow-Position fuehrt ihren Kontraktbezug (BELEG-052 Phase 1).

Revision ID: docflow_position_kontrakt_20261110
Revises: wms_pickposition_stand_20261110

Der alte Lieferschein buchte je Position mit Kontraktnummer einen Abruf auf ``domain_ops.kon_contract``; die
DocFlow-Position kannte keinen Kontrakt, die Belegmaske buchte deshalb keine Abrufe. Eine Spalte wie Charge und
Batch: gepflegt in der Maske, geprueft gegen die Kontrakte des Mandanten, beim Umwandeln mitgenommen.
"""
from __future__ import annotations

from alembic import op

revision = "docflow_position_kontrakt_20261110"
down_revision = "wms_pickposition_stand_20261110"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items ADD COLUMN IF NOT EXISTS contract_ref VARCHAR(50)")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_docflow.document_items DROP COLUMN IF EXISTS contract_ref")
