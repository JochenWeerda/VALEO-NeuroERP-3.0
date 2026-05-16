"""add driver_time_events table

Revision ID: driver_time_events_20260516
Revises: streckengeschaefte_table_merge_20260424
Create Date: 2026-05-16
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = "driver_time_events_20260516"
down_revision = "streckengeschaefte_table_merge_20260424"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "driver_time_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("employee_ref", sa.String(128), nullable=False),
        sa.Column("vehicle_id", sa.String(128), nullable=True),
        sa.Column("tour_ref", sa.String(128), nullable=True),
        sa.Column("event_type", sa.String(32), nullable=False),  # START/END/BREAK/PAUSE/TACHO
        sa.Column("event_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("absence_ref", sa.String(128), nullable=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="MANUAL"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("row_version", sa.Integer, nullable=False, server_default="1"),
        sa.CheckConstraint("event_type IN ('START','END','BREAK','PAUSE','TACHO')", name="ck_dte_event_type"),
        sa.CheckConstraint("source IN ('MANUAL','TACHO','IMPORT','SYSTEM')", name="ck_dte_source"),
        schema="domain_hr",
    )
    op.create_index("idx_dte_tenant_employee_ts", "driver_time_events", ["tenant_id", "employee_ref", "event_ts"], schema="domain_hr")
    op.create_index("idx_dte_tenant_vehicle", "driver_time_events", ["tenant_id", "vehicle_id"], schema="domain_hr")


def downgrade():
    op.drop_index("idx_dte_tenant_vehicle", table_name="driver_time_events", schema="domain_hr")
    op.drop_index("idx_dte_tenant_employee_ts", table_name="driver_time_events", schema="domain_hr")
    op.drop_table("driver_time_events", schema="domain_hr")
