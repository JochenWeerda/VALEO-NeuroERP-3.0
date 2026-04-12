"""Create connectors, reporting_units, schedules, and open_items tables in domain_shared

Revision ID: config_openitems_20260412
Revises: e7238c2e17a1
Create Date: 2026-04-12

These tables are used by config_service.py and liquidity.py via raw SQL
but were never created in a migration.
"""

from alembic import op
import sqlalchemy as sa

revision = "config_openitems_20260412"
down_revision = "e7238c2e17a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.connectors (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(80) NOT NULL,
            connector_key   VARCHAR(80) NOT NULL,
            connector_type  VARCHAR(40) NOT NULL,
            display_name    VARCHAR(200),
            config_json     JSONB,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_connectors_tenant
        ON domain_shared.connectors (tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.reporting_units (
            id              VARCHAR(36) PRIMARY KEY,
            tenant_id       VARCHAR(80) NOT NULL,
            unit_key        VARCHAR(80) NOT NULL,
            display_name    VARCHAR(200) NOT NULL,
            connector_id    VARCHAR(36),
            config_json     JSONB,
            is_active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_reporting_units_tenant
        ON domain_shared.reporting_units (tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.schedules (
            id                  VARCHAR(36) PRIMARY KEY,
            tenant_id           VARCHAR(80) NOT NULL,
            schedule_key        VARCHAR(80) NOT NULL,
            display_name        VARCHAR(200) NOT NULL,
            reporting_unit_id   VARCHAR(36),
            cron_expr           VARCHAR(80),
            lead_days           INTEGER NOT NULL DEFAULT 5,
            use_workday_rule    BOOLEAN NOT NULL DEFAULT FALSE,
            output_format       VARCHAR(40),
            config_json         JSONB,
            is_active           BOOLEAN NOT NULL DEFAULT TRUE,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_schedules_tenant
        ON domain_shared.schedules (tenant_id)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_shared.open_items (
            id              VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            tenant_id       VARCHAR(80) NOT NULL,
            type            VARCHAR(20) NOT NULL,
            partner_id      VARCHAR(80),
            partner_name    VARCHAR(200),
            document_number VARCHAR(80),
            document_date   DATE,
            due_date        DATE,
            amount          NUMERIC(15,2) NOT NULL DEFAULT 0,
            paid_amount     NUMERIC(15,2) NOT NULL DEFAULT 0,
            currency        VARCHAR(3) NOT NULL DEFAULT 'EUR',
            status          VARCHAR(20) NOT NULL DEFAULT 'open',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_open_items_tenant
        ON domain_shared.open_items (tenant_id)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_open_items_type_status
        ON domain_shared.open_items (type, status)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_open_items_due_date
        ON domain_shared.open_items (due_date)
    """)


    # Create a convenience view so raw SQL queries referencing
    # domain_shared.journal_entries (e.g. liquidity.py) resolve
    # against the actual domain_erp tables.
    op.execute("""
        CREATE OR REPLACE VIEW domain_shared.journal_entries AS
        SELECT
            jel.id,
            jel.tenant_id,
            jel.account_id   AS account_number,
            jel.debit,
            jel.credit,
            jel.description,
            je.entry_date,
            je.posting_date,
            je.status,
            je.source,
            je.entry_number
        FROM domain_erp.journal_entry_lines jel
        JOIN domain_erp.journal_entries je ON je.id = jel.journal_entry_id
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS domain_shared.journal_entries")
    op.execute("DROP TABLE IF EXISTS domain_shared.open_items")
    op.execute("DROP TABLE IF EXISTS domain_shared.schedules")
    op.execute("DROP TABLE IF EXISTS domain_shared.reporting_units")
    op.execute("DROP TABLE IF EXISTS domain_shared.connectors")
