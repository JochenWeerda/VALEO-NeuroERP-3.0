"""WMS-Pickposition fuehrt ihren Stand (BELEG-052 Phase 1).

Revision ID: wms_pickposition_stand_20261110
Revises: docflow_auftraege_uebernahme_20261109

``warehouse_service`` legt Pickpositionen mit Stand an (OPEN/PARTIAL/DONE/SKIPPED) und schliesst die Pickliste danach;
``warehouse_wms_structure_20260517`` legte die Spalte nie an. Jede Anlage scheiterte - es gab keine einzige Pickliste,
und damit keinen Lagerabgang aus einem Lieferschein.
"""
from __future__ import annotations

from alembic import op

revision = "wms_pickposition_stand_20261110"
down_revision = "docflow_auftraege_uebernahme_20261109"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_inventory.pick_list_lines "
               "ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'OPEN'")
    op.execute("ALTER TABLE domain_inventory.pick_list_lines DROP CONSTRAINT IF EXISTS ck_pick_list_lines_status")
    op.execute("ALTER TABLE domain_inventory.pick_list_lines ADD CONSTRAINT ck_pick_list_lines_status "
               "CHECK (status IN ('OPEN', 'PARTIAL', 'DONE', 'SKIPPED'))")


def downgrade() -> None:
    op.execute("ALTER TABLE domain_inventory.pick_list_lines DROP CONSTRAINT IF EXISTS ck_pick_list_lines_status")
    op.execute("ALTER TABLE domain_inventory.pick_list_lines DROP COLUMN IF EXISTS status")
