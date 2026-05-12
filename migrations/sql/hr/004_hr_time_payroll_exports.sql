CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.payroll_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    period_from DATE NOT NULL,
    period_to DATE NOT NULL,
    target_system TEXT NOT NULL DEFAULT 'datev',
    status TEXT NOT NULL DEFAULT 'blocked',
    items JSONB NOT NULL DEFAULT '[]'::jsonb,
    blockers JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    CONSTRAINT payroll_exports_period_ck CHECK (period_to >= period_from),
    CONSTRAINT payroll_exports_status_ck CHECK (status IN ('ready', 'blocked', 'exported'))
);

CREATE INDEX IF NOT EXISTS payroll_exports_tenant_period_idx
    ON domain_hr.payroll_exports (tenant_id, period_from, period_to);

COMMENT ON TABLE domain_hr.payroll_exports IS 'Payroll export packages generated from approved HR-Time entries';
