"""RFQ tables for procurement quotation process.

Revision ID: proc_rfq_20260611
Revises: proc_ers_credit_20260611
"""

from alembic import op


revision = "proc_rfq_20260611"
down_revision = "proc_ers_credit_20260611"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_requests (
            id              BIGSERIAL PRIMARY KEY,
            article_id      TEXT NOT NULL,
            quantity        NUMERIC(18, 4) NOT NULL,
            needed_by_date  DATE,
            notes           TEXT,
            status          TEXT NOT NULL DEFAULT 'OFFEN',
            tenant_id       VARCHAR(36) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_quotes (
            id            BIGSERIAL PRIMARY KEY,
            rfq_id        BIGINT NOT NULL REFERENCES domain_einkauf.rfq_requests(id) ON DELETE CASCADE,
            supplier_id   TEXT NOT NULL,
            unit_price    NUMERIC(18, 4) NOT NULL,
            delivery_days INT,
            notes         TEXT,
            status        TEXT NOT NULL DEFAULT 'OFFEN',
            received_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            tenant_id     VARCHAR(36) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS rfq_requests_tenant_idx
            ON domain_einkauf.rfq_requests (tenant_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS rfq_quotes_rfq_tenant_idx
            ON domain_einkauf.rfq_quotes (rfq_id, tenant_id, unit_price);
        """
    )


def downgrade() -> None:
    pass
