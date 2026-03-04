"""ensure bank_accounts table exists for finance bank modules

Revision ID: c6d7e8f9a0b1
Revises: f5a6b7c8d9e0
Create Date: 2026-03-04 16:20:00
"""

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "c6d7e8f9a0b1"
down_revision = "f5a6b7c8d9e0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    op.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS domain_erp.bank_accounts (
                id VARCHAR(64) PRIMARY KEY,
                tenant_id VARCHAR(64),
                account_number VARCHAR(50) NOT NULL,
                bank_name VARCHAR(255) NOT NULL,
                iban VARCHAR(34),
                bic VARCHAR(11),
                currency VARCHAR(3) DEFAULT 'EUR',
                balance NUMERIC(15,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )

    op.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_bank_accounts_tenant_account
            ON domain_erp.bank_accounts (tenant_id, account_number)
            """
        )
    )
    op.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_bank_accounts_tenant_id
            ON domain_erp.bank_accounts (tenant_id)
            """
        )
    )
    op.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_bank_accounts_is_active
            ON domain_erp.bank_accounts (is_active)
            """
        )
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_erp.bank_accounts")
