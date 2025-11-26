"""Extend opportunities with additional fields and new entities.

Revision ID: 002_extend_opportunities
Revises: 001_initial_crm_sales_schema
Create Date: 2025-01-27 12:00:00.000000

"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "002_extend_opportunities"
down_revision = "001_initial_crm_sales_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new fields to opportunities and create new tables."""
    
    # Add new columns to crm_sales_opportunities
    op.add_column("crm_sales_opportunities", sa.Column("number", sa.String(64), nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("currency", sa.String(3), nullable=True, server_default="EUR"))
    op.add_column("crm_sales_opportunities", sa.Column("expected_revenue", sa.Float, nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("source", sa.String(128), nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("owner_id", sa.String(64), nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("notes", sa.Text, nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("created_by", sa.String(64), nullable=True))
    op.add_column("crm_sales_opportunities", sa.Column("updated_by", sa.String(64), nullable=True))
    
    # Create unique index on number
    op.create_index(
        "ix_crm_sales_opportunities_number",
        "crm_sales_opportunities",
        ["number"],
        unique=True,
    )
    
    # Make number NOT NULL after populating with default values
    # Generate default numbers for existing records
    op.execute("""
        UPDATE crm_sales_opportunities 
        SET number = 'OPP-' || LPAD(ROW_NUMBER() OVER (ORDER BY created_at)::text, 6, '0')
        WHERE number IS NULL;
    """)
    
    op.alter_column("crm_sales_opportunities", "number", nullable=False)
    
    # Create opportunity_stages table
    op.create_table(
        "crm_sales_opportunity_stages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("stage_key", sa.String(64), nullable=False),
        sa.Column("order", sa.Float, nullable=False, server_default="0"),
        sa.Column("probability_default", sa.Float, nullable=True),
        sa.Column("required_fields", sa.Text, nullable=True),  # JSON array
        sa.Column("is_closed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_won", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Create unique constraint on tenant_id + stage_key
    op.create_unique_constraint(
        "uq_crm_sales_opportunity_stages_tenant_stage_key",
        "crm_sales_opportunity_stages",
        ["tenant_id", "stage_key"],
    )
    
    # Create opportunity_history table
    op.create_table(
        "crm_sales_opportunity_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.String(128), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),
        sa.Column("changed_by", sa.String(64), nullable=False),
        sa.Column("changed_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("change_reason", sa.Text, nullable=True),
    )
    
    # Create index on opportunity_id for faster lookups
    op.create_index(
        "ix_crm_sales_opportunity_history_opportunity_id",
        "crm_sales_opportunity_history",
        ["opportunity_id"],
    )
    
    # Create index on changed_at for time-based queries
    op.create_index(
        "ix_crm_sales_opportunity_history_changed_at",
        "crm_sales_opportunity_history",
        ["changed_at"],
    )
    
    # Seed default opportunity stages
    op.execute("""
        INSERT INTO crm_sales_opportunity_stages (id, tenant_id, name, stage_key, "order", probability_default, required_fields, is_closed, is_won, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'default', 'Initial Contact', 'initial_contact', 1, 10, '["name", "customer_id"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Needs Analysis', 'needs_analysis', 2, 25, '["description", "amount"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Value Proposition', 'value_proposition', 3, 40, '["amount", "expected_close_date"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Identify Decision Makers', 'identify_decision_makers', 4, 50, '["contact_id"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Proposal / Price Quote', 'proposal_price_quote', 5, 60, '["amount", "probability"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Negotiation / Review', 'negotiation_review', 6, 75, '["expected_close_date"]', false, false, now(), now()),
            (gen_random_uuid(), 'default', 'Closed Won', 'closed_won', 7, 100, '["actual_close_date"]', true, true, now(), now()),
            (gen_random_uuid(), 'default', 'Closed Lost', 'closed_lost', 8, 0, '[]', true, false, now(), now())
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Remove new fields and tables."""
    
    # Drop tables
    op.drop_table("crm_sales_opportunity_history")
    op.drop_table("crm_sales_opportunity_stages")
    
    # Drop index
    op.drop_index("ix_crm_sales_opportunities_number", table_name="crm_sales_opportunities")
    
    # Remove columns
    op.drop_column("crm_sales_opportunities", "updated_by")
    op.drop_column("crm_sales_opportunities", "created_by")
    op.drop_column("crm_sales_opportunities", "notes")
    op.drop_column("crm_sales_opportunities", "owner_id")
    op.drop_column("crm_sales_opportunities", "campaign_id")
    op.drop_column("crm_sales_opportunities", "source")
    op.drop_column("crm_sales_opportunities", "expected_revenue")
    op.drop_column("crm_sales_opportunities", "currency")
    op.drop_column("crm_sales_opportunities", "number")

