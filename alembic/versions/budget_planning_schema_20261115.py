"""Create tenant-bound budget plans and lines.

Revision ID: budget_planning_schema_20261115
Revises: docflow_position_kontrakt_20261110
"""
from alembic import op

revision = "budget_planning_schema_20261115"
down_revision = "docflow_position_kontrakt_20261110"
branch_labels = None
depends_on = None


def upgrade():
    # Existing account unique key uq_coa_id_tenant_bank_gl is owned by its migration.
    op.execute("ALTER TABLE domain_finance.kostenstellen ADD CONSTRAINT uq_kostenstellen_id_tenant_budget UNIQUE (id, tenant_id)")
    op.execute("""CREATE TABLE domain_finance.budget_plans (
        id VARCHAR(36) PRIMARY KEY,
        tenant_id VARCHAR(36) NOT NULL DEFAULT public.rls_current_tenant(),
        plan_year INTEGER NOT NULL CHECK (plan_year BETWEEN 1 AND 9999),
        plan_name VARCHAR(255) NOT NULL CHECK (length(trim(plan_name)) > 0),
        status VARCHAR(20) NOT NULL DEFAULT 'ENTWURF' CHECK (status IN ('ENTWURF', 'GENEHMIGT', 'GESPERRT')),
        CONSTRAINT uq_budget_plans_id_tenant UNIQUE (id, tenant_id)
    )""")
    op.execute("""CREATE TABLE domain_finance.budget_lines (
        id VARCHAR(36) PRIMARY KEY,
        tenant_id VARCHAR(36) NOT NULL DEFAULT public.rls_current_tenant(),
        plan_id VARCHAR(36) NOT NULL,
        account_id VARCHAR NOT NULL,
        kostenstelle_id VARCHAR(36),
        period_month INTEGER NOT NULL CHECK (period_month BETWEEN 1 AND 12),
        budgeted_amount NUMERIC(16,2) NOT NULL,
        CONSTRAINT fk_budget_line_plan FOREIGN KEY (plan_id, tenant_id)
            REFERENCES domain_finance.budget_plans (id, tenant_id),
        CONSTRAINT fk_budget_line_account FOREIGN KEY (account_id, tenant_id)
            REFERENCES domain_erp.chart_of_accounts (id, tenant_id),
        CONSTRAINT fk_budget_line_kostenstelle FOREIGN KEY (kostenstelle_id, tenant_id)
            REFERENCES domain_finance.kostenstellen (id, tenant_id)
    )""")
    op.execute("CREATE INDEX ix_budget_plans_tenant_year ON domain_finance.budget_plans (tenant_id, plan_year)")
    op.execute("CREATE INDEX ix_budget_plans_tenant_status_year ON domain_finance.budget_plans (tenant_id, status, plan_year)")
    op.execute("CREATE INDEX ix_budget_lines_tenant_plan ON domain_finance.budget_lines (tenant_id, plan_id)")
    op.execute("CREATE INDEX ix_budget_lines_tenant_account ON domain_finance.budget_lines (tenant_id, account_id)")
    op.execute("CREATE INDEX ix_budget_lines_tenant_kostenstelle ON domain_finance.budget_lines (tenant_id, kostenstelle_id)")
    for table in ("domain_finance.budget_plans", "domain_finance.budget_lines"):
        own = "tenant_id = public.rls_current_tenant()"
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({own})")
        op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({own})")
        op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({own}) WITH CHECK ({own})")
        op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({own})")
        op.execute(f"""DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_app') THEN
                GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO valeo_app;
            END IF;
        END $$""")


def downgrade():
    op.execute("DROP TABLE domain_finance.budget_lines")
    op.execute("DROP TABLE domain_finance.budget_plans")
    op.execute("ALTER TABLE domain_finance.kostenstellen DROP CONSTRAINT uq_kostenstellen_id_tenant_budget")
