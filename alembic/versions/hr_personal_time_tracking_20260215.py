"""hr personal time tracking tables

Revision ID: hr_personal_time_tracking_20260215
Revises: hr_training_onboarding_module_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "hr_personal_time_tracking_20260215"
down_revision = "hr_training_onboarding_module_20260215"
branch_labels = None
depends_on = None

DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_hr"))

    op.create_table(
        "time_entries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("employee_ref", sa.String(length=120), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("end_time", sa.Time(), nullable=True),
        sa.Column("hours", sa.Numeric(5, 2), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False, server_default=sa.text("'Arbeit'")),
        sa.Column("source", sa.String(length=40), nullable=False, server_default=sa.text("'manual'")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("hours >= 0 AND hours <= 24", name="ck_hr_time_entries_hours_range"),
        sa.CheckConstraint("entry_type IN ('Arbeit','Ueberstunden','Urlaub')", name="ck_hr_time_entries_type"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_time_entries_tenant_date",
        "time_entries",
        ["tenant_id", "entry_date"],
        unique=False,
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_time_entries_tenant_employee",
        "time_entries",
        ["tenant_id", "employee_ref"],
        unique=False,
        schema="domain_hr",
    )

    op.create_table(
        "driver_timesheets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("driver_name", sa.String(length=120), nullable=False),
        sa.Column("vehicle_plate", sa.String(length=40), nullable=False),
        sa.Column("tours", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("total_hours", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("overtime_hours", sa.Numeric(5, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("signature_data", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("total_hours >= 0 AND total_hours <= 24", name="ck_hr_driver_timesheets_total_hours"),
        sa.CheckConstraint("overtime_hours >= 0 AND overtime_hours <= 24", name="ck_hr_driver_timesheets_overtime_hours"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hr_driver_timesheets_tenant_date",
        "driver_timesheets",
        ["tenant_id", "entry_date"],
        unique=False,
        schema="domain_hr",
    )

    op.execute(
        sa.text(
            f"""
            INSERT INTO domain_hr.time_entries
              (id, tenant_id, employee_ref, entry_date, start_time, end_time, hours, entry_type, source, notes)
            VALUES
              ('7e4fa9d6-f05a-4b13-9f0a-8f5159944c91', '{DEFAULT_TENANT_ID}', 'EMP-1001', CURRENT_DATE, '07:00', '15:30', 8.00, 'Arbeit', 'seed', 'Seed-Zeiteintrag'),
              ('3c8eb78f-cba8-44d8-870f-503d880b4f09', '{DEFAULT_TENANT_ID}', 'EMP-1002', CURRENT_DATE, NULL, NULL, 0.00, 'Urlaub', 'seed', 'Seed-Urlaubseintrag')
            ON CONFLICT DO NOTHING;
            """
        )
    )


def downgrade() -> None:
    op.drop_index("idx_hr_driver_timesheets_tenant_date", table_name="driver_timesheets", schema="domain_hr")
    op.drop_table("driver_timesheets", schema="domain_hr")

    op.drop_index("idx_hr_time_entries_tenant_employee", table_name="time_entries", schema="domain_hr")
    op.drop_index("idx_hr_time_entries_tenant_date", table_name="time_entries", schema="domain_hr")
    op.drop_table("time_entries", schema="domain_hr")
