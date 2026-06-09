"""POS fiscal provider abstraction and evidence tables.

Revision ID: pos_fiscal_providers_20260609
Revises: crm_contacts_ext_kim_s4_20260609
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "pos_fiscal_providers_20260609"
down_revision = "crm_contacts_ext_kim_s4_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pos_fiscal_provider_configs",
        sa.Column("tenant_id", sa.String(64), primary_key=True),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("dsfinvk_provider", sa.String(30), nullable=False),
        sa.Column("cash_register_id", sa.String(120), nullable=False),
        sa.Column("client_id", sa.String(120), nullable=False),
        sa.Column("simulation_allowed", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.CheckConstraint(
            "provider IN ('fiskaly','swissbit_cloud','swissbit_gateway','simulation')",
            name="chk_pos_fiscal_provider",
        ),
        sa.CheckConstraint(
            "dsfinvk_provider IN ('fiskaly','simulation')",
            name="chk_pos_dsfinvk_provider",
        ),
        schema="domain_docflow",
    )
    op.create_table(
        "pos_fiscal_transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("transaction_id", sa.String(120), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_reference", sa.String(180)),
        sa.Column("terminal_id", sa.String(120), nullable=False),
        sa.Column("cash_register_id", sa.String(120), nullable=False),
        sa.Column("client_id", sa.String(120), nullable=False),
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("transaction_type", sa.String(30), nullable=False),
        sa.Column("state", sa.String(30), nullable=False),
        sa.Column("receipt_number", sa.String(120)),
        sa.Column("gross_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("payment_breakdown", postgresql.JSONB(), nullable=False),
        sa.Column("signature", sa.Text()),
        sa.Column("signature_counter", sa.BigInteger()),
        sa.Column("serial_number", sa.String(180)),
        sa.Column("qr_code_data", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("provider_response", postgresql.JSONB(), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tenant_id", "transaction_id", name="uq_pos_fiscal_transaction"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_pos_fiscal_tx_tenant_date_terminal",
        "pos_fiscal_transactions",
        ["tenant_id", "business_date", "terminal_id"],
        schema="domain_docflow",
    )
    op.create_table(
        "pos_fiscal_closings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("closing_id", sa.String(120), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_reference", sa.String(180)),
        sa.Column("cash_register_id", sa.String(120), nullable=False),
        sa.Column("terminal_id", sa.String(120), nullable=False),
        sa.Column("business_date", sa.Date(), nullable=False),
        sa.Column("transaction_count", sa.Integer(), nullable=False),
        sa.Column("gross_total", sa.Numeric(18, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("provider_response", postgresql.JSONB(), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tenant_id", "closing_id", name="uq_pos_fiscal_closing"),
        schema="domain_docflow",
    )
    op.create_table(
        "pos_fiscal_exports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("export_id", sa.String(120), nullable=False),
        sa.Column("export_type", sa.String(20), nullable=False),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("provider_reference", sa.String(180)),
        sa.Column("cash_register_id", sa.String(120), nullable=False),
        sa.Column("period_from", sa.Date(), nullable=False),
        sa.Column("period_to", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("download_url", sa.Text()),
        sa.Column("provider_response", postgresql.JSONB(), nullable=False),
        sa.Column("simulated", sa.Boolean(), nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("tenant_id", "export_id", name="uq_pos_fiscal_export"),
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_table("pos_fiscal_exports", schema="domain_docflow")
    op.drop_table("pos_fiscal_closings", schema="domain_docflow")
    op.drop_index(
        "ix_pos_fiscal_tx_tenant_date_terminal",
        table_name="pos_fiscal_transactions",
        schema="domain_docflow",
    )
    op.drop_table("pos_fiscal_transactions", schema="domain_docflow")
    op.drop_table("pos_fiscal_provider_configs", schema="domain_docflow")
