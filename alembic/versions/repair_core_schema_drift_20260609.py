"""Repair schema objects missing from databases stamped past older migrations.

Revision ID: repair_core_schema_20260609
Revises: merge_crm_pos_20260609
"""

from alembic import op
from sqlalchemy import text


revision = "repair_core_schema_20260609"
down_revision = "merge_crm_pos_20260609"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(text("CREATE SCHEMA IF NOT EXISTS domain_hr"))
    op.execute(
        text(
            """
            ALTER TABLE domain_inventory.agrar_settlements
              ADD COLUMN IF NOT EXISTS campaign_id VARCHAR(64);
            CREATE INDEX IF NOT EXISTS ix_agrar_settlements_campaign
              ON domain_inventory.agrar_settlements (campaign_id);

            ALTER TABLE domain_erp.chart_of_accounts
              ADD COLUMN IF NOT EXISTS subcategory VARCHAR(50),
              ADD COLUMN IF NOT EXISTS description TEXT,
              ADD COLUMN IF NOT EXISTS is_summary BOOLEAN DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS balance NUMERIC(15,2) DEFAULT 0,
              ADD COLUMN IF NOT EXISTS last_transaction_date TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS parent_account_id VARCHAR,
              ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;

            CREATE TABLE IF NOT EXISTS domain_hr.time_entries (
              id VARCHAR PRIMARY KEY,
              tenant_id VARCHAR NOT NULL,
              employee_ref VARCHAR(120) NOT NULL,
              entry_date DATE NOT NULL,
              start_time TIME,
              end_time TIME,
              hours NUMERIC(6,2) NOT NULL DEFAULT 0,
              entry_type VARCHAR(20) NOT NULL DEFAULT 'Arbeit',
              source VARCHAR(40) NOT NULL DEFAULT 'manual',
              status VARCHAR(20) NOT NULL DEFAULT 'Draft',
              cost_center VARCHAR,
              work_area VARCHAR,
              correction_reason TEXT,
              notes TEXT,
              approved_by VARCHAR,
              approved_at TIMESTAMPTZ,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
              created_by VARCHAR,
              updated_by VARCHAR,
              audit_ref VARCHAR,
              version INTEGER NOT NULL DEFAULT 1,
              CONSTRAINT time_entries_hours_positive_ck CHECK (hours >= 0)
            );
            ALTER TABLE domain_hr.time_entries
              ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'Draft';
            CREATE INDEX IF NOT EXISTS time_entries_tenant_employee_date_idx
              ON domain_hr.time_entries (tenant_id, employee_ref, entry_date);
            CREATE INDEX IF NOT EXISTS time_entries_tenant_status_idx
              ON domain_hr.time_entries (tenant_id, status);

            CREATE TABLE IF NOT EXISTS domain_inventory.drying_rule_sets (
              id VARCHAR PRIMARY KEY,
              tenant_id VARCHAR NOT NULL,
              crop_code VARCHAR(40) NOT NULL,
              site_id VARCHAR(64),
              valid_from DATE,
              valid_to DATE,
              version INTEGER NOT NULL DEFAULT 1,
              is_active BOOLEAN NOT NULL DEFAULT TRUE,
              method VARCHAR(40) NOT NULL,
              base_moisture_pct NUMERIC(5,2) NOT NULL,
              rounding_mode VARCHAR(20) NOT NULL DEFAULT 'ROUND_NEAREST',
              clamp_mode VARCHAR(20) NOT NULL DEFAULT 'HARD_ERROR',
              min_moisture_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
              max_moisture_pct NUMERIC(5,2) NOT NULL DEFAULT 60,
              start_threshold_moisture_pct NUMERIC(5,2),
              fee_basis VARCHAR(20) NOT NULL DEFAULT 'INVOICE_WEIGHT',
              created_at TIMESTAMPTZ DEFAULT NOW(),
              created_by VARCHAR(64),
              updated_at TIMESTAMPTZ,
              updated_by VARCHAR(64),
              contract_id VARCHAR,
              customer_id VARCHAR,
              is_customer_specific BOOLEAN NOT NULL DEFAULT FALSE,
              justification TEXT,
              document_id VARCHAR(64)
            );
            CREATE INDEX IF NOT EXISTS ix_drying_rule_sets_crop_site_valid
              ON domain_inventory.drying_rule_sets
              (tenant_id, crop_code, site_id, valid_from, valid_to, version);

            CREATE TABLE IF NOT EXISTS domain_inventory.drying_rule_lookup_rows (
              id VARCHAR PRIMARY KEY,
              rule_set_id VARCHAR NOT NULL
                REFERENCES domain_inventory.drying_rule_sets(id),
              moisture_pct NUMERIC(5,1) NOT NULL,
              entzug_pct_points NUMERIC(5,1) NOT NULL,
              loss_pct NUMERIC(8,4) NOT NULL,
              fee_value NUMERIC(12,4),
              fee_unit VARCHAR(20),
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE UNIQUE INDEX IF NOT EXISTS uq_drying_lookup_rule_moisture
              ON domain_inventory.drying_rule_lookup_rows
              (rule_set_id, moisture_pct);

            CREATE TABLE IF NOT EXISTS domain_inventory.drying_rule_factor_ranges (
              id VARCHAR PRIMARY KEY,
              rule_set_id VARCHAR NOT NULL
                REFERENCES domain_inventory.drying_rule_sets(id),
              from_moisture_incl NUMERIC(5,1) NOT NULL,
              to_moisture_incl NUMERIC(5,1) NOT NULL,
              factor NUMERIC(8,4) NOT NULL,
              created_at TIMESTAMPTZ DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS ix_drying_factor_rule_from_to
              ON domain_inventory.drying_rule_factor_ranges
              (rule_set_id, from_moisture_incl, to_moisture_incl);
            """
        )
    )


def downgrade() -> None:
    # This migration repairs previously expected production schema. Removing
    # those objects would reintroduce drift, so downgrade is intentionally empty.
    pass
