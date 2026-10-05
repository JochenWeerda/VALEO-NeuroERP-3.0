"""Tenant-safe L3 deep-mask parity foundations.

Revision ID: l3_deep_mask_parity_20260822
Revises: l3_legacy_interfaces_20260821
"""

from alembic import op

revision = "l3_deep_mask_parity_20260822"
down_revision = "l3_legacy_interfaces_20260821"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
      CREATE SCHEMA IF NOT EXISTS domain_compliance;
      CREATE TABLE IF NOT EXISTS domain_compliance.sanctions_list (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, alias_namen TEXT,
        land_code TEXT NOT NULL, liste TEXT NOT NULL, eintragstyp TEXT NOT NULL,
        eintrags_nr TEXT NOT NULL, is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE TABLE IF NOT EXISTS domain_compliance.sanctions_checks (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, geprueft_name TEXT NOT NULL,
        status TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'manual', entity_ref TEXT,
        checked_by TEXT, geprueft_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      ALTER TABLE domain_compliance.sanctions_checks
        ADD COLUMN IF NOT EXISTS tenant_id TEXT,
        ADD COLUMN IF NOT EXISTS scope TEXT NOT NULL DEFAULT 'manual',
        ADD COLUMN IF NOT EXISTS entity_ref TEXT,
        ADD COLUMN IF NOT EXISTS checked_by TEXT;
      UPDATE domain_compliance.sanctions_checks
        SET tenant_id = 'legacy-unassigned' WHERE tenant_id IS NULL;
      ALTER TABLE domain_compliance.sanctions_checks
        ALTER COLUMN tenant_id SET NOT NULL;
      CREATE INDEX IF NOT EXISTS ix_sanctions_checks_tenant_scope_time
        ON domain_compliance.sanctions_checks (tenant_id, scope, geprueft_am DESC);
      ALTER TABLE domain_ops.ops_chargen
        ADD COLUMN IF NOT EXISTS tenant_id TEXT NOT NULL DEFAULT 'legacy-unassigned',
        ADD COLUMN IF NOT EXISTS lieferanten_charge TEXT,
        ADD COLUMN IF NOT EXISTS anerkennungs_nr TEXT;
      CREATE INDEX IF NOT EXISTS ix_ops_chargen_tenant_status
        ON domain_ops.ops_chargen (tenant_id, status, qualitaetsstatus);
      CREATE TABLE IF NOT EXISTS domain_ops.ops_chargen_audit (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, charge_id TEXT NOT NULL,
        action TEXT NOT NULL, old_value TEXT, new_value TEXT, actor TEXT NOT NULL,
        reason TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_ops_chargen_audit_tenant_charge
        ON domain_ops.ops_chargen_audit (tenant_id, charge_id, created_at DESC);
      CREATE TABLE IF NOT EXISTS domain_reporting.l3_bonus_runs (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, report_id TEXT NOT NULL,
        from_date DATE NOT NULL, to_date DATE NOT NULL, rate_pct NUMERIC(8,4) NOT NULL,
        status TEXT NOT NULL, total_basis NUMERIC(16,2) NOT NULL DEFAULT 0,
        total_bonus NUMERIC(16,2) NOT NULL DEFAULT 0, currency TEXT NOT NULL DEFAULT 'EUR',
        correction_of TEXT, reason TEXT NOT NULL, actor TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      );
      CREATE INDEX IF NOT EXISTS ix_l3_bonus_runs_tenant_time
        ON domain_reporting.l3_bonus_runs (tenant_id, created_at DESC);
      CREATE TABLE IF NOT EXISTS domain_reporting.l3_bonus_run_lines (
        id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, run_id TEXT NOT NULL,
        line_no INTEGER NOT NULL, dimension_id TEXT NOT NULL, dimension_name TEXT,
        document_count INTEGER NOT NULL DEFAULT 0, basis_amount NUMERIC(16,2) NOT NULL,
        bonus_amount NUMERIC(16,2) NOT NULL, currency TEXT NOT NULL DEFAULT 'EUR',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), UNIQUE (tenant_id,run_id,line_no)
      );
      CREATE INDEX IF NOT EXISTS ix_l3_bonus_lines_tenant_run
        ON domain_reporting.l3_bonus_run_lines (tenant_id, run_id, line_no);
    """)


def downgrade() -> None:
    op.execute("""
      DROP INDEX IF EXISTS domain_compliance.ix_sanctions_checks_tenant_scope_time;
      ALTER TABLE domain_compliance.sanctions_checks
        DROP COLUMN IF EXISTS checked_by,
        DROP COLUMN IF EXISTS entity_ref,
        DROP COLUMN IF EXISTS scope,
        DROP COLUMN IF EXISTS tenant_id;
      DROP TABLE IF EXISTS domain_ops.ops_chargen_audit;
      DROP TABLE IF EXISTS domain_reporting.l3_bonus_run_lines;
      DROP TABLE IF EXISTS domain_reporting.l3_bonus_runs;
      DROP INDEX IF EXISTS domain_ops.ix_ops_chargen_tenant_status;
      ALTER TABLE domain_ops.ops_chargen
        DROP COLUMN IF EXISTS anerkennungs_nr,
        DROP COLUMN IF EXISTS lieferanten_charge,
        DROP COLUMN IF EXISTS tenant_id;
    """)
