"""Initial CRM Service schema.

Revision ID: 001_initial_crm_service_schema
Revises:
Create Date: 2025-11-15 10:57:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_service_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Service tables."""
    # Create enums
    enum_statements = [
        ("crm_service_case_status", "('new', 'assigned', 'in_progress', 'pending_customer', 'resolved', 'closed', 'escalated')"),
        ("crm_service_case_priority", "('low', 'medium', 'high', 'urgent')"),
        ("crm_service_case_type", "('incident', 'problem', 'question', 'feature_request', 'complaint')"),
        ("crm_service_sla_status", "('active', 'breached', 'warning', 'expired')"),
        ("crm_service_sla_priority", "('low', 'medium', 'high', 'urgent')"),
    ]
    for type_name, values in enum_statements:
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{type_name}') THEN
                    CREATE TYPE {type_name} AS ENUM {values};
                END IF;
            END$$;
            """
        )

    # SLAs table
    op.create_table(
        "crm_service_slas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("priority", postgresql.ENUM('low', 'medium', 'high', 'urgent', name='crm_service_sla_priority', create_type=False), nullable=False),
        sa.Column("response_time_hours", sa.Integer, nullable=False, server_default='24'),
        sa.Column("resolution_time_hours", sa.Integer, nullable=False, server_default='168'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Categories table (self-referencing for subcategories)
    op.create_table(
        "crm_service_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_service_categories.id")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default='0'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Cases table
    op.create_table(
        "crm_service_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("case_number", sa.String(32), nullable=False, unique=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", postgresql.ENUM('new', 'assigned', 'in_progress', 'pending_customer', 'resolved', 'closed', 'escalated', name='crm_service_case_status', create_type=False), nullable=False, server_default='new'),
        sa.Column("priority", postgresql.ENUM('low', 'medium', 'high', 'urgent', name='crm_service_case_priority', create_type=False), nullable=False, server_default='medium'),
        sa.Column("case_type", postgresql.ENUM('incident', 'problem', 'question', 'feature_request', 'complaint', name='crm_service_case_type', create_type=False), nullable=False, server_default='incident'),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True)),
        sa.Column("assigned_to", sa.String(64)),
        sa.Column("assigned_by", sa.String(64)),
        sa.Column("assigned_at", sa.DateTime),
        sa.Column("resolution", sa.Text),
        sa.Column("resolved_at", sa.DateTime),
        sa.Column("resolved_by", sa.String(64)),
        sa.Column("sla_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_service_slas.id")),
        sa.Column("sla_breached", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_service_categories.id")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Case history table
    op.create_table(
        "crm_service_case_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_service_cases.id"), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("old_value", sa.Text),
        sa.Column("new_value", sa.Text),
        sa.Column("field_name", sa.String(64)),
        sa.Column("performed_by", sa.String(64)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Knowledge articles table
    op.create_table(
        "crm_service_knowledge_articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("summary", sa.String(500)),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_service_categories.id")),
        sa.Column("tags", sa.String(500)),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("view_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("helpful_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("not_helpful_count", sa.Integer, nullable=False, server_default='0'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("published_at", sa.DateTime),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Service tables."""
    op.drop_table("crm_service_knowledge_articles")
    op.drop_table("crm_service_categories")
    op.drop_table("crm_service_slas")
    op.drop_table("crm_service_case_history")
    op.drop_table("crm_service_cases")

    op.execute("DROP TYPE crm_service_sla_status")
    op.execute("DROP TYPE crm_service_case_type")
    op.execute("DROP TYPE crm_service_case_priority")
    op.execute("DROP TYPE crm_service_case_status")


def _seed_initial_data():
    """Seed initial demo data."""
    # This will be populated when the service starts and finds existing customers
    pass
