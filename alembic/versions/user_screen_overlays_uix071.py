"""UIX-071 user screen overlays.

Revision ID: user_screen_overlays_uix071
Revises: entity_notes_uix062
Create Date: 2026-07-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "user_screen_overlays_uix071"
down_revision = "entity_notes_uix062"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.create_table(
        "user_screen_overlays",
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("screen_id", sa.String(length=96), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("overlay", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id", "user_id", "screen_id"),
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_table("user_screen_overlays", schema="domain_shared")
