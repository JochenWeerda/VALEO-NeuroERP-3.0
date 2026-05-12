CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.calendar_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    source_system TEXT NOT NULL DEFAULT 'valeo',
    provider TEXT NOT NULL DEFAULT 'internal',
    external_event_ref TEXT,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    employee_ref TEXT,
    resource_ref TEXT,
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'Europe/Berlin',
    visibility TEXT NOT NULL DEFAULT 'team',
    status TEXT NOT NULL DEFAULT 'confirmed',
    sync_state TEXT NOT NULL DEFAULT 'local',
    conflict_level TEXT NOT NULL DEFAULT 'none',
    source_ref TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT calendar_events_range_ck CHECK (ends_at > starts_at),
    CONSTRAINT calendar_events_visibility_ck CHECK (visibility IN ('public', 'team', 'private', 'busy_only')),
    CONSTRAINT calendar_events_sync_state_ck CHECK (sync_state IN ('local', 'pending', 'synced', 'failed')),
    CONSTRAINT calendar_events_conflict_level_ck CHECK (conflict_level IN ('none', 'warning', 'blocker'))
);

CREATE INDEX IF NOT EXISTS calendar_events_tenant_time_idx
    ON domain_hr.calendar_events (tenant_id, starts_at, ends_at);
CREATE INDEX IF NOT EXISTS calendar_events_tenant_employee_idx
    ON domain_hr.calendar_events (tenant_id, employee_ref);
CREATE INDEX IF NOT EXISTS calendar_events_tenant_type_idx
    ON domain_hr.calendar_events (tenant_id, event_type);

COMMENT ON TABLE domain_hr.calendar_events IS 'Provider-neutral HR-Time calendar events and busy blockers';
