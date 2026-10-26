"""Basis des CRM Analytics-Schemas aus app.db.models.

Ersetzt die nie angewendeten Vorgaengerrevisionen (doppelte Enum-Anlage, Revisions-IDs
laenger als version_num, Abweichung von den Modellen). Eigene Versionstabelle siehe env.py.

Revision ID: crm_analytics_0001
Revises:
Create Date: 2026-10-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "crm_analytics_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('crm_analytics_dashboards',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('executive', 'sales', 'service', 'marketing', 'custom', name='crm_analytics_dashboard_type'), nullable=False),
    sa.Column('config', sa.JSON(), nullable=False),
    sa.Column('filters', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_analytics_exports',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('format', sa.String(length=16), nullable=False),
    sa.Column('config', sa.JSON(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('requested_by', sa.String(length=64), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_analytics_metrics',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('count', 'sum', 'average', 'percentage', 'trend', name='crm_analytics_metric_type'), nullable=False),
    sa.Column('entity', sa.String(length=64), nullable=False),
    sa.Column('field', sa.String(length=64), nullable=False),
    sa.Column('aggregation', sa.String(length=32), nullable=False),
    sa.Column('filters', sa.JSON(), nullable=False),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('trend', sa.Float(), nullable=True),
    sa.Column('last_calculated', sa.DateTime(), nullable=True),
    sa.Column('calculation_interval', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_analytics_predictions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('model_type', sa.String(length=64), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('entity_type', sa.String(length=64), nullable=False),
    sa.Column('score', sa.Float(), nullable=False),
    sa.Column('confidence', sa.Float(), nullable=False),
    sa.Column('features', sa.JSON(), nullable=False),
    sa.Column('prediction_date', sa.DateTime(), nullable=False),
    sa.Column('valid_until', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('crm_analytics_reports',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type', sa.Enum('sales_performance', 'customer_satisfaction', 'case_management', 'lead_conversion', 'revenue_analysis', 'custom', name='crm_analytics_report_type'), nullable=False),
    sa.Column('config', sa.JSON(), nullable=False),
    sa.Column('filters', sa.JSON(), nullable=False),
    sa.Column('results', sa.JSON(), nullable=True),
    sa.Column('schedule', sa.String(length=128), nullable=True),
    sa.Column('last_run', sa.DateTime(), nullable=True),
    sa.Column('next_run', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_scheduled', sa.Boolean(), nullable=False),
    sa.Column('created_by', sa.String(length=64), nullable=True),
    sa.Column('updated_by', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('crm_analytics_reports')
    op.drop_table('crm_analytics_predictions')
    op.drop_table('crm_analytics_metrics')
    op.drop_table('crm_analytics_exports')
    op.drop_table('crm_analytics_dashboards')
    sa.Enum(name='crm_analytics_dashboard_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_analytics_metric_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='crm_analytics_report_type').drop(op.get_bind(), checkfirst=True)
