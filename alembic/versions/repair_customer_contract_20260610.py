"""Complete the canonical CRM customer runtime contract.

Revision ID: repair_customer_contract_20260610
Revises: repair_bp_contract_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_customer_contract_20260610"
down_revision = "repair_bp_contract_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_crm.customers
              ADD COLUMN IF NOT EXISTS city VARCHAR(50),
              ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10),
              ADD COLUMN IF NOT EXISTS country VARCHAR(50),
              ADD COLUMN IF NOT EXISTS industry VARCHAR(50),
              ADD COLUMN IF NOT EXISTS website VARCHAR(100),
              ADD COLUMN IF NOT EXISTS tax_id VARCHAR(50),
              ADD COLUMN IF NOT EXISTS chefanweisung TEXT,
              ADD COLUMN IF NOT EXISTS business_partner_id VARCHAR(36),
              ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
            """
        )
    )


def downgrade() -> None:
    # Customer master data must survive application rollback.
    pass
