"""Repair runtime columns required by current ORM and domain checks.

Revision ID: repair_runtime_cols_20260610
Revises: repair_article_dg_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_runtime_cols_20260610"
down_revision = "repair_article_dg_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_crm.business_partners
              ADD COLUMN IF NOT EXISTS legal_form VARCHAR(80),
              ADD COLUMN IF NOT EXISTS blocked_for_delivery BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS blocked_for_invoice BOOLEAN NOT NULL DEFAULT FALSE;

            ALTER TABLE domain_hr.time_entries
              ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;
            """
        )
    )


def downgrade() -> None:
    # Runtime master data and optimistic-lock versions must survive rollback.
    pass
