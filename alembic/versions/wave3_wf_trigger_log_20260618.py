"""wave3: wf_trigger_log + bank_statements + bank_statement_lines + waagen_quittungen

Revision ID: wave3_wf_trigger_log_20260618
Revises: comp_artikel_sperren_20260618
Create Date: 2026-06-18 10:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "wave3_wf_trigger_log_20260618"
down_revision = "comp_artikel_sperren_20260618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── domain_ops.wf_trigger_log ─────────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_ops")
    op.create_table(
        "wf_trigger_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("trigger_status", sa.String(64), nullable=False),
        sa.Column("actions", sa.Text(), nullable=True),
        sa.Column("result", sa.String(16), nullable=False, server_default="ok"),
        sa.Column("error_detail", sa.Text(), nullable=True),
        sa.Column("fired_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        schema="domain_ops",
    )
    op.create_index(
        "ix_wf_trigger_log_entity",
        "wf_trigger_log",
        ["entity_type", "entity_id"],
        schema="domain_ops",
    )

    # ── domain_finance.bank_statements ───────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")
    op.create_table(
        "bank_statements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("iban", sa.String(34), nullable=False),
        sa.Column("format", sa.String(16), nullable=False),
        sa.Column("filename", sa.String(255), nullable=True),
        sa.Column("line_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        schema="domain_finance",
    )

    # ── domain_finance.bank_statement_lines ──────────────────────
    op.create_table(
        "bank_statement_lines",
        sa.Column("id", sa.UUID(as_uuid=False), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("statement_id", sa.String(36), nullable=False, index=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 4), nullable=False),
        sa.Column("side", sa.String(8), nullable=False),
        sa.Column("reference", sa.String(255), nullable=True),
        sa.Column("purpose", sa.Text(), nullable=True),
        sa.Column("match_status", sa.String(16), nullable=False, server_default="offen"),
        sa.Column("matched_op_id", sa.String(36), nullable=True),
        sa.Column("source", sa.String(16), nullable=False),
        sa.ForeignKeyConstraint(
            ["statement_id"], ["domain_finance.bank_statements.id"],
            ondelete="CASCADE",
        ),
        schema="domain_finance",
    )

    # ── domain_agrar.waagen_quittungen ────────────────────────────
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    # Quittiert-Spalten zu weighing_tickets hinzufügen (falls nicht vorhanden)
    op.execute("""
        ALTER TABLE IF EXISTS domain_inventory.weighing_tickets
        ADD COLUMN IF NOT EXISTS quittiert BOOLEAN DEFAULT false,
        ADD COLUMN IF NOT EXISTS quittiert_am TIMESTAMPTZ
    """)
    op.execute("""
        CREATE OR REPLACE VIEW domain_agrar.weighing_tickets AS
        SELECT * FROM domain_inventory.weighing_tickets
    """)

    op.create_table(
        "waagen_quittungen",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False, index=True),
        sa.Column("weighing_ticket_id", sa.String(36), nullable=False, index=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("driver_id", sa.String(36), nullable=True),
        sa.Column("quittiert_am", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gps_lat", sa.Numeric(10, 6), nullable=True),
        sa.Column("gps_lon", sa.Numeric(10, 6), nullable=True),
        sa.Column("bemerkung", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="quittiert"),
        sa.UniqueConstraint("idempotency_key", "tenant_id",
                            name="uq_waagen_quittungen_idempotency"),
        schema="domain_agrar",
    )


def downgrade() -> None:
    op.drop_table("waagen_quittungen", schema="domain_agrar")
    op.execute("DROP VIEW IF EXISTS domain_agrar.weighing_tickets")
    op.execute("""
        ALTER TABLE IF EXISTS domain_inventory.weighing_tickets
        DROP COLUMN IF EXISTS quittiert,
        DROP COLUMN IF EXISTS quittiert_am
    """)
    op.drop_table("bank_statement_lines", schema="domain_finance")
    op.drop_table("bank_statements", schema="domain_finance")
    op.drop_index("ix_wf_trigger_log_entity", "wf_trigger_log", schema="domain_ops")
    op.drop_table("wf_trigger_log", schema="domain_ops")
