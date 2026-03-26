"""add finance P0 tables

Revision ID: finance_p0_001
Revises: add_sicherheiten_kl
Create Date: 2026-02-10

Adds missing tables for Finance P0 capabilities:
- finance_accounting_periods (FIBU-GL-05: Periodensteuerung)
- finance_payment_entries (FIBU-AR-03: Zahlungseingaenge)
- finance_open_items (FIBU-AR-03: Payment Matching)
- bank_accounts (FIBU-BNK-01: Bankstamm)
- bank_statements (FIBU-BNK-02: Kontoauszugsimport)
- bank_statement_lines (FIBU-BNK-02: Kontoauszugsimport)
- audit_log (FIBU-COMP-01: GoBD Audit Trail)
- finance_number_ranges (FIBU-GL-02: Nummernkreise)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "finance_p0_001"
down_revision: Union[str, None] = "add_sicherheiten_kl"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create domain_erp schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_erp")

    # ---- finance_accounting_periods ----
    op.create_table(
        "finance_accounting_periods",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),  # YYYY-MM
        sa.Column("status", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", sa.String(100), nullable=True),
        sa.Column("metadata", postgresql.JSONB, nullable=True, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "period", name="uq_accounting_period_tenant_period"),
        sa.Index("ix_fin_periods_tenant", "tenant_id"),
        sa.Index("ix_fin_periods_status", "status"),
    )

    # ---- finance_payment_entries (bank import entries for matching) ----
    op.create_table(
        "finance_payment_entries",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("bank_account", sa.String(50), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("value_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("reference", sa.String(200), nullable=True),
        sa.Column("remittance_info", sa.Text(), nullable=True),
        sa.Column("creditor_name", sa.String(200), nullable=True),
        sa.Column("creditor_iban", sa.String(34), nullable=True),
        sa.Column("debtor_name", sa.String(200), nullable=True),
        sa.Column("debtor_iban", sa.String(34), nullable=True),
        sa.Column("matched_op_id", sa.String(64), nullable=True),
        sa.Column("match_status", sa.String(20), nullable=False, server_default="UNMATCHED"),
        sa.Column("match_confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("match_reason", sa.String(200), nullable=True),
        sa.Column("statement_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_fin_payments_tenant", "tenant_id"),
        sa.Index("ix_fin_payments_status", "match_status"),
        sa.Index("ix_fin_payments_date", "booking_date"),
    )

    # ---- finance_open_items (normalized OP for payment matching) ----
    op.create_table(
        "finance_open_items",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("document_number", sa.String(50), nullable=False),
        sa.Column("document_type", sa.String(20), nullable=False, server_default="AR"),  # AR, AP
        sa.Column("customer_id", sa.String(36), nullable=True),
        sa.Column("customer_name", sa.String(200), nullable=True),
        sa.Column("supplier_id", sa.String(36), nullable=True),
        sa.Column("supplier_name", sa.String(200), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("open_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="EUR"),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_fin_oi_tenant", "tenant_id"),
        sa.Index("ix_fin_oi_customer", "customer_id"),
        sa.Index("ix_fin_oi_supplier", "supplier_id"),
        sa.Index("ix_fin_oi_status", "status"),
        sa.Index("ix_fin_oi_due_date", "due_date"),
    )

    # ---- bank_accounts (domain_erp schema) ----
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_accounts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            account_number VARCHAR(50) NOT NULL,
            bank_name VARCHAR(200) NOT NULL,
            iban VARCHAR(34),
            bic VARCHAR(11),
            currency VARCHAR(3) DEFAULT 'EUR',
            balance NUMERIC(15,2) DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_bank_accounts_tenant ON domain_erp.bank_accounts(tenant_id)")

    # ---- bank_statements ----
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_statements (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            bank_account_id UUID REFERENCES domain_erp.bank_accounts(id),
            statement_number VARCHAR(50),
            statement_date DATE NOT NULL,
            opening_balance NUMERIC(15,2),
            closing_balance NUMERIC(15,2),
            total_credit NUMERIC(15,2) DEFAULT 0,
            total_debit NUMERIC(15,2) DEFAULT 0,
            line_count INTEGER DEFAULT 0,
            import_format VARCHAR(20),
            filename VARCHAR(200),
            status VARCHAR(20) DEFAULT 'IMPORTED',
            imported_at TIMESTAMPTZ DEFAULT now(),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_bank_stmts_tenant ON domain_erp.bank_statements(tenant_id)")

    # ---- bank_statement_lines ----
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_erp.bank_statement_lines (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            statement_id UUID REFERENCES domain_erp.bank_statements(id),
            bank_account_id UUID REFERENCES domain_erp.bank_accounts(id),
            line_number INTEGER,
            booking_date DATE NOT NULL,
            value_date DATE,
            amount NUMERIC(15,2) NOT NULL,
            currency VARCHAR(3) DEFAULT 'EUR',
            reference VARCHAR(200),
            remittance_info TEXT,
            creditor_name VARCHAR(200),
            creditor_iban VARCHAR(34),
            debtor_name VARCHAR(200),
            debtor_iban VARCHAR(34),
            status VARCHAR(20) DEFAULT 'UNMATCHED',
            matched_op_id VARCHAR(64),
            match_confidence NUMERIC(3,2),
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_bsl_tenant ON domain_erp.bank_statement_lines(tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_bsl_status ON domain_erp.bank_statement_lines(status)")

    # ---- audit_log (GoBD compliance) ----
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id VARCHAR(36) PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
            user_id VARCHAR(100) NOT NULL,
            user_email VARCHAR(200),
            tenant_id VARCHAR(36) NOT NULL,
            action VARCHAR(50) NOT NULL,
            entity_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            changes JSONB DEFAULT '{}',
            ip_address VARCHAR(50),
            user_agent TEXT,
            correlation_id VARCHAR(64),
            created_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_log_tenant ON audit_log(tenant_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_log_entity ON audit_log(entity_type, entity_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_log_ts ON audit_log(timestamp)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_audit_log_user ON audit_log(user_id)")

    # ---- finance_number_ranges (Nummernkreise) ----
    op.create_table(
        "finance_number_ranges",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("range_type", sa.String(30), nullable=False),  # AR, AP, GL, ZE, ZA
        sa.Column("prefix", sa.String(20), nullable=False),
        sa.Column("current_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("min_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("max_number", sa.Integer(), nullable=False, server_default="999999"),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "range_type", "fiscal_year", name="uq_number_range"),
        sa.Index("ix_fin_nr_tenant", "tenant_id"),
    )

    # ---- Customers table in domain_erp schema (if not exists) ----
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_erp.customers (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            name VARCHAR(200) NOT NULL,
            company_name VARCHAR(200),
            email VARCHAR(200),
            phone VARCHAR(50),
            iban VARCHAR(34),
            bic VARCHAR(11),
            tax_id VARCHAR(50),
            payment_terms INTEGER DEFAULT 30,
            credit_limit NUMERIC(15,2),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_customers_tenant ON domain_erp.customers(tenant_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_erp.customers")
    op.drop_table("finance_number_ranges")
    op.execute("DROP TABLE IF EXISTS audit_log")
    op.execute("DROP TABLE IF EXISTS domain_erp.bank_statement_lines")
    op.execute("DROP TABLE IF EXISTS domain_erp.bank_statements")
    op.execute("DROP TABLE IF EXISTS domain_erp.bank_accounts")
    op.drop_table("finance_open_items")
    op.drop_table("finance_payment_entries")
    op.drop_table("finance_accounting_periods")

