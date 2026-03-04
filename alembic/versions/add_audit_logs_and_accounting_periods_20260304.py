"""FIBU-COMP-01 / FIBU-GL-05: domain_shared.audit_logs + finance_accounting_periods

Revision ID: f5a6b7c8d9e0
Revises: 05c409bd64c6
Create Date: 2026-03-04

Legt domain_shared.audit_logs (GoBD Audit-Trail-UI) und
finance_accounting_periods (Periodensteuerung) an, falls nicht vorhanden.
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "f5a6b7c8d9e0"
down_revision = "05c409bd64c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_shared"))

    # domain_shared.audit_logs (für Audit-Trail-UI und log_fibu_audit)
    r = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'domain_shared' AND table_name = 'audit_logs'"
        )
    )
    if r.scalar() is None:
        op.execute(text("""
            CREATE TABLE domain_shared.audit_logs (
                id VARCHAR NOT NULL PRIMARY KEY,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
                user_id VARCHAR NOT NULL,
                user_email VARCHAR(100) NOT NULL,
                tenant_id VARCHAR NOT NULL,
                action VARCHAR(50) NOT NULL,
                entity_type VARCHAR(50) NOT NULL,
                entity_id VARCHAR NOT NULL,
                changes JSONB NOT NULL DEFAULT '{}',
                ip_address VARCHAR(50) NULL,
                user_agent VARCHAR(200) NULL,
                correlation_id VARCHAR(50) NULL
            )
        """))
        op.execute(text("CREATE INDEX ix_audit_logs_timestamp ON domain_shared.audit_logs(timestamp)"))
        op.execute(text("CREATE INDEX ix_audit_logs_tenant_id ON domain_shared.audit_logs(tenant_id)"))
        op.execute(text("CREATE INDEX ix_audit_logs_entity ON domain_shared.audit_logs(entity_type, entity_id)"))

    # finance_accounting_periods (FIBU-GL-05 Periodensteuerung)
    r2 = conn.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'finance_accounting_periods'"
        )
    )
    if r2.scalar() is None:
        op.execute(text("""
            CREATE TABLE finance_accounting_periods (
                id VARCHAR NOT NULL PRIMARY KEY,
                tenant_id VARCHAR NOT NULL,
                period VARCHAR(7) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                closed_at TIMESTAMP WITH TIME ZONE NULL,
                closed_by VARCHAR NULL,
                metadata JSONB NULL DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE NULL DEFAULT now(),
                UNIQUE(tenant_id, period)
            )
        """))
        op.execute(text("CREATE INDEX ix_finance_accounting_periods_tenant ON finance_accounting_periods(tenant_id)"))
        op.execute(text("CREATE INDEX ix_finance_accounting_periods_status ON finance_accounting_periods(status)"))


def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS finance_accounting_periods"))
    # audit_logs nicht droppen – könnte von anderer Migration/001 abhängen
    # op.execute(text("DROP TABLE IF EXISTS domain_shared.audit_logs"))
