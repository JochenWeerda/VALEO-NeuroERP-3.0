CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.field_service_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_ref TEXT NOT NULL,
    customer_ref TEXT NOT NULL,
    territory_code TEXT NOT NULL,
    campaign_code TEXT,
    visit_type TEXT NOT NULL DEFAULT 'consulting',
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT field_service_range_ck CHECK (ends_at > starts_at),
    CONSTRAINT field_service_status_ck CHECK (status IN ('planned', 'warning', 'blocked', 'cancelled'))
);

CREATE INDEX IF NOT EXISTS field_service_tenant_employee_time_idx
    ON domain_hr.field_service_plans (tenant_id, employee_ref, starts_at, ends_at);

COMMENT ON TABLE domain_hr.field_service_plans IS 'Field service and agronomy visit plans connected to HR-Time availability';
