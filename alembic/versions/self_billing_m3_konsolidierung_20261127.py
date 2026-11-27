"""Self-Billing M3: Agrar-Erweiterung an DocFlow + Idempotenz.

Revision ID: self_billing_m3_konsolidierung_20261127
Revises: loeschauftrag_20261126
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "self_billing_m3_konsolidierung_20261127"
down_revision: Union[str, None] = "loeschauftrag_20261126"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "self_billing_invoices",
        sa.Column("docflow_header_id", sa.String(), nullable=True),
        schema="domain_finance",
    )
    op.add_column(
        "self_billing_invoices",
        sa.Column("journal_entry_id", sa.String(), nullable=True),
        schema="domain_finance",
    )
    op.add_column(
        "self_billing_invoices",
        sa.Column("taxation_type", sa.String(length=20), nullable=True),
        schema="domain_finance",
    )
    op.add_column(
        "self_billing_invoices",
        sa.Column("tax_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="domain_finance",
    )
    op.create_index(
        "ix_self_billing_invoices_docflow_header_id",
        "self_billing_invoices",
        ["docflow_header_id"],
        schema="domain_finance",
    )
    op.create_index(
        "ix_self_billing_invoices_journal_entry_id",
        "self_billing_invoices",
        ["journal_entry_id"],
        schema="domain_finance",
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_self_billing_invoices_tenant_ha_booked
        ON domain_finance.self_billing_invoices (tenant_id, harvest_acceptance_id)
        WHERE harvest_acceptance_id IS NOT NULL AND journal_entry_id IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_self_billing_invoices_tenant_ha_open
        ON domain_finance.self_billing_invoices (tenant_id, harvest_acceptance_id)
        WHERE harvest_acceptance_id IS NOT NULL AND status NOT IN ('cancelled')
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_finance.uq_self_billing_invoices_tenant_ha_open")
    op.execute("DROP INDEX IF EXISTS domain_finance.uq_self_billing_invoices_tenant_ha_booked")
    op.drop_index(
        "ix_self_billing_invoices_journal_entry_id",
        table_name="self_billing_invoices",
        schema="domain_finance",
    )
    op.drop_index(
        "ix_self_billing_invoices_docflow_header_id",
        table_name="self_billing_invoices",
        schema="domain_finance",
    )
    op.drop_column("self_billing_invoices", "tax_context", schema="domain_finance")
    op.drop_column("self_billing_invoices", "taxation_type", schema="domain_finance")
    op.drop_column("self_billing_invoices", "journal_entry_id", schema="domain_finance")
    op.drop_column("self_billing_invoices", "docflow_header_id", schema="domain_finance")
