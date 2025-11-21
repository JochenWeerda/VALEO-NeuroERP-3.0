"""Initial CRM Analytics schema.

Revision ID: 001_initial_crm_analytics_schema
Revises:
Create Date: 2025-11-15 11:34:00.000000

"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "001_initial_crm_analytics_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create CRM Analytics tables."""
    # Create enums
    op.execute("CREATE TYPE crm_analytics_dashboard_type AS ENUM ('executive', 'sales', 'service', 'marketing', 'custom')")
    op.execute("CREATE TYPE crm_analytics_report_type AS ENUM ('sales_performance', 'customer_satisfaction', 'case_management', 'lead_conversion', 'revenue_analysis', 'custom')")
    op.execute("CREATE TYPE crm_analytics_metric_type AS ENUM ('count', 'sum', 'average', 'percentage', 'trend')")
    op.execute("CREATE TYPE crm_analytics_notification_type AS ENUM ('email', 'in_app', 'sms', 'webhook')")

    # Dashboards table
    op.create_table(
        "crm_analytics_dashboards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("type", postgresql.ENUM('executive', 'sales', 'service', 'marketing', 'custom', name='crm_analytics_dashboard_type'), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("filters", postgresql.JSONB, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Reports table
    op.create_table(
        "crm_analytics_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("type", postgresql.ENUM('sales_performance', 'customer_satisfaction', 'case_management', 'lead_conversion', 'revenue_analysis', 'custom', name='crm_analytics_report_type'), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("filters", postgresql.JSONB, nullable=False),
        sa.Column("results", postgresql.JSONB),
        sa.Column("schedule", sa.String(128)),
        sa.Column("last_run", sa.DateTime),
        sa.Column("next_run", sa.DateTime),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("is_scheduled", sa.Boolean, nullable=False, server_default='false'),
        sa.Column("created_by", sa.String(64)),
        sa.Column("updated_by", sa.String(64)),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Metrics table
    op.create_table(
        "crm_analytics_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("type", postgresql.ENUM('count', 'sum', 'average', 'percentage', 'trend', name='crm_analytics_metric_type'), nullable=False),
        sa.Column("entity", sa.String(64), nullable=False),
        sa.Column("field", sa.String(64), nullable=False),
        sa.Column("aggregation", sa.String(32), nullable=False),
        sa.Column("filters", postgresql.JSONB, nullable=False),
        sa.Column("value", sa.Float),
        sa.Column("trend", sa.Float),
        sa.Column("last_calculated", sa.DateTime),
        sa.Column("calculation_interval", sa.Integer, nullable=False, server_default='300'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Predictions table
    op.create_table(
        "crm_analytics_predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("model_type", sa.String(64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("features", postgresql.JSONB, nullable=False),
        sa.Column("prediction_date", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("valid_until", sa.DateTime),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default='true'),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Exports table
    op.create_table(
        "crm_analytics_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("format", sa.String(16), nullable=False),
        sa.Column("config", postgresql.JSONB, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default='pending'),
        sa.Column("file_path", sa.String(500)),
        sa.Column("file_size", sa.Integer),
        sa.Column("requested_by", sa.String(64)),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("error_message", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Seed initial data
    _seed_initial_data()


def downgrade() -> None:
    """Drop CRM Analytics tables."""
    op.drop_table("crm_analytics_exports")
    op.drop_table("crm_analytics_predictions")
    op.drop_table("crm_analytics_metrics")
    op.drop_table("crm_analytics_reports")
    op.drop_table("crm_analytics_dashboards")

    op.execute("DROP TYPE crm_analytics_notification_type")
    op.execute("DROP TYPE crm_analytics_metric_type")
    op.execute("DROP TYPE crm_analytics_report_type")
    op.execute("DROP TYPE crm_analytics_dashboard_type")


def _seed_initial_data():
    """Seed initial demo analytics data."""
    # This will be populated when the service starts and finds existing data
    pass