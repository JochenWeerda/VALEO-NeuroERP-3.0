CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id UUID NOT NULL,
    date DATE NOT NULL,
    start TIMESTAMPTZ NOT NULL,
    "end" TIMESTAMPTZ NOT NULL,
    break_minutes INTEGER NOT NULL DEFAULT 0,
    project_id UUID,
    cost_center VARCHAR(100),
    source VARCHAR(20) NOT NULL DEFAULT 'Manual',
    status VARCHAR(20) NOT NULL DEFAULT 'Draft',
    approved_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1,
    created_by UUID,
    updated_by UUID,
    CONSTRAINT time_entries_end_after_start CHECK ("end" > start),
    CONSTRAINT time_entries_break_minutes_positive CHECK (break_minutes >= 0)
);

CREATE INDEX IF NOT EXISTS time_entries_tenant_employee_idx ON time_entries (tenant_id, employee_id);
CREATE INDEX IF NOT EXISTS time_entries_tenant_date_idx ON time_entries (tenant_id, date);
CREATE INDEX IF NOT EXISTS time_entries_tenant_status_idx ON time_entries (tenant_id, status);
CREATE INDEX IF NOT EXISTS time_entries_tenant_start_idx ON time_entries (tenant_id, start);
CREATE INDEX IF NOT EXISTS time_entries_employee_date_range_idx ON time_entries (employee_id, start, "end");
CREATE INDEX IF NOT EXISTS time_entries_tenant_project_idx ON time_entries (tenant_id, project_id);
CREATE UNIQUE INDEX IF NOT EXISTS time_entries_tenant_employee_start_uk ON time_entries (tenant_id, employee_id, start);

COMMENT ON TABLE time_entries IS 'Time tracking entries per employee and tenant (UTC timestamps)';
