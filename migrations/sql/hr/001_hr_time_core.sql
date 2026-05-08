CREATE SCHEMA IF NOT EXISTS domain_hr;
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS domain_hr.employee_time_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_ref TEXT NOT NULL,
    display_name TEXT NOT NULL,
    role_code TEXT NOT NULL DEFAULT 'employee',
    role_label TEXT NOT NULL DEFAULT 'Mitarbeiter',
    location_code TEXT NOT NULL DEFAULT 'main',
    department TEXT NOT NULL DEFAULT 'Allgemein',
    manager_ref TEXT,
    employment_type TEXT NOT NULL DEFAULT 'full_time',
    weekly_hours NUMERIC(5,2) NOT NULL DEFAULT 40.00,
    time_model TEXT NOT NULL DEFAULT 'standard',
    cost_center TEXT,
    payroll_group TEXT,
    qualifications JSONB NOT NULL DEFAULT '[]'::jsonb,
    can_drive BOOLEAN NOT NULL DEFAULT FALSE,
    driver_card_id TEXT,
    vehicle_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
    calendar_provider TEXT NOT NULL DEFAULT 'none',
    status TEXT NOT NULL DEFAULT 'active',
    source_system TEXT NOT NULL DEFAULT 'valeo',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    updated_by TEXT,
    CONSTRAINT employee_time_profiles_status_ck CHECK (status IN ('active', 'inactive', 'on_leave')),
    CONSTRAINT employee_time_profiles_employment_type_ck CHECK (employment_type IN ('full_time', 'part_time', 'temp', 'seasonal', 'contractor')),
    CONSTRAINT employee_time_profiles_time_model_ck CHECK (time_model IN ('standard', 'shift', 'driver', 'field_service', 'seasonal', 'flex'))
);

CREATE UNIQUE INDEX IF NOT EXISTS employee_time_profiles_tenant_employee_uk
    ON domain_hr.employee_time_profiles (tenant_id, employee_ref);
CREATE INDEX IF NOT EXISTS employee_time_profiles_tenant_role_idx
    ON domain_hr.employee_time_profiles (tenant_id, role_code);
CREATE INDEX IF NOT EXISTS employee_time_profiles_tenant_location_idx
    ON domain_hr.employee_time_profiles (tenant_id, location_code);
CREATE INDEX IF NOT EXISTS employee_time_profiles_tenant_status_idx
    ON domain_hr.employee_time_profiles (tenant_id, status);

CREATE TABLE IF NOT EXISTS domain_hr.time_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_ref TEXT NOT NULL,
    entry_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    hours NUMERIC(6,2) NOT NULL DEFAULT 0,
    entry_type TEXT NOT NULL DEFAULT 'Arbeit',
    source TEXT NOT NULL DEFAULT 'manual',
    status TEXT NOT NULL DEFAULT 'Draft',
    cost_center TEXT,
    work_area TEXT,
    correction_reason TEXT,
    notes TEXT,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    updated_by TEXT,
    audit_ref TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT time_entries_hours_positive_ck CHECK (hours >= 0)
);

ALTER TABLE domain_hr.time_entries
    ADD COLUMN IF NOT EXISTS source TEXT NOT NULL DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'Draft',
    ADD COLUMN IF NOT EXISTS cost_center TEXT,
    ADD COLUMN IF NOT EXISTS work_area TEXT,
    ADD COLUMN IF NOT EXISTS correction_reason TEXT,
    ADD COLUMN IF NOT EXISTS approved_by TEXT,
    ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS created_by TEXT,
    ADD COLUMN IF NOT EXISTS updated_by TEXT,
    ADD COLUMN IF NOT EXISTS audit_ref TEXT,
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

CREATE INDEX IF NOT EXISTS time_entries_tenant_employee_date_idx
    ON domain_hr.time_entries (tenant_id, employee_ref, entry_date);
CREATE INDEX IF NOT EXISTS time_entries_tenant_status_idx
    ON domain_hr.time_entries (tenant_id, status);
CREATE INDEX IF NOT EXISTS time_entries_tenant_source_idx
    ON domain_hr.time_entries (tenant_id, source);

CREATE TABLE IF NOT EXISTS domain_hr.driver_time_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    employee_ref TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'manual',
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER NOT NULL,
    tour_ref TEXT,
    vehicle_ref TEXT,
    location_ref TEXT,
    correction_status TEXT NOT NULL DEFAULT 'none',
    correction_reason TEXT,
    audit_ref TEXT,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT,
    updated_by TEXT,
    CONSTRAINT driver_time_events_range_ck CHECK (ends_at > starts_at),
    CONSTRAINT driver_time_events_duration_ck CHECK (duration_minutes >= 0)
);

CREATE INDEX IF NOT EXISTS driver_time_events_tenant_employee_date_idx
    ON domain_hr.driver_time_events (tenant_id, employee_ref, event_date);
CREATE INDEX IF NOT EXISTS driver_time_events_tenant_tour_idx
    ON domain_hr.driver_time_events (tenant_id, tour_ref);
CREATE INDEX IF NOT EXISTS driver_time_events_tenant_vehicle_idx
    ON domain_hr.driver_time_events (tenant_id, vehicle_ref);

COMMENT ON TABLE domain_hr.employee_time_profiles IS 'Canonical HR-Time profile per employee for scheduling, payroll and driver-time planning';
COMMENT ON TABLE domain_hr.time_entries IS 'Canonical working time and absence entries with approval, correction and audit metadata';
COMMENT ON TABLE domain_hr.driver_time_events IS 'Driver-specific work, driving, break, rest and tachograph/telematics events';
