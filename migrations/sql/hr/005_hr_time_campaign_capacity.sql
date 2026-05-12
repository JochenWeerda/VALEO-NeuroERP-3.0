CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.campaign_capacity_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    campaign_code TEXT NOT NULL,
    name TEXT NOT NULL,
    period_from DATE NOT NULL,
    period_to DATE NOT NULL,
    location_code TEXT NOT NULL DEFAULT 'main',
    role_demand JSONB NOT NULL DEFAULT '{}'::jsonb,
    expected_volume NUMERIC(12,2),
    status TEXT NOT NULL DEFAULT 'planned',
    findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT campaign_capacity_period_ck CHECK (period_to >= period_from),
    CONSTRAINT campaign_capacity_status_ck CHECK (status IN ('planned', 'warning', 'blocked'))
);

CREATE INDEX IF NOT EXISTS campaign_capacity_tenant_period_idx
    ON domain_hr.campaign_capacity_plans (tenant_id, period_from, period_to);

COMMENT ON TABLE domain_hr.campaign_capacity_plans IS 'Season and campaign capacity plans with HR-Time staffing findings';
