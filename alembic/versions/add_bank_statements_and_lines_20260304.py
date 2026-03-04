"""FIBU-AR-03 / FIBU-BNK-02: bank_statements und bank_statement_lines (Zahlungseingänge, Kontoauszugsimport)

Revision ID: e4f5a6b7c8d9
Revises: b0c1d2e3f4a5
Create Date: 2026-03-04

Legt domain_erp.bank_statements und domain_erp.bank_statement_lines an für
Payment-Matching (Zahlungseingänge) und Kontoauszugsimport (CAMT/MT940/CSV).
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "e4f5a6b7c8d9"
down_revision = "b0c1d2e3f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_erp"))

    bs_exists = conn.execute(text("SELECT to_regclass('domain_erp.bank_statements')")).scalar()
    if not bs_exists:
        op.execute(text("""
            CREATE TABLE domain_erp.bank_statements (
                id VARCHAR NOT NULL PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                bank_account_id VARCHAR NOT NULL,
                account_iban VARCHAR(100) NULL,
                statement_date DATE NOT NULL,
                opening_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
                closing_balance NUMERIC(15,2) NOT NULL DEFAULT 0,
                format VARCHAR(20) NULL,
                total_lines INTEGER NOT NULL DEFAULT 0,
                imported_lines INTEGER NOT NULL DEFAULT 0,
                status VARCHAR(50) NULL DEFAULT 'imported',
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now()
            )
        """))
        op.execute(text("CREATE INDEX ix_bank_statements_tenant_id ON domain_erp.bank_statements(tenant_id)"))
        op.execute(text("CREATE INDEX ix_bank_statements_bank_account_id ON domain_erp.bank_statements(bank_account_id)"))

    bsl_exists = conn.execute(text("SELECT to_regclass('domain_erp.bank_statement_lines')")).scalar()
    if not bsl_exists:
        op.execute(text("""
            CREATE TABLE domain_erp.bank_statement_lines (
                id VARCHAR NOT NULL PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                statement_id VARCHAR NOT NULL,
                line_number INTEGER NOT NULL,
                booking_date DATE NOT NULL,
                value_date DATE NOT NULL,
                amount NUMERIC(15,2) NOT NULL,
                currency VARCHAR(3) NULL DEFAULT 'EUR',
                reference VARCHAR(255) NULL,
                remittance_info TEXT NULL,
                creditor_name VARCHAR(255) NULL,
                creditor_iban VARCHAR(50) NULL,
                debtor_name VARCHAR(255) NULL,
                debtor_iban VARCHAR(50) NULL,
                status VARCHAR(50) NULL DEFAULT 'UNMATCHED',
                matched_op_id VARCHAR(255) NULL,
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                updated_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now()
            )
        """))
        op.execute(text("CREATE INDEX ix_bank_statement_lines_tenant_id ON domain_erp.bank_statement_lines(tenant_id)"))
        op.execute(text("CREATE INDEX ix_bank_statement_lines_statement_id ON domain_erp.bank_statement_lines(statement_id)"))
        op.execute(text("CREATE INDEX ix_bank_statement_lines_status ON domain_erp.bank_statement_lines(status)"))
    else:
        # Falls Tabelle ohne matched_op_id existiert, Spalte nachtragen
        r = conn.execute(text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'domain_erp' AND table_name = 'bank_statement_lines' AND column_name = 'matched_op_id'
        """))
        if r.scalar() is None:
            op.execute(text("ALTER TABLE domain_erp.bank_statement_lines ADD COLUMN matched_op_id VARCHAR(255) NULL"))


def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS domain_erp.bank_statement_lines"))
    op.execute(text("DROP TABLE IF EXISTS domain_erp.bank_statements"))
