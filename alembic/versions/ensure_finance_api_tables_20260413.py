"""Ensure finance API tables exist on all upgrade paths

Revision ID: ensure_finance_api_tables_20260413
Revises: exchange_rates_compat_20260413
Create Date: 2026-04-13
"""

from alembic import op


revision = "ensure_finance_api_tables_20260413"
down_revision = "exchange_rates_compat_20260413"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_rules (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            level INTEGER NOT NULL,
            days_overdue_min INTEGER NOT NULL DEFAULT 0,
            days_overdue_max INTEGER,
            fee_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            fee_percentage NUMERIC(7,4) NOT NULL DEFAULT 0,
            interest_rate NUMERIC(7,4) NOT NULL DEFAULT 0,
            payment_deadline_days INTEGER NOT NULL DEFAULT 14,
            block_customer BOOLEAN NOT NULL DEFAULT FALSE,
            escalate_to_collection BOOLEAN NOT NULL DEFAULT FALSE,
            description_template TEXT,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.dunning_notices (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            op_id VARCHAR(64),
            debtor_id VARCHAR(64),
            dunning_level INTEGER NOT NULL DEFAULT 1,
            dunning_date DATE NOT NULL,
            due_date DATE,
            open_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            dunning_fee NUMERIC(15,2) NOT NULL DEFAULT 0,
            interest NUMERIC(15,2) NOT NULL DEFAULT 0,
            total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            payment_deadline DATE,
            status VARCHAR(32) NOT NULL DEFAULT 'created',
            sent_date DATE,
            payment_date DATE,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_runs (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            run_number VARCHAR(50) NOT NULL,
            execution_date DATE NOT NULL,
            initiator_name VARCHAR(255) NOT NULL,
            initiator_iban VARCHAR(34) NOT NULL,
            initiator_bic VARCHAR(11),
            total_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            payment_count INTEGER NOT NULL DEFAULT 0,
            status VARCHAR(32) NOT NULL DEFAULT 'draft',
            approved_at TIMESTAMPTZ,
            approved_by VARCHAR(128),
            executed_at TIMESTAMPTZ,
            sepa_file_id VARCHAR(128),
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_run_items (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            payment_run_id VARCHAR(64) NOT NULL,
            creditor_id VARCHAR(64),
            creditor_name VARCHAR(255),
            iban VARCHAR(34),
            bic VARCHAR(11),
            amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            purpose TEXT,
            op_id VARCHAR(64),
            invoice_number VARCHAR(100),
            discount_used BOOLEAN NOT NULL DEFAULT FALSE,
            discount_amount NUMERIC(15,2) NOT NULL DEFAULT 0,
            end_to_end_id VARCHAR(64),
            status VARCHAR(32) NOT NULL DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.payment_returns (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            payment_run_id VARCHAR(64) NOT NULL,
            payment_item_id VARCHAR(64) NOT NULL,
            return_reason VARCHAR(100),
            return_date DATE,
            notes TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_erp.exchange_rates (
            id VARCHAR(64) PRIMARY KEY,
            tenant_id VARCHAR(64) NOT NULL,
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate NUMERIC(18,8) NOT NULL,
            valid_from DATE,
            valid_to DATE,
            rate_date DATE NOT NULL DEFAULT CURRENT_DATE,
            rate_type VARCHAR(32) NOT NULL DEFAULT 'SPOT',
            source VARCHAR(64),
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )

    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_payment_runs_tenant_run_number
        ON domain_erp.payment_runs (tenant_id, run_number)
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_exchange_rates_tenant_pair_date_type
        ON domain_erp.exchange_rates (tenant_id, from_currency, to_currency, rate_date, rate_type)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_erp.uq_exchange_rates_tenant_pair_date_type")
    op.execute("DROP INDEX IF EXISTS domain_erp.uq_payment_runs_tenant_run_number")
    op.execute("DROP TABLE IF EXISTS domain_erp.exchange_rates")
    op.execute("DROP TABLE IF EXISTS domain_erp.payment_returns")
    op.execute("DROP TABLE IF EXISTS domain_erp.payment_run_items")
    op.execute("DROP TABLE IF EXISTS domain_erp.payment_runs")
    op.execute("DROP TABLE IF EXISTS domain_erp.dunning_notices")
    op.execute("DROP TABLE IF EXISTS domain_erp.dunning_rules")
