"""Initial CRM Sales schema.

Revision ID: 001_initial_crm_sales_schema
Revises:
Create Date: 2025-11-14 21:30:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_sales_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Sales tables."""
    # Create enums
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crm_sales_opportunity_status') THEN
                CREATE TYPE crm_sales_opportunity_status AS ENUM (
                    'prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'
                );
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'crm_sales_opportunity_stage') THEN
                CREATE TYPE crm_sales_opportunity_stage AS ENUM (
                    'initial_contact', 'needs_analysis', 'value_proposition', 'identify_decision_makers',
                    'proposal_price_quote', 'negotiation_review', 'closed_won', 'closed_lost'
                );
            END IF;
        END$$;
        """
    )

    # Opportunities table
    op.create_table(
        "crm_sales_opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("amount", sa.Float),
        sa.Column("probability", sa.Float),
        sa.Column("expected_close_date", sa.DateTime),
        sa.Column("actual_close_date", sa.DateTime),
        sa.Column("status", postgresql.ENUM('prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost', name='crm_sales_opportunity_status', create_type=False), nullable=False, server_default='prospecting'),
        sa.Column("stage", postgresql.ENUM('initial_contact', 'needs_analysis', 'value_proposition', 'identify_decision_makers', 'proposal_price_quote', 'negotiation_review', 'closed_won', 'closed_lost', name='crm_sales_opportunity_stage', create_type=False), nullable=False, server_default='initial_contact'),
        sa.Column("lead_source", sa.String(128)),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Quotes table
    op.create_table(
        "crm_sales_quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("quote_number", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_opportunities.id")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True)),
        sa.Column("subtotal", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("tax_amount", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("discount_amount", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("total_amount", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("valid_until", sa.DateTime),
        sa.Column("status", sa.String(32), nullable=False, server_default='draft'),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Quote line items table
    op.create_table(
        "crm_sales_quote_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_quotes.id"), nullable=False),
        sa.Column("product_id", sa.String(64)),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("quantity", sa.Float, nullable=False, server_default='1.0'),
        sa.Column("unit_price", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("discount_percent", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("line_total", sa.Float, nullable=False, server_default='0.0'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Sales activities table
    op.create_table(
        "crm_sales_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_opportunities.id")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True)),
        sa.Column("activity_type", sa.String(32), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(32), nullable=False, server_default='planned'),
        sa.Column("priority", sa.String(16), nullable=False, server_default='medium'),
        sa.Column("scheduled_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_minutes", sa.Float),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("outcome", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Sales tables."""
    op.drop_table("crm_sales_activities")
    op.drop_table("crm_sales_quote_line_items")
    op.drop_table("crm_sales_quotes")
    op.drop_table("crm_sales_opportunities")

    op.execute("DROP TYPE crm_sales_opportunity_stage")
    op.execute("DROP TYPE crm_sales_opportunity_status")


def _seed_initial_data():
    """Seed initial demo data."""
    # This will be populated when the service starts and finds existing customers
    pass
