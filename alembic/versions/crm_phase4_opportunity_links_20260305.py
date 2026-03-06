"""CRM Phase 4: Opportunity links to offer/order, loss_reason

Revision ID: crm_phase4_links_20260305
Revises: einkauf_missing_20260305
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa

revision = "crm_phase4_links_20260305"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    try:
        conn.execute(sa.text("""
            ALTER TABLE domain_crm.crm_opportunities
            ADD COLUMN IF NOT EXISTS sales_offer_id VARCHAR(64)
        """))
    except Exception:
        pass
    try:
        conn.execute(sa.text("""
            ALTER TABLE domain_crm.crm_opportunities
            ADD COLUMN IF NOT EXISTS sales_order_id VARCHAR(64)
        """))
    except Exception:
        pass
    try:
        conn.execute(sa.text("""
            ALTER TABLE domain_crm.crm_opportunities
            ADD COLUMN IF NOT EXISTS loss_reason VARCHAR(200)
        """))
    except Exception:
        pass


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE domain_crm.crm_opportunities DROP COLUMN IF EXISTS sales_offer_id"))
    conn.execute(sa.text("ALTER TABLE domain_crm.crm_opportunities DROP COLUMN IF EXISTS sales_order_id"))
    conn.execute(sa.text("ALTER TABLE domain_crm.crm_opportunities DROP COLUMN IF EXISTS loss_reason"))
