"""Align exchange rate table with API contract

Revision ID: exchange_rates_compat_20260413
Revises: config_openitems_20260412
Create Date: 2026-04-13
"""

from alembic import op
from sqlalchemy import text


revision = "exchange_rates_compat_20260413"
down_revision = "config_openitems_20260412"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates'
              ) THEN
                IF NOT EXISTS (
                  SELECT 1
                  FROM information_schema.columns
                  WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates' AND column_name = 'rate_date'
                ) THEN
                  ALTER TABLE domain_erp.exchange_rates ADD COLUMN rate_date DATE;
                END IF;

                IF NOT EXISTS (
                  SELECT 1
                  FROM information_schema.columns
                  WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates' AND column_name = 'rate_type'
                ) THEN
                  ALTER TABLE domain_erp.exchange_rates ADD COLUMN rate_type VARCHAR(32);
                END IF;
              END IF;
            END
            $$;
            """
        )
    )

    op.execute(
        text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates'
              ) THEN
                UPDATE domain_erp.exchange_rates
                SET rate_date = COALESCE(rate_date, valid_from),
                    rate_type = COALESCE(NULLIF(rate_type, ''), 'SPOT')
                WHERE rate_date IS NULL OR rate_type IS NULL OR rate_type = '';

                ALTER TABLE domain_erp.exchange_rates
                  ALTER COLUMN rate_date SET NOT NULL,
                  ALTER COLUMN rate_type SET NOT NULL,
                  ALTER COLUMN rate_type SET DEFAULT 'SPOT';

                CREATE UNIQUE INDEX IF NOT EXISTS uq_exchange_rates_tenant_pair_date_type
                ON domain_erp.exchange_rates (tenant_id, from_currency, to_currency, rate_date, rate_type);
              END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        text(
            """
            DROP INDEX IF EXISTS domain_erp.uq_exchange_rates_tenant_pair_date_type;
            """
        )
    )

    op.execute(
        text(
            """
            DO $$
            BEGIN
              IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates' AND column_name = 'rate_type'
              ) THEN
                ALTER TABLE domain_erp.exchange_rates DROP COLUMN rate_type;
              END IF;

              IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'domain_erp' AND table_name = 'exchange_rates' AND column_name = 'rate_date'
              ) THEN
                ALTER TABLE domain_erp.exchange_rates DROP COLUMN rate_date;
              END IF;
            END
            $$;
            """
        )
    )
