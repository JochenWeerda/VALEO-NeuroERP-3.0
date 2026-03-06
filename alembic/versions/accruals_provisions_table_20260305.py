"""Accruals and Provisions table (FIBU-CLS-03)

Revision ID: accruals_provisions_20260305
Revises: crm_phase4_links_20260305
Create Date: 2026-03-05
"""

from alembic import op
import sqlalchemy as sa

revision = "accruals_provisions_20260305"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_erp"))
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS domain_erp.accruals_provisions (
            id                  VARCHAR(36) PRIMARY KEY,
            tenant_id           VARCHAR(64) NOT NULL DEFAULT 'system',
            description         VARCHAR(500) NOT NULL,
            amount              NUMERIC(18,4) NOT NULL,
            account_number      VARCHAR(20) NOT NULL,
            counterpart_account VARCHAR(20) NOT NULL,
            period              VARCHAR(7) NOT NULL,
            accrual_type        VARCHAR(50) NOT NULL,
            status              VARCHAR(20) NOT NULL DEFAULT 'draft',
            created_at          TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ap_tenant ON domain_erp.accruals_provisions(tenant_id)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS idx_ap_period ON domain_erp.accruals_provisions(period)"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS domain_erp.accruals_provisions"))
