"""PROD-FIBU-001: fibu_journal_ref auf ProduktionsAuftrag

Revision ID: prod_fibu_journal_ref_20260618
Revises: mobile_event_queue_20260619
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "prod_fibu_journal_ref_20260618"
down_revision = "mobile_event_queue_20260619"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "futtermittel_produktionsauftraege",
        sa.Column("fibu_journal_ref", sa.String(128), nullable=True,
                  comment="JournalEntry-Referenz nach Produktionsabschluss"),
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_column(
        "futtermittel_produktionsauftraege",
        "fibu_journal_ref",
        schema="domain_shared",
    )
