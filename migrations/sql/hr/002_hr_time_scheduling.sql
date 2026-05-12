CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.shifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
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
    CONSTRAINT shifts_status_ck CHECK (status IN ('planned', 'warning', 'blocked', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS shifts_tenant_date_idx
    ON domain_hr.shifts (tenant_id, shift_date);
CREATE INDEX IF NOT EXISTS shifts_tenant_location_idx
    ON domain_hr.shifts (tenant_id, location_code);
CREATE INDEX IF NOT EXISTS shifts_tenant_status_idx
    ON domain_hr.shifts (tenant_id, status);

COMMENT ON TABLE domain_hr.shifts IS 'Planned HR-Time shifts and work assignments with qualification and absence conflicts';
