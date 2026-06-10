"""Normalize finance account values and restore HR shift schema.

Revision ID: normalize_fin_hr_20260610
Revises: repair_core_schema_20260609
"""

from alembic import op
from sqlalchemy import text


revision = "normalize_fin_hr_20260610"
down_revision = "repair_core_schema_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            UPDATE domain_erp.chart_of_accounts
            SET account_type = CASE
                  WHEN account_number LIKE '8%' THEN 'revenue'
                  ELSE 'asset'
                END,
                category = CASE
                  WHEN account_number LIKE '8%' THEN 'revenue'
                  ELSE 'current_assets'
                END
            WHERE account_type NOT IN ('asset', 'liability', 'equity', 'revenue', 'expense')
               OR category NOT IN (
                 'current_assets', 'fixed_assets', 'current_liabilities',
                 'long_term_liabilities', 'equity', 'revenue',
                 'cost_of_goods_sold', 'operating_expenses',
                 'other_expenses', 'other_income'
               );

            CREATE TABLE IF NOT EXISTS domain_hr.shifts (
              id VARCHAR PRIMARY KEY,
              tenant_id VARCHAR NOT NULL,
              shift_date DATE NOT NULL,
              name TEXT NOT NULL,
              location_code TEXT NOT NULL DEFAULT 'main',
              required_role TEXT NOT NULL DEFAULT 'employee',
              required_qualifications JSONB NOT NULL DEFAULT '[]'::jsonb,
              required_headcount INTEGER NOT NULL DEFAULT 1,
              starts_at TIME NOT NULL,
              ends_at TIME NOT NULL,
              assigned_employee_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
              status TEXT NOT NULL DEFAULT 'planned',
              conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
              notes TEXT,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              created_by TEXT,
              updated_by TEXT,
              CONSTRAINT shifts_required_headcount_ck CHECK (required_headcount > 0),
              CONSTRAINT shifts_status_ck
                CHECK (status IN ('planned', 'warning', 'blocked', 'cancelled'))
            );
            CREATE INDEX IF NOT EXISTS shifts_tenant_date_idx
              ON domain_hr.shifts (tenant_id, shift_date);
            CREATE INDEX IF NOT EXISTS shifts_tenant_location_idx
              ON domain_hr.shifts (tenant_id, location_code);
            CREATE INDEX IF NOT EXISTS shifts_tenant_status_idx
              ON domain_hr.shifts (tenant_id, status);
            """
        )
    )


def downgrade() -> None:
    pass
