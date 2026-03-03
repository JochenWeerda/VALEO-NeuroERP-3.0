"""chart_of_accounts und journal_entry_lines anlegen (Nachlauf zu journal_entries)

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-03-03

Legt domain_erp.chart_of_accounts an, falls fehlend (z. B. wenn 001 nicht in der
Kette liegt), und danach domain_erp.journal_entry_lines, falls noch nicht vorhanden.
"""

from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "f8a9b0c1d2e3"
down_revision = "e7f8a9b0c1d2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_erp"))

    coa_exists = conn.execute(text("SELECT to_regclass('domain_erp.chart_of_accounts')")).scalar()
    if not coa_exists:
        op.execute(text("""
            CREATE TABLE domain_erp.chart_of_accounts (
                id VARCHAR NOT NULL PRIMARY KEY,
                tenant_id VARCHAR NULL REFERENCES domain_shared.tenants(id),
                account_number VARCHAR(20) NOT NULL,
                account_name VARCHAR(255) NOT NULL,
                account_type VARCHAR(50) NOT NULL,
                category VARCHAR(100) NULL,
                is_active BOOLEAN NULL DEFAULT true,
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                UNIQUE(account_number)
            )
        """))

    jel_exists = conn.execute(text("SELECT to_regclass('domain_erp.journal_entry_lines')")).scalar()
    coa_now = conn.execute(text("SELECT to_regclass('domain_erp.chart_of_accounts')")).scalar()
    if not jel_exists and coa_now:
        op.execute(text("""
            CREATE TABLE domain_erp.journal_entry_lines (
                id VARCHAR NOT NULL PRIMARY KEY,
                journal_entry_id VARCHAR NOT NULL REFERENCES domain_erp.journal_entries(id) ON DELETE CASCADE,
                account_id VARCHAR NOT NULL REFERENCES domain_erp.chart_of_accounts(id),
                description VARCHAR(255) NULL,
                debit NUMERIC(15,2) NULL DEFAULT 0,
                credit NUMERIC(15,2) NULL DEFAULT 0,
                cost_center VARCHAR(100) NULL,
                project VARCHAR(100) NULL,
                line_number INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now()
            )
        """))


def downgrade() -> None:
    # Nur journal_entry_lines zurücknehmen; chart_of_accounts nicht löschen (kann von 001 stammen)
    op.execute(text("DROP TABLE IF EXISTS domain_erp.journal_entry_lines"))
