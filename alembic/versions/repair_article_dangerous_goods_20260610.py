"""Repair dangerous-goods columns required by the Article runtime model.

Revision ID: repair_article_dg_20260610
Revises: repair_runtime_schema_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_article_dg_20260610"
down_revision = "repair_runtime_schema_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_inventory.articles
              ADD COLUMN IF NOT EXISTS gefahrgut_un_nummer VARCHAR(20),
              ADD COLUMN IF NOT EXISTS gefahrgut_verpackungsgruppe VARCHAR(5),
              ADD COLUMN IF NOT EXISTS gefahrgut_anhaenge VARCHAR(200);

            ALTER TABLE domain_inventory.warehouses
              ADD COLUMN IF NOT EXISTS city VARCHAR(50),
              ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10),
              ADD COLUMN IF NOT EXISTS country VARCHAR(2) DEFAULT 'DE',
              ADD COLUMN IF NOT EXISTS contact_person VARCHAR(100),
              ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
              ADD COLUMN IF NOT EXISTS email VARCHAR(100),
              ADD COLUMN IF NOT EXISTS warehouse_type VARCHAR(20) DEFAULT 'standard',
              ADD COLUMN IF NOT EXISTS total_capacity NUMERIC(12,2),
              ADD COLUMN IF NOT EXISTS used_capacity NUMERIC(12,2) DEFAULT 0,
              ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

            ALTER TABLE domain_crm.business_partners
              ADD COLUMN IF NOT EXISTS matchcode VARCHAR(120);
            """
        )
    )


def downgrade() -> None:
    # These columns may already contain regulated master data. A production
    # rollback must not destroy them.
    pass
