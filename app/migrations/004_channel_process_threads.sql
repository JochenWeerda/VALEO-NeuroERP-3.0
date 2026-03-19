CREATE TABLE IF NOT EXISTS domain_shared.channel_process_threads (
    thread_id VARCHAR PRIMARY KEY,
    kanal VARCHAR(32) NOT NULL,
    tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
    process_definition_key VARCHAR(120) NOT NULL,
    command_name VARCHAR(120) NOT NULL,
    aggregate_type VARCHAR(120) NOT NULL,
    aggregate_id VARCHAR(120) NOT NULL,
    rolle VARCHAR(120) NOT NULL,
    issuer_type VARCHAR(32) NOT NULL,
    employee_ref VARCHAR(120),
    channel_user_id VARCHAR(120),
    request_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(40) NOT NULL,
    execution JSONB NOT NULL DEFAULT '{}'::jsonb,
    approval_requirement JSONB,
    approval_record JSONB,
    message TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_channel_process_threads_tenant
    ON domain_shared.channel_process_threads (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_channel_process_threads_status
    ON domain_shared.channel_process_threads (status, is_active);

CREATE INDEX IF NOT EXISTS idx_channel_process_threads_process
    ON domain_shared.channel_process_threads (process_definition_key, aggregate_type, aggregate_id);

CREATE TABLE IF NOT EXISTS domain_shared.channel_thread_audit_items (
    id BIGSERIAL PRIMARY KEY,
    thread_id VARCHAR NOT NULL REFERENCES domain_shared.channel_process_threads(thread_id) ON DELETE CASCADE,
    position INTEGER NOT NULL DEFAULT 0,
    audit_type VARCHAR(80) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_channel_thread_audit_items_thread
    ON domain_shared.channel_thread_audit_items (thread_id, position);
