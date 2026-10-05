"""UIX-062 entity notes for collab rail.

Revision ID: entity_notes_uix062
Revises: calendar_items_uix063
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "entity_notes_uix062"
down_revision = "calendar_items_uix063"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.create_table(
        "entity_notes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("body", sa.String(length=4000), nullable=False),
        sa.Column("mentions", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_entity_notes_lookup",
        "entity_notes",
        ["tenant_id", "entity_type", "entity_id", sa.text("created_at DESC")],
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_entity_notes_lookup", table_name="entity_notes", schema="domain_shared")
    op.drop_table("entity_notes", schema="domain_shared")
